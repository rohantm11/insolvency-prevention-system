"""
Synthetic Data Generator for Insolvency Prevention System.

Generates realistic company financial data and employee data based on
industry-standard distributions and correlations.

Usage:
    # Default: 4000 healthy (not at risk) + 3000 at-risk companies for training
    python scripts/generate_data.py

    # Custom scale
    python scripts/generate_data.py --healthy 4000 --at-risk 3000 --output-dir data

    # Legacy: fixed total with percentage-based distribution
    python scripts/generate_data.py --companies 500 --employees 2000
"""

import argparse
import random
import string
from pathlib import Path
from typing import Tuple
import numpy as np
import pandas as pd
from datetime import datetime

# Set random seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# =============================================================================
# Industry Constants and Distributions
# =============================================================================

INDUSTRIES = [
    'Technology', 'Healthcare', 'Financial Services', 'Manufacturing',
    'Retail', 'Energy', 'Telecommunications', 'Construction',
    'Transportation', 'Real Estate', 'Consumer Goods', 'Utilities',
    'Agriculture', 'Mining', 'Entertainment'
]

COMPANY_PREFIXES = [
    'Global', 'Premier', 'Advanced', 'Strategic', 'Dynamic', 'Prime',
    'Elite', 'Apex', 'Summit', 'Pinnacle', 'Vanguard', 'Quantum',
    'Stellar', 'Omega', 'Alpha', 'United', 'Pioneer', 'Titan',
    'Nova', 'Horizon', 'Century', 'Pacific', 'Atlantic', 'Continental',
    'National', 'International', 'Metropolitan', 'Universal', 'Central'
]

COMPANY_SUFFIXES = [
    'Technologies', 'Industries', 'Solutions', 'Systems', 'Group',
    'Holdings', 'Partners', 'Enterprises', 'Corporation', 'Dynamics',
    'Innovations', 'Services', 'Ventures', 'Manufacturing', 'Logistics',
    'International', 'Corp', 'Inc', 'Ltd', 'Co'
]

DEPARTMENTS = [
    'Engineering', 'Sales', 'Marketing', 'Human Resources', 'Finance',
    'Customer Service', 'IT', 'Operations', 'Research & Development',
    'Legal', 'Product', 'Quality Assurance', 'Supply Chain', 'Administration'
]

JOB_ROLES = {
    'Engineering': ['Software Engineer', 'Senior Engineer', 'Technical Lead', 'Engineering Manager', 'DevOps Engineer', 'Data Engineer'],
    'Sales': ['Sales Representative', 'Account Executive', 'Sales Manager', 'Business Development', 'Sales Director'],
    'Marketing': ['Marketing Specialist', 'Marketing Manager', 'Brand Strategist', 'Content Manager', 'Digital Marketing'],
    'Human Resources': ['HR Manager', 'Recruiter', 'HR Specialist', 'Training Manager', 'Compensation Analyst'],
    'Finance': ['Accountant', 'Financial Analyst', 'Controller', 'Finance Manager', 'Treasury Analyst'],
    'Customer Service': ['Service Representative', 'Support Specialist', 'Customer Success Manager', 'Service Manager'],
    'IT': ['IT Specialist', 'System Administrator', 'Network Engineer', 'IT Manager', 'Security Analyst'],
    'Operations': ['Operations Analyst', 'Operations Manager', 'Quality Specialist', 'Process Engineer', 'Logistics Coordinator'],
    'Research & Development': ['Research Scientist', 'R&D Engineer', 'R&D Manager', 'Innovation Specialist'],
    'Legal': ['Legal Counsel', 'Contract Specialist', 'Compliance Officer', 'Paralegal'],
    'Product': ['Product Manager', 'Product Owner', 'Product Analyst', 'UX Designer'],
    'Quality Assurance': ['QA Engineer', 'QA Lead', 'Test Analyst', 'Quality Manager'],
    'Supply Chain': ['Supply Chain Analyst', 'Procurement Specialist', 'Inventory Manager', 'Logistics Manager'],
    'Administration': ['Executive Assistant', 'Office Manager', 'Administrative Coordinator', 'Receptionist']
}

