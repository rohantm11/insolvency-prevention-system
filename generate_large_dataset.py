"""
Generate 10,000 realistic company financial data files for robust model training.
Includes more varied scenarios, industry-specific patterns, and economic cycles.
"""

import numpy as np
import pandas as pd
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading

# Create data directory
DATA_DIR = Path("data/training_companies_10k")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Lock for thread-safe printing
print_lock = threading.Lock()

# Expanded industry sectors with detailed characteristics
INDUSTRIES = {
    "Technology": {"volatility": 1.3, "growth": 1.2, "leverage": 0.6, "margin": 1.4},
    "Healthcare": {"volatility": 0.9, "growth": 1.1, "leverage": 0.7, "margin": 1.2},
    "Pharmaceuticals": {"volatility": 1.1, "growth": 1.0, "leverage": 0.8, "margin": 1.5},
    "Manufacturing": {"volatility": 0.8, "growth": 0.9, "leverage": 1.0, "margin": 0.8},
    "Retail": {"volatility": 1.0, "growth": 0.95, "leverage": 1.1, "margin": 0.5},
    "E-Commerce": {"volatility": 1.4, "growth": 1.3, "leverage": 0.9, "margin": 0.7},
    "Financial Services": {"volatility": 1.2, "growth": 1.0, "leverage": 2.5, "margin": 1.1},
    "Banking": {"volatility": 1.1, "growth": 0.9, "leverage": 3.0, "margin": 0.9},
    "Insurance": {"volatility": 0.8, "growth": 0.85, "leverage": 2.0, "margin": 1.0},
    "Energy": {"volatility": 1.5, "growth": 0.8, "leverage": 1.3, "margin": 1.2},
    "Renewable Energy": {"volatility": 1.6, "growth": 1.4, "leverage": 1.2, "margin": 0.6},
    "Oil & Gas": {"volatility": 1.7, "growth": 0.7, "leverage": 1.4, "margin": 1.3},
    "Consumer Goods": {"volatility": 0.7, "growth": 0.9, "leverage": 0.9, "margin": 0.9},
    "Telecommunications": {"volatility": 0.9, "growth": 0.95, "leverage": 1.4, "margin": 1.0},
    "Real Estate": {"volatility": 1.0, "growth": 0.85, "leverage": 1.8, "margin": 0.8},
    "REIT": {"volatility": 1.1, "growth": 0.8, "leverage": 2.0, "margin": 0.7},
    "Transportation": {"volatility": 1.0, "growth": 0.9, "leverage": 1.2, "margin": 0.6},
    "Airlines": {"volatility": 1.8, "growth": 0.8, "leverage": 1.5, "margin": 0.3},
    "Logistics": {"volatility": 0.9, "growth": 1.05, "leverage": 1.0, "margin": 0.7},
    "Utilities": {"volatility": 0.5, "growth": 0.7, "leverage": 1.6, "margin": 0.8},
    "Construction": {"volatility": 1.2, "growth": 0.95, "leverage": 1.1, "margin": 0.6},
    "Agriculture": {"volatility": 1.3, "growth": 0.8, "leverage": 0.9, "margin": 0.5},
    "Mining": {"volatility": 1.6, "growth": 0.75, "leverage": 1.2, "margin": 1.1},
    "Hospitality": {"volatility": 1.4, "growth": 0.9, "leverage": 1.3, "margin": 0.4},
    "Entertainment": {"volatility": 1.5, "growth": 1.1, "leverage": 1.0, "margin": 0.8},
    "Media": {"volatility": 1.2, "growth": 0.85, "leverage": 0.9, "margin": 0.9},
    "Software": {"volatility": 1.2, "growth": 1.3, "leverage": 0.5, "margin": 1.6},
    "Semiconductors": {"volatility": 1.5, "growth": 1.2, "leverage": 0.7, "margin": 1.3},
    "Biotechnology": {"volatility": 1.8, "growth": 1.2, "leverage": 0.6, "margin": 0.4},
    "Automotive": {"volatility": 1.1, "growth": 0.85, "leverage": 1.2, "margin": 0.7},
}

