# API Documentation

Complete API reference for the Insolvency Prevention System.

**Base URL**: `http://localhost:8000`

**API Documentation UI**: `http://localhost:8000/docs` (Swagger UI)

## Table of Contents
- [Health Check](#health-check)
- [Financial Analysis](#financial-analysis)
- [Employee Analysis](#employee-analysis)
- [Report Generation](#report-generation)
- [Error Handling](#error-handling)

---

## Health Check

### GET /api/health

Check API health status and model availability.

**Response**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "insolvency_model_metrics": {
    "accuracy": 0.89,
    "precision": 0.85,
    "recall": 0.82,
    "f1_score": 0.83,
    "roc_auc": 0.91
  },
  "employee_model_metrics": {
    "accuracy": 0.85,
    "precision": 0.81,
    "recall": 0.79,
    "f1_score": 0.80,
    "roc_auc": 0.89
  }
}
```

---

## Financial Analysis

### POST /api/financial/analyze

Analyze a single company's financial data for insolvency risk.

**Request Body**
```json
{
  "company_id": "COMP_001",
  "company_name": "Example Corp",
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
  "return_on_equity": 0.15
}
```

**Request Fields**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_id` | string | No | Unique company identifier |
| `company_name` | string | No | Company name |
| `working_capital_to_total_assets` | float | Yes | Working Capital / Total Assets |
| `retained_earnings_to_total_assets` | float | Yes | Retained Earnings / Total Assets |
| `ebit_to_total_assets` | float | Yes | EBIT / Total Assets |
| `market_value_equity_to_total_liabilities` | float | Yes | Market Value of Equity / Total Liabilities |
| `sales_to_total_assets` | float | Yes | Sales / Total Assets |
| `current_ratio` | float | Yes | Current Assets / Current Liabilities |
| `quick_ratio` | float | Yes | Quick Assets / Current Liabilities |
| `debt_to_equity` | float | Yes | Total Debt / Total Equity |
| `interest_coverage` | float | Yes | EBIT / Interest Expense |
| `net_profit_margin` | float | Yes | Net Income / Revenue |
| `return_on_assets` | float | Yes | Net Income / Total Assets |
| `return_on_equity` | float | Yes | Net Income / Shareholders Equity |

**Response**
```json
{
  "prediction": {
    "company_id": "COMP_001",
    "company_name": "Example Corp",
    "probability_of_distress": 0.15,
    "risk_category": "Low",
    "estimated_time_to_event": null,
    "z_score": 3.25,
    "z_score_zone": "Safe"
  },
  "explanation": {
    "shap_values": {
      "debt_to_equity": -0.12,
      "current_ratio": 0.08,
      "net_profit_margin": 0.05
    },
    "top_risk_drivers": [
      {
        "feature": "debt_to_equity",
        "value": 0.8,
        "shap_value": -0.12,
        "direction": "decreases risk"
      }
    ],
    "base_value": 0.25,
    "prediction_value": 0.15
  }
}
```

---

### POST /api/financial/upload

Upload a CSV file with multiple companies' financial data.

**Request**
- Content-Type: `multipart/form-data`
- File field: `file` (CSV)

**CSV Format**
```csv
company_id,company_name,working_capital_to_total_assets,retained_earnings_to_total_assets,ebit_to_total_assets,market_value_equity_to_total_liabilities,sales_to_total_assets,current_ratio,quick_ratio,debt_to_equity,interest_coverage,net_profit_margin,return_on_assets,return_on_equity
COMP_001,Acme Corp,0.25,0.35,0.12,2.5,1.2,2.0,1.5,0.8,5.0,0.10,0.08,0.15
COMP_002,Beta Inc,0.15,0.20,0.08,1.5,0.9,1.5,1.0,1.2,3.0,0.05,0.04,0.08
```

**Response**
```json
{
  "total_companies": 2,
  "predictions": [
    {
      "company_id": "COMP_001",
      "company_name": "Acme Corp",
      "probability_of_distress": 0.15,
      "risk_category": "Low",
      "estimated_time_to_event": null,
      "z_score": 3.25,
      "z_score_zone": "Safe"
    },
    {
      "company_id": "COMP_002",
      "company_name": "Beta Inc",
      "probability_of_distress": 0.45,
      "risk_category": "Medium",
      "estimated_time_to_event": 3,
      "z_score": 2.10,
      "z_score_zone": "Grey"
    }
  ],
  "summary": {
    "high_risk_count": 0,
    "medium_risk_count": 1,
    "low_risk_count": 1,
    "avg_probability": 0.30,
    "z_score_distress_count": 0
  }
}
```

---

### GET /api/financial/feature-importance

Get feature importance from the insolvency prediction model.

**Response**
```json
{
  "feature_importance": {
    "debt_to_equity": 0.25,
    "interest_coverage": 0.18,
    "current_ratio": 0.15,
    "net_profit_margin": 0.12,
    "working_capital_to_total_assets": 0.10
  },
  "model_metrics": {
    "accuracy": 0.89,
    "precision": 0.85,
    "recall": 0.82,
    "f1_score": 0.83,
    "roc_auc": 0.91
  }
}
```

---

## Employee Analysis

### POST /api/employee/analyze

Analyze a single employee's data for attrition risk.

**Request Body**
```json
{
  "employee_id": "EMP_001",
  "name": "John Doe",
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
  "over_time": "No"
}
```

**Request Fields**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `employee_id` | string | No | - | Unique employee identifier |
| `name` | string | No | - | Employee name |
| `age` | int | Yes | 18-100 | Employee age |
| `gender` | string | Yes | Male/Female | Gender |
| `department` | string | Yes | - | Department name |
| `job_role` | string | Yes | - | Job title |
| `job_level` | int | Yes | 1-5 | Job level/seniority |
| `performance_rating` | int | Yes | 1-4 | Performance score |
| `job_satisfaction` | int | Yes | 1-4 | Job satisfaction score |
| `job_involvement` | int | Yes | 1-4 | Job involvement score |
| `environment_satisfaction` | int | Yes | 1-4 | Work environment satisfaction |
| `monthly_income` | int | Yes | > 0 | Monthly salary |
| `percent_salary_hike` | int | Yes | 0-100 | Last salary increase % |
| `stock_option_level` | int | Yes | 0-3 | Stock options tier |
| `years_at_company` | int | Yes | >= 0 | Tenure at company |
| `years_in_current_role` | int | Yes | >= 0 | Time in current role |
| `total_working_years` | int | Yes | >= 0 | Total career experience |
| `distance_from_home` | int | Yes | >= 0 | Commute distance (km) |
| `business_travel` | string | Yes | Non-Travel/Travel_Rarely/Travel_Frequently | Travel frequency |
| `over_time` | string | Yes | Yes/No | Works overtime |

**Response**
```json
{
  "prediction": {
    "employee_id": "EMP_001",
    "name": "John Doe",
    "department": "Engineering",
    "retention_score": 78.5,
    "attrition_probability": 0.22,
    "attrition_risk": "Low",
    "layoff_priority": "Low"
  },
  "explanation": {
    "shap_values": {
      "monthly_income": 0.15,
      "job_satisfaction": 0.08,
      "years_at_company": -0.12
    },
    "top_factors": [
      {
        "feature": "monthly_income",
        "value": 8000,
        "shap_value": 0.15,
        "direction": "increases retention"
      }
    ],
    "base_value": 0.35,
    "prediction_value": 0.22
  }
}
```

---

### POST /api/employee/upload

Upload a CSV file with multiple employees' data.

**Request**
- Content-Type: `multipart/form-data`
- File field: `file` (CSV)

**CSV Format**
```csv
employee_id,name,age,gender,department,job_role,job_level,performance_rating,job_satisfaction,job_involvement,environment_satisfaction,monthly_income,percent_salary_hike,stock_option_level,years_at_company,years_in_current_role,total_working_years,distance_from_home,business_travel,over_time
EMP_001,John Doe,35,Male,Engineering,Software Engineer,3,3,3,3,3,8000,15,1,5,3,10,10,Travel_Rarely,No
EMP_002,Jane Smith,28,Female,Sales,Sales Rep,2,4,4,4,3,5500,12,0,2,2,5,25,Travel_Frequently,Yes
```

**Response**
```json
{
  "total_employees": 2,
  "predictions": [
    {
      "employee_id": "EMP_001",
      "name": "John Doe",
      "department": "Engineering",
      "retention_score": 78.5,
      "attrition_probability": 0.22,
      "attrition_risk": "Low",
      "layoff_priority": "Low"
    },
    {
      "employee_id": "EMP_002",
      "name": "Jane Smith",
      "department": "Sales",
      "retention_score": 45.2,
      "attrition_probability": 0.55,
      "attrition_risk": "High",
      "layoff_priority": "Medium"
    }
  ],
  "summary": {
    "high_attrition_risk_count": 1,
    "medium_attrition_risk_count": 0,
    "low_attrition_risk_count": 1,
    "avg_retention_score": 61.85,
    "avg_attrition_probability": 0.385,
    "high_layoff_priority_count": 0
  }
}
```

---

### POST /api/employee/simulate-layoff

Simulate layoff recommendations based on budget constraints.

**Request**
- Content-Type: `multipart/form-data`
- Query Parameters:
  - `budget_cut_percent` (float, required): Target budget reduction (0-100)
  - `min_per_dept` (int, optional, default=1): Minimum employees to keep per department
- File field: `file` (CSV with employee data)

**Example Request**
```
POST /api/employee/simulate-layoff?budget_cut_percent=10&min_per_dept=2
Content-Type: multipart/form-data

file: employees.csv
```

**Response**
```json
{
  "target_budget_cut": 10.0,
  "target_monthly_savings": 25000.0,
  "actual_monthly_savings": 24500.0,
  "employees_affected": 5,
  "savings_achieved_percent": 9.8,
  "recommendations": [
    {
      "employee_id": "EMP_015",
      "name": "Mike Wilson",
      "department": "Marketing",
      "monthly_income": 5500,
      "retention_score": 32.5,
      "layoff_recommended": true,
      "layoff_reason": "Low retention score, high cost"
    },
    {
      "employee_id": "EMP_001",
      "name": "John Doe",
      "department": "Engineering",
      "monthly_income": 8000,
      "retention_score": 78.5,
      "layoff_recommended": false,
      "layoff_reason": "High performer, critical role"
    }
  ],
  "department_breakdown": {
    "Marketing": 2,
    "Sales": 2,
    "Operations": 1
  }
}
```

---

### GET /api/employee/feature-importance

Get feature importance from the employee scoring model.

**Response**
```json
{
  "feature_importance": {
    "monthly_income": 0.22,
    "job_satisfaction": 0.18,
    "over_time": 0.15,
    "years_at_company": 0.12,
    "age": 0.10
  },
  "model_metrics": {
    "accuracy": 0.85,
    "precision": 0.81,
    "recall": 0.79,
    "f1_score": 0.80,
    "roc_auc": 0.89
  }
}
```

---

## Report Generation

### POST /api/reports/insolvency

Generate an insolvency risk assessment PDF report.

**Request Body**
```json
{
  "company_id": "COMP_001",
  "company_name": "Example Corp",
  "company_data": {
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
    "return_on_equity": 0.15
  }
}
```

**Response**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=insolvency_report_COMP_001_20240115_143022.pdf`

**PDF Contents**
- Company identification and analysis date
- Risk score with color-coded indicator
- Altman Z-Score analysis
- Time to event estimate (if applicable)
- Top 10 risk drivers with SHAP values
- Recommendations section

---

### POST /api/reports/layoff

Generate a layoff simulation PDF report.

**Request**
- Content-Type: `multipart/form-data`
- Query Parameters:
  - `budget_cut_percent` (float, required): Target budget reduction
  - `min_per_dept` (int, optional, default=1): Minimum employees per department
- File field: `file` (CSV with employee data)

**Response**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=layoff_report_20240115_143022.pdf`

**PDF Contents**
- Simulation parameters
- Summary statistics (targets vs. actuals)
- Complete list of employees with recommendations
- Cost savings analysis
- Department impact breakdown

---

## Error Handling

### Error Response Format

All errors return a consistent JSON format:

```json
{
  "error": "Error Type",
  "detail": "Detailed error message"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request data or missing required fields |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Models not loaded or service unavailable |

### Common Errors

**400 - Invalid File Type**
```json
{
  "detail": "File must be a CSV"
}
```

**400 - Missing Required Columns**
```json
{
  "detail": "CSV must contain 'department' and 'monthly_income' columns"
}
```

**503 - Model Not Loaded**
```json
{
  "detail": "Insolvency model not loaded"
}
```

**500 - Analysis Failed**
```json
{
  "error": "Internal Server Error",
  "detail": "Analysis failed: [specific error message]"
}
```

---

## Rate Limiting

Currently, there are no rate limits implemented. For production deployments, consider adding rate limiting at the reverse proxy level (nginx).

## Authentication

The current API does not require authentication. For production deployments, implement JWT-based authentication or API key validation.

## CORS

The API allows all origins for development. In production, configure specific allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
