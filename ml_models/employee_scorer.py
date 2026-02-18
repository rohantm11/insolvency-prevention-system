"""
Employee Scorer Model.

This module contains an XGBoost-based model for predicting employee attrition,
calculating retention scores, and providing layoff recommendations.
"""

import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)


class EmployeeScorer:
    """
    XGBoost-based model for employee attrition prediction and retention scoring.

    Predicts attrition risk, calculates retention scores based on performance
    and satisfaction metrics, and provides layoff recommendations with
    department constraints.
    """

    # Feature columns for prediction (categorical will be encoded)
    FEATURE_COLUMNS = [
        "age",
        "gender",
        "department",
        "job_role",
        "job_level",
        "performance_rating",
        "job_satisfaction",
        "job_involvement",
        "environment_satisfaction",
        "monthly_income",
        "percent_salary_hike",
        "stock_option_level",
        "years_at_company",
        "years_in_current_role",
        "total_working_years",
        "distance_from_home",
        "business_travel",
        "over_time",
    ]

    # Categorical columns requiring encoding
    CATEGORICAL_COLUMNS = [
        "gender",
        "department",
        "job_role",
        "business_travel",
        "over_time",
    ]

    # Retention score weights
    RETENTION_WEIGHTS = {
        "performance": 0.30,
        "job_satisfaction": 0.20,
        "job_involvement": 0.20,
        "tenure_bonus": 0.30,
    }

    def __init__(self, random_state: int = 42):
        """
        Initialize the EmployeeScorer.

        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.model: xgb.XGBClassifier | None = None
        self.explainer: shap.TreeExplainer | None = None
        self.label_encoders: dict[str, LabelEncoder] = {}
        self.is_fitted = False
        self.metrics: dict[str, float] = {}
        self.feature_names: list[str] = []

    def _encode_categorical(
        self,
        df: pd.DataFrame,
        fit: bool = False
    ) -> pd.DataFrame:
        """
        Encode categorical columns using LabelEncoder.

        Args:
            df: DataFrame with categorical columns
            fit: Whether to fit the encoders (True for training)

        Returns:
            DataFrame with encoded categorical columns
        """
        df_encoded = df.copy()

        for col in self.CATEGORICAL_COLUMNS:
            if col in df_encoded.columns:
                if fit:
                    self.label_encoders[col] = LabelEncoder()
                    df_encoded[col] = self.label_encoders[col].fit_transform(
                        df_encoded[col].astype(str)
                    )
                else:
                    if col in self.label_encoders:
                        # Handle unseen categories
                        df_encoded[col] = df_encoded[col].astype(str)
                        known_classes = set(self.label_encoders[col].classes_)
                        df_encoded[col] = df_encoded[col].apply(
                            lambda x: x if x in known_classes else self.label_encoders[col].classes_[0]
                        )
                        df_encoded[col] = self.label_encoders[col].transform(df_encoded[col])

        return df_encoded

    def train(
        self,
        df: pd.DataFrame,
        target_col: str = "attrition",
        test_size: float = 0.2,
    ) -> dict[str, float]:
        """
        Train the XGBoost model on employee data.

        Args:
            df: DataFrame containing features and target column
            target_col: Name of the target column (default: 'attrition')
            test_size: Fraction of data to use for testing (default: 0.2)

        Returns:
            Dictionary containing evaluation metrics
        """
        # Identify available feature columns
        self.feature_names = [col for col in self.FEATURE_COLUMNS if col in df.columns]

        if not self.feature_names:
            raise ValueError(f"No valid feature columns found. Expected: {self.FEATURE_COLUMNS}")

        X = df[self.feature_names].copy()

        # Convert target to binary (Yes=1, No=0)
        y = df[target_col].copy()
        if pd.api.types.is_numeric_dtype(y) and set(pd.unique(y.dropna())).issubset({0, 1}):
            y = y.astype(int)
        else:
            y = (y.astype(str).str.strip().str.lower() == "yes").astype(int)

        # Encode categorical columns
        X = self._encode_categorical(X, fit=True)

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

        # Initialize and train XGBoost model
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            scale_pos_weight=scale_pos_weight,
            random_state=self.random_state,
            eval_metric="logloss",
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
        Generate predictions with retention assessment.

        Args:
            df: DataFrame containing feature columns

        Returns:
            DataFrame with columns:
                - retention_score: Score from 0-100 (higher = more valuable)
                - attrition_probability: Probability of leaving (0-1)
                - attrition_risk: 'Low', 'Medium', or 'High'
                - layoff_priority: 'Low', 'Medium', or 'High' (for cost reduction)
        """
        if not self.is_fitted or self.model is None:
            raise ValueError("Model must be trained before making predictions")

        X = df[self.feature_names].copy()
        X = self._encode_categorical(X, fit=False)
        X = X.fillna(X.median())

        # Get attrition probability
        attrition_proba = self.model.predict_proba(X)[:, 1]

        # Calculate retention scores
        retention_scores = self.calculate_retention_score(df)

        # Categorize attrition risk
        attrition_risk = []
        for prob in attrition_proba:
            if prob < 0.3:
                attrition_risk.append("Low")
            elif prob < 0.6:
                attrition_risk.append("Medium")
            else:
                attrition_risk.append("High")

        # Determine layoff priority (inverse of retention score)
        layoff_priority = []
        for score in retention_scores:
            if score >= 70:
                layoff_priority.append("Low")  # High value = keep
            elif score >= 40:
                layoff_priority.append("Medium")
            else:
                layoff_priority.append("High")  # Low value = consider for layoff

        return pd.DataFrame({
            "retention_score": np.round(retention_scores, 2),
            "attrition_probability": np.round(attrition_proba, 4),
            "attrition_risk": attrition_risk,
            "layoff_priority": layoff_priority,
        })

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
                - top_factors: Top 10 features contributing to prediction
                - base_value: Expected model output
                - prediction_value: Actual prediction for this sample
        """
        if not self.is_fitted or self.explainer is None:
            raise ValueError("Model must be trained before explaining predictions")

        X = df[self.feature_names].copy()
        X = self._encode_categorical(X, fit=False)
        X = X.fillna(X.median())

        # Get single sample
        sample = X.iloc[[index]]

        # Calculate SHAP values
        shap_values = self.explainer.shap_values(sample)

        # For binary classification, shap_values might be a list
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        shap_values = shap_values.flatten()

        # Create feature importance dictionary
        feature_shap = dict(zip(self.feature_names, shap_values))

        # Sort by absolute SHAP value
        sorted_features = sorted(
            feature_shap.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        # Get original values for explanation
        original_row = df.iloc[index]

        # Get top 10 factors
        top_factors = []
        for feature_name, shap_value in sorted_features[:10]:
            original_value = original_row.get(feature_name, sample[feature_name].values[0])
            direction = "increases" if shap_value > 0 else "decreases"
            top_factors.append({
                "feature": feature_name,
                "shap_value": round(shap_value, 4),
                "original_value": original_value,
                "impact": f"{direction} attrition risk",
            })

        return {
            "shap_values": {k: round(v, 4) for k, v in feature_shap.items()},
            "top_factors": top_factors,
            "base_value": round(float(self.explainer.expected_value), 4) if not isinstance(
                self.explainer.expected_value, np.ndarray
            ) else round(float(self.explainer.expected_value[1]), 4),
            "prediction_value": round(float(self.model.predict_proba(sample)[0, 1]), 4),
        }

    def calculate_retention_score(self, df: pd.DataFrame) -> np.ndarray:
        """
        Calculate retention score based on weighted factors.

        Formula:
            - Performance Rating: 30% (scaled from 1-4 to 0-100)
            - Job Satisfaction: 20% (scaled from 1-4 to 0-100)
            - Job Involvement: 20% (scaled from 1-4 to 0-100)
            - Tenure Bonus: up to 30% (based on years at company)

        Args:
            df: DataFrame with employee data

        Returns:
            Array of retention scores (0-100)
        """
        n_samples = len(df)
        scores = np.zeros(n_samples)

        # Performance component (30%)
        if "performance_rating" in df.columns:
            # Scale 1-4 to 0-100
            perf_score = ((df["performance_rating"] - 1) / 3) * 100
            scores += perf_score * self.RETENTION_WEIGHTS["performance"]

        # Job Satisfaction component (20%)
        if "job_satisfaction" in df.columns:
            sat_score = ((df["job_satisfaction"] - 1) / 3) * 100
            scores += sat_score * self.RETENTION_WEIGHTS["job_satisfaction"]

        # Job Involvement component (20%)
        if "job_involvement" in df.columns:
            inv_score = ((df["job_involvement"] - 1) / 3) * 100
            scores += inv_score * self.RETENTION_WEIGHTS["job_involvement"]

        # Tenure Bonus (up to 30%)
        if "years_at_company" in df.columns:
            # Cap tenure bonus at 10 years (full 30%)
            tenure_years = df["years_at_company"].clip(upper=10)
            tenure_score = (tenure_years / 10) * 100
            scores += tenure_score * self.RETENTION_WEIGHTS["tenure_bonus"]

        return np.clip(scores, 0, 100)

    def simulate_layoffs(
        self,
        df: pd.DataFrame,
        budget_cut_percent: float,
        min_per_dept: int = 1
    ) -> pd.DataFrame:
        """
        Simulate layoff recommendations based on budget constraints.

        Uses retention scores and attrition risk to recommend layoffs
        while respecting minimum employees per department.

        Args:
            df: DataFrame with employee data (must include 'department' and 'monthly_income')
            budget_cut_percent: Target budget reduction as percentage (0-100)
            min_per_dept: Minimum employees to retain per department

        Returns:
            DataFrame with layoff recommendations:
                - employee_id: Employee identifier
                - name: Employee name
                - department: Department
                - monthly_income: Monthly salary
                - retention_score: Calculated retention score
                - layoff_recommended: Boolean (True = recommend layoff)
                - layoff_reason: Explanation for recommendation
        """
        if "department" not in df.columns or "monthly_income" not in df.columns:
            raise ValueError("DataFrame must contain 'department' and 'monthly_income' columns")

        # Get predictions
        predictions = self.predict(df)
        df_work = df.copy()
        df_work["retention_score"] = predictions["retention_score"]
        df_work["layoff_priority"] = predictions["layoff_priority"]
        df_work["attrition_probability"] = predictions["attrition_probability"]

        # Calculate target savings
        total_payroll = df_work["monthly_income"].sum()
        target_savings = total_payroll * (budget_cut_percent / 100)

        # Sort by layoff priority (High first) then by retention score (Low first)
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        df_work["priority_rank"] = df_work["layoff_priority"].map(priority_order)
        df_work = df_work.sort_values(
            ["priority_rank", "retention_score"],
            ascending=[True, True]
        )

        # Track department counts
        dept_counts = df_work["department"].value_counts().to_dict()
        dept_remaining = dept_counts.copy()

        # Select employees for layoff (use itertuples for speed; stateful loop required)
        layoff_recommended = []
        layoff_reasons = []
        cumulative_savings = 0

        for row in df_work.itertuples(index=False):
            dept = row.department

            # Check if we've reached target savings
            if cumulative_savings >= target_savings:
                layoff_recommended.append(False)
                layoff_reasons.append("Budget target reached")
                continue

            # Check department minimum
            if dept_remaining[dept] <= min_per_dept:
                layoff_recommended.append(False)
                layoff_reasons.append(f"Department minimum ({min_per_dept}) reached")
                continue

            # Recommend for layoff
            layoff_recommended.append(True)
            dept_remaining[dept] -= 1
            cumulative_savings += row.monthly_income

            # Generate reason
            reasons = []
            if row.retention_score < 40:
                reasons.append("Low retention score")
            if row.layoff_priority == "High":
                reasons.append("High layoff priority")
            if row.attrition_probability > 0.5:
                reasons.append("High attrition risk")
            layoff_reasons.append("; ".join(reasons) if reasons else "Budget optimization")

        df_work["layoff_recommended"] = layoff_recommended
        df_work["layoff_reason"] = layoff_reasons

        # Prepare output
        output_cols = ["employee_id", "name", "department", "monthly_income",
                       "retention_score", "layoff_recommended", "layoff_reason"]
        output_cols = [col for col in output_cols if col in df_work.columns]

        result = df_work[output_cols].sort_values("layoff_recommended", ascending=False)

        # Add summary statistics
        actual_savings = df_work[df_work["layoff_recommended"]]["monthly_income"].sum()
        n_layoffs = df_work["layoff_recommended"].sum()

        print(f"\nLayoff Simulation Summary:")
        print(f"  Target budget cut: {budget_cut_percent:.1f}%")
        print(f"  Target monthly savings: ${target_savings:,.0f}")
        print(f"  Actual monthly savings: ${actual_savings:,.0f}")
        print(f"  Employees affected: {n_layoffs}")
        print(f"  Savings achieved: {(actual_savings/total_payroll)*100:.1f}%")

        return result.reset_index(drop=True)

    def save_model(self, path: str | Path) -> None:
        """
        Save the trained model to disk.

        Args:
            path: File path to save the model
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained before saving")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            "model": self.model,
            "label_encoders": self.label_encoders,
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
        self.label_encoders = model_data.get("label_encoders", {})
        self.feature_names = model_data["feature_names"]
        self.metrics = model_data["metrics"]
        self.random_state = model_data.get("random_state", 42)  # Default if not present

        # Recreate SHAP explainer
        self.explainer = shap.TreeExplainer(self.model)
        self.is_fitted = True


