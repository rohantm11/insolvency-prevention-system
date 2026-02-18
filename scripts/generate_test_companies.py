"""
Generate comprehensive test data for SolvencyInsight system.

Creates 20 company folders:
- 10 companies with HIGH insolvency risk
- 10 companies with LOW insolvency risk (safe)

Each folder contains:
- company_data.csv: Single company financial data
- employee_data.csv: 200-400 employees matching company profile

Data is industry-realistic and internally consistent.
"""

import os
import random
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta


# Industry definitions with realistic parameters
INDUSTRIES = {
    'retail': {
        'sector': 'Consumer Discretionary',
        'departments': ['Sales', 'Store Operations', 'Merchandising', 'E-Commerce', 'Supply Chain',
                       'Marketing', 'Customer Service', 'HR', 'Finance', 'IT', 'Loss Prevention'],
        'job_roles': {
            'Sales': ['Sales Associate', 'Sales Lead', 'Department Manager', 'Regional Sales Manager'],
            'Store Operations': ['Store Manager', 'Assistant Manager', 'Operations Coordinator', 'Shift Supervisor'],
            'Merchandising': ['Merchandiser', 'Visual Merchandiser', 'Buyer', 'Category Manager'],
            'E-Commerce': ['E-Commerce Specialist', 'Digital Marketing Manager', 'Web Developer', 'UX Designer'],
            'Supply Chain': ['Warehouse Associate', 'Inventory Manager', 'Logistics Coordinator', 'Supply Chain Analyst'],
            'Marketing': ['Marketing Coordinator', 'Brand Manager', 'Social Media Manager', 'Marketing Director'],
            'Customer Service': ['Customer Service Rep', 'Call Center Agent', 'Customer Success Manager', 'Service Director'],
            'HR': ['HR Coordinator', 'Recruiter', 'HR Manager', 'HR Director'],
            'Finance': ['Accountant', 'Financial Analyst', 'Controller', 'CFO'],
            'IT': ['IT Support', 'Systems Administrator', 'Software Developer', 'IT Manager'],
            'Loss Prevention': ['Security Officer', 'LP Specialist', 'LP Manager', 'Regional LP Director']
        },
        'avg_income_multiplier': 0.85,
        'travel_profile': {'Non-Travel': 0.6, 'Travel_Rarely': 0.3, 'Travel_Frequently': 0.1}
    },
    'technology': {
        'sector': 'Technology',
        'departments': ['Engineering', 'Product', 'Sales', 'Marketing', 'Customer Success',
                       'HR', 'Finance', 'Legal', 'Operations', 'Research'],
        'job_roles': {
            'Engineering': ['Software Engineer', 'Senior Engineer', 'Staff Engineer', 'Engineering Manager', 'VP Engineering'],
            'Product': ['Product Manager', 'Senior PM', 'Director of Product', 'VP Product'],
            'Sales': ['SDR', 'Account Executive', 'Senior AE', 'Sales Manager', 'VP Sales'],
            'Marketing': ['Marketing Coordinator', 'Content Manager', 'Growth Manager', 'CMO'],
            'Customer Success': ['CSM', 'Senior CSM', 'CS Manager', 'VP Customer Success'],
            'HR': ['HR Coordinator', 'Recruiter', 'HR Manager', 'VP People'],
            'Finance': ['Accountant', 'FP&A Analyst', 'Controller', 'CFO'],
            'Legal': ['Paralegal', 'Legal Counsel', 'Senior Counsel', 'General Counsel'],
            'Operations': ['Operations Analyst', 'Operations Manager', 'COO'],
            'Research': ['Research Scientist', 'Senior Researcher', 'Research Director']
        },
        'avg_income_multiplier': 1.4,
        'travel_profile': {'Non-Travel': 0.4, 'Travel_Rarely': 0.45, 'Travel_Frequently': 0.15}
    },
    'healthcare': {
        'sector': 'Healthcare',
        'departments': ['Clinical', 'Nursing', 'Administration', 'Finance', 'IT',
                       'HR', 'Quality', 'Research', 'Pharmacy', 'Support Services'],
        'job_roles': {
            'Clinical': ['Medical Assistant', 'Physician Assistant', 'Nurse Practitioner', 'Physician', 'Chief Medical Officer'],
            'Nursing': ['RN', 'Charge Nurse', 'Nurse Manager', 'Director of Nursing', 'CNO'],
            'Administration': ['Admin Assistant', 'Office Manager', 'Department Director', 'COO', 'CEO'],
            'Finance': ['Billing Specialist', 'Accountant', 'Revenue Cycle Manager', 'CFO'],
            'IT': ['IT Support', 'Health IT Specialist', 'IT Manager', 'CIO'],
            'HR': ['HR Coordinator', 'HR Manager', 'VP HR'],
            'Quality': ['Quality Analyst', 'Quality Manager', 'Chief Quality Officer'],
            'Research': ['Research Coordinator', 'Clinical Research Manager', 'Director of Research'],
            'Pharmacy': ['Pharmacy Tech', 'Pharmacist', 'Pharmacy Director'],
            'Support Services': ['Housekeeper', 'Dietary Aide', 'Maintenance Tech', 'Facilities Manager']
        },
        'avg_income_multiplier': 1.15,
        'travel_profile': {'Non-Travel': 0.75, 'Travel_Rarely': 0.2, 'Travel_Frequently': 0.05}
    },
    'manufacturing': {
        'sector': 'Industrials',
        'departments': ['Production', 'Quality', 'Engineering', 'Maintenance', 'Supply Chain',
                       'Warehouse', 'HR', 'Finance', 'Sales', 'R&D'],
        'job_roles': {
            'Production': ['Production Worker', 'Machine Operator', 'Production Lead', 'Production Manager', 'Plant Manager'],
            'Quality': ['Quality Inspector', 'Quality Technician', 'Quality Engineer', 'Quality Manager'],
            'Engineering': ['Manufacturing Engineer', 'Process Engineer', 'Senior Engineer', 'Engineering Manager'],
            'Maintenance': ['Maintenance Tech', 'Senior Tech', 'Maintenance Supervisor', 'Maintenance Manager'],
            'Supply Chain': ['Procurement Specialist', 'Planner', 'Supply Chain Manager', 'VP Supply Chain'],
            'Warehouse': ['Warehouse Worker', 'Forklift Operator', 'Warehouse Lead', 'Warehouse Manager'],
            'HR': ['HR Coordinator', 'HR Generalist', 'HR Manager', 'VP HR'],
            'Finance': ['Accountant', 'Cost Accountant', 'Controller', 'CFO'],
            'Sales': ['Inside Sales Rep', 'Account Manager', 'Sales Manager', 'VP Sales'],
            'R&D': ['R&D Technician', 'R&D Engineer', 'Senior R&D Engineer', 'R&D Director']
        },
        'avg_income_multiplier': 0.95,
        'travel_profile': {'Non-Travel': 0.7, 'Travel_Rarely': 0.25, 'Travel_Frequently': 0.05}
    },
    'financial': {
        'sector': 'Financials',
        'departments': ['Banking', 'Lending', 'Wealth Management', 'Risk', 'Compliance',
                       'IT', 'Operations', 'HR', 'Marketing', 'Legal'],
        'job_roles': {
            'Banking': ['Teller', 'Personal Banker', 'Branch Manager', 'Regional Manager', 'SVP Banking'],
            'Lending': ['Loan Officer', 'Underwriter', 'Senior Underwriter', 'Lending Manager', 'Chief Credit Officer'],
            'Wealth Management': ['Financial Advisor', 'Senior Advisor', 'Portfolio Manager', 'Managing Director'],
            'Risk': ['Risk Analyst', 'Senior Risk Analyst', 'Risk Manager', 'Chief Risk Officer'],
            'Compliance': ['Compliance Analyst', 'Compliance Officer', 'Senior Compliance Officer', 'Chief Compliance Officer'],
            'IT': ['IT Support', 'Systems Analyst', 'IT Manager', 'CIO'],
            'Operations': ['Operations Specialist', 'Operations Analyst', 'Operations Manager', 'COO'],
            'HR': ['HR Coordinator', 'HR Manager', 'VP HR'],
            'Marketing': ['Marketing Coordinator', 'Marketing Manager', 'CMO'],
            'Legal': ['Paralegal', 'Legal Counsel', 'General Counsel']
        },
        'avg_income_multiplier': 1.25,
        'travel_profile': {'Non-Travel': 0.5, 'Travel_Rarely': 0.4, 'Travel_Frequently': 0.1}
    },
    'energy': {
        'sector': 'Energy',
        'departments': ['Operations', 'Engineering', 'Safety', 'Maintenance', 'Environmental',
                       'Finance', 'HR', 'Legal', 'IT', 'Business Development'],
        'job_roles': {
            'Operations': ['Field Operator', 'Control Room Operator', 'Operations Supervisor', 'Operations Manager', 'VP Operations'],
            'Engineering': ['Field Engineer', 'Project Engineer', 'Senior Engineer', 'Engineering Manager', 'VP Engineering'],
            'Safety': ['Safety Technician', 'Safety Specialist', 'Safety Manager', 'VP Safety'],
            'Maintenance': ['Maintenance Tech', 'Senior Tech', 'Maintenance Supervisor', 'Maintenance Manager'],
            'Environmental': ['Environmental Specialist', 'Senior Specialist', 'Environmental Manager', 'VP Environmental'],
            'Finance': ['Accountant', 'Financial Analyst', 'Controller', 'CFO'],
            'HR': ['HR Coordinator', 'HR Manager', 'VP HR'],
            'Legal': ['Paralegal', 'Legal Counsel', 'General Counsel'],
            'IT': ['IT Support', 'Systems Admin', 'IT Manager', 'CIO'],
            'Business Development': ['BD Analyst', 'BD Manager', 'VP Business Development']
        },
        'avg_income_multiplier': 1.2,
        'travel_profile': {'Non-Travel': 0.3, 'Travel_Rarely': 0.4, 'Travel_Frequently': 0.3}
    },
    'hospitality': {
        'sector': 'Consumer Discretionary',
        'departments': ['Front Desk', 'Housekeeping', 'Food & Beverage', 'Events', 'Maintenance',
                       'Sales', 'Marketing', 'HR', 'Finance', 'Management'],
        'job_roles': {
            'Front Desk': ['Front Desk Agent', 'Night Auditor', 'Front Desk Supervisor', 'Front Office Manager'],
            'Housekeeping': ['Housekeeper', 'Housekeeping Supervisor', 'Executive Housekeeper'],
            'Food & Beverage': ['Server', 'Bartender', 'Line Cook', 'Executive Chef', 'F&B Director'],
            'Events': ['Event Coordinator', 'Event Manager', 'Director of Events'],
            'Maintenance': ['Maintenance Tech', 'Engineer', 'Chief Engineer'],
            'Sales': ['Sales Coordinator', 'Sales Manager', 'Director of Sales'],
            'Marketing': ['Marketing Coordinator', 'Marketing Manager', 'Director of Marketing'],
            'HR': ['HR Coordinator', 'HR Manager', 'VP HR'],
            'Finance': ['Accountant', 'Controller', 'CFO'],
            'Management': ['Department Head', 'Assistant GM', 'General Manager', 'Regional VP']
        },
        'avg_income_multiplier': 0.75,
        'travel_profile': {'Non-Travel': 0.8, 'Travel_Rarely': 0.15, 'Travel_Frequently': 0.05}
    },
    'construction': {
        'sector': 'Industrials',
        'departments': ['Field Operations', 'Project Management', 'Estimating', 'Safety', 'Equipment',
                       'Preconstruction', 'Finance', 'HR', 'Legal', 'Business Development'],
        'job_roles': {
            'Field Operations': ['Laborer', 'Skilled Tradesman', 'Foreman', 'Superintendent', 'VP Field Operations'],
            'Project Management': ['Project Coordinator', 'Assistant PM', 'Project Manager', 'Senior PM', 'VP Projects'],
            'Estimating': ['Junior Estimator', 'Estimator', 'Senior Estimator', 'Chief Estimator'],
            'Safety': ['Safety Coordinator', 'Safety Manager', 'Director of Safety'],
            'Equipment': ['Equipment Operator', 'Mechanic', 'Equipment Manager'],
            'Preconstruction': ['Preconstruction Coordinator', 'Preconstruction Manager', 'VP Preconstruction'],
            'Finance': ['Accountant', 'Project Accountant', 'Controller', 'CFO'],
            'HR': ['HR Coordinator', 'HR Manager', 'VP HR'],
            'Legal': ['Contract Administrator', 'Legal Counsel', 'General Counsel'],
            'Business Development': ['BD Coordinator', 'BD Manager', 'VP Business Development']
        },
        'avg_income_multiplier': 1.0,
        'travel_profile': {'Non-Travel': 0.2, 'Travel_Rarely': 0.5, 'Travel_Frequently': 0.3}
    }
}

