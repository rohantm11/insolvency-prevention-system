"""
Generate 400-700 employee records per company (random count per company).
Reads company CSVs from data/good/ and data/bad/, writes one employee CSV per company
into data/employees/ with columns matching the backend employee template.

Usage (from project root):
    python scripts/generate_employees.py --data-dir data
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import argparse
import random
import csv

# Employee CSV columns (must match backend EMPLOYEE_CSV_HEADER)
EMPLOYEE_HEADER = [
    "employee_id",
    "name",
    "gender",
    "age",
    "department",
    "job_role",
    "job_level",
    "performance_rating",
    "job_satisfaction",
    "job_involvement",
    "environment_satisfaction",
    "monthly_income",
    "percent_salary_hike",
    "stock_option_level",
    "years_at_company",
    "years_in_current_role",
    "total_working_years",
    "distance_from_home",
    "business_travel",
    "over_time",
]

DEPARTMENTS = [
    "Engineering",
    "Research and Development",
    "Sales",
    "Human Resources",
    "Finance",
    "Marketing",
    "Operations",
    "Legal",
    "Support",
    "IT",
]

JOB_ROLES = [
    "Software Engineer",
    "Research Scientist",
    "Sales Representative",
    "HR Manager",
    "Financial Analyst",
    "Marketing Manager",
    "Operations Manager",
    "Legal Counsel",
    "Support Specialist",
    "IT Administrator",
    "Data Scientist",
    "Product Manager",
    "Accountant",
    "Business Analyst",
]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
]

GENDERS = ["Male", "Female"]
BUSINESS_TRAVEL = ["Non-Travel", "Travel_Rarely", "Travel_Frequently"]
OVER_TIME = ["Yes", "No"]

RANDOM_SEED = 123
random.seed(RANDOM_SEED)


def random_name(company_id: str, emp_index: int) -> str:
    """Return a unique name for the employee."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"


def generate_employee_row(company_id: str, emp_index: int, global_index: int) -> list:
    """Generate one employee record as a list of values in EMPLOYEE_HEADER order."""
    emp_id = f"EMP_{company_id}_{emp_index:05d}"
    name = random_name(company_id, emp_index)
    gender = random.choice(GENDERS)
    age = random.randint(22, 58)
    department = random.choice(DEPARTMENTS)
    job_role = random.choice(JOB_ROLES)
    job_level = random.randint(1, 5)
    performance_rating = random.randint(1, 4)
    job_satisfaction = random.randint(1, 4)
    job_involvement = random.randint(1, 4)
    environment_satisfaction = random.randint(1, 4)
    # monthly_income: 3000-18000 with some spread
    base = random.choice([4000, 5000, 6000, 7000, 8000, 9000, 10000, 12000, 15000])
    monthly_income = base + random.randint(-500, 1500)
    monthly_income = max(2500, min(20000, monthly_income))
    percent_salary_hike = random.randint(11, 25)
    stock_option_level = random.randint(0, 3)
    years_at_company = random.randint(0, 15)
    years_in_current_role = min(random.randint(0, 10), years_at_company)
    total_working_years = years_at_company + random.randint(0, 10)
    distance_from_home = random.randint(1, 29)
    business_travel = random.choice(BUSINESS_TRAVEL)
    over_time = random.choice(OVER_TIME)

    return [
        emp_id,
        name,
        gender,
        age,
        department,
        job_role,
        job_level,
        performance_rating,
        job_satisfaction,
        job_involvement,
        environment_satisfaction,
        monthly_income,
        percent_salary_hike,
        stock_option_level,
        years_at_company,
        years_in_current_role,
        total_working_years,
        distance_from_home,
        business_travel,
        over_time,
    ]


def get_company_id_from_csv(csv_path: Path) -> str | None:
    """Read first data row and return company_id. Return None if missing or invalid."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row = next(reader, None)
        if not row:
            return None
        return (row.get("company_id") or "").strip() or None


def main():
    parser = argparse.ArgumentParser(
        description="Generate 400-700 employee records per company; store in data/employees/"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Base data directory containing good/ and bad/ company CSVs",
    )
    parser.add_argument(
        "--min-employees",
        type=int,
        default=400,
        help="Minimum employees per company",
    )
    parser.add_argument(
        "--max-employees",
        type=int,
        default=700,
        help="Maximum employees per company",
    )
    args = parser.parse_args()

    base = Path(args.data_dir)
    good_dir = base / "good"
    bad_dir = base / "bad"
    employees_dir = base / "employees"
    employees_dir.mkdir(parents=True, exist_ok=True)

    company_files = []
    if good_dir.is_dir():
        company_files.extend(sorted(good_dir.glob("*.csv")))
    if bad_dir.is_dir():
        company_files.extend(sorted(bad_dir.glob("*.csv")))

    if not company_files:
        print("No company CSV files found in data/good/ or data/bad/. Run generate_single_company_files.py first.")
        sys.exit(1)

    print("=" * 60)
    print("Generating employee records per company")
    print("=" * 60)
    print(f"  Companies: {len(company_files)}")
    print(f"  Employees per company: {args.min_employees}-{args.max_employees} (random)")
    print(f"  Output: {employees_dir}")
    print()

    total_employees = 0
    for i, csv_path in enumerate(company_files):
        company_id = get_company_id_from_csv(csv_path)
        if not company_id:
            print(f"  Skip (no company_id): {csv_path.name}")
            continue

        n = random.randint(args.min_employees, args.max_employees)
        out_path = employees_dir / f"{company_id}.csv"

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(EMPLOYEE_HEADER)
            for j in range(1, n + 1):
                row = generate_employee_row(company_id, j, total_employees + j)
                writer.writerow(row)

        total_employees += n
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{len(company_files)} companies, ~{total_employees} employees so far...")

    print()
    print("=" * 60)
    print("Done.")
    print(f"  Employee files: {len(company_files)} in {employees_dir}")
    print(f"  Total employee records: {total_employees}")
    print("=" * 60)


if __name__ == "__main__":
    main()