# Company size categories
COMPANY_SIZES = {
    "micro": {"revenue_mult": 0.3, "stability": 0.7, "access_capital": 0.6},
    "small": {"revenue_mult": 0.6, "stability": 0.8, "access_capital": 0.75},
    "medium": {"revenue_mult": 1.0, "stability": 0.9, "access_capital": 0.85},
    "large": {"revenue_mult": 1.5, "stability": 1.0, "access_capital": 0.95},
    "enterprise": {"revenue_mult": 2.0, "stability": 1.1, "access_capital": 1.0},
}

# Economic cycle phases
ECONOMIC_CYCLES = ["expansion", "peak", "contraction", "trough"]

# Company name components
PREFIXES = [
    "Global", "National", "American", "United", "Premier", "Advanced", "Strategic",
    "Innovative", "Dynamic", "Integrated", "Pacific", "Atlantic", "Summit", "Apex",
    "Prime", "Elite", "Precision", "Quantum", "Nexus", "Vertex", "Horizon", "Pinnacle",
    "Sterling", "Paramount", "Vanguard", "Titan", "Nova", "Zenith", "Omega", "Alpha",
    "Delta", "Sigma", "Core", "Peak", "Vista", "Metro", "Crown", "Royal", "Eagle",
    "Phoenix", "Liberty", "Freedom", "Pioneer", "Frontier", "Heritage", "Legacy"
]

CORE_NAMES = [
    "Tech", "Systems", "Solutions", "Industries", "Holdings", "Group", "Corp",
    "Enterprises", "Partners", "Associates", "Dynamics", "Resources", "Services",
    "Logistics", "Networks", "Ventures", "Capital", "Management", "Development",
    "International", "Consulting", "Analytics", "Digital", "Bio", "Med", "Pharma",
    "Energy", "Power", "Materials", "Components", "Devices", "Instruments", "Labs",
    "Works", "Manufacturing", "Products", "Brands", "Retail", "Commerce", "Trade"
]

SUFFIXES = ["Inc", "LLC", "Corp", "Ltd", "Co", "Group", "Holdings", "International", "PLC", "SA"]


def generate_company_name(idx):
    """Generate a unique realistic company name."""
    np.random.seed(idx + 1000)
    prefix = np.random.choice(PREFIXES)
    core = np.random.choice(CORE_NAMES)
    suffix = np.random.choice(SUFFIXES)
    return f"{prefix} {core} {suffix}"


def apply_economic_cycle(data, cycle, is_distressed):
    """Adjust financial ratios based on economic cycle."""
    adjustments = {
        "expansion": {"profit": 1.15, "liquidity": 1.1, "leverage": 0.95},
        "peak": {"profit": 1.2, "liquidity": 1.05, "leverage": 1.0},
        "contraction": {"profit": 0.8, "liquidity": 0.9, "leverage": 1.1},
        "trough": {"profit": 0.7, "liquidity": 0.85, "leverage": 1.15},
    }

    adj = adjustments[cycle]

    # Distressed companies are more affected by economic cycles
    if is_distressed:
        impact = 1.5
    else:
        impact = 1.0

    # Apply cycle effects
    data['net_profit_margin'] *= adj['profit'] ** impact
    data['return_on_assets'] *= adj['profit'] ** impact
    data['return_on_equity'] *= adj['profit'] ** impact
    data['current_ratio'] *= adj['liquidity'] ** impact
    data['quick_ratio'] *= adj['liquidity'] ** impact
    data['debt_to_equity'] *= adj['leverage'] ** impact

    return data