# Company name components
NAME_PREFIXES = ['Global', 'American', 'Pacific', 'Atlantic', 'National', 'United', 'Premier',
                 'Elite', 'Summit', 'Apex', 'Pinnacle', 'Crown', 'Sterling', 'Golden', 'Diamond',
                 'Platinum', 'Silver', 'Iron', 'Titan', 'Vanguard', 'Pioneer', 'Frontier', 'Legacy',
                 'Heritage', 'Dynasty', 'Empire', 'Republic', 'Continental', 'Metropolitan', 'Coastal']

NAME_SUFFIXES = ['Industries', 'Corporation', 'Holdings', 'Group', 'Partners', 'Solutions',
                 'Enterprises', 'International', 'Services', 'Systems', 'Technologies', 'Associates',
                 'Ventures', 'Capital', 'Management', 'Resources', 'Dynamics', 'Networks', 'Alliance']

FIRST_NAMES = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph',
               'Thomas', 'Christopher', 'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth',
               'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen', 'Daniel', 'Matthew', 'Anthony',
               'Mark', 'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua', 'Kenneth', 'Nancy',
               'Betty', 'Margaret', 'Sandra', 'Ashley', 'Dorothy', 'Kimberly', 'Emily', 'Donna',
               'Michelle', 'Carol', 'Amanda', 'Melissa', 'Deborah', 'Stephanie', 'Rebecca', 'Laura',
               'Helen', 'Sharon', 'Cynthia', 'Angela', 'Katherine', 'Nicole', 'Samantha', 'Ruth']

LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
              'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
              'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
              'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
              'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
              'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter']


def generate_company_name(industry: str) -> str:
    """Generate a unique company name."""
    prefix = random.choice(NAME_PREFIXES)
    suffix = random.choice(NAME_SUFFIXES)
    return f"{prefix} {suffix}"


def generate_safe_company_financials(industry: str) -> dict:
    """Generate financial ratios for a SAFE (low risk) company."""
    return {
        'working_capital_to_total_assets': round(random.uniform(0.20, 0.45), 4),
        'retained_earnings_to_total_assets': round(random.uniform(0.25, 0.50), 4),
        'ebit_to_total_assets': round(random.uniform(0.08, 0.18), 4),
        'market_value_equity_to_total_liabilities': round(random.uniform(2.0, 5.0), 4),
        'sales_to_total_assets': round(random.uniform(1.0, 1.8), 4),
        'current_ratio': round(random.uniform(1.8, 3.5), 4),
        'quick_ratio': round(random.uniform(1.2, 2.5), 4),
        'debt_to_equity': round(random.uniform(0.3, 0.9), 4),
        'interest_coverage': round(random.uniform(6.0, 20.0), 4),
        'net_profit_margin': round(random.uniform(0.06, 0.18), 4),
        'return_on_assets': round(random.uniform(0.08, 0.18), 4),
        'return_on_equity': round(random.uniform(0.12, 0.28), 4)
    }


