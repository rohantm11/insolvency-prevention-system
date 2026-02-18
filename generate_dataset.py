"""
Generate 500 realistic company financial data files for model training.
Industry-standard financial ratios with realistic distributions and correlations.
"""

import numpy as np
import pandas as pd
import os
from pathlib import Path

# Create data directory
DATA_DIR = Path("data/training_companies")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Industry sectors with typical financial characteristics
INDUSTRIES = [
    "Technology", "Healthcare", "Manufacturing", "Retail", "Financial Services",
    "Energy", "Consumer Goods", "Telecommunications", "Real Estate", "Transportation",
    "Utilities", "Construction", "Agriculture", "Mining", "Hospitality"
]

# Company name prefixes and suffixes for realistic names
PREFIXES = [
    "Global", "National", "American", "United", "Premier", "Advanced", "Strategic",
    "Innovative", "Dynamic", "Integrated", "Pacific", "Atlantic", "Summit", "Apex",
    "Prime", "Elite", "Precision", "Quantum", "Nexus", "Vertex", "Horizon", "Pinnacle",
    "Sterling", "Paramount", "Vanguard", "Titan", "Nova", "Zenith", "Omega", "Alpha"
]

CORE_NAMES = [
    "Tech", "Systems", "Solutions", "Industries", "Holdings", "Group", "Corp",
    "Enterprises", "Partners", "Associates", "Dynamics", "Resources", "Services",
    "Logistics", "Networks", "Ventures", "Capital", "Management", "Development",
    "International", "Consulting", "Analytics", "Digital", "Bio", "Med", "Pharma",
    "Energy", "Power", "Materials", "Components", "Devices", "Instruments"
]

SUFFIXES = ["Inc", "LLC", "Corp", "Ltd", "Co", "Group", "Holdings", "International"]

np.random.seed(42)

def generate_company_name(idx):
    """Generate a realistic company name."""
    prefix = np.random.choice(PREFIXES)
    core = np.random.choice(CORE_NAMES)
    suffix = np.random.choice(SUFFIXES)
    return f"{prefix} {core} {suffix}"

def generate_healthy_company():
    """Generate financial ratios for a healthy company."""
    # Strong fundamentals with some natural variation
    base_strength = np.random.uniform(0.6, 1.0)  # Overall financial health factor

    return {
        'working_capital_to_total_assets': np.clip(np.random.normal(0.25 * base_strength, 0.08), -0.1, 0.5),
        'retained_earnings_to_total_assets': np.clip(np.random.normal(0.35 * base_strength, 0.1), 0, 0.6),
        'ebit_to_total_assets': np.clip(np.random.normal(0.12 * base_strength, 0.04), -0.05, 0.25),
        'market_value_equity_to_total_liabilities': np.clip(np.random.normal(2.5 * base_strength, 0.6), 0.5, 5.0),
        'sales_to_total_assets': np.clip(np.random.normal(1.2 * base_strength, 0.3), 0.3, 2.5),
        'current_ratio': np.clip(np.random.normal(2.0 * base_strength, 0.4), 0.8, 4.0),
        'quick_ratio': np.clip(np.random.normal(1.5 * base_strength, 0.35), 0.5, 3.0),
        'debt_to_equity': np.clip(np.random.normal(0.6 / base_strength, 0.25), 0.1, 2.0),
        'interest_coverage': np.clip(np.random.normal(6.0 * base_strength, 2.0), 1.0, 15.0),
        'net_profit_margin': np.clip(np.random.normal(0.08 * base_strength, 0.03), -0.05, 0.2),
        'return_on_assets': np.clip(np.random.normal(0.08 * base_strength, 0.025), -0.03, 0.15),
        'return_on_equity': np.clip(np.random.normal(0.15 * base_strength, 0.05), -0.1, 0.3),
        'is_insolvent': 0
    }

def generate_distressed_company():
    """Generate financial ratios for a distressed/at-risk company."""
    # Weak fundamentals with high variation
    distress_level = np.random.uniform(0.3, 0.8)  # How distressed (lower = worse)

    return {
        'working_capital_to_total_assets': np.clip(np.random.normal(-0.05 + 0.1 * distress_level, 0.1), -0.3, 0.15),
        'retained_earnings_to_total_assets': np.clip(np.random.normal(-0.05 + 0.15 * distress_level, 0.12), -0.3, 0.2),
        'ebit_to_total_assets': np.clip(np.random.normal(-0.02 + 0.05 * distress_level, 0.05), -0.15, 0.08),
        'market_value_equity_to_total_liabilities': np.clip(np.random.normal(0.6 + 0.4 * distress_level, 0.3), 0.1, 1.5),
        'sales_to_total_assets': np.clip(np.random.normal(0.5 + 0.3 * distress_level, 0.2), 0.1, 1.2),
        'current_ratio': np.clip(np.random.normal(0.8 + 0.4 * distress_level, 0.3), 0.2, 1.5),
        'quick_ratio': np.clip(np.random.normal(0.5 + 0.3 * distress_level, 0.25), 0.1, 1.2),
        'debt_to_equity': np.clip(np.random.normal(3.0 - distress_level, 1.0), 1.0, 6.0),
        'interest_coverage': np.clip(np.random.normal(1.0 + distress_level, 0.8), 0.1, 3.0),
        'net_profit_margin': np.clip(np.random.normal(-0.05 + 0.05 * distress_level, 0.04), -0.2, 0.03),
        'return_on_assets': np.clip(np.random.normal(-0.03 + 0.04 * distress_level, 0.03), -0.12, 0.04),
        'return_on_equity': np.clip(np.random.normal(-0.1 + 0.1 * distress_level, 0.08), -0.3, 0.1),
        'is_insolvent': 1
    }