FIRST_NAMES = [
    'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph',
    'Thomas', 'Charles', 'Christopher', 'Daniel', 'Matthew', 'Anthony', 'Mark',
    'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua', 'Kenneth', 'Kevin', 'Brian',
    'George', 'Timothy', 'Ronald', 'Edward', 'Jason', 'Jeffrey', 'Ryan',
    'Mary', 'Patricia', 'Jennifer', 'Linda', 'Barbara', 'Elizabeth', 'Susan',
    'Jessica', 'Sarah', 'Karen', 'Lisa', 'Nancy', 'Betty', 'Margaret', 'Sandra',
    'Ashley', 'Kimberly', 'Emily', 'Donna', 'Michelle', 'Dorothy', 'Carol',
    'Amanda', 'Melissa', 'Deborah', 'Stephanie', 'Rebecca', 'Sharon', 'Laura'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
    'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen',
    'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera'
]

BUSINESS_TRAVEL = ['Non-Travel', 'Travel_Rarely', 'Travel_Frequently']

# =============================================================================
# Financial Data Generators (codependent ratios)
# =============================================================================
# Ratios are derived from a small set of drivers so relationships hold:
# - quick_ratio <= current_ratio (quick assets subset of current assets)
# - return_on_assets = net_profit_margin * sales_to_total_assets (DuPont)
# - return_on_equity ≈ ROA * (1 + debt_to_equity) (equity multiplier)
# - interest_coverage consistent with EBIT/TA and leverage
# =============================================================================

def _round4(x: float) -> float:
    return round(float(x), 4)


def generate_healthy_company_ratios() -> dict:
    """Generate financial ratios for a healthy company (codependent)."""
    # Driver ratios (Altman + key metrics)
    working_capital_ratio = np.random.uniform(0.1, 0.4)
    retained_earnings_ratio = np.random.uniform(0.2, 0.5)
    ebit_ratio = np.random.uniform(0.05, 0.2)
    market_equity_ratio = np.random.uniform(1.0, 4.0)
    sales_ratio = np.random.uniform(0.8, 2.0)
    current_ratio = np.random.uniform(1.5, 3.5)
    debt_to_equity = np.random.uniform(0.3, 1.5)
    net_profit_margin = np.random.uniform(0.05, 0.25)

    # Derived (codependent)
    quick_ratio = min(current_ratio - 0.01, current_ratio * np.random.uniform(0.5, 0.9))
    return_on_assets = net_profit_margin * sales_ratio
    return_on_equity = return_on_assets * (1 + debt_to_equity) * np.random.uniform(0.95, 1.08)
    interest_coverage = max(3.0, (ebit_ratio / max(0.01, debt_to_equity * 0.08)) * np.random.uniform(0.8, 1.2))

    return {
        'working_capital_to_total_assets': _round4(working_capital_ratio),
        'retained_earnings_to_total_assets': _round4(retained_earnings_ratio),
        'ebit_to_total_assets': _round4(ebit_ratio),
        'market_value_equity_to_total_liabilities': _round4(market_equity_ratio),
        'sales_to_total_assets': _round4(sales_ratio),
        'current_ratio': _round4(current_ratio),
        'quick_ratio': _round4(quick_ratio),
        'debt_to_equity': _round4(debt_to_equity),
        'interest_coverage': _round4(interest_coverage),
        'net_profit_margin': _round4(net_profit_margin),
        'return_on_assets': _round4(return_on_assets),
        'return_on_equity': _round4(return_on_equity),
        'is_bankrupt': 0,
        'years_to_bankruptcy': None
    }


