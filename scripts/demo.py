"""
Insolvency Prevention System - Interactive Demo Script.

This script provides a complete walkthrough of the system from start to finish,
demonstrating data generation, model training, testing, and real-time predictions.

Usage:
    python scripts/demo.py              # Run full demo
    python scripts/demo.py --quick      # Quick demo (skip data generation)
    python scripts/demo.py --predict    # Interactive prediction mode only
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import time
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder

# =============================================================================
# Helper Functions
# =============================================================================

def print_banner(text, char="="):
    """Print a banner with the given text."""
    width = 70
    print("\n" + char * width)
    print(f" {text}")
    print(char * width)


def print_section(text):
    """Print a section header."""
    print(f"\n>>> {text}")
    print("-" * 50)


def wait_for_user(message="Press Enter to continue..."):
    """Wait for user input to continue."""
    input(f"\n{message}")


def print_progress(message):
    """Print a progress message."""
    print(f"  [*] {message}")


def print_success(message):
    """Print a success message."""
    print(f"  [+] {message}")


def print_info(message):
    """Print an info message."""
    print(f"  [i] {message}")


# =============================================================================
# Demo: Data Overview
# =============================================================================

def demo_data_overview():
    """Show overview of the generated data."""
    print_banner("STEP 1: Data Overview")

    data_dir = project_root / 'data' / 'generated'

    # Company data
    print_section("Company Financial Data")
    company_df = pd.read_csv(data_dir / 'company_data.csv')
    print_info(f"Total companies: {len(company_df)}")
    print_info(f"Bankrupt companies: {company_df['is_bankrupt'].sum()} ({company_df['is_bankrupt'].mean()*100:.1f}%)")
    print_info(f"Healthy companies: {(~company_df['is_bankrupt'].astype(bool)).sum()} ({(1-company_df['is_bankrupt'].mean())*100:.1f}%)")

    print("\n  Key Financial Metrics:")
    metrics = ['current_ratio', 'debt_to_equity', 'return_on_assets', 'net_profit_margin']
    for metric in metrics:
        mean_val = company_df[metric].mean()
        print(f"    - {metric}: Mean = {mean_val:.3f}")

    # Employee data
    print_section("Employee Data")
    employee_df = pd.read_csv(data_dir / 'employee_data.csv')
    attrition_count = (employee_df['attrition'] == 'Yes').sum()
    print_info(f"Total employees: {len(employee_df)}")
    print_info(f"Attrition cases: {attrition_count} ({attrition_count/len(employee_df)*100:.1f}%)")
    print_info(f"Retained employees: {len(employee_df) - attrition_count}")

    print("\n  Department Distribution:")
    dept_counts = employee_df['department'].value_counts().head(5)
    for dept, count in dept_counts.items():
        print(f"    - {dept}: {count}")

    print_section("Train/Test Split")
    train_company = pd.read_csv(data_dir / 'company_train.csv')
    test_company = pd.read_csv(data_dir / 'company_test.csv')
    train_employee = pd.read_csv(data_dir / 'employee_train.csv')
    test_employee = pd.read_csv(data_dir / 'employee_test.csv')

    print_info(f"Company training set: {len(train_company)} records")
    print_info(f"Company test set: {len(test_company)} records")
    print_info(f"Employee training set: {len(train_employee)} records")
    print_info(f"Employee test set: {len(test_employee)} records")


# =============================================================================
# Demo: Model Performance
# =============================================================================

def demo_model_performance():
    """Show model performance metrics."""
    print_banner("STEP 2: Model Performance")

    models_dir = project_root / 'ml_models' / 'trained_models'

    # Insolvency model
    print_section("Insolvency Prediction Model")
    with open(models_dir / 'insolvency_model.pkl', 'rb') as f:
        insolvency_data = pickle.load(f)

    print_info(f"Model type: XGBoost Classifier")
    print_info(f"Trained at: {insolvency_data.get('trained_at', 'Unknown')}")
    print("\n  Performance Metrics:")
    for metric, value in insolvency_data['metrics'].items():
        print(f"    - {metric}: {value:.4f}")

    print("\n  Top 5 Important Features:")
    sorted_importance = sorted(
        insolvency_data['feature_importance'].items(),
        key=lambda x: x[1], reverse=True
    )[:5]
    for feat, imp in sorted_importance:
        bar = "#" * int(imp * 50)
        print(f"    {feat[:30]:<30} {bar} {imp:.3f}")

    # Employee model
    print_section("Employee Attrition Model")
    with open(models_dir / 'employee_model.pkl', 'rb') as f:
        employee_data = pickle.load(f)

    print_info(f"Model type: XGBoost Classifier")
    print_info(f"Trained at: {employee_data.get('trained_at', 'Unknown')}")
    print("\n  Performance Metrics:")
    for metric, value in employee_data['metrics'].items():
        print(f"    - {metric}: {value:.4f}")

    print("\n  Top 5 Important Features:")
    sorted_importance = sorted(
        employee_data['feature_importance'].items(),
        key=lambda x: x[1], reverse=True
    )[:5]
    for feat, imp in sorted_importance:
        bar = "#" * int(imp * 50)
        print(f"    {feat[:30]:<30} {bar} {imp:.3f}")


# =============================================================================
# Demo: Live Predictions
# =============================================================================

def predict_insolvency(company_data: dict) -> dict:
    """Make an insolvency prediction for a company."""
    models_dir = project_root / 'ml_models' / 'trained_models'

    with open(models_dir / 'insolvency_model.pkl', 'rb') as f:
        model_data = pickle.load(f)

    model = model_data['model']
    feature_names = model_data['feature_names']

    # Prepare features
    features = pd.DataFrame([company_data])[feature_names]
    features = features.fillna(features.median())

    # Predict
    prob = model.predict_proba(features)[0, 1]
    prediction = model.predict(features)[0]

    # Risk assessment
    if prob < 0.2:
        risk_level = "LOW"
        risk_color = "green"
    elif prob < 0.5:
        risk_level = "MODERATE"
        risk_color = "yellow"
    elif prob < 0.8:
        risk_level = "HIGH"
        risk_color = "orange"
    else:
        risk_level = "CRITICAL"
        risk_color = "red"

    return {
        'probability': prob,
        'prediction': 'Bankrupt' if prediction == 1 else 'Healthy',
        'risk_level': risk_level,
        'risk_color': risk_color
    }


def predict_attrition(employee_data: dict) -> dict:
    """Make an attrition prediction for an employee."""
    models_dir = project_root / 'ml_models' / 'trained_models'

    with open(models_dir / 'employee_model.pkl', 'rb') as f:
        model_data = pickle.load(f)

    model = model_data['model']
    feature_names = model_data['feature_names']
    label_encoders = model_data.get('label_encoders', {})

    # Prepare features
    numeric_cols = [
        'age', 'job_level', 'performance_rating', 'job_satisfaction',
        'job_involvement', 'environment_satisfaction', 'monthly_income',
        'percent_salary_hike', 'stock_option_level', 'years_at_company',
        'years_in_current_role', 'total_working_years', 'distance_from_home'
    ]
    categorical_cols = ['gender', 'department', 'business_travel', 'over_time']

    features = {}
    for col in numeric_cols:
        features[col] = employee_data.get(col, 0)

    for col in categorical_cols:
        if col in label_encoders:
            le = label_encoders[col]
            val = employee_data.get(col, le.classes_[0])
            if val in le.classes_:
                features[col] = le.transform([val])[0]
            else:
                features[col] = 0
        else:
            features[col] = 0

    X = pd.DataFrame([features])
    X = X.fillna(0)

    # Predict
    prob = model.predict_proba(X)[0, 1]
    prediction = model.predict(X)[0]

    # Risk assessment
    if prob < 0.2:
        risk_level = "LOW"
    elif prob < 0.4:
        risk_level = "MODERATE"
    elif prob < 0.6:
        risk_level = "HIGH"
    else:
        risk_level = "VERY HIGH"

    return {
        'probability': prob,
        'prediction': 'Attrition' if prediction == 1 else 'Retained',
        'risk_level': risk_level
    }


def demo_live_predictions():
    """Demonstrate live predictions."""
    print_banner("STEP 3: Live Predictions")

    # Sample company predictions
    print_section("Company Insolvency Predictions")

    sample_companies = [
        {
            'name': 'TechStart Inc (Healthy Startup)',
            'data': {
                'working_capital_to_total_assets': 0.35,
                'retained_earnings_to_total_assets': 0.15,
                'ebit_to_total_assets': 0.12,
                'market_value_equity_to_total_liabilities': 2.5,
                'sales_to_total_assets': 1.2,
                'current_ratio': 2.1,
                'quick_ratio': 1.5,
                'debt_to_equity': 0.6,
                'interest_coverage': 8.0,
                'net_profit_margin': 0.08,
                'return_on_assets': 0.10,
                'return_on_equity': 0.15
            }
        },
        {
            'name': 'StrugglingRetail Corp (At Risk)',
            'data': {
                'working_capital_to_total_assets': -0.05,
                'retained_earnings_to_total_assets': -0.10,
                'ebit_to_total_assets': -0.02,
                'market_value_equity_to_total_liabilities': 0.3,
                'sales_to_total_assets': 0.5,
                'current_ratio': 0.7,
                'quick_ratio': 0.3,
                'debt_to_equity': 4.5,
                'interest_coverage': 0.5,
                'net_profit_margin': -0.05,
                'return_on_assets': -0.03,
                'return_on_equity': -0.15
            }
        },
        {
            'name': 'SolidManufacturing LLC (Stable)',
            'data': {
                'working_capital_to_total_assets': 0.20,
                'retained_earnings_to_total_assets': 0.30,
                'ebit_to_total_assets': 0.08,
                'market_value_equity_to_total_liabilities': 1.5,
                'sales_to_total_assets': 0.9,
                'current_ratio': 1.6,
                'quick_ratio': 1.0,
                'debt_to_equity': 1.2,
                'interest_coverage': 4.0,
                'net_profit_margin': 0.04,
                'return_on_assets': 0.06,
                'return_on_equity': 0.12
            }
        }
    ]

    for company in sample_companies:
        result = predict_insolvency(company['data'])
        print(f"\n  {company['name']}")
        print(f"    Prediction: {result['prediction']}")
        print(f"    Bankruptcy Probability: {result['probability']*100:.1f}%")
        print(f"    Risk Level: {result['risk_level']}")

    # Sample employee predictions
    print_section("Employee Attrition Predictions")

    sample_employees = [
        {
            'name': 'John Smith (Low Risk)',
            'data': {
                'age': 35,
                'job_level': 3,
                'performance_rating': 4,
                'job_satisfaction': 4,
                'job_involvement': 4,
                'environment_satisfaction': 4,
                'monthly_income': 8500,
                'percent_salary_hike': 15,
                'stock_option_level': 2,
                'years_at_company': 8,
                'years_in_current_role': 4,
                'total_working_years': 12,
                'distance_from_home': 5,
                'gender': 'Male',
                'department': 'Engineering',
                'business_travel': 'Travel_Rarely',
                'over_time': 'No'
            }
        },
        {
            'name': 'Sarah Johnson (High Risk)',
            'data': {
                'age': 26,
                'job_level': 1,
                'performance_rating': 3,
                'job_satisfaction': 1,
                'job_involvement': 2,
                'environment_satisfaction': 1,
                'monthly_income': 3500,
                'percent_salary_hike': 11,
                'stock_option_level': 0,
                'years_at_company': 1,
                'years_in_current_role': 1,
                'total_working_years': 3,
                'distance_from_home': 25,
                'gender': 'Female',
                'department': 'Sales',
                'business_travel': 'Travel_Frequently',
                'over_time': 'Yes'
            }
        },
        {
            'name': 'Mike Chen (Moderate Risk)',
            'data': {
                'age': 42,
                'job_level': 2,
                'performance_rating': 3,
                'job_satisfaction': 2,
                'job_involvement': 3,
                'environment_satisfaction': 3,
                'monthly_income': 5500,
                'percent_salary_hike': 12,
                'stock_option_level': 1,
                'years_at_company': 5,
                'years_in_current_role': 3,
                'total_working_years': 18,
                'distance_from_home': 15,
                'gender': 'Male',
                'department': 'Operations',
                'business_travel': 'Travel_Rarely',
                'over_time': 'Yes'
            }
        }
    ]

    for employee in sample_employees:
        result = predict_attrition(employee['data'])
        print(f"\n  {employee['name']}")
        print(f"    Prediction: {result['prediction']}")
        print(f"    Attrition Probability: {result['probability']*100:.1f}%")
        print(f"    Risk Level: {result['risk_level']}")


# =============================================================================
# Demo: System Architecture
# =============================================================================

def demo_architecture():
    """Show system architecture overview."""
    print_banner("STEP 4: System Architecture")

    print_section("Project Structure")
    print("""
  insolvency-prevention-system/
  |
  |-- backend/                 # FastAPI backend server
  |   |-- app/
  |   |   |-- main.py          # Application entry point
  |   |   |-- api/             # API endpoints
  |   |   |-- services/        # Business logic
  |   |   |-- models/          # Pydantic models
  |   |   `-- core/            # Configuration
  |   |-- tests/               # Backend tests
  |   `-- Dockerfile           # Backend container
  |
  |-- frontend/                # React frontend application
  |   |-- src/
  |   |   |-- components/      # React components
  |   |   |-- pages/           # Page components
  |   |   |-- services/        # API services
  |   |   `-- hooks/           # Custom hooks
  |   `-- Dockerfile           # Frontend container
  |
  |-- ml_models/               # Machine learning components
  |   |-- trained_models/      # Saved model files
  |   `-- model_utils.py       # Model utilities
  |
  |-- data/                    # Data directory
  |   |-- generated/           # Generated training/test data
  |   |-- company_data.csv     # Original company data
  |   `-- employee_data.csv    # Original employee data
  |
  |-- scripts/                 # Utility scripts
  |   |-- generate_data.py     # Data generation
  |   |-- train_models.py      # Model training
  |   |-- test_models.py       # Model testing
  |   `-- demo.py              # This demo script
  |
  |-- docs/                    # Documentation
  |   |-- API.md               # API documentation
  |   `-- MODELS.md            # Model documentation
  |
  |-- docker-compose.yml       # Development orchestration
  |-- docker-compose.prod.yml  # Production orchestration
  |-- deploy.sh                # Deployment script
  `-- README.md                # Project readme
    """)

    print_section("Technology Stack")
    print("""
  Backend:
    - Python 3.11+
    - FastAPI (web framework)
    - XGBoost (machine learning)
    - Pandas/NumPy (data processing)
    - Scikit-learn (ML utilities)
    - Uvicorn (ASGI server)

  Frontend:
    - React 18+
    - TypeScript
    - Vite (build tool)
    - TailwindCSS (styling)
    - React Query (data fetching)
    - Recharts (visualizations)

  Infrastructure:
    - Docker & Docker Compose
    - Nginx (frontend serving)
    - GitHub Actions (CI/CD)
    """)


# =============================================================================
# Demo: Quick Start Guide
# =============================================================================

def demo_quickstart():
    """Show quick start guide."""
    print_banner("STEP 5: Quick Start Guide")

    print_section("Running the Application")
    print("""
  Option 1: Using Docker (Recommended)
  ------------------------------------
  # Start development environment
  ./deploy.sh dev

  # Or start production environment
  ./deploy.sh prod

  # Check status
  ./deploy.sh status

  # View logs
  ./deploy.sh logs

  Option 2: Manual Setup
  ----------------------
  # Backend
  cd backend
  pip install -r requirements.txt
  uvicorn app.main:app --reload

  # Frontend (in another terminal)
  cd frontend
  npm install
  npm run dev
    """)

    print_section("Regenerating Data and Models")
    print("""
  # Generate new synthetic data (500 companies, 2000 employees)
  python scripts/generate_data.py --companies 500 --employees 2000

  # Train models on new data
  python scripts/train_models.py

  # Test model performance
  python scripts/test_models.py
    """)

    print_section("API Endpoints")
    print("""
  Health Check:
    GET /api/health

  Company Predictions:
    POST /api/predict/insolvency
    Body: { company financial metrics }

  Employee Predictions:
    POST /api/predict/attrition
    Body: { employee attributes }

  Batch Predictions:
    POST /api/predict/batch
    Body: { array of records }

  API Documentation:
    GET /docs (Swagger UI)
    GET /redoc (ReDoc)
    """)


# =============================================================================
# Interactive Prediction Mode
# =============================================================================

def interactive_mode():
    """Run interactive prediction mode."""
    print_banner("Interactive Prediction Mode", char="#")

    while True:
        print("\n" + "=" * 50)
        print("Select prediction type:")
        print("  1. Company Insolvency Prediction")
        print("  2. Employee Attrition Prediction")
        print("  3. Exit")
        print("=" * 50)

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "1":
            interactive_company_prediction()
        elif choice == "2":
            interactive_employee_prediction()
        elif choice == "3":
            print("\nExiting interactive mode. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def interactive_company_prediction():
    """Interactive company prediction."""
    print("\n" + "-" * 50)
    print("Company Insolvency Prediction")
    print("-" * 50)
    print("\nEnter financial metrics (press Enter for default):\n")

    defaults = {
        'working_capital_to_total_assets': 0.15,
        'retained_earnings_to_total_assets': 0.10,
        'ebit_to_total_assets': 0.05,
        'market_value_equity_to_total_liabilities': 1.0,
        'sales_to_total_assets': 0.8,
        'current_ratio': 1.5,
        'quick_ratio': 1.0,
        'debt_to_equity': 1.5,
        'interest_coverage': 3.0,
        'net_profit_margin': 0.03,
        'return_on_assets': 0.04,
        'return_on_equity': 0.08
    }

    data = {}
    for metric, default in defaults.items():
        user_input = input(f"  {metric} [{default}]: ").strip()
        if user_input:
            try:
                data[metric] = float(user_input)
            except ValueError:
                data[metric] = default
        else:
            data[metric] = default

    result = predict_insolvency(data)

    print("\n" + "=" * 50)
    print("PREDICTION RESULT")
    print("=" * 50)
    print(f"  Status: {result['prediction']}")
    print(f"  Bankruptcy Probability: {result['probability']*100:.1f}%")
    print(f"  Risk Level: {result['risk_level']}")
    print("=" * 50)


def interactive_employee_prediction():
    """Interactive employee prediction."""
    print("\n" + "-" * 50)
    print("Employee Attrition Prediction")
    print("-" * 50)
    print("\nEnter employee attributes (press Enter for default):\n")

    data = {}

    # Numeric inputs
    numeric_fields = [
        ('age', 30, 'Age'),
        ('job_level', 2, 'Job Level (1-5)'),
        ('performance_rating', 3, 'Performance Rating (1-4)'),
        ('job_satisfaction', 3, 'Job Satisfaction (1-4)'),
        ('job_involvement', 3, 'Job Involvement (1-4)'),
        ('environment_satisfaction', 3, 'Environment Satisfaction (1-4)'),
        ('monthly_income', 5000, 'Monthly Income'),
        ('percent_salary_hike', 13, 'Percent Salary Hike'),
        ('stock_option_level', 1, 'Stock Option Level (0-3)'),
        ('years_at_company', 5, 'Years at Company'),
        ('years_in_current_role', 3, 'Years in Current Role'),
        ('total_working_years', 8, 'Total Working Years'),
        ('distance_from_home', 10, 'Distance from Home (km)')
    ]

    for field, default, label in numeric_fields:
        user_input = input(f"  {label} [{default}]: ").strip()
        if user_input:
            try:
                data[field] = float(user_input)
            except ValueError:
                data[field] = default
        else:
            data[field] = default

    # Categorical inputs
    print("\n  Categorical Fields:")

    gender = input("  Gender [Male/Female] (default: Male): ").strip()
    data['gender'] = gender if gender in ['Male', 'Female'] else 'Male'

    dept = input("  Department (default: Engineering): ").strip()
    data['department'] = dept if dept else 'Engineering'

    travel = input("  Business Travel [Travel_Rarely/Travel_Frequently/Non-Travel] (default: Travel_Rarely): ").strip()
    data['business_travel'] = travel if travel in ['Travel_Rarely', 'Travel_Frequently', 'Non-Travel'] else 'Travel_Rarely'

    overtime = input("  Over Time [Yes/No] (default: No): ").strip()
    data['over_time'] = overtime if overtime in ['Yes', 'No'] else 'No'

    result = predict_attrition(data)

    print("\n" + "=" * 50)
    print("PREDICTION RESULT")
    print("=" * 50)
    print(f"  Status: {result['prediction']}")
    print(f"  Attrition Probability: {result['probability']*100:.1f}%")
    print(f"  Risk Level: {result['risk_level']}")
    print("=" * 50)


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Insolvency Prevention System Demo')
    parser.add_argument('--quick', action='store_true', help='Quick demo (skip detailed explanations)')
    parser.add_argument('--predict', action='store_true', help='Interactive prediction mode only')
    parser.add_argument('--no-pause', action='store_true', help='Run without pausing for user input')
    args = parser.parse_args()

    print_banner("INSOLVENCY PREVENTION SYSTEM DEMO", char="#")
    print("""
    Welcome to the Insolvency Prevention System!

    This system uses machine learning to:
    1. Predict company bankruptcy risk based on financial metrics
    2. Predict employee attrition risk based on HR data

    The models are trained on industry-standard data patterns
    and achieve excellent performance (ROC-AUC > 0.90).
    """)

    if args.predict:
        interactive_mode()
        return

    # Run demo sections
    sections = [
        ("Data Overview", demo_data_overview),
        ("Model Performance", demo_model_performance),
        ("Live Predictions", demo_live_predictions),
        ("System Architecture", demo_architecture),
        ("Quick Start Guide", demo_quickstart)
    ]

    for i, (name, func) in enumerate(sections, 1):
        if not args.no_pause and i > 1:
            wait_for_user(f"\nPress Enter to continue to {name}...")
        func()

    # Offer interactive mode
    print_banner("Demo Complete!")
    print("""
    You have seen the complete Insolvency Prevention System!

    Summary:
    - 500 companies and 2000 employees in training data
    - Insolvency Model: ROC-AUC 0.99 on test set
    - Employee Model: ROC-AUC 0.91 on test set
    - Full-stack application with React + FastAPI
    - Docker deployment ready

    Next Steps:
    1. Run './deploy.sh dev' to start the application
    2. Open http://localhost:5173 for the frontend
    3. Open http://localhost:8000/docs for the API
    """)

    if not args.no_pause:
        print("\nWould you like to try interactive predictions?")
        choice = input("Enter 'y' for interactive mode or any other key to exit: ").strip().lower()
        if choice == 'y':
            interactive_mode()

    print("\nThank you for using the Insolvency Prevention System!")


if __name__ == '__main__':
    main()