def generate_borderline_company():
    """Generate financial ratios for a borderline/grey zone company."""
    # Mixed signals - some good, some concerning
    direction = np.random.choice([0, 1])  # Will tip healthy or distressed
    uncertainty = np.random.uniform(0.4, 0.6)

    return {
        'working_capital_to_total_assets': np.clip(np.random.normal(0.08, 0.08), -0.15, 0.25),
        'retained_earnings_to_total_assets': np.clip(np.random.normal(0.12, 0.1), -0.1, 0.3),
        'ebit_to_total_assets': np.clip(np.random.normal(0.04, 0.04), -0.08, 0.12),
        'market_value_equity_to_total_liabilities': np.clip(np.random.normal(1.2, 0.4), 0.4, 2.2),
        'sales_to_total_assets': np.clip(np.random.normal(0.85, 0.25), 0.3, 1.5),
        'current_ratio': np.clip(np.random.normal(1.3, 0.35), 0.6, 2.2),
        'quick_ratio': np.clip(np.random.normal(0.9, 0.3), 0.3, 1.6),
        'debt_to_equity': np.clip(np.random.normal(1.4, 0.5), 0.5, 3.0),
        'interest_coverage': np.clip(np.random.normal(2.5, 1.0), 0.5, 5.0),
        'net_profit_margin': np.clip(np.random.normal(0.02, 0.03), -0.08, 0.08),
        'return_on_assets': np.clip(np.random.normal(0.02, 0.025), -0.05, 0.07),
        'return_on_equity': np.clip(np.random.normal(0.04, 0.06), -0.12, 0.15),
        'is_insolvent': direction
    }

def add_industry_adjustments(data, industry):
    """Adjust ratios based on industry norms."""
    adjustments = {
        "Technology": {'sales_to_total_assets': 0.8, 'net_profit_margin': 1.3, 'debt_to_equity': 0.7},
        "Healthcare": {'net_profit_margin': 1.2, 'return_on_assets': 1.1, 'current_ratio': 1.1},
        "Manufacturing": {'sales_to_total_assets': 1.2, 'working_capital_to_total_assets': 1.1},
        "Retail": {'sales_to_total_assets': 1.5, 'net_profit_margin': 0.6, 'current_ratio': 0.9},
        "Financial Services": {'debt_to_equity': 2.0, 'return_on_equity': 1.2, 'current_ratio': 0.8},
        "Energy": {'debt_to_equity': 1.3, 'ebit_to_total_assets': 1.2},
        "Consumer Goods": {'sales_to_total_assets': 1.3, 'net_profit_margin': 0.9},
        "Telecommunications": {'debt_to_equity': 1.4, 'ebit_to_total_assets': 1.1},
        "Real Estate": {'debt_to_equity': 1.5, 'return_on_assets': 0.8, 'current_ratio': 0.7},
        "Transportation": {'sales_to_total_assets': 1.1, 'debt_to_equity': 1.2},
        "Utilities": {'debt_to_equity': 1.6, 'net_profit_margin': 0.8, 'sales_to_total_assets': 0.6},
        "Construction": {'working_capital_to_total_assets': 1.2, 'current_ratio': 1.2},
        "Agriculture": {'sales_to_total_assets': 0.9, 'net_profit_margin': 0.7},
        "Mining": {'debt_to_equity': 1.3, 'ebit_to_total_assets': 1.3},
        "Hospitality": {'sales_to_total_assets': 1.4, 'net_profit_margin': 0.5, 'debt_to_equity': 1.2}
    }

    if industry in adjustments:
        for key, multiplier in adjustments[industry].items():
            if key in data and key != 'is_insolvent':
                data[key] = data[key] * multiplier

    return data

def generate_quarterly_history(base_data, quarters=8):
    """Generate quarterly historical data with trends."""
    history = []
    is_insolvent = base_data['is_insolvent']

    # Determine trend direction
    if is_insolvent:
        # Deteriorating trend for distressed companies
        trend = np.random.uniform(-0.03, -0.01)
    else:
        # Stable or improving for healthy companies
        trend = np.random.uniform(-0.005, 0.02)

    for q in range(quarters, 0, -1):
        quarter_data = base_data.copy()

        # Apply trend and seasonal variation
        time_factor = 1 + trend * q + np.random.normal(0, 0.02)
        seasonal = 1 + 0.05 * np.sin(2 * np.pi * q / 4)  # Quarterly seasonality

        for key in quarter_data:
            if key not in ['is_insolvent', 'company_id', 'company_name', 'industry', 'quarter']:
                quarter_data[key] = quarter_data[key] * time_factor * seasonal
                # Add random noise
                quarter_data[key] += np.random.normal(0, abs(quarter_data[key]) * 0.05)

        quarter_data['quarter'] = f"Q{((quarters - q) % 4) + 1}_{2024 - (quarters - q) // 4}"
        history.append(quarter_data)

    return history