def generate_distressed_company_ratios() -> dict:
    """Generate financial ratios for a distressed company (codependent)."""
    working_capital_ratio = np.random.uniform(-0.2, 0.1)
    retained_earnings_ratio = np.random.uniform(-0.3, 0.1)
    ebit_ratio = np.random.uniform(-0.1, 0.05)
    market_equity_ratio = np.random.uniform(0.1, 1.0)
    sales_ratio = np.random.uniform(0.3, 0.9)
    current_ratio = np.random.uniform(0.4, 1.2)
    debt_to_equity = np.random.uniform(3.0, 8.0)
    net_profit_margin = np.random.uniform(-0.2, 0.02)

    quick_ratio = min(current_ratio - 0.01, current_ratio * np.random.uniform(0.3, 0.7))
    return_on_assets = net_profit_margin * sales_ratio
    return_on_equity = return_on_assets * (1 + debt_to_equity) * np.random.uniform(0.9, 1.15)
    interest_coverage = (ebit_ratio / max(0.05, debt_to_equity * 0.12)) * np.random.uniform(0.7, 1.3)
    interest_coverage = np.clip(interest_coverage, -1.0, 2.0)

    years_to_bankruptcy = random.choice([1, 2, 3, 4, 5])

    return {
        'working_capital_to_total_assets': _round4(working_capital_ratio),
        'retained_earnings_to_total_assets': _round4(retained_earnings_ratio),
        'ebit_to_total_assets': _round4(ebit_ratio),
        'market_value_equity_to_total_liabilities': _round4(market_equity_ratio),
        'sales_to_total_assets': _round4(sales_ratio),
        'current_ratio': _round4(current_ratio),
        'quick_ratio': _round4(quick_ratio),
        'debt_to_equity': _round4(debt_to_equity),
        'interest_coverage': _round4(interest_coverage),
        'net_profit_margin': _round4(net_profit_margin),
        'return_on_assets': _round4(return_on_assets),
        'return_on_equity': _round4(return_on_equity),
        'is_bankrupt': 1,
        'years_to_bankruptcy': years_to_bankruptcy
    }


def generate_grey_zone_company_ratios() -> dict:
    """Generate financial ratios for a company in the grey zone (codependent)."""
    working_capital_ratio = np.random.uniform(0.0, 0.2)
    retained_earnings_ratio = np.random.uniform(0.05, 0.25)
    ebit_ratio = np.random.uniform(0.02, 0.1)
    market_equity_ratio = np.random.uniform(0.8, 2.0)
    sales_ratio = np.random.uniform(0.6, 1.2)
    current_ratio = np.random.uniform(1.0, 2.0)
    debt_to_equity = np.random.uniform(1.5, 3.5)
    net_profit_margin = np.random.uniform(-0.02, 0.08)

    quick_ratio = min(current_ratio - 0.01, current_ratio * np.random.uniform(0.4, 0.8))
    return_on_assets = net_profit_margin * sales_ratio
    return_on_equity = return_on_assets * (1 + debt_to_equity) * np.random.uniform(0.92, 1.1)
    interest_coverage = (ebit_ratio / max(0.03, debt_to_equity * 0.1)) * np.random.uniform(0.75, 1.25)
    interest_coverage = np.clip(interest_coverage, 0.5, 6.0)

    is_bankrupt = 1 if random.random() < 0.3 else 0
    years_to_bankruptcy = random.choice([3, 4, 5, 6, 7]) if is_bankrupt else None

    return {
        'working_capital_to_total_assets': _round4(working_capital_ratio),
        'retained_earnings_to_total_assets': _round4(retained_earnings_ratio),
        'ebit_to_total_assets': _round4(ebit_ratio),
        'market_value_equity_to_total_liabilities': _round4(market_equity_ratio),
        'sales_to_total_assets': _round4(sales_ratio),
        'current_ratio': _round4(current_ratio),
        'quick_ratio': _round4(quick_ratio),
        'debt_to_equity': _round4(debt_to_equity),
        'interest_coverage': _round4(interest_coverage),
        'net_profit_margin': _round4(net_profit_margin),
        'return_on_assets': _round4(return_on_assets),
        'return_on_equity': _round4(return_on_equity),
        'is_bankrupt': is_bankrupt,
        'years_to_bankruptcy': years_to_bankruptcy
    }


