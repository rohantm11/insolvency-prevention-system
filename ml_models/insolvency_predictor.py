"""
Insolvency Prediction Model.

This module contains an XGBoost-based machine learning model for predicting
company insolvency/bankruptcy based on financial indicators including
Altman Z-score components.
"""

import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)


class InsolvencyPredictor:
    """
    XGBoost-based model for predicting company insolvency/bankruptcy risk.

    Uses financial ratios including Altman Z-score components to predict
    the probability of financial distress. Includes SHAP-based explanations
    for model interpretability.
    """

    # Feature columns used for prediction
    FEATURE_COLUMNS = [
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

    # Altman Z-score coefficients (original formula for public manufacturing companies)
    ALTMAN_COEFFICIENTS = {
        "working_capital_to_total_assets": 1.2,
        "retained_earnings_to_total_assets": 1.4,
        "ebit_to_total_assets": 3.3,
        "market_value_equity_to_total_liabilities": 0.6,
        "sales_to_total_assets": 1.0,
    }

    def __init__(self, random_state: int = 42):
        """
        Initialize the InsolvencyPredictor.

        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.model: xgb.XGBClassifier | None = None
        self.explainer: shap.TreeExplainer | None = None
        self.is_fitted = False
        self.metrics: dict[str, float] = {}
        self.feature_names: list[str] = []

    def train(
        self,
        df: pd.DataFrame,
        target_col: str = "is_bankrupt",
        test_size: float = 0.2,
    ) -> dict[str, float]:
        """
        Train the XGBoost model on financial data.

        Args:
            df: DataFrame containing features and target column
            target_col: Name of the target column (default: 'is_bankrupt')
            test_size: Fraction of data to use for testing (default: 0.2)

        Returns:
            Dictionary containing evaluation metrics
        """
        # Identify available feature columns
        self.feature_names = [col for col in self.FEATURE_COLUMNS if col in df.columns]

        if not self.feature_names:
            raise ValueError(f"No valid feature columns found in DataFrame. Expected: {self.FEATURE_COLUMNS}")

        X = df[self.feature_names].copy()
        y = df[target_col].copy()

        # Handle missing values
        X = X.fillna(X.median())

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=y
        )

        # Calculate scale_pos_weight for class imbalance
        n_negative = (y_train == 0).sum()
        n_positive = (y_train == 1).sum()
        scale_pos_weight = n_negative / n_positive if n_positive > 0 else 1.0

        # Initialize and train XGBoost model with regularization for better calibration
        self.model = xgb.XGBClassifier(
            n_estimators=50,  # Fewer trees to reduce overfitting
            max_depth=3,  # Shallower trees for less extreme predictions
            learning_rate=0.05,  # Lower learning rate for smoother predictions
            scale_pos_weight=scale_pos_weight,
            random_state=self.random_state,
            eval_metric="logloss",
            reg_alpha=0.5,  # L1 regularization
            reg_lambda=1.0,  # L2 regularization
            min_child_weight=3,  # Require more samples per leaf
            subsample=0.8,  # Use 80% of data per tree
            colsample_bytree=0.8,  # Use 80% of features per tree
        )

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        # Create SHAP explainer
        self.explainer = shap.TreeExplainer(self.model)
        self.is_fitted = True

        # Calculate metrics on test set
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        self.metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_pred_proba),
        }

        return self.metrics

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate predictions with risk assessment.

        Args:
            df: DataFrame containing feature columns

        Returns:
            DataFrame with columns:
                - probability_of_distress: Probability of bankruptcy (0-1)
                - risk_category: 'Low', 'Medium', or 'High'
                - estimated_time_to_event: Estimated years until potential bankruptcy
        """
        if not self.is_fitted or self.model is None:
            raise ValueError("Model must be trained before making predictions")

        X = df[self.feature_names].copy()
        X = X.fillna(X.median())

        # Get probability of distress (class 1)
        raw_probabilities = self.model.predict_proba(X)[:, 1]

        # Apply probability smoothing to avoid extreme 0.0 and 1.0 values
        # Uses a sigmoid-based transformation that compresses extremes
        # This makes probabilities more realistic (e.g., 0.02-0.98 range)
        probabilities = 0.02 + 0.96 * raw_probabilities  # Map to [0.02, 0.98]

        # Categorize risk
        risk_categories = []
        for prob in probabilities:
            if prob < 0.3:
                risk_categories.append("Low")
            elif prob < 0.7:
                risk_categories.append("Medium")
            else:
                risk_categories.append("High")

        # Estimate time to event (higher risk = sooner)
        # Scale: probability 1.0 -> 1 year, probability 0.0 -> 5+ years
        estimated_times = []
        for prob in probabilities:
            if prob < 0.1:
                estimated_times.append(None)  # Low risk, no imminent threat
            else:
                # Inverse relationship: higher probability = shorter time
                years = max(1, int(5 * (1 - prob) + 0.5))
                estimated_times.append(years)

        results = pd.DataFrame({
            "probability_of_distress": np.round(probabilities, 4),
            "risk_category": risk_categories,
            "estimated_time_to_event": estimated_times,
        })

        return results

    def explain_prediction(
        self,
        df: pd.DataFrame,
        index: int = 0
    ) -> dict[str, Any]:
        """
        Explain a single prediction using SHAP values.

        Args:
            df: DataFrame containing feature columns
            index: Index of the sample to explain (default: 0)

        Returns:
            Dictionary containing:
                - shap_values: Raw SHAP values for each feature
                - top_risk_drivers: Top 10 features contributing to risk (sorted)
                - base_value: Expected model output
                - prediction_value: Actual prediction for this sample
        """
        if not self.is_fitted or self.explainer is None:
            raise ValueError("Model must be trained before explaining predictions")

        X = df[self.feature_names].copy()
        X = X.fillna(X.median())

        # Get single sample
        sample = X.iloc[[index]]

        # Calculate SHAP values
        shap_values = self.explainer.shap_values(sample)

        # For binary classification, shap_values might be a list
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Use class 1 (bankrupt) values

        shap_values = shap_values.flatten()

        # Create feature importance dictionary
        feature_shap = dict(zip(self.feature_names, shap_values))

        # Sort by absolute SHAP value (impact on prediction)
        sorted_features = sorted(
            feature_shap.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        # Get top 10 risk drivers with their values and directions
        top_risk_drivers = []
        for feature_name, shap_value in sorted_features[:10]:
            feature_value = sample[feature_name].values[0]
            direction = "increases" if shap_value > 0 else "decreases"
            top_risk_drivers.append({
                "feature": feature_name,
                "shap_value": round(shap_value, 4),
                "feature_value": round(feature_value, 4),
                "impact": direction,
            })

        return {
            "shap_values": {k: round(v, 4) for k, v in feature_shap.items()},
            "top_risk_drivers": top_risk_drivers,
            "base_value": round(float(self.explainer.expected_value), 4) if not isinstance(
                self.explainer.expected_value, np.ndarray
            ) else round(float(self.explainer.expected_value[1]), 4),
            "prediction_value": round(float(self.model.predict_proba(sample)[0, 1]), 4),
        }

    def calculate_altman_zscore(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the traditional Altman Z-score for each company.

        Z-score = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5

        Where:
            X1 = Working Capital / Total Assets
            X2 = Retained Earnings / Total Assets
            X3 = EBIT / Total Assets
            X4 = Market Value of Equity / Total Liabilities
            X5 = Sales / Total Assets

        Interpretation:
            Z > 2.99: Safe zone
            1.81 < Z < 2.99: Grey zone
            Z < 1.81: Distress zone

        Args:
            df: DataFrame with Altman Z-score component columns

        Returns:
            DataFrame with z_score and z_score_zone columns
        """
        # Check for required columns
        required_cols = list(self.ALTMAN_COEFFICIENTS.keys())
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            raise ValueError(f"Missing required columns for Altman Z-score: {missing_cols}")

        # Calculate Z-score
        z_score = sum(
            df[col] * coef
            for col, coef in self.ALTMAN_COEFFICIENTS.items()
        )

        # Determine zone
        zones = []
        for z in z_score:
            if z > 2.99:
                zones.append("Safe")
            elif z > 1.81:
                zones.append("Grey")
            else:
                zones.append("Distress")

        return pd.DataFrame({
            "z_score": np.round(z_score, 4),
            "z_score_zone": zones,
        })

    def save_model(self, path: str | Path) -> None:
        """
        Save the trained model to disk.

        Args:
            path: File path to save the model (will save as .pkl)
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained before saving")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            "model": self.model,
            "feature_names": self.feature_names,
            "metrics": self.metrics,
            "random_state": self.random_state,
        }

        with open(path, "wb") as f:
            pickle.dump(model_data, f)

    def load_model(self, path: str | Path) -> None:
        """
        Load a trained model from disk.

        Args:
            path: File path to load the model from
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        with open(path, "rb") as f:
            model_data = pickle.load(f)

        self.model = model_data["model"]
        self.feature_names = model_data["feature_names"]
        self.metrics = model_data["metrics"]
        self.random_state = model_data.get("random_state", 42)  # Default if not present

        # Recreate SHAP explainer
        self.explainer = shap.TreeExplainer(self.model)
        self.is_fitted = True


if __name__ == "__main__":
    from pathlib import Path

    # Paths
    data_path = Path(__file__).parent.parent / "data" / "company_data.csv"
    model_path = Path(__file__).parent / "trained_models" / "insolvency_model.pkl"

    print("=" * 70)
    print("INSOLVENCY PREDICTOR - TRAINING AND EVALUATION")
    print("=" * 70)

    # Load data
    print(f"\nLoading data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"  Total companies: {len(df)}")
    print(f"  Bankruptcy rate: {df['is_bankrupt'].mean():.1%}")

    # Initialize and train model
    print("\n" + "-" * 70)
    print("TRAINING MODEL")
    print("-" * 70)

    predictor = InsolvencyPredictor(random_state=42)
    metrics = predictor.train(df, target_col="is_bankrupt")

    print("\nModel Performance Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric.upper()}: {value:.4f}")

    # Calculate Altman Z-scores
    print("\n" + "-" * 70)
    print("ALTMAN Z-SCORE ANALYSIS")
    print("-" * 70)

    z_scores = predictor.calculate_altman_zscore(df)
    df_with_z = pd.concat([df[["company_id", "company_name", "is_bankrupt"]], z_scores], axis=1)

    print("\nZ-Score Zone Distribution:")
    for zone in ["Safe", "Grey", "Distress"]:
        count = (z_scores["z_score_zone"] == zone).sum()
        print(f"  {zone}: {count} companies ({count/len(df)*100:.1f}%)")

    # Sample predictions
    print("\n" + "-" * 70)
    print("SAMPLE PREDICTIONS")
    print("-" * 70)

    predictions = predictor.predict(df)
    df_results = pd.concat([
        df[["company_id", "company_name", "is_bankrupt"]],
        predictions,
        z_scores
    ], axis=1)

    # Show 5 sample predictions
    print("\nSample Predictions (5 companies):")
    sample_indices = [0, 1, 2, 3, 4]
    for idx in sample_indices:
        row = df_results.iloc[idx]
        print(f"\n  {row['company_name']} ({row['company_id']}):")
        print(f"    Actual Status: {'Bankrupt' if row['is_bankrupt'] == 1 else 'Healthy'}")
        print(f"    Probability of Distress: {row['probability_of_distress']:.1%}")
        print(f"    Risk Category: {row['risk_category']}")
        print(f"    Altman Z-Score: {row['z_score']:.2f} ({row['z_score_zone']})")
        if pd.notna(row['estimated_time_to_event']):
            print(f"    Estimated Time to Event: {int(row['estimated_time_to_event'])} years")

    # Explain a high-risk prediction
    print("\n" + "-" * 70)
    print("PREDICTION EXPLANATION (High-Risk Company)")
    print("-" * 70)

    # Find a high-risk company
    high_risk_idx = df_results[df_results["risk_category"] == "High"].index[0]
    explanation = predictor.explain_prediction(df, index=high_risk_idx)

    company = df_results.iloc[high_risk_idx]
    print(f"\nExplaining prediction for: {company['company_name']}")
    print(f"Probability of Distress: {explanation['prediction_value']:.1%}")
    print(f"Base Value: {explanation['base_value']:.4f}")

    print("\nTop 10 Risk Drivers:")
    for i, driver in enumerate(explanation["top_risk_drivers"], 1):
        print(f"  {i:2d}. {driver['feature']}")
        print(f"      Value: {driver['feature_value']:.4f}, SHAP: {driver['shap_value']:+.4f} ({driver['impact']} risk)")

    # Save model
    print("\n" + "-" * 70)
    print("SAVING MODEL")
    print("-" * 70)

    predictor.save_model(model_path)
    print(f"\nModel saved to: {model_path}")

    # Verify load
    print("\nVerifying model load...")
    new_predictor = InsolvencyPredictor()
    new_predictor.load_model(model_path)
    print("  Model loaded successfully!")
    print(f"  Loaded metrics: {new_predictor.metrics}")

    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