def generate_healthy_company(industry_chars, size_chars, economic_cycle):
    """Generate financial ratios for a healthy company with fine-grained variation."""

    # Base financial health factor (0.6 to 1.0 for healthy)
    base_strength = np.random.uniform(0.65, 1.0)

    # Size affects stability
    stability = size_chars['stability'] * base_strength

    # Industry affects margins and leverage
    margin_mult = industry_chars['margin']
    leverage_mult = industry_chars['leverage']

    data = {
        'working_capital_to_total_assets': np.clip(
            np.random.normal(0.22 * stability, 0.06) * (1/leverage_mult), -0.1, 0.5
        ),
        'retained_earnings_to_total_assets': np.clip(
            np.random.normal(0.32 * stability, 0.08), 0, 0.6
        ),
        'ebit_to_total_assets': np.clip(
            np.random.normal(0.10 * stability * margin_mult, 0.03), -0.05, 0.25
        ),
        'market_value_equity_to_total_liabilities': np.clip(
            np.random.normal(2.2 * stability / leverage_mult, 0.5), 0.5, 5.0
        ),
        'sales_to_total_assets': np.clip(
            np.random.normal(1.1 * size_chars['revenue_mult'], 0.25), 0.3, 2.5
        ),
        'current_ratio': np.clip(
            np.random.normal(1.9 * stability, 0.35), 0.9, 4.0
        ),
        'quick_ratio': np.clip(
            np.random.normal(1.4 * stability, 0.3), 0.5, 3.0
        ),
        'debt_to_equity': np.clip(
            np.random.normal(0.65 * leverage_mult / stability, 0.2), 0.1, 2.5
        ),
        'interest_coverage': np.clip(
            np.random.normal(5.5 * stability * margin_mult, 1.8), 1.5, 15.0
        ),
        'net_profit_margin': np.clip(
            np.random.normal(0.07 * stability * margin_mult, 0.025), -0.03, 0.2
        ),
        'return_on_assets': np.clip(
            np.random.normal(0.07 * stability * margin_mult, 0.02), -0.02, 0.15
        ),
        'return_on_equity': np.clip(
            np.random.normal(0.13 * stability * margin_mult, 0.04), -0.08, 0.3
        ),
        'is_insolvent': 0
    }

    # Apply economic cycle effects
    data = apply_economic_cycle(data, economic_cycle, is_distressed=False)

    return data


def generate_distressed_company(industry_chars, size_chars, economic_cycle):
    """Generate financial ratios for a distressed company with fine-grained variation."""

    # Distress severity (0.2 to 0.7, lower = more distressed)
    distress_level = np.random.uniform(0.2, 0.7)

    # Smaller companies in distress have worse access to capital
    capital_access = size_chars['access_capital'] * distress_level

    # Industry volatility affects distress severity
    volatility = industry_chars['volatility']
    leverage_mult = industry_chars['leverage']

    data = {
        'working_capital_to_total_assets': np.clip(
            np.random.normal(-0.08 + 0.15 * distress_level, 0.08 * volatility), -0.35, 0.12
        ),
        'retained_earnings_to_total_assets': np.clip(
            np.random.normal(-0.1 + 0.2 * distress_level, 0.1 * volatility), -0.4, 0.15
        ),
        'ebit_to_total_assets': np.clip(
            np.random.normal(-0.04 + 0.06 * distress_level, 0.04 * volatility), -0.2, 0.06
        ),
        'market_value_equity_to_total_liabilities': np.clip(
            np.random.normal(0.5 + 0.4 * distress_level, 0.25 * volatility), 0.05, 1.4
        ),
        'sales_to_total_assets': np.clip(
            np.random.normal(0.45 + 0.3 * distress_level, 0.18), 0.1, 1.1
        ),
        'current_ratio': np.clip(
            np.random.normal(0.7 + 0.4 * distress_level, 0.25 * volatility), 0.2, 1.4
        ),
        'quick_ratio': np.clip(
            np.random.normal(0.4 + 0.35 * distress_level, 0.2 * volatility), 0.08, 1.1
        ),
        'debt_to_equity': np.clip(
            np.random.normal(3.5 * leverage_mult - distress_level * 1.5, 0.8), 1.2, 8.0
        ),
        'interest_coverage': np.clip(
            np.random.normal(0.8 + distress_level * 1.2, 0.6 * volatility), 0.05, 2.8
        ),
        'net_profit_margin': np.clip(
            np.random.normal(-0.08 + 0.08 * distress_level, 0.04 * volatility), -0.25, 0.02
        ),
        'return_on_assets': np.clip(
            np.random.normal(-0.05 + 0.05 * distress_level, 0.03 * volatility), -0.15, 0.03
        ),
        'return_on_equity': np.clip(
            np.random.normal(-0.15 + 0.12 * distress_level, 0.07 * volatility), -0.4, 0.08
        ),
        'is_insolvent': 1
    }

    # Apply economic cycle effects (more severe for distressed)
    data = apply_economic_cycle(data, economic_cycle, is_distressed=True)

    return data