def generate_company_data(
    num_companies: int | None = None,
    num_healthy: int | None = None,
    num_distressed: int | None = None,
) -> pd.DataFrame:
    """Generate a dataset of company financial records.

    Either pass num_companies (uses 60% healthy, 25% grey, 15% distressed)
    or pass num_healthy and num_distressed for exact counts (no grey zone).
    """
    if num_healthy is not None and num_distressed is not None:
        # Explicit counts: good (healthy) companies + at-risk (distressed) only
        total = num_healthy + num_distressed
        counts = (num_healthy, 0, num_distressed)  # healthy, grey, distressed
    elif num_companies is not None:
        # Legacy: percentage-based distribution
        num_healthy = int(num_companies * 0.60)
        num_grey = int(num_companies * 0.25)
        num_distressed = num_companies - num_healthy - num_grey
        total = num_companies
        counts = (num_healthy, num_grey, num_distressed)
    else:
        raise ValueError("Provide either num_companies or both num_healthy and num_distressed")

    num_healthy, num_grey, num_distressed = counts
    companies = []
    idx = 0

    def add_company(category: str) -> None:
        nonlocal idx
        idx += 1
        # Use index for uniqueness so we can generate 6k+ companies without name collisions
        name = f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)} #{idx}"
        company_id = f"COMP_{idx:05d}"
        industry = random.choice(INDUSTRIES)
        if category == 'healthy':
            ratios = generate_healthy_company_ratios()
        elif category == 'grey':
            ratios = generate_grey_zone_company_ratios()
        else:
            ratios = generate_distressed_company_ratios()
        company = {
            'company_id': company_id,
            'company_name': name,
            'industry': industry,
            **ratios
        }
        companies.append(company)

    for _ in range(num_healthy):
        add_company('healthy')
    for _ in range(num_grey):
        add_company('grey')
    for _ in range(num_distressed):
        add_company('distressed')

    # Shuffle to randomize order
    random.shuffle(companies)

    return pd.DataFrame(companies)


# =============================================================================
# Employee Data Generators
# =============================================================================

def generate_stable_employee() -> dict:
    """Generate an employee with low attrition risk."""
    age = random.randint(28, 55)
    years_at_company = random.randint(3, min(20, age - 22))
    years_in_role = random.randint(1, min(years_at_company, 10))
    total_working_years = random.randint(years_at_company, age - 20)

    return {
        'age': age,
        'job_level': random.choices([2, 3, 4, 5], weights=[25, 35, 30, 10])[0],
        'performance_rating': random.choices([2, 3, 4], weights=[20, 50, 30])[0],
        'job_satisfaction': random.choices([2, 3, 4], weights=[15, 45, 40])[0],
        'job_involvement': random.choices([2, 3, 4], weights=[15, 45, 40])[0],
        'environment_satisfaction': random.choices([2, 3, 4], weights=[15, 45, 40])[0],
        'monthly_income': random.randint(6000, 15000),
        'percent_salary_hike': random.randint(12, 25),
        'stock_option_level': random.choices([0, 1, 2, 3], weights=[20, 35, 30, 15])[0],
        'years_at_company': years_at_company,
        'years_in_current_role': years_in_role,
        'total_working_years': total_working_years,
        'distance_from_home': random.randint(1, 20),
        'business_travel': random.choices(BUSINESS_TRAVEL, weights=[30, 55, 15])[0],
        'over_time': random.choices(['No', 'Yes'], weights=[80, 20])[0],
        'attrition': 'No'
    }


