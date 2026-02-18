"""
Model Training Script for Insolvency Prevention System.

Trains XGBoost models on generated data and saves them for production use.

Usage:
    python scripts/train_models.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import pickle
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')


# =============================================================================
# Insolvency Model Training
# =============================================================================

def train_insolvency_model(data_path: Path, output_path: Path) -> dict:
    """Train the insolvency prediction model."""
    print("\n" + "="*60)
    print("Training Insolvency Prediction Model")
    print("="*60)

    # Load data
    df = pd.read_csv(data_path)
    print(f"\nLoaded {len(df)} company records")

    # Features for insolvency prediction
    feature_cols = [
        'working_capital_to_total_assets',
        'retained_earnings_to_total_assets',
        'ebit_to_total_assets',
        'market_value_equity_to_total_liabilities',
        'sales_to_total_assets',
        'current_ratio',
        'quick_ratio',
        'debt_to_equity',
        'interest_coverage',
        'net_profit_margin',
        'return_on_assets',
        'return_on_equity'
    ]

    X = df[feature_cols].copy()
    y = df['is_bankrupt'].copy()

    # Handle missing values
    X = X.fillna(X.median())

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
    print(f"Positive class (bankrupt): {y.sum()} ({y.mean()*100:.1f}%)")

    # Calculate class weight
    n_neg = (y_train == 0).sum()
    n_pos = (y_train == 1).sum()
    scale_pos_weight = n_neg / n_pos if n_pos > 0 else 1

    # Train XGBoost model
    model = XGBClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        eval_metric='logloss',
        random_state=42,
        use_label_encoder=False
    )

    print("\nTraining model...")
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1_score': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_pred_proba)
    }

    print("\n" + "-"*40)
    print("Model Performance:")
    print("-"*40)
    for name, value in metrics.items():
        print(f"  {name}: {value:.4f}")

    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
    print(f"\n  Cross-val ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")

    # Feature importance
    importance = dict(zip(feature_cols, model.feature_importances_))
    sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)

    print("\nTop 5 Feature Importances:")
    for feat, imp in sorted_importance[:5]:
        print(f"  {feat}: {imp:.4f}")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix:")
    print(f"  TN: {cm[0,0]}, FP: {cm[0,1]}")
    print(f"  FN: {cm[1,0]}, TP: {cm[1,1]}")

    # Save model
    model_data = {
        'model': model,
        'feature_names': feature_cols,
        'metrics': metrics,
        'feature_importance': importance,
        'trained_at': datetime.now().isoformat()
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        pickle.dump(model_data, f)

    print(f"\nModel saved to: {output_path}")

    return metrics


# =============================================================================
# Employee Model Training
# =============================================================================

def train_employee_model(data_path: Path, output_path: Path) -> dict:
    """Train the employee attrition prediction model."""
    print("\n" + "="*60)
    print("Training Employee Attrition Model")
    print("="*60)

    # Load data
    df = pd.read_csv(data_path)
    print(f"\nLoaded {len(df)} employee records")

    # Features for employee scoring
    feature_cols = [
        'age', 'job_level', 'performance_rating', 'job_satisfaction',
        'job_involvement', 'environment_satisfaction', 'monthly_income',
        'percent_salary_hike', 'stock_option_level', 'years_at_company',
        'years_in_current_role', 'total_working_years', 'distance_from_home'
    ]

    categorical_cols = ['gender', 'department', 'business_travel', 'over_time']

    # Prepare features
    X = df[feature_cols].copy()

    # Encode categorical variables
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(df[col])
        label_encoders[col] = le

    # Target variable
    y = (df['attrition'] == 'Yes').astype(int)

    # Handle missing values
    X = X.fillna(X.median())

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
    print(f"Positive class (attrition): {y.sum()} ({y.mean()*100:.1f}%)")

    # Calculate class weight
    n_neg = (y_train == 0).sum()
    n_pos = (y_train == 1).sum()
    scale_pos_weight = n_neg / n_pos if n_pos > 0 else 1

    # Train XGBoost model
    model = XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        eval_metric='logloss',
        random_state=42,
        use_label_encoder=False
    )

    print("\nTraining model...")
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1_score': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_pred_proba)
    }

    print("\n" + "-"*40)
    print("Model Performance:")
    print("-"*40)
    for name, value in metrics.items():
        print(f"  {name}: {value:.4f}")

    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
    print(f"\n  Cross-val ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")

    # Feature importance
    all_features = feature_cols + categorical_cols
    importance = dict(zip(all_features, model.feature_importances_))
    sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)

    print("\nTop 5 Feature Importances:")
    for feat, imp in sorted_importance[:5]:
        print(f"  {feat}: {imp:.4f}")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix:")
    print(f"  TN: {cm[0,0]}, FP: {cm[0,1]}")
    print(f"  FN: {cm[1,0]}, TP: {cm[1,1]}")

    # Save model
    model_data = {
        'model': model,
        'feature_names': all_features,
        'label_encoders': label_encoders,
        'metrics': metrics,
        'feature_importance': importance,
        'trained_at': datetime.now().isoformat()
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        pickle.dump(model_data, f)

    print(f"\nModel saved to: {output_path}")

    return metrics


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    print("\n" + "#"*60)
    print("# Insolvency Prevention System - Model Training Pipeline")
    print("#"*60)

    # Paths: use data/ (default from generate_data.py); fall back to data/generated/
    data_dir = project_root / 'data'
    if not (data_dir / 'company_train.csv').exists() and (project_root / 'data' / 'generated' / 'company_train.csv').exists():
        data_dir = project_root / 'data' / 'generated'
    models_dir = project_root / 'ml_models' / 'trained_models'

    company_data = data_dir / 'company_train.csv'
    employee_data = data_dir / 'employee_train.csv'

    if not company_data.exists():
        print(f"\nError: Training data not found at {company_data}")
        print("Run: python scripts/generate_data.py  (generates 4000 healthy + 3000 at-risk by default)")
        print("  or: python scripts/generate_data.py --healthy 4000 --at-risk 3000 --output-dir data")
        sys.exit(1)

    # Train models
    insolvency_metrics = train_insolvency_model(
        company_data,
        models_dir / 'insolvency_model.pkl'
    )

    employee_metrics = train_employee_model(
        employee_data,
        models_dir / 'employee_model.pkl'
    )

    # Summary
    print("\n" + "="*60)
    print("Training Complete - Summary")
    print("="*60)
    print("\nInsolvency Model:")
    print(f"  ROC-AUC: {insolvency_metrics['roc_auc']:.4f}")
    print(f"  Accuracy: {insolvency_metrics['accuracy']:.4f}")
    print(f"  F1-Score: {insolvency_metrics['f1_score']:.4f}")

    print("\nEmployee Model:")
    print(f"  ROC-AUC: {employee_metrics['roc_auc']:.4f}")
    print(f"  Accuracy: {employee_metrics['accuracy']:.4f}")
    print(f"  F1-Score: {employee_metrics['f1_score']:.4f}")

    print(f"\nModels saved to: {models_dir}")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