def generate_borderline_company(industry_chars, size_chars, economic_cycle):
    """Generate financial ratios for a borderline/grey zone company."""

    # Borderline companies can go either way
    direction = np.random.choice([0, 1], p=[0.55, 0.45])
    uncertainty = np.random.uniform(0.35, 0.65)

    volatility = industry_chars['volatility']
    leverage_mult = industry_chars['leverage']
    margin_mult = industry_chars['margin']

    data = {
        'working_capital_to_total_assets': np.clip(
            np.random.normal(0.06, 0.07 * volatility), -0.18, 0.22
        ),
        'retained_earnings_to_total_assets': np.clip(
            np.random.normal(0.1, 0.09 * volatility), -0.15, 0.28
        ),
        'ebit_to_total_assets': np.clip(
            np.random.normal(0.03 * margin_mult, 0.035 * volatility), -0.1, 0.1
        ),
        'market_value_equity_to_total_liabilities': np.clip(
            np.random.normal(1.1 / leverage_mult, 0.35), 0.35, 2.0
        ),
        'sales_to_total_assets': np.clip(
            np.random.normal(0.8, 0.22), 0.25, 1.4
        ),
        'current_ratio': np.clip(
            np.random.normal(1.25, 0.3 * volatility), 0.55, 2.0
        ),
        'quick_ratio': np.clip(
            np.random.normal(0.85, 0.25 * volatility), 0.3, 1.5
        ),
        'debt_to_equity': np.clip(
            np.random.normal(1.5 * leverage_mult, 0.45), 0.6, 3.2
        ),
        'interest_coverage': np.clip(
            np.random.normal(2.2 * margin_mult, 0.9), 0.4, 4.5
        ),
        'net_profit_margin': np.clip(
            np.random.normal(0.015 * margin_mult, 0.03 * volatility), -0.1, 0.06
        ),
        'return_on_assets': np.clip(
            np.random.normal(0.015 * margin_mult, 0.022 * volatility), -0.06, 0.055
        ),
        'return_on_equity': np.clip(
            np.random.normal(0.03 * margin_mult, 0.055 * volatility), -0.15, 0.12
        ),
        'is_insolvent': direction
    }

    # Apply economic cycle effects
    data = apply_economic_cycle(data, economic_cycle, is_distressed=(direction == 1))

    return data


def generate_single_company(idx, company_type):
    """Generate a single company's data."""

    # Select random characteristics
    industry_name = np.random.choice(list(INDUSTRIES.keys()))
    industry_chars = INDUSTRIES[industry_name]

    size_name = np.random.choice(list(COMPANY_SIZES.keys()), p=[0.15, 0.30, 0.30, 0.18, 0.07])
    size_chars = COMPANY_SIZES[size_name]

    economic_cycle = np.random.choice(ECONOMIC_CYCLES, p=[0.35, 0.15, 0.30, 0.20])

    # Generate base financial data
    if company_type == 'healthy':
        base_data = generate_healthy_company(industry_chars, size_chars, economic_cycle)
    elif company_type == 'distressed':
        base_data = generate_distressed_company(industry_chars, size_chars, economic_cycle)
    else:
        base_data = generate_borderline_company(industry_chars, size_chars, economic_cycle)

    # Add metadata
    company_name = generate_company_name(idx)
    company_id = f"COMP_{idx:05d}"

    base_data['company_id'] = company_id
    base_data['company_name'] = company_name
    base_data['industry'] = industry_name
    base_data['company_size'] = size_name
    base_data['economic_cycle'] = economic_cycle

    return base_data


