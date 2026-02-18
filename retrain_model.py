"""
Retrain the insolvency prediction model with the new 500-company dataset.
"""

import sys
sys.path.insert(0, 'ml_models')

import pandas as pd
import numpy as np
from insolvency_predictor import InsolvencyPredictor

def main():
    print("="*60)
    print("RETRAINING INSOLVENCY MODEL WITH 500-COMPANY DATASET")
    print("="*60)

    # Load the combined training data
    df = pd.read_csv("data/training_companies/_combined_training_data.csv")
    print(f"\nLoaded {len(df)} companies")
    print(f"Class distribution:\n{df['is_insolvent'].value_counts()}")

    # Prepare features
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

    # Prepare training dataframe with features and target
    train_df = df[feature_cols + ['is_insolvent']].copy()

    X = df[feature_cols]
    y = df['is_insolvent']

    # Initialize and train the predictor
    print("\nTraining model...")
    predictor = InsolvencyPredictor()
    metrics = predictor.train(train_df, target_col='is_insolvent')

    print("\n" + "="*60)
    print("TRAINING COMPLETE - MODEL METRICS")
    print("="*60)
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")

    # Test with a sample prediction
    print("\n" + "="*60)
    print("SAMPLE PREDICTIONS")
    print("="*60)

    # Healthy company example
    healthy_sample = X[y == 0].iloc[0:1]
    healthy_pred = predictor.predict(healthy_sample)
    print(f"\nHealthy company sample:")
    print(f"  Probability: {healthy_pred['probability_of_distress'].iloc[0]*100:.1f}%")
    print(f"  Category: {healthy_pred['risk_category'].iloc[0]}")

    # Distressed company example
    distressed_sample = X[y == 1].iloc[0:1]
    distressed_pred = predictor.predict(distressed_sample)
    print(f"\nDistressed company sample:")
    print(f"  Probability: {distressed_pred['probability_of_distress'].iloc[0]*100:.1f}%")
    print(f"  Category: {distressed_pred['risk_category'].iloc[0]}")

    print("\n" + "="*60)
    print("Model saved to: ml_models/saved_models/")
    print("="*60)

if __name__ == "__main__":
    main()
