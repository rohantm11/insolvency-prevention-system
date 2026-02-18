"""
API endpoint tests for the Insolvency Prevention System.

Run with: pytest tests/test_api.py -v
Or run directly: python tests/test_api.py
"""

import io
import json
import sys
from pathlib import Path

import requests

# Configuration
BASE_URL = "http://localhost:8004"
DATA_DIR = Path(__file__).parent.parent / "data"


def test_health_endpoint():
    """Test the health check endpoint."""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/health")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert data["status"] == "healthy"
    assert data["models_loaded"] is True
    assert "insolvency_model_metrics" in data
    assert "employee_model_metrics" in data

    print(f"Status: {data['status']}")
    print(f"Models loaded: {data['models_loaded']}")
    print("PASSED")
    return True


def test_financial_analyze_endpoint():
    """Test single company financial analysis."""
    print("\n=== Testing Financial Analyze Endpoint ===")

    # Test data for a high-risk company
    company_data = {
        "company_id": "TEST_001",
        "company_name": "Test Company",
        "working_capital_to_total_assets": 0.05,
        "retained_earnings_to_total_assets": -0.1,
        "ebit_to_total_assets": 0.02,
        "market_value_equity_to_total_liabilities": 0.5,
        "sales_to_total_assets": 0.8,
        "current_ratio": 0.9,
        "quick_ratio": 0.5,
        "debt_to_equity": 2.5,
        "interest_coverage": 1.2,
        "net_profit_margin": -0.05,
        "return_on_assets": -0.03,
        "return_on_equity": -0.1
    }

    response = requests.post(
        f"{BASE_URL}/api/financial/analyze",
        json=company_data
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "prediction" in data
    assert "explanation" in data

    pred = data["prediction"]
    assert pred["company_id"] == "TEST_001"
    assert 0 <= pred["probability_of_distress"] <= 1
    assert pred["risk_category"] in ["Low", "Medium", "High"]
    assert pred["z_score_zone"] in ["Safe", "Grey", "Distress"]

    expl = data["explanation"]
    assert "shap_values" in expl
    assert "top_risk_drivers" in expl

    print(f"Probability of distress: {pred['probability_of_distress']:.2%}")
    print(f"Risk category: {pred['risk_category']}")
    print(f"Z-Score: {pred['z_score']:.3f} ({pred['z_score_zone']})")
    print(f"Top risk driver: {expl['top_risk_drivers'][0]['feature']}")
    print("PASSED")
    return True


def test_employee_analyze_endpoint():
    """Test single employee analysis."""
    print("\n=== Testing Employee Analyze Endpoint ===")

    # Test data for a high attrition risk employee
    employee_data = {
        "employee_id": "EMP_TEST",
        "name": "John Doe",
        "age": 28,
        "gender": "Male",
        "department": "Sales",
        "job_role": "Sales Representative",
        "job_level": 1,
        "performance_rating": 2,
        "job_satisfaction": 1,
        "job_involvement": 1,
        "environment_satisfaction": 1,
        "monthly_income": 3000,
        "percent_salary_hike": 11,
        "stock_option_level": 0,
        "years_at_company": 1,
        "years_in_current_role": 1,
        "total_working_years": 2,
        "distance_from_home": 30,
        "business_travel": "Travel_Frequently",
        "over_time": "Yes"
    }

    response = requests.post(
        f"{BASE_URL}/api/employee/analyze",
        json=employee_data
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "prediction" in data
    assert "explanation" in data

    pred = data["prediction"]
    assert pred["employee_id"] == "EMP_TEST"
    assert 0 <= pred["retention_score"] <= 100
    assert 0 <= pred["attrition_probability"] <= 1
    assert pred["attrition_risk"] in ["Low", "Medium", "High"]
    assert pred["layoff_priority"] in ["Low", "Medium", "High"]

    expl = data["explanation"]
    assert "shap_values" in expl
    assert "top_factors" in expl

    print(f"Retention score: {pred['retention_score']:.1f}")
    print(f"Attrition probability: {pred['attrition_probability']:.2%}")
    print(f"Attrition risk: {pred['attrition_risk']}")
    print(f"Layoff priority: {pred['layoff_priority']}")
    print(f"Top factor: {expl['top_factors'][0]['feature']}")
    print("PASSED")
    return True


def test_layoff_simulation_endpoint():
    """Test layoff simulation with CSV upload."""
    print("\n=== Testing Layoff Simulation Endpoint ===")

    csv_path = DATA_DIR / "employee_data.csv"
    assert csv_path.exists(), f"Test data not found: {csv_path}"

    with open(csv_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/api/employee/simulate-layoff",
            params={"budget_cut_percent": 15, "min_per_dept": 2},
            files={"file": ("employee_data.csv", f, "text/csv")}
        )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert data["target_budget_cut"] == 15.0
    assert data["target_monthly_savings"] > 0
    assert data["actual_monthly_savings"] > 0
    assert data["employees_affected"] > 0
    assert "recommendations" in data
    assert "department_breakdown" in data

    print(f"Target budget cut: {data['target_budget_cut']}%")
    print(f"Target monthly savings: ${data['target_monthly_savings']:,.2f}")
    print(f"Actual monthly savings: ${data['actual_monthly_savings']:,.2f}")
    print(f"Employees affected: {data['employees_affected']}")
    print(f"Savings achieved: {data['savings_achieved_percent']:.1f}%")
    print(f"Departments affected: {list(data['department_breakdown'].keys())}")
    print("PASSED")
    return True


def test_insolvency_report_generation():
    """Test PDF report generation for insolvency analysis."""
    print("\n=== Testing Insolvency Report Generation ===")

    request_data = {
        "company_id": "COMP_PDF_TEST",
        "company_name": "PDF Test Corp",
        "company_data": {
            "working_capital_to_total_assets": 0.15,
            "retained_earnings_to_total_assets": 0.20,
            "ebit_to_total_assets": 0.08,
            "market_value_equity_to_total_liabilities": 1.5,
            "sales_to_total_assets": 1.0,
            "current_ratio": 1.5,
            "quick_ratio": 1.0,
            "debt_to_equity": 1.2,
            "interest_coverage": 3.0,
            "net_profit_margin": 0.05,
            "return_on_assets": 0.04,
            "return_on_equity": 0.08
        }
    }

    response = requests.post(
        f"{BASE_URL}/api/reports/insolvency",
        json=request_data
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.headers.get("content-type") == "application/pdf"
    assert len(response.content) > 1000, "PDF seems too small"

    # Verify PDF header
    assert response.content[:4] == b"%PDF", "Response is not a valid PDF"

    print(f"PDF size: {len(response.content):,} bytes")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print("PASSED")
    return True


def test_layoff_report_generation():
    """Test PDF report generation for layoff simulation."""
    print("\n=== Testing Layoff Report Generation ===")

    csv_path = DATA_DIR / "employee_data.csv"
    assert csv_path.exists(), f"Test data not found: {csv_path}"

    with open(csv_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/api/reports/layoff",
            params={"budget_cut_percent": 10, "min_per_dept": 3},
            files={"file": ("employee_data.csv", f, "text/csv")}
        )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.headers.get("content-type") == "application/pdf"
    assert len(response.content) > 1000, "PDF seems too small"

    # Verify PDF header
    assert response.content[:4] == b"%PDF", "Response is not a valid PDF"

    print(f"PDF size: {len(response.content):,} bytes")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print("PASSED")
    return True


def test_feature_importance_endpoints():
    """Test feature importance endpoints."""
    print("\n=== Testing Feature Importance Endpoints ===")

    # Financial feature importance
    response = requests.get(f"{BASE_URL}/api/financial/feature-importance")
    assert response.status_code == 200
    data = response.json()
    assert "feature_importance" in data
    assert "model_metrics" in data
    print(f"Financial features: {len(data['feature_importance'])}")

    # Employee feature importance
    response = requests.get(f"{BASE_URL}/api/employee/feature-importance")
    assert response.status_code == 200
    data = response.json()
    assert "feature_importance" in data
    assert "model_metrics" in data
    print(f"Employee features: {len(data['feature_importance'])}")

    print("PASSED")
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("INSOLVENCY PREVENTION SYSTEM - API TESTS")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")

    tests = [
        ("Health Check", test_health_endpoint),
        ("Financial Analysis", test_financial_analyze_endpoint),
        ("Employee Analysis", test_employee_analyze_endpoint),
        ("Layoff Simulation", test_layoff_simulation_endpoint),
        ("Insolvency Report", test_insolvency_report_generation),
        ("Layoff Report", test_layoff_report_generation),
        ("Feature Importance", test_feature_importance_endpoints),
    ]

    results = []

    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except AssertionError as e:
            print(f"FAILED: {e}")
            results.append((name, False, str(e)))
        except requests.exceptions.ConnectionError:
            print(f"FAILED: Cannot connect to server at {BASE_URL}")
            results.append((name, False, "Connection failed"))
        except Exception as e:
            print(f"ERROR: {e}")
            results.append((name, False, str(e)))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed

    for name, success, error in results:
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {name}")
        if error:
            print(f"         Error: {error}")

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    if failed > 0:
        print(f"\nWARNING: {failed} test(s) failed!")
        return 1
    else:
        print("\nAll tests passed!")
        return 0


if __name__ == "__main__":
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Server not running at {BASE_URL}")
        print("Please start the server with:")
        print("  cd backend && uvicorn app.main:app --port 8004")
        sys.exit(1)

    exit_code = run_all_tests()
    sys.exit(exit_code)
