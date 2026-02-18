"""
Insolvency Prediction Model V2 - Enhanced with Feature Engineering.

This module contains an improved XGBoost-based machine learning model for predicting
company insolvency/bankruptcy with:
- Advanced feature engineering (derived ratios, interaction features)
- Hyperparameter-tuned XGBoost
- Cross-validation for robust evaluation
- SHAP-based explanations for all features
"""

import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)
from sklearn.preprocessing import StandardScaler


class InsolvencyPredictorV2:
    """
    Enhanced XGBoost-based model for predicting company insolvency/bankruptcy risk.

    Features:
    - Advanced feature engineering with derived financial metrics
    - Fine-tuned XGBoost parameters for high accuracy
    - Cross-validation for robust performance estimation
    - SHAP-based explanations for interpretability
    """

    # Base feature columns from input data
    BASE_FEATURES = [
        "working_capital_to_total_assets",
        "retained_earnings_to_total_assets",
        "ebit_to_total_assets",
        "market_value_equity_to_total_liabilities",
        "sales_to_total_assets",
        "current_ratio",
        "quick_ratio",
        "debt_to_equity",
        "interest_coverage",
        "net_profit_margin",
        "return_on_assets",
        "return_on_equity",
    ]

    # Altman Z-score coefficients
    ALTMAN_COEFFICIENTS = {
        "working_capital_to_total_assets": 1.2,
        "retained_earnings_to_total_assets": 1.4,
        "ebit_to_total_assets": 3.3,
        "market_value_equity_to_total_liabilities": 0.6,
        "sales_to_total_assets": 1.0,
    }

    def __init__(self, random_state: int = 42):
        """Initialize the InsolvencyPredictorV2."""
        self.random_state = random_state
        self.model: xgb.XGBClassifier | None = None
        self.explainer: shap.TreeExplainer | None = None
        self.scaler: StandardScaler | None = None
        self.is_fitted = False
        self.metrics: dict[str, float] = {}
        self.feature_names: list[str] = []
        self.cv_scores: list[float] = []

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create derived features for more nuanced analysis.

        Args:
            df: DataFrame with base features

        Returns:
            DataFrame with base + engineered features
        """
        X = df.copy()

        # 1. Altman Z-Score (critical bankruptcy predictor)
        X['altman_z_score'] = (
            1.2 * X['working_capital_to_total_assets'] +
            1.4 * X['retained_earnings_to_total_assets'] +
            3.3 * X['ebit_to_total_assets'] +
            0.6 * X['market_value_equity_to_total_liabilities'] +
            1.0 * X['sales_to_total_assets']
        )

        # 2. Z-Score zone indicators (Safe: >2.99, Grey: 1.81-2.99, Distress: <1.81)
        X['z_score_safe'] = (X['altman_z_score'] > 2.99).astype(float)
        X['z_score_grey'] = ((X['altman_z_score'] >= 1.81) & (X['altman_z_score'] <= 2.99)).astype(float)
        X['z_score_distress'] = (X['altman_z_score'] < 1.81).astype(float)

        # 3. Liquidity Stress Indicators
        X['liquidity_gap'] = X['current_ratio'] - X['quick_ratio']  # Inventory dependence
        X['severe_liquidity_stress'] = (X['current_ratio'] < 1.0).astype(float)
        X['moderate_liquidity_stress'] = ((X['current_ratio'] >= 1.0) & (X['current_ratio'] < 1.5)).astype(float)

        # 4. Leverage Risk Indicators
        X['high_leverage'] = (X['debt_to_equity'] > 2.0).astype(float)
        X['extreme_leverage'] = (X['debt_to_equity'] > 4.0).astype(float)
        X['leverage_coverage_ratio'] = X['interest_coverage'] / (X['debt_to_equity'] + 0.1)

        # 5. Profitability Distress Indicators
        X['negative_profit'] = (X['net_profit_margin'] < 0).astype(float)
        X['negative_roa'] = (X['return_on_assets'] < 0).astype(float)
        X['negative_roe'] = (X['return_on_equity'] < 0).astype(float)
        X['profitability_score'] = (
            X['net_profit_margin'] + X['return_on_assets'] + X['return_on_equity']
        ) / 3

        # 6. Working Capital Health
        X['negative_working_capital'] = (X['working_capital_to_total_assets'] < 0).astype(float)
        X['working_capital_trend'] = X['working_capital_to_total_assets'] * X['sales_to_total_assets']

        # 7. Asset Efficiency Metrics
        X['asset_utilization'] = X['sales_to_total_assets'] * X['ebit_to_total_assets']
        X['capital_efficiency'] = X['return_on_assets'] / (X['debt_to_equity'] + 0.5)

        # 8. Coverage Ratios
        X['interest_coverage_safe'] = (X['interest_coverage'] > 3.0).astype(float)
        X['interest_coverage_danger'] = (X['interest_coverage'] < 1.5).astype(float)

        # 9. Interaction Features (capture complex relationships)
        X['leverage_liquidity_interaction'] = X['debt_to_equity'] * (1 / (X['current_ratio'] + 0.1))
        X['profit_leverage_interaction'] = X['net_profit_margin'] * (1 / (X['debt_to_equity'] + 0.1))
        X['z_score_leverage_interaction'] = X['altman_z_score'] / (X['debt_to_equity'] + 0.5)

        # 10. Composite Risk Scores
        X['financial_distress_score'] = (
            X['negative_working_capital'] +
            X['severe_liquidity_stress'] +
            X['high_leverage'] +
            X['negative_profit'] +
            X['interest_coverage_danger']
        )

        X['financial_health_score'] = (
            X['z_score_safe'] +
            X['interest_coverage_safe'] +
            (X['current_ratio'] > 2.0).astype(float) +
            (X['debt_to_equity'] < 1.0).astype(float) +
            (X['net_profit_margin'] > 0.05).astype(float)
        )

        # 11. Retained Earnings Indicators (accumulated profits/losses)
        X['negative_retained_earnings'] = (X['retained_earnings_to_total_assets'] < 0).astype(float)
        X['strong_retained_earnings'] = (X['retained_earnings_to_total_assets'] > 0.3).astype(float)

        # 12. Market Value Indicators
        X['low_market_value'] = (X['market_value_equity_to_total_liabilities'] < 1.0).astype(float)
        X['strong_market_value'] = (X['market_value_equity_to_total_liabilities'] > 2.0).astype(float)

        # Handle any infinities or NaNs
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median())

        return X

    def train(
        self,
        df: pd.DataFrame,
        target_col: str = "is_insolvent",
        test_size: float = 0.2,
        use_cv: bool = True,
    ) -> dict[str, float]:
        """
        Train the enhanced XGBoost model with feature engineering.

        Args:
            df: DataFrame containing features and target column
            target_col: Name of the target column
            test_size: Fraction of data to use for testing
            use_cv: Whether to perform cross-validation

        Returns:
            Dictionary containing evaluation metrics
        """
        # Identify available base features
        available_features = [col for col in self.BASE_FEATURES if col in df.columns]

        if len(available_features) < len(self.BASE_FEATURES):
            missing = set(self.BASE_FEATURES) - set(available_features)
            print(f"Warning: Missing features: {missing}")

        # Extract base features and target
        X_base = df[available_features].copy()
        y = df[target_col].copy()

        # Engineer features
        print("Engineering features...")
        X = self._engineer_features(X_base)
        self.feature_names = list(X.columns)
        print(f"Total features after engineering: {len(self.feature_names)}")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=y
        )

        # Calculate class weights
        n_negative = (y_train == 0).sum()
        n_positive = (y_train == 1).sum()
        scale_pos_weight = n_negative / n_positive if n_positive > 0 else 1.0

        # Fine-tuned XGBoost model
        print("Training XGBoost model...")
        self.model = xgb.XGBClassifier(
            # Tree parameters
            n_estimators=200,          # More trees for complex patterns
            max_depth=6,               # Deeper trees to capture interactions
            min_child_weight=5,        # Prevent overfitting on small leaves
            gamma=0.1,                 # Minimum loss reduction for split

            # Learning parameters
            learning_rate=0.05,        # Lower learning rate, more trees
            subsample=0.8,             # Row sampling
            colsample_bytree=0.8,      # Feature sampling per tree
            colsample_bylevel=0.8,     # Feature sampling per level

            # Regularization (prevent overfitting)
            reg_alpha=0.5,             # L1 regularization
            reg_lambda=2.0,            # L2 regularization (increased)

            # Other
            scale_pos_weight=scale_pos_weight,
            random_state=self.random_state,
            eval_metric='logloss',
            early_stopping_rounds=20,
            n_jobs=-1,
        )

        # Train with early stopping
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        print(f"Best iteration: {self.model.best_iteration}")

        # Create SHAP explainer
        print("Creating SHAP explainer...")
        self.explainer = shap.TreeExplainer(self.model)
        self.is_fitted = True

        # Evaluate on test set
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        self.metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_pred_proba),
        }

        # Cross-validation for robust estimate (use a fresh model without early stopping)
        if use_cv:
            print("Performing 5-fold cross-validation...")
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state)

            # Create a model without early stopping for CV
            cv_model = xgb.XGBClassifier(
                n_estimators=self.model.best_iteration + 1,  # Use best iteration from training
                max_depth=6,
                min_child_weight=5,
                gamma=0.1,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                colsample_bylevel=0.8,
                reg_alpha=0.5,
                reg_lambda=2.0,
                scale_pos_weight=scale_pos_weight,
                random_state=self.random_state,
                eval_metric='logloss',
                n_jobs=-1,
            )

            self.cv_scores = cross_val_score(
                cv_model, X, y, cv=cv, scoring='roc_auc', n_jobs=-1
            )
            self.metrics['cv_roc_auc_mean'] = self.cv_scores.mean()
            self.metrics['cv_roc_auc_std'] = self.cv_scores.std()

        # Print classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Healthy', 'Distressed']))

        # Print confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(f"  TN: {cm[0,0]:4d}  FP: {cm[0,1]:4d}")
        print(f"  FN: {cm[1,0]:4d}  TP: {cm[1,1]:4d}")

        # Save model
        self._save_model()

        return self.metrics

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate predictions with risk assessment.

        Args:
            df: DataFrame containing base feature columns

        Returns:
            DataFrame with probability, risk category, and time estimates
        """
        if not self.is_fitted or self.model is None:
            raise ValueError("Model must be trained before making predictions")

        # Get available features
        available_features = [col for col in self.BASE_FEATURES if col in df.columns]
        X_base = df[available_features].copy()

        # Engineer features
        X = self._engineer_features(X_base)

        # Ensure all trained features are present
        for col in self.feature_names:
            if col not in X.columns:
                X[col] = 0

        X = X[self.feature_names]

        # Get probabilities
        raw_probabilities = self.model.predict_proba(X)[:, 1]

        # Apply probability smoothing (map to 2%-98% range)
        probabilities = 0.02 + 0.96 * raw_probabilities

        # Calculate Altman Z-Score for additional context
        z_scores = (
            1.2 * X_base['working_capital_to_total_assets'] +
            1.4 * X_base['retained_earnings_to_total_assets'] +
            3.3 * X_base['ebit_to_total_assets'] +
            0.6 * X_base['market_value_equity_to_total_liabilities'] +
            1.0 * X_base['sales_to_total_assets']
        )

        # Categorize risk
        risk_categories = []
        for prob in probabilities:
            if prob < 0.25:
                risk_categories.append("Low")
            elif prob < 0.55:
                risk_categories.append("Medium")
            else:
                risk_categories.append("High")

        # Estimate time to potential event
        estimated_times = []
        for prob in probabilities:
            if prob < 0.15:
                estimated_times.append(None)
            else:
                years = max(1, int(5 * (1 - prob) + 0.5))
                estimated_times.append(years)

        # Z-Score zones
        z_zones = []
        for z in z_scores:
            if z > 2.99:
                z_zones.append("Safe")
            elif z >= 1.81:
                z_zones.append("Grey")
            else:
                z_zones.append("Distress")

        results = pd.DataFrame({
            "probability_of_distress": np.round(probabilities, 4),
            "risk_category": risk_categories,
            "estimated_time_to_event": estimated_times,
            "z_score": np.round(z_scores.values, 4),
            "z_score_zone": z_zones,
        })

        return results

    def explain_prediction(self, df: pd.DataFrame, index: int = 0) -> dict[str, Any]:
        """
        Explain a single prediction using SHAP values.

        Args:
            df: DataFrame containing feature columns
            index: Index of the sample to explain

        Returns:
            Dictionary with SHAP values and top risk drivers
        """
        if not self.is_fitted or self.explainer is None:
            raise ValueError("Model must be trained before explaining predictions")

        # Get available features
        available_features = [col for col in self.BASE_FEATURES if col in df.columns]
        X_base = df[available_features].copy()

        # Engineer features
        X = self._engineer_features(X_base)

        # Ensure all trained features are present
        for col in self.feature_names:
            if col not in X.columns:
                X[col] = 0

        X = X[self.feature_names]

        # Get single sample
        sample = X.iloc[[index]]

        # Calculate SHAP values
        shap_values = self.explainer.shap_values(sample)

        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        shap_values = shap_values.flatten()

        # Create feature importance dictionary
        shap_dict = dict(zip(self.feature_names, shap_values))

        # Sort by absolute importance
        sorted_features = sorted(
            shap_dict.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        # Get top risk drivers with context
        top_drivers = []
        for feature, shap_val in sorted_features[:15]:
            original_value = sample[feature].values[0]
            impact = "increases_risk" if shap_val > 0 else "decreases_risk"

            top_drivers.append({
                "feature": feature,
                "shap_value": float(shap_val),
                "original_value": float(original_value),
                "impact": impact,
            })

        return {
            "shap_values": shap_dict,
            "top_risk_drivers": top_drivers,
            "base_value": float(self.explainer.expected_value) if not isinstance(
                self.explainer.expected_value, np.ndarray
            ) else float(self.explainer.expected_value[1]),
            "prediction_value": float(self.model.predict_proba(sample)[0, 1]),
        }

    def get_feature_importance(self) -> dict[str, float]:
        """Get feature importance scores from the model."""
        if not self.is_fitted:
            raise ValueError("Model must be trained first")

        importance = self.model.feature_importances_
        return dict(sorted(
            zip(self.feature_names, importance),
            key=lambda x: x[1],
            reverse=True
        ))

    def _save_model(self) -> None:
        """Save the trained model and components."""
        save_dir = Path(__file__).parent / "saved_models"
        save_dir.mkdir(exist_ok=True)

        model_data = {
            "model": self.model,
            "explainer": self.explainer,
            "feature_names": self.feature_names,
            "metrics": self.metrics,
            "cv_scores": self.cv_scores,
        }

        with open(save_dir / "insolvency_model_v2.pkl", "wb") as f:
            pickle.dump(model_data, f)

        print(f"Model saved to {save_dir / 'insolvency_model_v2.pkl'}")

    def load_model(self) -> bool:
        """Load a previously trained model."""
        model_path = Path(__file__).parent / "saved_models" / "insolvency_model_v2.pkl"

        if not model_path.exists():
            return False

        with open(model_path, "rb") as f:
            model_data = pickle.load(f)

        self.model = model_data["model"]
        self.explainer = model_data["explainer"]
        self.feature_names = model_data["feature_names"]
        self.metrics = model_data["metrics"]
        self.cv_scores = model_data.get("cv_scores", [])
        self.is_fitted = True

        return True


# For backward compatibility, also export as the original name
InsolvencyPredictor = InsolvencyPredictorV2
