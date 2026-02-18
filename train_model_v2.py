"""
Train the enhanced InsolvencyPredictorV2 model with the 10,000-company dataset.
"""

import sys
sys.path.insert(0, 'ml_models')

import pandas as pd
import numpy as np
from insolvency_predictor_v2 import InsolvencyPredictorV2

def main():
    print("="*70)
    print("TRAINING ENHANCED INSOLVENCY MODEL V2 WITH 10,000 COMPANIES")
    print("="*70)

    # Load the 10k dataset
    df = pd.read_csv("data/training_companies_10k/_combined_training_data_10k.csv")
    print(f"\nLoaded {len(df)} companies")
    print(f"\nClass distribution:")
    print(df['is_insolvent'].value_counts())
    print(f"\nClass balance: {df['is_insolvent'].mean()*100:.1f}% distressed")

    # Feature columns
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

    # Prepare training dataframe
    train_df = df[feature_cols + ['is_insolvent']].copy()

    # Initialize and train the enhanced predictor
    print("\n" + "="*70)
    print("TRAINING MODEL")
    print("="*70)

    predictor = InsolvencyPredictorV2()
    metrics = predictor.train(train_df, target_col='is_insolvent', use_cv=True)

    print("\n" + "="*70)
    print("FINAL MODEL METRICS")
    print("="*70)
    for metric, value in metrics.items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.4f}")

    # Cross-validation results
    if predictor.cv_scores is not None and len(predictor.cv_scores) > 0:
        print(f"\n5-Fold CV ROC-AUC scores: {[f'{s:.4f}' for s in predictor.cv_scores]}")
        print(f"CV Mean: {predictor.cv_scores.mean():.4f} (+/- {predictor.cv_scores.std()*2:.4f})")

    # Feature importance (top 20)
    print("\n" + "="*70)
    print("TOP 20 FEATURE IMPORTANCES")
    print("="*70)
    importance = predictor.get_feature_importance()
    for i, (feature, imp) in enumerate(list(importance.items())[:20]):
        print(f"  {i+1:2d}. {feature:<45} {imp:.4f}")

    # Test predictions
    print("\n" + "="*70)
    print("SAMPLE PREDICTIONS")
    print("="*70)

    X = df[feature_cols]
    y = df['is_insolvent']

    # Test on a few samples
    print("\nHealthy company samples:")
    healthy_samples = X[y == 0].iloc[:3]
    healthy_preds = predictor.predict(healthy_samples)
    for i in range(3):
        print(f"  Sample {i+1}: Prob={healthy_preds['probability_of_distress'].iloc[i]*100:.1f}%, "
              f"Risk={healthy_preds['risk_category'].iloc[i]}, Z={healthy_preds['z_score'].iloc[i]:.2f}")

    print("\nDistressed company samples:")
    distressed_samples = X[y == 1].iloc[:3]
    distressed_preds = predictor.predict(distressed_samples)
    for i in range(3):
        print(f"  Sample {i+1}: Prob={distressed_preds['probability_of_distress'].iloc[i]*100:.1f}%, "
              f"Risk={distressed_preds['risk_category'].iloc[i]}, Z={distressed_preds['z_score'].iloc[i]:.2f}")

    # SHAP explanation for one sample
    print("\n" + "="*70)
    print("SHAP EXPLANATION (DISTRESSED SAMPLE)")
    print("="*70)
    explanation = predictor.explain_prediction(distressed_samples, index=0)
    print(f"\nBase value: {explanation['base_value']:.4f}")
    print(f"Prediction value: {explanation['prediction_value']:.4f}")
    print("\nTop 10 risk drivers:")
    for driver in explanation['top_risk_drivers'][:10]:
        print(f"  {driver['feature']:<40} SHAP: {driver['shap_value']:+.4f} ({driver['impact']})")

    print("\n" + "="*70)
    print("MODEL V2 TRAINING COMPLETE!")
    print("="*70)
    print(f"\nModel saved to: ml_models/saved_models/insolvency_model_v2.pkl")

    return predictor, metrics

if __name__ == "__main__":
    predictor, metrics = main()