def generate_risky_company_financials(industry: str) -> dict:
    """Generate financial ratios for an AT-RISK (high insolvency risk) company."""
    return {
        'working_capital_to_total_assets': round(random.uniform(-0.15, 0.08), 4),
        'retained_earnings_to_total_assets': round(random.uniform(-0.25, 0.05), 4),
        'ebit_to_total_assets': round(random.uniform(-0.08, 0.03), 4),
        'market_value_equity_to_total_liabilities': round(random.uniform(0.2, 0.8), 4),
        'sales_to_total_assets': round(random.uniform(0.4, 0.8), 4),
        'current_ratio': round(random.uniform(0.5, 1.0), 4),
        'quick_ratio': round(random.uniform(0.2, 0.6), 4),
        'debt_to_equity': round(random.uniform(3.0, 8.0), 4),
        'interest_coverage': round(random.uniform(0.2, 1.2), 4),
        'net_profit_margin': round(random.uniform(-0.12, 0.01), 4),
        'return_on_assets': round(random.uniform(-0.10, 0.02), 4),
        'return_on_equity': round(random.uniform(-0.35, -0.05), 4)
    }


def generate_employee(
    employee_id: int,
    industry: str,
    company_health: str,  # 'safe' or 'risky'
    industry_data: dict
) -> dict:
    """Generate a single employee record consistent with company health."""

    # Select department weighted by industry
    departments = industry_data['departments']
    # Weight production/operations departments higher
    dept = random.choice(departments)

    # Select job role from department
    job_roles = industry_data['job_roles'].get(dept, ['Associate', 'Manager', 'Director'])
    job_role = random.choice(job_roles)

    # Determine job level from role (infer from position in list)
    role_index = job_roles.index(job_role) if job_role in job_roles else 0
    job_level = min(5, max(1, role_index + 1))

    # Base income by level (annual, will convert to monthly)
    base_incomes = {1: 35000, 2: 50000, 3: 75000, 4: 110000, 5: 160000}
    base_income = base_incomes[job_level]

    # Apply industry multiplier
    income_multiplier = industry_data['avg_income_multiplier']
    annual_income = base_income * income_multiplier * random.uniform(0.85, 1.15)
    monthly_income = int(annual_income / 12)

    # Age correlated with job level
    min_age = 22 + (job_level - 1) * 4
    max_age = 35 + (job_level - 1) * 8
    age = random.randint(min_age, min(65, max_age))

    # Years at company
    max_years = min(age - 22, 30)
    years_at_company = random.randint(0, max_years)
    years_in_current_role = random.randint(0, years_at_company)
    total_working_years = age - random.randint(18, 24)

    # Satisfaction scores influenced by company health
    if company_health == 'safe':
        # Higher satisfaction at healthy companies
        job_satisfaction = random.choices([1, 2, 3, 4], weights=[0.05, 0.15, 0.35, 0.45])[0]
        environment_satisfaction = random.choices([1, 2, 3, 4], weights=[0.05, 0.15, 0.35, 0.45])[0]
        job_involvement = random.choices([1, 2, 3, 4], weights=[0.05, 0.20, 0.35, 0.40])[0]
        performance_rating = random.choices([1, 2, 3, 4], weights=[0.02, 0.08, 0.45, 0.45])[0]
        percent_salary_hike = random.randint(12, 25)
        stock_option_level = random.choices([0, 1, 2, 3], weights=[0.2, 0.3, 0.3, 0.2])[0]
        over_time = random.choices(['Yes', 'No'], weights=[0.25, 0.75])[0]
    else:
        # Lower satisfaction at struggling companies
        job_satisfaction = random.choices([1, 2, 3, 4], weights=[0.25, 0.35, 0.25, 0.15])[0]
        environment_satisfaction = random.choices([1, 2, 3, 4], weights=[0.30, 0.35, 0.25, 0.10])[0]
        job_involvement = random.choices([1, 2, 3, 4], weights=[0.20, 0.35, 0.30, 0.15])[0]
        performance_rating = random.choices([1, 2, 3, 4], weights=[0.10, 0.25, 0.45, 0.20])[0]
        percent_salary_hike = random.randint(8, 14)
        stock_option_level = random.choices([0, 1, 2, 3], weights=[0.6, 0.25, 0.1, 0.05])[0]
        over_time = random.choices(['Yes', 'No'], weights=[0.45, 0.55])[0]

    # Travel profile from industry
    travel_profile = industry_data['travel_profile']
    business_travel = random.choices(
        list(travel_profile.keys()),
        weights=list(travel_profile.values())
    )[0]

    # Distance from home
    distance_from_home = random.randint(1, 35)

    # Gender
    gender = random.choice(['Male', 'Female'])

    # Name
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)

    return {
        'employee_id': f'EMP_{employee_id:05d}',
        'name': f'{first_name} {last_name}',
        'gender': gender,
        'department': dept,
        'job_role': job_role,
        'age': age,
        'job_level': job_level,
        'performance_rating': performance_rating,
        'job_satisfaction': job_satisfaction,
        'job_involvement': job_involvement,
        'environment_satisfaction': environment_satisfaction,
        'monthly_income': monthly_income,
        'percent_salary_hike': percent_salary_hike,
        'stock_option_level': stock_option_level,
        'years_at_company': years_at_company,
        'years_in_current_role': years_in_current_role,
        'total_working_years': total_working_years,
        'distance_from_home': distance_from_home,
        'business_travel': business_travel,
        'over_time': over_time
    }


