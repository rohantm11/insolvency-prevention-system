import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from backend.app.main import app
    with TestClient(app) as c:
        yield c


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json()


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "models_loaded" in data


def test_analyze_company_valid(client):
    payload = {
        "company_id": "TEST_001",
        "company_name": "Test Corp",
        "working_capital_to_total_assets": 0.25,
        "retained_earnings_to_total_assets": 0.35,
        "ebit_to_total_assets": 0.12,
        "market_value_equity_to_total_liabilities": 2.5,
        "sales_to_total_assets": 1.2,
        "current_ratio": 2.0,
        "quick_ratio": 1.5,
        "debt_to_equity": 0.8,
        "interest_coverage": 5.0,
        "net_profit_margin": 0.10,
        "return_on_assets": 0.08,
        "return_on_equity": 0.15,
    }
    r = client.post("/api/financial/analyze", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "prediction" in data
    assert "explanation" in data
    pred = data["prediction"]
    assert 0 <= pred["probability_of_distress"] <= 1
    assert pred["risk_category"] in ("Low", "Medium", "High")
    assert pred["z_score_zone"] in ("Safe", "Grey", "Distress")


def test_analyze_company_missing_fields(client):
    r = client.post("/api/financial/analyze", json={"company_id": "X"})
    assert r.status_code == 422


def test_analyze_company_out_of_range(client):
    payload = {
        "working_capital_to_total_assets": 999,  # exceeds ge/le bounds
        "retained_earnings_to_total_assets": 0.35,
        "ebit_to_total_assets": 0.12,
        "market_value_equity_to_total_liabilities": 2.5,
        "sales_to_total_assets": 1.2,
        "current_ratio": 2.0,
        "quick_ratio": 1.5,
        "debt_to_equity": 0.8,
        "interest_coverage": 5.0,
        "net_profit_margin": 0.10,
        "return_on_assets": 0.08,
        "return_on_equity": 0.15,
    }
    r = client.post("/api/financial/analyze", json=payload)
    assert r.status_code == 422


def test_analyze_employee_valid(client):
    payload = {
        "employee_id": "EMP_001",
        "name": "Test Employee",
        "age": 35,
        "gender": "Male",
        "department": "Engineering",
        "job_role": "Software Engineer",
        "job_level": 3,
        "performance_rating": 3,
        "job_satisfaction": 3,
        "job_involvement": 3,
        "environment_satisfaction": 3,
        "monthly_income": 8000,
        "percent_salary_hike": 15,
        "stock_option_level": 1,
        "years_at_company": 5,
        "years_in_current_role": 3,
        "total_working_years": 10,
        "distance_from_home": 10,
        "business_travel": "Travel_Rarely",
        "over_time": "No",
    }
    r = client.post("/api/employee/analyze", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "prediction" in data
    pred = data["prediction"]
    assert 0 <= pred["retention_score"] <= 100
    assert pred["attrition_risk"] in ("Low", "Medium", "High")


def test_feature_importance_financial(client):
    r = client.get("/api/financial/feature-importance")
    assert r.status_code == 200
    data = r.json()
    assert len(data["feature_importance"]) > 0


def test_feature_importance_employee(client):
    r = client.get("/api/employee/feature-importance")
    assert r.status_code == 200
    data = r.json()
    assert len(data["feature_importance"]) > 0
