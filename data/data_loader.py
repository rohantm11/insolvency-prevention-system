"""
data_loader.py  —  SolvencyInsight unified data loader
=======================================================

Single entry point for ALL data loading in the project.
Replaces the scattered pd.read_csv() calls across:
  - scripts/train_models.py
  - scripts/demo.py
  - scripts/generate_test_companies.py
  - backend/app/main.py
  - ml_models/insolvency_predictor.py
  - ml_models/employee_scorer.py

USAGE
-----
from data.data_loader import load_data, DataSource

# Synthetic (default — always works, no download needed)
company_df, employee_df = load_data(source=DataSource.SYNTHETIC)

# Real UCI Polish bankruptcy + IBM HR attrition (auto-downloads once)
company_df, employee_df = load_data(source=DataSource.REAL)

# Controlled via environment variable — no code changes needed
# DATA_SOURCE=real python scripts/train_models.py
company_df, employee_df = load_data()

Both paths return DataFrames with IDENTICAL column names, order,
and dtypes so that train_models.py and all other consumers need
zero changes.

COLUMN CONTRACT
---------------
company_df  — always contains in this order:
  company_id, company_name, industry,
  working_capital_to_total_assets, retained_earnings_to_total_assets,
  ebit_to_total_assets, market_value_equity_to_total_liabilities,
  sales_to_total_assets, current_ratio, quick_ratio, debt_to_equity,
  interest_coverage, net_profit_margin, return_on_assets,
  return_on_equity, is_bankrupt, years_to_bankruptcy

employee_df — always contains in this order:
  employee_id, name, age, gender, department, job_role, job_level,
  performance_rating, job_satisfaction, job_involvement,
  environment_satisfaction, monthly_income, percent_salary_hike,
  stock_option_level, years_at_company, years_in_current_role,
  total_working_years, distance_from_home, business_travel,
  over_time, attrition

REAL DATASET NOTES
------------------
Company  → UCI ML Repository "Polish Companies Bankruptcy Data"
           Stefanowski & Idkowiak (2016), ~10,000 records, 64 features.
           Auto-downloaded to data/real/ on first call (~4 MB).
           Falls back to synthetic if download fails.

Employee → IBM HR Analytics Employee Attrition (public domain)
           1,470 records, 35 features. Industry-standard benchmark.
           Auto-downloaded to data/real/ on first call (~300 KB).
           Falls back to synthetic if download fails.
"""

from __future__ import annotations

import logging
import os
import warnings
from enum import Enum
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE      = Path(__file__).parent           # data/
_REAL_DIR  = _HERE / "real"                  # data/real/  (created on demand)
_SYNTH_COMPANY  = _HERE / "company_data.csv"
_SYNTH_EMPLOYEE = _HERE / "employee_data.csv"

_UCI_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "00365/data.zip"
)
_IBM_URL = (
    "https://raw.githubusercontent.com/IBM/employee-attrition-aif360/"
    "master/data/emp_attrition.csv"
)

# ---------------------------------------------------------------------------
# Public enum
# ---------------------------------------------------------------------------
class DataSource(str, Enum):
    SYNTHETIC = "synthetic"
    REAL      = "real"

