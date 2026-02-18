"""
Model Testing Script for Insolvency Prevention System.

Tests trained models on held-out test data and generates detailed reports.

Usage:
    python scripts/test_models.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    precision_recall_curve, roc_curve
)
import warnings
warnings.filterwarnings('ignore')


def test_insolvency_model(model_path: Path, test_data_path: Path) -> dict:
    """Test the insolvency prediction model on held-out test data."""
    print("\n" + "="*60)
    print("Testing Insolvency Prediction Model")
    print("="*60)

    # Load model
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)

    model = model_data['model']
    feature_cols = model_data['feature_names']

    print(f"Model trained at: {model_data.get('trained_at', 'Unknown')}")
    print(f"Training metrics: ROC-AUC = {model_data['metrics']['roc_auc']:.4f}")

    # Load test data
    df = pd.read_csv(test_data_path)
    print(f"\nTest set size: {len(df)} companies")

    X_test = df[feature_cols].fillna(df[feature_cols].median())
    y_test = df['is_bankrupt']

    print(f"Positive class (bankrupt): {y_test.sum()} ({y_test.mean()*100:.1f}%)")

    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1_score': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_pred_proba)
    }

    print("\n" + "-"*40)
    print("Test Set Performance:")
    print("-"*40)
    for name, value in metrics.items():
        print(f"  {name}: {value:.4f}")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix:")
    print(f"  TN: {cm[0,0]}, FP: {cm[0,1]}")
    print(f"  FN: {cm[1,0]}, TP: {cm[1,1]}")

    # Classification Report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Healthy', 'Bankrupt']))

    # Sample predictions
    print("\nSample Predictions (first 10):")
    print("-"*70)
    for i in range(min(10, len(df))):
        actual = "Bankrupt" if y_test.iloc[i] == 1 else "Healthy"
        predicted = "Bankrupt" if y_pred[i] == 1 else "Healthy"
        prob = y_pred_proba[i]
        status = "[OK]" if y_test.iloc[i] == y_pred[i] else "[X]"
        print(f"  {status:4} {df.iloc[i]['company_name'][:25]:<25} | Actual: {actual:<9} | Pred: {predicted:<9} | Prob: {prob:.3f}")

    return metrics


def test_employee_model(model_path: Path, test_data_path: Path) -> dict:
    """Test the employee attrition model on held-out test data."""
    print("\n" + "="*60)
    print("Testing Employee Attrition Model")
    print("="*60)

    # Load model
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)

    model = model_data['model']
    feature_names = model_data['feature_names']
    label_encoders = model_data.get('label_encoders', {})

    print(f"Model trained at: {model_data.get('trained_at', 'Unknown')}")
    print(f"Training metrics: ROC-AUC = {model_data['metrics']['roc_auc']:.4f}")

    # Load test data
    df = pd.read_csv(test_data_path)
    print(f"\nTest set size: {len(df)} employees")

    # Prepare features
    numeric_cols = [
        'age', 'job_level', 'performance_rating', 'job_satisfaction',
        'job_involvement', 'environment_satisfaction', 'monthly_income',
        'percent_salary_hike', 'stock_option_level', 'years_at_company',
        'years_in_current_role', 'total_working_years', 'distance_from_home'
    ]
    categorical_cols = ['gender', 'department', 'business_travel', 'over_time']

    X_test = df[numeric_cols].copy()

    # Encode categorical variables using saved encoders
    for col in categorical_cols:
        if col in label_encoders:
            # Handle unseen labels by mapping to most frequent
            le = label_encoders[col]
            X_test[col] = df[col].apply(
                lambda x: le.transform([x])[0] if x in le.classes_ else 0
            )
        else:
            # Create new encoder if not saved
            le = LabelEncoder()
            X_test[col] = le.fit_transform(df[col])

    X_test = X_test.fillna(X_test.median())
    y_test = (df['attrition'] == 'Yes').astype(int)

    print(f"Positive class (attrition): {y_test.sum()} ({y_test.mean()*100:.1f}%)")

    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1_score': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_pred_proba)
    }

    print("\n" + "-"*40)
    print("Test Set Performance:")
    print("-"*40)
    for name, value in metrics.items():
        print(f"  {name}: {value:.4f}")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix:")
    print(f"  TN: {cm[0,0]}, FP: {cm[0,1]}")
    print(f"  FN: {cm[1,0]}, TP: {cm[1,1]}")

    # Classification Report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Retained', 'Attrition']))

    # Sample predictions
    print("\nSample Predictions (first 10):")
    print("-"*80)
    for i in range(min(10, len(df))):
        actual = "Attrition" if y_test.iloc[i] == 1 else "Retained"
        predicted = "Attrition" if y_pred[i] == 1 else "Retained"
        prob = y_pred_proba[i]
        status = "[OK]" if y_test.iloc[i] == y_pred[i] else "[X]"
        name = df.iloc[i]['name'][:20]
        dept = df.iloc[i]['department'][:15]
        print(f"  {status:4} {name:<20} | {dept:<15} | Actual: {actual:<9} | Pred: {predicted:<9} | Prob: {prob:.3f}")

    return metrics


def main():
    print("\n" + "#"*60)
    print("# Insolvency Prevention System - Model Testing")
    print("#"*60)

    # Paths
    data_dir = project_root / 'data' / 'generated'
    models_dir = project_root / 'ml_models' / 'trained_models'

    # Test files
    company_test = data_dir / 'company_test.csv'
    employee_test = data_dir / 'employee_test.csv'
    insolvency_model = models_dir / 'insolvency_model.pkl'
    employee_model = models_dir / 'employee_model.pkl'

    # Check files exist
    for f in [company_test, employee_test, insolvency_model, employee_model]:
        if not f.exists():
            print(f"\nError: Required file not found: {f}")
            print("Run generate_data.py and train_models.py first.")
            sys.exit(1)

    # Run tests
    insolvency_metrics = test_insolvency_model(insolvency_model, company_test)
    employee_metrics = test_employee_model(employee_model, employee_test)

    # Summary
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)

    print("\nInsolvency Model (on held-out test set):")
    print(f"  ROC-AUC:  {insolvency_metrics['roc_auc']:.4f}")
    print(f"  Accuracy: {insolvency_metrics['accuracy']:.4f}")
    print(f"  F1-Score: {insolvency_metrics['f1_score']:.4f}")
    print(f"  Precision: {insolvency_metrics['precision']:.4f}")
    print(f"  Recall:   {insolvency_metrics['recall']:.4f}")

    print("\nEmployee Model (on held-out test set):")
    print(f"  ROC-AUC:  {employee_metrics['roc_auc']:.4f}")
    print(f"  Accuracy: {employee_metrics['accuracy']:.4f}")
    print(f"  F1-Score: {employee_metrics['f1_score']:.4f}")
    print(f"  Precision: {employee_metrics['precision']:.4f}")
    print(f"  Recall:   {employee_metrics['recall']:.4f}")

    # Overall assessment
    print("\n" + "-"*60)
    avg_auc = (insolvency_metrics['roc_auc'] + employee_metrics['roc_auc']) / 2

    if avg_auc >= 0.9:
        assessment = "EXCELLENT - Models are production-ready"
    elif avg_auc >= 0.8:
        assessment = "GOOD - Models perform well"
    elif avg_auc >= 0.7:
        assessment = "FAIR - Models may need improvement"
    else:
        assessment = "POOR - Models need significant improvement"

    print(f"Overall Assessment: {assessment}")
    print(f"Average ROC-AUC: {avg_auc:.4f}")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