def generate_company_test_data(
    company_id: int,
    industry: str,
    is_safe: bool,
    num_employees: int,
    output_dir: Path
):
    """Generate complete test data for a single company."""

    industry_data = INDUSTRIES[industry]
    company_health = 'safe' if is_safe else 'risky'
    risk_status = 'SAFE' if is_safe else 'AT_RISK'

    # Generate unique company name
    company_name = generate_company_name(industry)

    # Create folder name
    folder_name = f"{company_id:02d}_{company_name.replace(' ', '_')}_{risk_status}"
    company_dir = output_dir / folder_name
    company_dir.mkdir(parents=True, exist_ok=True)

    # Generate company financial data
    if is_safe:
        financials = generate_safe_company_financials(industry)
    else:
        financials = generate_risky_company_financials(industry)

    company_data = {
        'company_id': f'COMP_{company_id:03d}',
        'company_name': company_name,
        'industry': industry.title(),
        **financials
    }

    # Save company data
    company_df = pd.DataFrame([company_data])
    company_df.to_csv(company_dir / 'company_data.csv', index=False)

    # Generate employees
    employees = []
    for emp_id in range(1, num_employees + 1):
        emp = generate_employee(
            employee_id=emp_id,
            industry=industry,
            company_health=company_health,
            industry_data=industry_data
        )
        employees.append(emp)

    # Save employee data
    employee_df = pd.DataFrame(employees)
    employee_df.to_csv(company_dir / 'employee_data.csv', index=False)

    print(f"  Created: {folder_name}")
    print(f"    - Company: {company_name} ({industry.title()})")
    print(f"    - Risk Status: {risk_status}")
    print(f"    - Employees: {num_employees}")

    return folder_name