def generate_attrition_risk_employee() -> dict:
    """Generate an employee with high attrition risk."""
    age = random.randint(22, 45)
    years_at_company = random.randint(0, 5)
    years_in_role = random.randint(0, min(years_at_company, 3))
    total_working_years = random.randint(years_at_company, max(age - 20, years_at_company))

    return {
        'age': age,
        'job_level': random.choices([1, 2, 3], weights=[40, 40, 20])[0],
        'performance_rating': random.choices([1, 2, 3], weights=[25, 50, 25])[0],
        'job_satisfaction': random.choices([1, 2, 3], weights=[40, 40, 20])[0],
        'job_involvement': random.choices([1, 2, 3], weights=[40, 40, 20])[0],
        'environment_satisfaction': random.choices([1, 2, 3], weights=[40, 40, 20])[0],
        'monthly_income': random.randint(3000, 7000),
        'percent_salary_hike': random.randint(10, 15),
        'stock_option_level': random.choices([0, 1], weights=[70, 30])[0],
        'years_at_company': years_at_company,
        'years_in_current_role': years_in_role,
        'total_working_years': total_working_years,
        'distance_from_home': random.randint(10, 30),
        'business_travel': random.choices(BUSINESS_TRAVEL, weights=[10, 40, 50])[0],
        'over_time': random.choices(['No', 'Yes'], weights=[30, 70])[0],
        'attrition': 'Yes'
    }


def generate_moderate_employee() -> dict:
    """Generate an employee with moderate characteristics."""
    age = random.randint(24, 50)
    years_at_company = random.randint(1, 10)
    years_in_role = random.randint(0, min(years_at_company, 6))
    total_working_years = random.randint(years_at_company, max(age - 22, years_at_company))

    # 20% attrition rate for moderate employees
    attrition = 'Yes' if random.random() < 0.20 else 'No'

    return {
        'age': age,
        'job_level': random.choices([1, 2, 3, 4], weights=[20, 35, 30, 15])[0],
        'performance_rating': random.choices([2, 3, 4], weights=[30, 45, 25])[0],
        'job_satisfaction': random.choices([1, 2, 3, 4], weights=[15, 30, 35, 20])[0],
        'job_involvement': random.choices([1, 2, 3, 4], weights=[15, 30, 35, 20])[0],
        'environment_satisfaction': random.choices([1, 2, 3, 4], weights=[15, 30, 35, 20])[0],
        'monthly_income': random.randint(4000, 11000),
        'percent_salary_hike': random.randint(11, 22),
        'stock_option_level': random.choices([0, 1, 2, 3], weights=[30, 35, 25, 10])[0],
        'years_at_company': years_at_company,
        'years_in_current_role': years_in_role,
        'total_working_years': total_working_years,
        'distance_from_home': random.randint(1, 25),
        'business_travel': random.choices(BUSINESS_TRAVEL, weights=[25, 50, 25])[0],
        'over_time': random.choices(['No', 'Yes'], weights=[55, 45])[0],
        'attrition': attrition
    }


def generate_employee_data(num_employees: int) -> pd.DataFrame:
    """Generate a dataset of employee records."""
    employees = []

    # Distribution: 50% stable, 35% moderate, 15% high-risk (realistic attrition ~16%)
    num_stable = int(num_employees * 0.50)
    num_moderate = int(num_employees * 0.35)
    num_high_risk = num_employees - num_stable - num_moderate

    for i in range(num_employees):
        employee_id = f"EMP_{i+1:05d}"
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        gender = random.choice(['Male', 'Female'])
        department = random.choice(DEPARTMENTS)
        job_role = random.choice(JOB_ROLES.get(department, ['Specialist']))

        # Determine employee category
        if i < num_stable:
            attrs = generate_stable_employee()
        elif i < num_stable + num_moderate:
            attrs = generate_moderate_employee()
        else:
            attrs = generate_attrition_risk_employee()

        employee = {
            'employee_id': employee_id,
            'name': name,
            'gender': gender,
            'department': department,
            'job_role': job_role,
            **attrs
        }
        employees.append(employee)

    # Shuffle to randomize order
    random.shuffle(employees)

    return pd.DataFrame(employees)


# =============================================================================
# Test Data Generation
# =============================================================================

