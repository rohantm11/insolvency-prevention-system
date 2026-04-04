import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest

from data.generate_dummy_data import generate_company_data, validate_company_data


def test_quick_ratio_never_exceeds_current():
    df = generate_company_data(n_samples=500, seed=99)
    violations = (df["quick_ratio"] > df["current_ratio"] + 0.01).sum()
    assert violations == 0, f"{violations} rows have quick_ratio > current_ratio"


def test_dupont_identity_holds():
    df = generate_company_data(n_samples=500, seed=99)
    dupont_roa = df["net_profit_margin"] * df["sales_to_total_assets"]
    diff = (df["return_on_assets"] - dupont_roa).abs()
    bad = (diff > 0.05).sum()
    assert bad < len(df) * 0.02, (
        f"DuPont identity violated in {bad} rows ({bad/len(df)*100:.1f}%)"
    )


def test_bankrupt_companies_have_lower_z_scores():
    df = generate_company_data(n_samples=500, seed=99)
    z_healthy = df.loc[df["is_bankrupt"] == 0, "altman_z_score"].mean()
    z_bankrupt = df.loc[df["is_bankrupt"] == 1, "altman_z_score"].mean()
    assert z_healthy > z_bankrupt, (
        f"Healthy Z ({z_healthy:.2f}) should exceed bankrupt Z ({z_bankrupt:.2f})"
    )


def test_debt_to_equity_in_realistic_range():
    df = generate_company_data(n_samples=500, seed=99)
    non_fin = df[df["industry"] != "Financial Services"]
    assert non_fin["debt_to_equity"].max() <= 21, (
        f"Non-financial D/E max {non_fin['debt_to_equity'].max():.1f} exceeds 20"
    )


def test_class_balance():
    df = generate_company_data(n_samples=1000, seed=99)
    bankrupt_pct = df["is_bankrupt"].mean()
    assert 0.10 < bankrupt_pct < 0.35, (
        f"Bankrupt ratio {bankrupt_pct:.2f} outside expected 10-35%"
    )


def test_interest_coverage_sign_matches_ebit():
    df = generate_company_data(n_samples=500, seed=99)
    negative_ebit = df["ebit_to_total_assets"] < 0
    negative_ic = df["interest_coverage"] < 0
    # Most companies with negative EBIT should have negative interest coverage
    agreement = (negative_ebit & negative_ic).sum() / max(negative_ebit.sum(), 1)
    assert agreement > 0.5, (
        f"Only {agreement:.0%} of negative-EBIT companies have negative IC"
    )