def main():
    """Generate all test company data."""
    print("=" * 70)
    print("SolvencyInsight - Test Data Generator")
    print("=" * 70)

    # Set output directory
    output_dir = Path(__file__).parent.parent / 'test_data' / 'companies'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clear existing test data
    import shutil
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    random.seed(42)  # For reproducibility
    np.random.seed(42)

    # Define 20 companies - 10 safe, 10 at-risk
    # Distribute across industries for variety
    industry_list = list(INDUSTRIES.keys())

    companies = []

    # 10 SAFE companies
    print("\n" + "-" * 70)
    print("Generating 10 SAFE (Low Risk) Companies")
    print("-" * 70)

    safe_companies = [
        (1, 'technology', True, 280),    # Tech company - larger
        (2, 'healthcare', True, 320),    # Healthcare - larger
        (3, 'financial', True, 250),     # Bank - medium
        (4, 'manufacturing', True, 350), # Manufacturing - larger
        (5, 'retail', True, 400),        # Retail - many employees
        (6, 'energy', True, 220),        # Energy - medium
        (7, 'construction', True, 280),  # Construction - medium-large
        (8, 'hospitality', True, 380),   # Hotel - many employees
        (9, 'technology', True, 200),    # Another tech - smaller
        (10, 'healthcare', True, 260),   # Another healthcare
    ]

    for company_id, industry, is_safe, num_employees in safe_companies:
        generate_company_test_data(company_id, industry, is_safe, num_employees, output_dir)

    # 10 AT-RISK companies
    print("\n" + "-" * 70)
    print("Generating 10 AT-RISK (High Insolvency Risk) Companies")
    print("-" * 70)

    risky_companies = [
        (11, 'retail', False, 350),        # Struggling retailer
        (12, 'hospitality', False, 290),   # Struggling hotel
        (13, 'manufacturing', False, 320), # Struggling manufacturer
        (14, 'energy', False, 240),        # Energy company in trouble
        (15, 'construction', False, 260),  # Construction company
        (16, 'technology', False, 200),    # Failed tech startup
        (17, 'financial', False, 220),     # Troubled bank
        (18, 'retail', False, 380),        # Another struggling retailer
        (19, 'healthcare', False, 300),    # Healthcare facility issues
        (20, 'manufacturing', False, 280), # Another manufacturer
    ]

    for company_id, industry, is_safe, num_employees in risky_companies:
        generate_company_test_data(company_id, industry, is_safe, num_employees, output_dir)

    print("\n" + "=" * 70)
    print("Test Data Generation Complete!")
    print("=" * 70)
    print(f"\nOutput directory: {output_dir}")
    print(f"Total companies: 20 (10 safe, 10 at-risk)")
    print(f"Total employees: ~5,800")

    # Create index file
    index_data = []
    for folder in sorted(output_dir.iterdir()):
        if folder.is_dir():
            company_df = pd.read_csv(folder / 'company_data.csv')
            employee_df = pd.read_csv(folder / 'employee_data.csv')

            index_data.append({
                'folder': folder.name,
                'company_id': company_df['company_id'].iloc[0],
                'company_name': company_df['company_name'].iloc[0],
                'industry': company_df['industry'].iloc[0],
                'risk_status': 'SAFE' if 'SAFE' in folder.name else 'AT_RISK',
                'num_employees': len(employee_df)
            })

    index_df = pd.DataFrame(index_data)
    index_df.to_csv(output_dir / '_index.csv', index=False)
    print(f"\nIndex file created: {output_dir / '_index.csv'}")


if __name__ == '__main__':
    main()