def generate_single_company_file(idx, company_type):
    """Generate a single company CSV file with historical data."""

    # Generate base financial data
    if company_type == 'healthy':
        base_data = generate_healthy_company()
    elif company_type == 'distressed':
        base_data = generate_distressed_company()
    else:
        base_data = generate_borderline_company()

    # Add company metadata
    company_name = generate_company_name(idx)
    industry = np.random.choice(INDUSTRIES)
    company_id = f"COMP_{idx:04d}"

    base_data['company_id'] = company_id
    base_data['company_name'] = company_name
    base_data['industry'] = industry

    # Apply industry adjustments
    base_data = add_industry_adjustments(base_data, industry)

    # Generate quarterly history
    history = generate_quarterly_history(base_data, quarters=8)

    # Create DataFrame
    df = pd.DataFrame(history)

    # Reorder columns
    cols = ['company_id', 'company_name', 'industry', 'quarter',
            'working_capital_to_total_assets', 'retained_earnings_to_total_assets',
            'ebit_to_total_assets', 'market_value_equity_to_total_liabilities',
            'sales_to_total_assets', 'current_ratio', 'quick_ratio',
            'debt_to_equity', 'interest_coverage', 'net_profit_margin',
            'return_on_assets', 'return_on_equity', 'is_insolvent']
    df = df[cols]

    # Round numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].round(4)

    # Save to CSV
    filename = DATA_DIR / f"{company_id}_{company_name.replace(' ', '_')[:20]}.csv"
    df.to_csv(filename, index=False)

    return company_id, company_name, industry, base_data['is_insolvent']

def main():
    print("="*60)
    print("GENERATING 500 COMPANY FINANCIAL DATA FILES")
    print("="*60)

    # Distribution: 45% healthy, 35% distressed, 20% borderline
    n_healthy = 225
    n_distressed = 175
    n_borderline = 100

    companies = []

    print(f"\nGenerating {n_healthy} healthy companies...")
    for i in range(n_healthy):
        info = generate_single_company_file(i + 1, 'healthy')
        companies.append(info)
        if (i + 1) % 50 == 0:
            print(f"  Created {i + 1}/{n_healthy} healthy company files")

    print(f"\nGenerating {n_distressed} distressed companies...")
    for i in range(n_distressed):
        info = generate_single_company_file(n_healthy + i + 1, 'distressed')
        companies.append(info)
        if (i + 1) % 50 == 0:
            print(f"  Created {i + 1}/{n_distressed} distressed company files")

    print(f"\nGenerating {n_borderline} borderline companies...")
    for i in range(n_borderline):
        info = generate_single_company_file(n_healthy + n_distressed + i + 1, 'borderline')
        companies.append(info)
        if (i + 1) % 50 == 0:
            print(f"  Created {i + 1}/{n_borderline} borderline company files")

    # Create master index file
    index_df = pd.DataFrame(companies, columns=['company_id', 'company_name', 'industry', 'is_insolvent'])
    index_df.to_csv(DATA_DIR / "_company_index.csv", index=False)

    # Create combined training dataset
    print("\nCreating combined training dataset...")
    all_data = []
    for file in DATA_DIR.glob("COMP_*.csv"):
        df = pd.read_csv(file)
        # Use most recent quarter for training
        latest = df.iloc[-1].to_dict()
        all_data.append(latest)

    combined_df = pd.DataFrame(all_data)
    combined_df.to_csv(DATA_DIR / "_combined_training_data.csv", index=False)

    # Print summary
    print("\n" + "="*60)
    print("GENERATION COMPLETE!")
    print("="*60)
    print(f"\nTotal companies generated: {len(companies)}")
    print(f"  - Healthy: {n_healthy} ({n_healthy/len(companies)*100:.1f}%)")
    print(f"  - Distressed: {n_distressed} ({n_distressed/len(companies)*100:.1f}%)")
    print(f"  - Borderline: {n_borderline} ({n_borderline/len(companies)*100:.1f}%)")

    print(f"\nIndustry distribution:")
    industry_counts = index_df['industry'].value_counts()
    for industry, count in industry_counts.items():
        print(f"  - {industry}: {count}")

    print(f"\nFiles saved to: {DATA_DIR.absolute()}")
    print(f"  - 500 individual company CSV files")
    print(f"  - _company_index.csv (master index)")
    print(f"  - _combined_training_data.csv (training dataset)")

    return combined_df

if __name__ == "__main__":
    df = main()
    print(f"\nCombined dataset shape: {df.shape}")
    print(f"Class distribution:\n{df['is_insolvent'].value_counts()}")