# ---------------------------------------------------------------------------
# Column contracts — mirrors train_models.py feature_cols exactly
# ---------------------------------------------------------------------------
COMPANY_FEATURE_COLS = [
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

COMPANY_ALL_COLS = (
    ["company_id", "company_name", "industry"]
    + COMPANY_FEATURE_COLS
    + ["is_bankrupt", "years_to_bankruptcy"]
)

EMPLOYEE_FEATURE_COLS = [
    "age", "job_level", "performance_rating", "job_satisfaction",
    "job_involvement", "environment_satisfaction", "monthly_income",
    "percent_salary_hike", "stock_option_level", "years_at_company",
    "years_in_current_role", "total_working_years", "distance_from_home",
]
EMPLOYEE_CATEGORICAL_COLS = ["gender", "department", "business_travel", "over_time"]

EMPLOYEE_ALL_COLS = (
    ["employee_id", "name"]
    + EMPLOYEE_FEATURE_COLS
    + ["gender", "department", "job_role", "business_travel", "over_time", "attrition"]
)


def load_data(
    source: DataSource | str | None = None,
    n_synthetic: int = 1000,
    seed: int = 42,
    verbose: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load company and employee data from the requested source.

    Parameters
    ----------
    source      : DataSource.SYNTHETIC | DataSource.REAL | None
                  If None, reads DATA_SOURCE environment variable
                  (defaults to "synthetic" if not set).
    n_synthetic : Number of companies to generate (synthetic only).
                  Employee count is always 5 × n_synthetic.
    seed        : Random seed (synthetic only).
    verbose     : Print progress messages.

    Returns
    -------
    (company_df, employee_df) — both conform to column contracts above.
    """
    if source is None:
        env_val = os.environ.get("DATA_SOURCE", "synthetic").lower()
        source  = DataSource(env_val)
    else:
        source = DataSource(source)

    if verbose:
        print(f"[SolvencyInsight] Loading data — source: {source.value.upper()}")

    if source == DataSource.SYNTHETIC:
        return _load_synthetic(n_synthetic, seed, verbose)
    else:
        return _load_real(n_synthetic, seed, verbose)


# ---------------------------------------------------------------------------
# Synthetic path
# ---------------------------------------------------------------------------
def _load_synthetic(
    n_companies: int, seed: int, verbose: bool
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load from cached CSVs if they exist and are large enough,
    otherwise generate fresh synthetic data.
    """
    n_employees = n_companies * 5

    need_generate = (
        not _SYNTH_COMPANY.exists()
        or not _SYNTH_EMPLOYEE.exists()
        or len(pd.read_csv(_SYNTH_COMPANY)) < n_companies * 0.9
    )

    if need_generate:
        if verbose:
            print(f"  Generating synthetic data "
                  f"({n_companies} companies, {n_employees} employees)...")
        from data.generate_dummy_data import (
            generate_company_data,
            generate_employee_data,
        )
        company_df  = generate_company_data(n_samples=n_companies, seed=seed)
        employee_df = generate_employee_data(n_samples=n_employees, seed=seed)
        company_df.to_csv(_SYNTH_COMPANY,  index=False)
        employee_df.to_csv(_SYNTH_EMPLOYEE, index=False)
        if verbose:
            print(f"  Saved to {_SYNTH_COMPANY} and {_SYNTH_EMPLOYEE}")
    else:
        if verbose:
            print(f"  Reading cached synthetic CSVs from {_HERE}/")
        company_df  = pd.read_csv(_SYNTH_COMPANY)
        employee_df = pd.read_csv(_SYNTH_EMPLOYEE)

    company_df  = _enforce_company_schema(company_df)
    employee_df = _enforce_employee_schema(employee_df)

    _print_summary(company_df, employee_df, "SYNTHETIC")
    return company_df, employee_df


# ---------------------------------------------------------------------------
# Real dataset path
# ---------------------------------------------------------------------------
def _load_real(
    n_synthetic_fallback: int, seed: int, verbose: bool
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Download / cache and normalise the UCI Polish bankruptcy dataset
    and the IBM HR attrition dataset.
    """
    _REAL_DIR.mkdir(parents=True, exist_ok=True)

    company_df  = _load_real_company(verbose)
    employee_df = _load_real_employee(n_synthetic_fallback, seed, verbose)

    company_df  = _enforce_company_schema(company_df)
    employee_df = _enforce_employee_schema(employee_df)

    _print_summary(company_df, employee_df, "REAL")
    return company_df, employee_df


def _load_real_company(verbose: bool) -> pd.DataFrame:
    """
    Download UCI Polish Companies Bankruptcy dataset and map to
    our internal schema.

    UCI feature mapping (Zieba et al. 2016):
      Attr3  → working_capital_to_total_assets
      Attr6  → retained_earnings_to_total_assets
      Attr7  → ebit_to_total_assets
      Attr8  → market_value_equity_to_total_liabilities
      Attr9  → sales_to_total_assets
      Attr4  → current_ratio
      Attr5  → quick_ratio proxy (cash ratio × 365, normalised)
      Attr2  → debt_to_equity (derived from liabilities/assets)
      Attr24 → interest_coverage proxy
      Attr15 → net_profit_margin proxy
      Attr1  → return_on_assets
      Attr18 → return_on_equity proxy
      class  → is_bankrupt
    """
    cached = _REAL_DIR / "company_real.csv"
    if cached.exists():
        if verbose:
            print(f"  [company] Reading cached real data from {cached}")
        return pd.read_csv(cached)

    if verbose:
        print("  [company] Downloading UCI Polish Bankruptcy dataset...")

    try:
        import io, zipfile, requests
        resp = requests.get(_UCI_URL, timeout=30)
        resp.raise_for_status()

        frames = []
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            for fname in z.namelist():
                if fname.endswith(".arff") or fname.endswith(".csv"):
                    with z.open(fname) as f:
                        raw = f.read().decode("utf-8", errors="ignore")
                        frames.append(_parse_uci_arff(raw))

        if not frames:
            raise ValueError("No usable files found in UCI zip.")

        raw_df = pd.concat(frames, ignore_index=True)
        if verbose:
            print(f"  [company] Downloaded {len(raw_df):,} records.")

        mapped = _map_uci_to_schema(raw_df)
        mapped.to_csv(cached, index=False)
        if verbose:
            print(f"  [company] Cached to {cached}")
        return mapped

    except Exception as exc:
        warnings.warn(
            f"[data_loader] UCI download failed ({exc}). "
            f"Falling back to synthetic company data.",
            RuntimeWarning,
        )
        from data.generate_dummy_data import generate_company_data
        return generate_company_data(n_samples=1000, seed=42)


def _parse_uci_arff(raw: str) -> pd.DataFrame:
    """Parse UCI .arff format into a DataFrame."""
    lines      = raw.splitlines()
    data_start = next(
        (i for i, l in enumerate(lines) if l.strip().upper() == "@DATA"),
        None,
    )
    if data_start is None:
        return pd.DataFrame()

    attrs = [
        l.split()[1]
        for l in lines[:data_start]
        if l.strip().upper().startswith("@ATTRIBUTE")
    ]
    data_lines = [
        l.strip() for l in lines[data_start + 1:]
        if l.strip() and not l.strip().startswith("%")
    ]
    rows = [row.split(",") for row in data_lines]
    df   = pd.DataFrame(rows, columns=attrs)
    df   = df.apply(pd.to_numeric, errors="coerce")
    return df


def _map_uci_to_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Map UCI Attr1…Attr64 + class columns to our internal schema."""
    col  = lambda n: f"Attr{n}"
    safe = lambda s: pd.to_numeric(s, errors="coerce")
    n    = len(df)

    out = pd.DataFrame()
    out["company_id"]   = [f"REAL_{i:05d}" for i in range(1, n + 1)]
    out["company_name"] = [f"Company_{i:05d}" for i in range(1, n + 1)]
    out["industry"]     = "Unknown"

    out["working_capital_to_total_assets"]          = safe(df.get(col(3),  np.nan))
    out["retained_earnings_to_total_assets"]        = safe(df.get(col(6),  np.nan))
    out["ebit_to_total_assets"]                     = safe(df.get(col(7),  np.nan))
    out["market_value_equity_to_total_liabilities"] = safe(df.get(col(8),  np.nan))
    out["sales_to_total_assets"]                    = safe(df.get(col(9),  np.nan))
    out["current_ratio"]                            = safe(df.get(col(4),  np.nan))

    x5 = safe(df.get(col(5), np.nan))
    out["quick_ratio"] = (x5 / 365).clip(0, 20)

    x2 = safe(df.get(col(2), np.nan)).clip(0, 0.9999)
    out["debt_to_equity"]    = (x2 / (1 - x2)).clip(0, 200)
    out["interest_coverage"] = safe(df.get(col(24), np.nan)).clip(-30, 80)
    out["net_profit_margin"] = safe(df.get(col(15), np.nan)).clip(-1.5, 1.5)
    out["return_on_assets"]  = safe(df.get(col(1),  np.nan)).clip(-1.0, 1.0)
    out["return_on_equity"]  = safe(df.get(col(18), np.nan)).clip(-5.0, 5.0)

    if "class" in df.columns:
        out["is_bankrupt"] = pd.to_numeric(df["class"], errors="coerce").fillna(0).astype(int)
    else:
        out["is_bankrupt"] = 0

    out["years_to_bankruptcy"] = np.nan

    for c in COMPANY_FEATURE_COLS:
        if c in out.columns:
            med = out[c].median()
            out[c] = out[c].fillna(med if not np.isnan(med) else 0.0)

    return out


def _load_real_employee(
    n_synthetic_fallback: int, seed: int, verbose: bool
) -> pd.DataFrame:
    """
    Download IBM HR Analytics attrition dataset and normalise to schema.
    Falls back to synthetic employee data if download fails.
    """
    cached = _REAL_DIR / "employee_real.csv"
    if cached.exists():
        if verbose:
            print(f"  [employee] Reading cached real data from {cached}")
        return pd.read_csv(cached)

    if verbose:
        print("  [employee] Downloading IBM HR Attrition dataset...")

    try:
        import io, requests
        resp = requests.get(_IBM_URL, timeout=20)
        resp.raise_for_status()

        raw_df = pd.read_csv(io.StringIO(resp.text))
        mapped = _map_ibm_to_schema(raw_df)
        mapped.to_csv(cached, index=False)
        if verbose:
            print(f"  [employee] {len(mapped):,} records cached to {cached}")
        return mapped

    except Exception as exc:
        warnings.warn(
            f"[data_loader] IBM HR download failed ({exc}). "
            f"Falling back to synthetic employee data.",
            RuntimeWarning,
        )
        from data.generate_dummy_data import generate_employee_data
        return generate_employee_data(
            n_samples=n_synthetic_fallback * 5, seed=seed
        )


def _map_ibm_to_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map IBM HR Analytics column names to our internal schema.
    IBM column names map directly — only renaming needed.
    """
    rename_map = {
        "Age":                     "age",
        "JobLevel":                "job_level",
        "PerformanceRating":       "performance_rating",
        "JobSatisfaction":         "job_satisfaction",
        "JobInvolvement":          "job_involvement",
        "EnvironmentSatisfaction": "environment_satisfaction",
        "MonthlyIncome":           "monthly_income",
        "PercentSalaryHike":       "percent_salary_hike",
        "StockOptionLevel":        "stock_option_level",
        "YearsAtCompany":          "years_at_company",
        "YearsInCurrentRole":      "years_in_current_role",
        "TotalWorkingYears":       "total_working_years",
        "DistanceFromHome":        "distance_from_home",
        "Gender":                  "gender",
        "Department":              "department",
        "JobRole":                 "job_role",
        "BusinessTravel":          "business_travel",
        "OverTime":                "over_time",
        "Attrition":               "attrition",
    }
    out = df.rename(columns=rename_map).copy()

    travel_map = {
        "Non-Travel":        "Non-Travel",
        "Travel_Rarely":     "Travel_Rarely",
        "Travel_Frequently": "Travel_Frequently",
    }
    if "business_travel" in out.columns:
        out["business_travel"] = (
            out["business_travel"].map(travel_map).fillna("Travel_Rarely")
        )

    n = len(out)
    if "employee_id" not in out.columns:
        emp_num = out.get("EmployeeNumber", pd.Series(range(1, n + 1)))
        out["employee_id"] = [f"IBM_{int(x):05d}" for x in emp_num]
    if "name" not in out.columns:
        out["name"] = [f"Employee_{i:05d}" for i in range(1, n + 1)]

    return out


def _enforce_company_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Guarantee company DataFrame has exactly the columns train_models.py
    expects, in the right order, with the right dtypes.
    Drops altman_z_score if present — informational only, not a feature.
    """
    df = df.copy()

    # Drop informational columns not expected by training script
    df.drop(columns=["altman_z_score"], errors="ignore", inplace=True)

    # Add missing mandatory columns with safe defaults
    if "company_id" not in df.columns:
        df.insert(0, "company_id",
                  [f"COMP_{i:04d}" for i in range(1, len(df) + 1)])
    if "company_name" not in df.columns:
        df.insert(1, "company_name", df["company_id"])
    if "industry" not in df.columns:
        df.insert(2, "industry", "Unknown")
    if "years_to_bankruptcy" not in df.columns:
        df["years_to_bankruptcy"] = np.where(
            df["is_bankrupt"] == 1, np.nan, np.nan
        )

    # Clip extremes to the same ranges used during training
    clip_map = {
        "debt_to_equity":    (-50,  200),
        "interest_coverage": (-30,   80),
        "net_profit_margin": (-1.5, 1.5),
        "return_on_assets":  (-1.0, 1.0),
        "return_on_equity":  (-5.0, 5.0),
    }
    for col, (lo, hi) in clip_map.items():
        if col in df.columns:
            df[col] = df[col].clip(lo, hi)

    # Return only known columns in the correct order
    present = [c for c in COMPANY_ALL_COLS if c in df.columns]
    return df[present].reset_index(drop=True)


def _enforce_employee_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Guarantee employee DataFrame has exactly the columns train_models.py
    expects, in the right order, with the right dtypes.
    """
    df = df.copy()

    if "employee_id" not in df.columns:
        df.insert(0, "employee_id",
                  [f"EMP_{i:05d}" for i in range(1, len(df) + 1)])
    if "name" not in df.columns:
        df.insert(1, "name", df["employee_id"])
    if "job_role" not in df.columns:
        df["job_role"] = "Unknown"

    present = [c for c in EMPLOYEE_ALL_COLS if c in df.columns]
    return df[present].reset_index(drop=True)


def _print_summary(
    company_df: pd.DataFrame,
    employee_df: pd.DataFrame,
    label: str,
) -> None:
    bkr = company_df["is_bankrupt"].mean()
    att = (
        (employee_df["attrition"] == "Yes").mean()
        if "attrition" in employee_df.columns
        else float("nan")
    )
    print(f"\n  -- {label} DATA SUMMARY -------------------------------")
    print(f"  Companies : {len(company_df):>6,}  |  Bankruptcy rate : {bkr:.1%}")
    print(f"  Employees : {len(employee_df):>6,}  |  Attrition rate  : {att:.1%}")
    print(f"  -----------------------------------------------------\n")
