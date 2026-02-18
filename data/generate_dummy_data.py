"""
Generate dummy data for testing the Insolvency Prevention System.

This script creates synthetic datasets for:
- Company financial data (for insolvency prediction using Altman Z-score components)
- Employee performance data (for attrition prediction)
"""

import numpy as np
import pandas as pd
from pathlib import Path


# Company name components for generating realistic names
COMPANY_PREFIXES = [
    "Global", "United", "Premier", "Advanced", "Dynamic", "Strategic", "Prime",
    "Elite", "Apex", "Summit", "Horizon", "Pinnacle", "Vanguard", "Pioneer",
    "Quantum", "Stellar", "Alpha", "Omega", "Nova", "Titan"
]

COMPANY_SUFFIXES = [
    "Industries", "Solutions", "Technologies", "Systems", "Enterprises", "Corp",
    "Holdings", "Group", "Partners", "Dynamics", "Innovations", "Ventures",
    "Services", "International", "Logistics", "Manufacturing"
]

INDUSTRIES = [
    "Technology", "Manufacturing", "Healthcare", "Financial Services", "Retail",
    "Energy", "Transportation", "Construction", "Telecommunications", "Real Estate"
]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
]

DEPARTMENTS = [
    "Sales", "Research & Development", "Human Resources", "Finance", "Marketing",
    "Operations", "Engineering", "Customer Service", "IT", "Legal"
]