def main():
    print("="*70)
    print("GENERATING 10,000 COMPANY FINANCIAL DATA FILES")
    print("="*70)

    # Distribution: 42% healthy, 38% distressed, 20% borderline
    n_healthy = 4200
    n_distressed = 3800
    n_borderline = 2000
    total = n_healthy + n_distressed + n_borderline

    all_data = []

    print(f"\nGenerating {n_healthy} healthy companies...")
    for i in range(n_healthy):
        data = generate_single_company(i + 1, 'healthy')
        all_data.append(data)
        if (i + 1) % 1000 == 0:
            print(f"  Progress: {i + 1}/{n_healthy}")

    print(f"\nGenerating {n_distressed} distressed companies...")
    for i in range(n_distressed):
        data = generate_single_company(n_healthy + i + 1, 'distressed')
        all_data.append(data)
        if (i + 1) % 1000 == 0:
            print(f"  Progress: {i + 1}/{n_distressed}")

    print(f"\nGenerating {n_borderline} borderline companies...")
    for i in range(n_borderline):
        data = generate_single_company(n_healthy + n_distressed + i + 1, 'borderline')
        all_data.append(data)
        if (i + 1) % 500 == 0:
            print(f"  Progress: {i + 1}/{n_borderline}")

    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Shuffle the data
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Round numeric columns
    numeric_cols = ['working_capital_to_total_assets', 'retained_earnings_to_total_assets',
                    'ebit_to_total_assets', 'market_value_equity_to_total_liabilities',
                    'sales_to_total_assets', 'current_ratio', 'quick_ratio',
                    'debt_to_equity', 'interest_coverage', 'net_profit_margin',
                    'return_on_assets', 'return_on_equity']
    df[numeric_cols] = df[numeric_cols].round(4)

    # Save combined training data
    output_path = DATA_DIR / "_combined_training_data_10k.csv"
    df.to_csv(output_path, index=False)

    # Save index
    index_df = df[['company_id', 'company_name', 'industry', 'company_size', 'economic_cycle', 'is_insolvent']]
    index_df.to_csv(DATA_DIR / "_company_index_10k.csv", index=False)

    # Print summary
    print("\n" + "="*70)
    print("GENERATION COMPLETE!")
    print("="*70)

    print(f"\nTotal companies generated: {len(df)}")
    print(f"\nClass distribution:")
    print(df['is_insolvent'].value_counts())

    print(f"\nIndustry distribution (top 10):")
    print(df['industry'].value_counts().head(10))

    print(f"\nCompany size distribution:")
    print(df['company_size'].value_counts())

    print(f"\nEconomic cycle distribution:")
    print(df['economic_cycle'].value_counts())

    print(f"\nFiles saved to: {DATA_DIR.absolute()}")
    print(f"  - _combined_training_data_10k.csv ({len(df)} rows)")
    print(f"  - _company_index_10k.csv")

    # Feature statistics
    print("\n" + "="*70)
    print("FEATURE STATISTICS BY CLASS")
    print("="*70)

    for col in numeric_cols[:6]:  # Show first 6 features
        healthy_mean = df[df['is_insolvent'] == 0][col].mean()
        distress_mean = df[df['is_insolvent'] == 1][col].mean()
        print(f"\n{col}:")
        print(f"  Healthy mean:    {healthy_mean:.4f}")
        print(f"  Distressed mean: {distress_mean:.4f}")
        print(f"  Difference:      {healthy_mean - distress_mean:.4f}")

    return df


if __name__ == "__main__":
    df = main()