if __name__ == "__main__":
    from pathlib import Path

    # Paths
    data_path = Path(__file__).parent.parent / "data" / "employee_data.csv"
    model_path = Path(__file__).parent / "trained_models" / "employee_model.pkl"

    print("=" * 70)
    print("EMPLOYEE SCORER - TRAINING AND EVALUATION")
    print("=" * 70)

    # Load data
    print(f"\nLoading data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"  Total employees: {len(df)}")
    print(f"  Attrition rate: {(df['attrition'] == 'Yes').mean():.1%}")

    # Initialize and train model
    print("\n" + "-" * 70)
    print("TRAINING MODEL")
    print("-" * 70)

    scorer = EmployeeScorer(random_state=42)
    metrics = scorer.train(df, target_col="attrition")

    print("\nModel Performance Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric.upper()}: {value:.4f}")

    # Calculate retention scores
    print("\n" + "-" * 70)
    print("RETENTION SCORE ANALYSIS")
    print("-" * 70)

    retention_scores = scorer.calculate_retention_score(df)
    print(f"\nRetention Score Statistics:")
    print(f"  Mean: {np.mean(retention_scores):.1f}")
    print(f"  Std: {np.std(retention_scores):.1f}")
    print(f"  Min: {np.min(retention_scores):.1f}")
    print(f"  Max: {np.max(retention_scores):.1f}")

    # Sample predictions
    print("\n" + "-" * 70)
    print("SAMPLE PREDICTIONS")
    print("-" * 70)

    predictions = scorer.predict(df)
    df_results = pd.concat([
        df[["employee_id", "name", "department", "job_role", "attrition"]],
        predictions
    ], axis=1)

    # Show 5 sample predictions
    print("\nSample Predictions (5 employees):")
    for idx in range(5):
        row = df_results.iloc[idx]
        print(f"\n  {row['name']} ({row['employee_id']}):")
        print(f"    Department: {row['department']}")
        print(f"    Actual Attrition: {row['attrition']}")
        print(f"    Retention Score: {row['retention_score']:.1f}")
        print(f"    Attrition Probability: {row['attrition_probability']:.1%}")
        print(f"    Attrition Risk: {row['attrition_risk']}")
        print(f"    Layoff Priority: {row['layoff_priority']}")

    # Explain a high-risk prediction
    print("\n" + "-" * 70)
    print("PREDICTION EXPLANATION (High Attrition Risk)")
    print("-" * 70)

    # Find a high-risk employee
    high_risk_mask = df_results["attrition_risk"] == "High"
    if high_risk_mask.any():
        high_risk_idx = df_results[high_risk_mask].index[0]
        explanation = scorer.explain_prediction(df, index=high_risk_idx)

        emp = df_results.iloc[high_risk_idx]
        print(f"\nExplaining prediction for: {emp['name']}")
        print(f"Attrition Probability: {explanation['prediction_value']:.1%}")
        print(f"Base Value: {explanation['base_value']:.4f}")

        print("\nTop 10 Factors:")
        for i, factor in enumerate(explanation["top_factors"], 1):
            print(f"  {i:2d}. {factor['feature']}")
            print(f"      Value: {factor['original_value']}, SHAP: {factor['shap_value']:+.4f}")
            print(f"      ({factor['impact']})")
    else:
        print("\nNo high-risk employees found in sample.")

    # Simulate layoffs
    print("\n" + "-" * 70)
    print("LAYOFF SIMULATION (10% Budget Cut)")
    print("-" * 70)

    layoff_results = scorer.simulate_layoffs(df, budget_cut_percent=10, min_per_dept=2)

    print("\nTop 10 Layoff Recommendations:")
    recommended = layoff_results[layoff_results["layoff_recommended"] == True].head(10)
    for row in recommended.itertuples(index=False):
        print(f"  - {row.name} ({row.department})")
        print(f"    Income: ${row.monthly_income:,}, Score: {row.retention_score:.1f}")
        print(f"    Reason: {row.layoff_reason}")

    # Save model
    print("\n" + "-" * 70)
    print("SAVING MODEL")
    print("-" * 70)

    scorer.save_model(model_path)
    print(f"\nModel saved to: {model_path}")

    # Verify load
    print("\nVerifying model load...")
    new_scorer = EmployeeScorer()
    new_scorer.load_model(model_path)
    print("  Model loaded successfully!")
    print(f"  Loaded metrics: {new_scorer.metrics}")

    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