JOB_ROLES = {
    "Sales": ["Sales Representative", "Account Manager", "Sales Director", "Business Development"],
    "Research & Development": ["Research Scientist", "Product Developer", "R&D Manager", "Lab Technician"],
    "Human Resources": ["HR Specialist", "Recruiter", "HR Manager", "Training Coordinator"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Manager", "Controller"],
    "Marketing": ["Marketing Specialist", "Content Creator", "Marketing Manager", "Brand Strategist"],
    "Operations": ["Operations Analyst", "Process Engineer", "Operations Manager", "Quality Specialist"],
    "Engineering": ["Software Engineer", "Mechanical Engineer", "Engineering Manager", "Technical Lead"],
    "Customer Service": ["Support Specialist", "Customer Success Manager", "Service Representative", "Support Lead"],
    "IT": ["System Administrator", "Network Engineer", "IT Manager", "Security Analyst"],
    "Legal": ["Legal Counsel", "Compliance Officer", "Paralegal", "Contract Specialist"]
}


def generate_company_data(n_samples: int = 100, seed: int = 42) -> pd.DataFrame:
    """
    Generate dummy company financial data for insolvency prediction.

    Uses Altman Z-score components and additional financial ratios.
    Bankrupt companies (~20%) have systematically worse financial ratios.

    Args:
        n_samples: Number of company records to generate
        seed: Random seed for reproducibility

    Returns:
        DataFrame with company financial features and bankruptcy labels
    """
    np.random.seed(seed)

    # Target ~20% bankruptcy rate
    n_bankrupt = int(n_samples * 0.20)
    n_healthy = n_samples - n_bankrupt

    # Generate company identifiers
    company_ids = [f"COMP_{i:04d}" for i in range(1, n_samples + 1)]

    # Generate unique company names
    company_names = []
    used_names = set()
    for _ in range(n_samples):
        while True:
            name = f"{np.random.choice(COMPANY_PREFIXES)} {np.random.choice(COMPANY_SUFFIXES)}"
            if name not in used_names:
                used_names.add(name)
                company_names.append(name)
                break

    industries = np.random.choice(INDUSTRIES, n_samples)

    # Generate financial ratios for HEALTHY companies
    # Altman Z-score components (healthy ranges)
    healthy_wc_ta = np.random.uniform(0.1, 0.4, n_healthy)  # Working Capital / Total Assets
    healthy_re_ta = np.random.uniform(0.2, 0.5, n_healthy)  # Retained Earnings / Total Assets
    healthy_ebit_ta = np.random.uniform(0.05, 0.2, n_healthy)  # EBIT / Total Assets
    healthy_mve_tl = np.random.uniform(1.0, 4.0, n_healthy)  # Market Value Equity / Total Liabilities
    healthy_sales_ta = np.random.uniform(0.8, 2.0, n_healthy)  # Sales / Total Assets

    # Additional ratios (healthy ranges)
    healthy_current = np.random.uniform(1.5, 3.5, n_healthy)
    healthy_quick = np.random.uniform(1.0, 2.5, n_healthy)
    healthy_dte = np.random.uniform(0.3, 1.5, n_healthy)
    healthy_interest_cov = np.random.uniform(3.0, 15.0, n_healthy)
    healthy_npm = np.random.uniform(0.05, 0.25, n_healthy)
    healthy_roa = np.random.uniform(0.05, 0.20, n_healthy)
    healthy_roe = np.random.uniform(0.10, 0.30, n_healthy)

    # Generate financial ratios for BANKRUPT companies (worse ratios)
    # Altman Z-score components (distressed ranges)
    bankrupt_wc_ta = np.random.uniform(-0.2, 0.1, n_bankrupt)  # Often negative
    bankrupt_re_ta = np.random.uniform(-0.3, 0.1, n_bankrupt)  # Often negative
    bankrupt_ebit_ta = np.random.uniform(-0.1, 0.05, n_bankrupt)  # Low or negative
    bankrupt_mve_tl = np.random.uniform(0.1, 1.0, n_bankrupt)  # Low
    bankrupt_sales_ta = np.random.uniform(0.3, 0.9, n_bankrupt)  # Lower sales efficiency

    # Additional ratios (distressed ranges)
    bankrupt_current = np.random.uniform(0.4, 1.2, n_bankrupt)
    bankrupt_quick = np.random.uniform(0.2, 0.8, n_bankrupt)
    bankrupt_dte = np.random.uniform(2.0, 8.0, n_bankrupt)  # High leverage
    bankrupt_interest_cov = np.random.uniform(-1.0, 2.0, n_bankrupt)  # Low or negative
    bankrupt_npm = np.random.uniform(-0.20, 0.02, n_bankrupt)  # Often negative
    bankrupt_roa = np.random.uniform(-0.15, 0.03, n_bankrupt)
    bankrupt_roe = np.random.uniform(-0.30, 0.05, n_bankrupt)

    # Combine healthy and bankrupt data
    working_capital_to_total_assets = np.concatenate([healthy_wc_ta, bankrupt_wc_ta])
    retained_earnings_to_total_assets = np.concatenate([healthy_re_ta, bankrupt_re_ta])
    ebit_to_total_assets = np.concatenate([healthy_ebit_ta, bankrupt_ebit_ta])
    market_value_equity_to_total_liabilities = np.concatenate([healthy_mve_tl, bankrupt_mve_tl])
    sales_to_total_assets = np.concatenate([healthy_sales_ta, bankrupt_sales_ta])

    current_ratio = np.concatenate([healthy_current, bankrupt_current])
    quick_ratio = np.concatenate([healthy_quick, bankrupt_quick])
    debt_to_equity = np.concatenate([healthy_dte, bankrupt_dte])
    interest_coverage = np.concatenate([healthy_interest_cov, bankrupt_interest_cov])
    net_profit_margin = np.concatenate([healthy_npm, bankrupt_npm])
    return_on_assets = np.concatenate([healthy_roa, bankrupt_roa])
    return_on_equity = np.concatenate([healthy_roe, bankrupt_roe])

    # Bankruptcy labels
    is_bankrupt = np.array([0] * n_healthy + [1] * n_bankrupt)

    # Years to bankruptcy (only for bankrupt companies)
    years_to_bankruptcy = np.where(
        is_bankrupt == 1,
        np.random.randint(1, 6, n_samples),  # 1-5 years
        np.nan
    )

    # Create DataFrame
    data = pd.DataFrame({
        "company_id": company_ids,
        "company_name": company_names,
        "industry": industries,
        "working_capital_to_total_assets": np.round(working_capital_to_total_assets, 4),
        "retained_earnings_to_total_assets": np.round(retained_earnings_to_total_assets, 4),
        "ebit_to_total_assets": np.round(ebit_to_total_assets, 4),
        "market_value_equity_to_total_liabilities": np.round(market_value_equity_to_total_liabilities, 4),
        "sales_to_total_assets": np.round(sales_to_total_assets, 4),
        "current_ratio": np.round(current_ratio, 4),
        "quick_ratio": np.round(quick_ratio, 4),
        "debt_to_equity": np.round(debt_to_equity, 4),
        "interest_coverage": np.round(interest_coverage, 4),
        "net_profit_margin": np.round(net_profit_margin, 4),
        "return_on_assets": np.round(return_on_assets, 4),
        "return_on_equity": np.round(return_on_equity, 4),
        "is_bankrupt": is_bankrupt,
        "years_to_bankruptcy": years_to_bankruptcy,
    })

    # Shuffle to mix healthy and bankrupt companies
    data = data.sample(frac=1, random_state=seed).reset_index(drop=True)

    return data


def generate_employee_data(n_samples: int = 500, seed: int = 42) -> pd.DataFrame:
    """
    Generate dummy employee data for attrition prediction.

    Attrition (~16%) correlates with low satisfaction and performance.

    Args:
        n_samples: Number of employee records to generate
        seed: Random seed for reproducibility

    Returns:
        DataFrame with employee features and attrition labels
    """
    np.random.seed(seed)

    # Employee identifiers
    employee_ids = [f"EMP_{i:05d}" for i in range(1, n_samples + 1)]

    # Generate names
    names = [
        f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)}"
        for _ in range(n_samples)
    ]

    # Demographics
    ages = np.random.randint(22, 60, n_samples)
    genders = np.random.choice(["Male", "Female"], n_samples, p=[0.52, 0.48])

    # Department and job info
    departments = np.random.choice(DEPARTMENTS, n_samples)
    job_roles = [np.random.choice(JOB_ROLES[dept]) for dept in departments]
    job_levels = np.random.randint(1, 6, n_samples)  # 1-5

    # Performance and satisfaction metrics (1-4 scale)
    # Generate base scores that will influence attrition
    base_satisfaction = np.random.uniform(1, 4, n_samples)

    performance_rating = np.clip(
        np.round(base_satisfaction + np.random.uniform(-0.5, 0.5, n_samples)), 1, 4
    ).astype(int)

    job_satisfaction = np.clip(
        np.round(base_satisfaction + np.random.uniform(-0.3, 0.3, n_samples)), 1, 4
    ).astype(int)

    job_involvement = np.clip(
        np.round(base_satisfaction + np.random.uniform(-0.4, 0.4, n_samples)), 1, 4
    ).astype(int)

    environment_satisfaction = np.clip(
        np.round(base_satisfaction + np.random.uniform(-0.3, 0.3, n_samples)), 1, 4
    ).astype(int)

    # Compensation
    base_income = 3000 + (job_levels * 1500) + (ages - 22) * 50
    monthly_income = np.round(
        base_income + np.random.uniform(-500, 1500, n_samples)
    ).astype(int)

    percent_salary_hike = np.random.randint(11, 25, n_samples)
    stock_option_level = np.random.randint(0, 4, n_samples)  # 0-3

    # Work history
    max_tenure = np.minimum(ages - 22, 40)  # Can't work more years than age allows
    years_at_company = np.array([
        np.random.randint(0, max(1, mt + 1)) for mt in max_tenure
    ])

    years_in_current_role = np.array([
        np.random.randint(0, max(1, yac + 1)) for yac in years_at_company
    ])

    total_working_years = np.array([
        np.random.randint(yac, max(yac + 1, age - 21))
        for yac, age in zip(years_at_company, ages)
    ])

    # Other factors
    distance_from_home = np.random.randint(1, 30, n_samples)
    business_travel = np.random.choice(
        ["Non-Travel", "Travel_Rarely", "Travel_Frequently"],
        n_samples,
        p=[0.15, 0.70, 0.15]
    )
    over_time = np.random.choice(["Yes", "No"], n_samples, p=[0.28, 0.72])

    # Calculate attrition probability based on factors
    # Low satisfaction/performance -> higher attrition
    attrition_score = (
        (4 - performance_rating) * 0.15 +
        (4 - job_satisfaction) * 0.20 +
        (4 - job_involvement) * 0.10 +
        (4 - environment_satisfaction) * 0.15 +
        (over_time == "Yes").astype(float) * 0.15 +
        (business_travel == "Travel_Frequently").astype(float) * 0.10 +
        (distance_from_home > 20).astype(float) * 0.05 +
        (years_at_company < 2).astype(float) * 0.10 +
        np.random.uniform(0, 0.3, n_samples)  # Random noise
    )

    # Normalize to achieve ~16% attrition rate
    threshold = np.percentile(attrition_score, 84)
    attrition = np.where(attrition_score >= threshold, "Yes", "No")

    # Create DataFrame
    data = pd.DataFrame({
        "employee_id": employee_ids,
        "name": names,
        "age": ages,
        "gender": genders,
        "department": departments,
        "job_role": job_roles,
        "job_level": job_levels,
        "performance_rating": performance_rating,
        "job_satisfaction": job_satisfaction,
        "job_involvement": job_involvement,
        "environment_satisfaction": environment_satisfaction,
        "monthly_income": monthly_income,
        "percent_salary_hike": percent_salary_hike,
        "stock_option_level": stock_option_level,
        "years_at_company": years_at_company,
        "years_in_current_role": years_in_current_role,
        "total_working_years": total_working_years,
        "distance_from_home": distance_from_home,
        "business_travel": business_travel,
        "over_time": over_time,
        "attrition": attrition,
    })

    return data


