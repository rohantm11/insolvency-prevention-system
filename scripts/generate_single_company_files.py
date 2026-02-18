"""
Generate 6,000 single-company CSV files (like single_company_sample.csv):
- 3,000 good (not at risk) in data/good/
- 3,000 bad (at risk) in data/bad/

Each file has one row: same columns as single_company_sample.csv, unique company name, varying stats.

Usage:
    python scripts/generate_single_company_files.py --output-dir data
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import argparse
import random
import numpy as np
import pandas as pd

# Load generate_data from scripts/ (run from project root: python scripts/generate_single_company_files.py)
sys.path.insert(0, str(project_root / "scripts"))
from generate_data import (
    INDUSTRIES,
    COMPANY_PREFIXES,
    COMPANY_SUFFIXES,
    generate_healthy_company_ratios,
    generate_distressed_company_ratios,
)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Columns for single-company CSV (same as single_company_sample.csv) - no is_bankrupt / years_to_bankruptcy
CSV_COLUMNS = [
    "company_id",
    "company_name",
    "industry",
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


def make_company_name(idx: int) -> str:
    return f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)} #{idx}"


def main():
    parser = argparse.ArgumentParser(description="Generate 6k single-company CSV files (3k good, 3k bad)")
    parser.add_argument("--output-dir", type=str, default="data", help="Base output directory (creates good/ and bad/ inside)")
    parser.add_argument("--good", type=int, default=3000, help="Number of good (not at risk) company files")
    parser.add_argument("--bad", type=int, default=3000, help="Number of bad (at risk) company files")
    args = parser.parse_args()

    base = Path(args.output_dir)
    good_dir = base / "good"
    bad_dir = base / "bad"
    good_dir.mkdir(parents=True, exist_ok=True)
    bad_dir.mkdir(parents=True, exist_ok=True)

    n_good = args.good
    n_bad = args.bad

    print("=" * 60)
    print("Generating single-company CSV files")
    print("=" * 60)
    print(f"  Good (not at risk): {n_good} files -> {good_dir}")
    print(f"  Bad (at risk):      {n_bad} files -> {bad_dir}")
    print()

    for i in range(1, n_good + 1):
        name = make_company_name(i)
        company_id = f"COMP_GOOD_{i:05d}"
        industry = random.choice(INDUSTRIES)
        ratios = generate_healthy_company_ratios()
        row = {
            "company_id": company_id,
            "company_name": name,
            "industry": industry,
            **{k: ratios[k] for k in ratios if k in CSV_COLUMNS},
        }
        df = pd.DataFrame([row])
        df = df[CSV_COLUMNS]
        out_path = good_dir / f"{i:05d}.csv"
        df.to_csv(out_path, index=False)
        if i % 500 == 0:
            print(f"  Good: {i}/{n_good}")

    print(f"  Good: {n_good}/{n_good} done.")

    for i in range(1, n_bad + 1):
        name = make_company_name(n_good + i)
        company_id = f"COMP_BAD_{i:05d}"
        industry = random.choice(INDUSTRIES)
        ratios = generate_distressed_company_ratios()
        row = {
            "company_id": company_id,
            "company_name": name,
            "industry": industry,
            **{k: ratios[k] for k in ratios if k in CSV_COLUMNS},
        }
        df = pd.DataFrame([row])
        df = df[CSV_COLUMNS]
        out_path = bad_dir / f"{i:05d}.csv"
        df.to_csv(out_path, index=False)
        if i % 500 == 0:
            print(f"  Bad:  {i}/{n_bad}")

    print(f"  Bad:  {n_bad}/{n_bad} done.")
    print()
    print("=" * 60)
    print("Done.")
    print(f"  {good_dir.absolute()}  ({n_good} files)")
    print(f"  {bad_dir.absolute()}  ({n_bad} files)")
    print("=" * 60)


if __name__ == "__main__":
    main()