def split_train_test(df: pd.DataFrame, test_ratio: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split data into training and test sets."""
    df_shuffled = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    split_idx = int(len(df_shuffled) * (1 - test_ratio))
    return df_shuffled[:split_idx], df_shuffled[split_idx:]


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate synthetic training data')
    parser.add_argument('--companies', type=int, default=None, help='Total companies (uses 60%% healthy, 25%% grey, 15%% distressed)')
    parser.add_argument('--healthy', type=int, default=None, help='Number of healthy (not at risk) companies')
    parser.add_argument('--at-risk', type=int, default=None, dest='at_risk', help='Number of at-risk (distressed) companies')
    parser.add_argument('--employees', type=int, default=2000, help='Number of employees to generate')
    parser.add_argument('--output-dir', type=str, default='data', help='Output directory')
    parser.add_argument('--test-ratio', type=float, default=0.2, help='Test set ratio')
    args = parser.parse_args()

    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("Insolvency Prevention System - Data Generator")
    print(f"{'='*60}\n")

    # Generate company data: prefer explicit --healthy / --at-risk for training scale
    if args.healthy is not None and args.at_risk is not None:
        total = args.healthy + args.at_risk
        print(f"Generating {total} company financial records ({args.healthy} healthy, {args.at_risk} at-risk)...")
        company_df = generate_company_data(num_healthy=args.healthy, num_distressed=args.at_risk)
    elif args.companies is not None:
        print(f"Generating {args.companies} company financial records (60%% healthy, 25%% grey, 15%% distressed)...")
        company_df = generate_company_data(num_companies=args.companies)
    else:
        # Default: scaled training set (4000 good + 3000 at-risk)
        args.healthy = 4000
        args.at_risk = 3000
        total = args.healthy + args.at_risk
        print(f"Generating {total} company financial records ({args.healthy} healthy, {args.at_risk} at-risk)...")
        company_df = generate_company_data(num_healthy=args.healthy, num_distressed=args.at_risk)

    # Add human-readable label: good (no insolvency risk) vs bad (at risk)
    company_df = company_df.copy()
    company_df['label'] = company_df['is_bankrupt'].map({0: 'good', 1: 'bad'})

    # Split into train/test
    company_train, company_test = split_train_test(company_df, args.test_ratio)

    # Save company data
    company_df.to_csv(output_dir / 'company_data.csv', index=False)
    company_train.to_csv(output_dir / 'company_train.csv', index=False)
    company_test.to_csv(output_dir / 'company_test.csv', index=False)

    # Statistics
    bankrupt_count = company_df['is_bankrupt'].sum()
    print(f"  Total companies: {len(company_df)}")
    print(f"  Healthy companies: {len(company_df) - bankrupt_count}")
    print(f"  Distressed companies: {bankrupt_count}")
    print(f"  Train set: {len(company_train)}, Test set: {len(company_test)}")

    # Generate employee data
    print(f"\nGenerating {args.employees} employee records...")
    employee_df = generate_employee_data(args.employees)

    # Split into train/test
    employee_train, employee_test = split_train_test(employee_df, args.test_ratio)

    # Save employee data
    employee_df.to_csv(output_dir / 'employee_data.csv', index=False)
    employee_train.to_csv(output_dir / 'employee_train.csv', index=False)
    employee_test.to_csv(output_dir / 'employee_test.csv', index=False)

    # Statistics
    attrition_count = (employee_df['attrition'] == 'Yes').sum()
    print(f"  Total employees: {len(employee_df)}")
    print(f"  Retained employees: {len(employee_df) - attrition_count}")
    print(f"  Attrition cases: {attrition_count}")
    print(f"  Attrition rate: {attrition_count/len(employee_df)*100:.1f}%")
    print(f"  Train set: {len(employee_train)}, Test set: {len(employee_test)}")

    print(f"\n{'='*60}")
    print("Data generation complete!")
    print(f"Files saved to: {output_dir.absolute()}")
    print(f"{'='*60}\n")

    # Print sample records
    print("Sample Company Record:")
    print(company_df.iloc[0].to_dict())
    print("\nSample Employee Record:")
    print(employee_df.iloc[0].to_dict())


if __name__ == '__main__':
    main()