def main():
    """Generate and save dummy datasets."""
    output_dir = Path(__file__).parent

    # Generate company financial data
    print("=" * 60)
    print("GENERATING COMPANY FINANCIAL DATA")
    print("=" * 60)
    company_data = generate_company_data(n_samples=100)
    company_data.to_csv(output_dir / "company_data.csv", index=False)

    bankruptcy_rate = company_data['is_bankrupt'].mean()
    print(f"  Total companies: {len(company_data)}")
    print(f"  Bankruptcy rate: {bankruptcy_rate:.1%}")
    print(f"  Industries: {company_data['industry'].nunique()}")
    print(f"\n  Sample bankrupt company ratios:")
    bankrupt_sample = company_data[company_data['is_bankrupt'] == 1].iloc[0]
    print(f"    - Current Ratio: {bankrupt_sample['current_ratio']:.2f}")
    print(f"    - Debt to Equity: {bankrupt_sample['debt_to_equity']:.2f}")
    print(f"    - Net Profit Margin: {bankrupt_sample['net_profit_margin']:.2%}")
    print(f"\n  Sample healthy company ratios:")
    healthy_sample = company_data[company_data['is_bankrupt'] == 0].iloc[0]
    print(f"    - Current Ratio: {healthy_sample['current_ratio']:.2f}")
    print(f"    - Debt to Equity: {healthy_sample['debt_to_equity']:.2f}")
    print(f"    - Net Profit Margin: {healthy_sample['net_profit_margin']:.2%}")
    print(f"\n  Saved to: {output_dir / 'company_data.csv'}")

    # Generate employee data
    print("\n" + "=" * 60)
    print("GENERATING EMPLOYEE DATA")
    print("=" * 60)
    employee_data = generate_employee_data(n_samples=500)
    employee_data.to_csv(output_dir / "employee_data.csv", index=False)

    attrition_rate = (employee_data['attrition'] == 'Yes').mean()
    print(f"  Total employees: {len(employee_data)}")
    print(f"  Attrition rate: {attrition_rate:.1%}")
    print(f"  Departments: {employee_data['department'].nunique()}")
    print(f"\n  Attrition by satisfaction level:")
    for sat_level in [1, 2, 3, 4]:
        subset = employee_data[employee_data['job_satisfaction'] == sat_level]
        att_rate = (subset['attrition'] == 'Yes').mean() if len(subset) > 0 else 0
        print(f"    - Job Satisfaction {sat_level}: {att_rate:.1%} attrition ({len(subset)} employees)")
    print(f"\n  Saved to: {output_dir / 'employee_data.csv'}")

    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
