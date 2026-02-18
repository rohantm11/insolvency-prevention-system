# Machine Learning Models Documentation

This document describes the ML models used in the Insolvency Prevention System, including their architecture, features, training process, and SHAP-based explanations.

## Table of Contents
- [Model Overview](#model-overview)
- [Insolvency Predictor](#insolvency-predictor)
- [Employee Scorer](#employee-scorer)
- [SHAP Explanations](#shap-explanations)
- [Model Training](#model-training)
- [Performance Metrics](#performance-metrics)

---

## Model Overview

Both models use **XGBoost** (Extreme Gradient Boosting) for classification tasks:

| Model | Task | Algorithm | Target |
|-------|------|-----------|--------|
| Insolvency Predictor | Binary Classification | XGBClassifier | is_bankrupt (0/1) |
| Employee Scorer | Binary Classification | XGBClassifier | attrition (Yes/No) |

### Why XGBoost?

1. **High Performance**: Consistently achieves top results in structured data tasks
2. **Handles Imbalanced Data**: Built-in `scale_pos_weight` for class imbalance
3. **Feature Importance**: Native feature importance and SHAP compatibility
4. **Robustness**: Handles missing values and mixed data types well
5. **Speed**: Efficient training and inference

---

## Insolvency Predictor

### Purpose
Predicts the probability of company financial distress/bankruptcy based on financial ratios.

### Model Architecture

```
XGBClassifier(
    n_estimators=100,      # Number of boosting rounds
    max_depth=5,           # Maximum tree depth
    learning_rate=0.1,     # Step size shrinkage
    scale_pos_weight=auto, # Computed from class distribution
    eval_metric='logloss'  # Binary cross-entropy loss
)
```

### Input Features

The model uses 12 financial ratio features:

| Feature | Description | Altman Component |
|---------|-------------|------------------|
| `working_capital_to_total_assets` | Working Capital / Total Assets | X1 |
| `retained_earnings_to_total_assets` | Retained Earnings / Total Assets | X2 |
| `ebit_to_total_assets` | EBIT / Total Assets | X3 |
| `market_value_equity_to_total_liabilities` | Market Value of Equity / Total Liabilities | X4 |
| `sales_to_total_assets` | Sales / Total Assets | X5 |
| `current_ratio` | Current Assets / Current Liabilities | - |
| `quick_ratio` | Quick Assets / Current Liabilities | - |
| `debt_to_equity` | Total Debt / Total Equity | - |
| `interest_coverage` | EBIT / Interest Expense | - |
| `net_profit_margin` | Net Income / Revenue | - |
| `return_on_assets` | Net Income / Total Assets | - |
| `return_on_equity` | Net Income / Shareholders Equity | - |

### Altman Z-Score Calculation

The model also calculates the traditional Altman Z-Score:

```
Z = 1.2×X1 + 1.4×X2 + 3.3×X3 + 0.6×X4 + 1.0×X5
```

**Interpretation:**
- **Z > 2.99**: Safe Zone - Low probability of bankruptcy
- **1.81 < Z < 2.99**: Grey Zone - Uncertain, warrants attention
- **Z < 1.81**: Distress Zone - High probability of bankruptcy

### Output

| Field | Type | Description |
|-------|------|-------------|
| `probability_of_distress` | float (0-1) | ML-predicted bankruptcy probability |
| `risk_category` | string | "Low" (<30%), "Medium" (30-70%), "High" (>70%) |
| `estimated_time_to_event` | int/null | Estimated years until potential bankruptcy |
| `z_score` | float | Traditional Altman Z-Score |
| `z_score_zone` | string | "Safe", "Grey", or "Distress" |

### Risk Categorization Logic

```python
if probability < 0.3:
    risk_category = "Low"
elif probability < 0.7:
    risk_category = "Medium"
else:
    risk_category = "High"
```

---

## Employee Scorer

### Purpose
Predicts employee attrition risk and calculates retention scores for workforce optimization.

### Model Architecture

```
XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    scale_pos_weight=auto,
    eval_metric='logloss'
)
```

### Input Features

The model uses 18 employee features:

| Feature | Type | Range/Values | Description |
|---------|------|--------------|-------------|
| `age` | int | 18-100 | Employee age |
| `gender` | categorical | Male/Female | Gender |
| `department` | categorical | varies | Department name |
| `job_role` | categorical | varies | Job title |
| `job_level` | int | 1-5 | Seniority level |
| `performance_rating` | int | 1-4 | Performance score |
| `job_satisfaction` | int | 1-4 | Job satisfaction rating |
| `job_involvement` | int | 1-4 | Engagement level |
| `environment_satisfaction` | int | 1-4 | Work environment rating |
| `monthly_income` | int | >0 | Monthly salary |
| `percent_salary_hike` | int | 0-100 | Last salary increase % |
| `stock_option_level` | int | 0-3 | Stock options tier |
| `years_at_company` | int | >=0 | Tenure at company |
| `years_in_current_role` | int | >=0 | Time in current role |
| `total_working_years` | int | >=0 | Total career experience |
| `distance_from_home` | int | >=0 | Commute distance (km) |
| `business_travel` | categorical | Non-Travel/Travel_Rarely/Travel_Frequently | Travel frequency |
| `over_time` | categorical | Yes/No | Works overtime |

### Categorical Encoding

Categorical features are encoded using `LabelEncoder`:

```python
CATEGORICAL_COLUMNS = [
    "gender",
    "department",
    "job_role",
    "business_travel",
    "over_time"
]
```

### Retention Score Calculation

The retention score (0-100) is calculated using a weighted formula:

```python
RETENTION_WEIGHTS = {
    "performance": 0.30,      # Performance rating (30%)
    "job_satisfaction": 0.20, # Job satisfaction (20%)
    "job_involvement": 0.20,  # Job involvement (20%)
    "tenure_bonus": 0.30      # Years at company (30%)
}
```

**Calculation:**
```python
score = 0
# Scale 1-4 ratings to 0-100
score += ((performance_rating - 1) / 3) * 100 * 0.30
score += ((job_satisfaction - 1) / 3) * 100 * 0.20
score += ((job_involvement - 1) / 3) * 100 * 0.20
# Tenure bonus (caps at 10 years)
score += (min(years_at_company, 10) / 10) * 100 * 0.30
```

### Output

| Field | Type | Description |
|-------|------|-------------|
| `retention_score` | float (0-100) | Weighted employee value score |
| `attrition_probability` | float (0-1) | ML-predicted leaving probability |
| `attrition_risk` | string | "Low", "Medium", or "High" |
| `layoff_priority` | string | "Low" (keep), "Medium", "High" (consider layoff) |

### Layoff Priority Logic

```python
if retention_score >= 70:
    layoff_priority = "Low"    # High value, keep
elif retention_score >= 40:
    layoff_priority = "Medium"
else:
    layoff_priority = "High"   # Low value, consider for layoff
```

### Layoff Simulation Algorithm

The `simulate_layoffs()` method optimizes workforce reduction:

1. **Sort employees** by layoff priority (High first), then retention score (Low first)
2. **Iterate through sorted list**, selecting for layoff until:
   - Target budget savings reached, OR
   - Department minimum constraint violated
3. **Generate recommendations** with reasons

```python
def simulate_layoffs(df, budget_cut_percent, min_per_dept=1):
    # Calculate target savings
    target_savings = total_payroll * (budget_cut_percent / 100)

    # Select layoffs respecting constraints
    for employee in sorted_employees:
        if savings >= target_savings:
            break
        if dept_count[employee.dept] <= min_per_dept:
            continue  # Skip - department minimum

        recommend_layoff(employee)
        savings += employee.monthly_income
```

---

## SHAP Explanations

Both models use **SHAP (SHapley Additive exPlanations)** for model interpretability.

### What is SHAP?

SHAP values explain how each feature contributes to a prediction:
- **Positive SHAP value**: Feature increases the prediction (risk)
- **Negative SHAP value**: Feature decreases the prediction (risk)
- **Magnitude**: Strength of the contribution

### Implementation

```python
# Create TreeExplainer for XGBoost
explainer = shap.TreeExplainer(model)

# Calculate SHAP values for a sample
shap_values = explainer.shap_values(sample)
```

### Explanation Output Structure

```json
{
  "shap_values": {
    "debt_to_equity": -0.12,
    "current_ratio": 0.08,
    "net_profit_margin": 0.05
  },
  "top_risk_drivers": [
    {
      "feature": "debt_to_equity",
      "shap_value": -0.12,
      "feature_value": 0.8,
      "impact": "decreases risk"
    }
  ],
  "base_value": 0.25,
  "prediction_value": 0.15
}
```

### Interpreting SHAP Values

**For Insolvency Model:**
- `base_value`: Average bankruptcy probability across training data
- Positive SHAP = feature increases bankruptcy risk
- Negative SHAP = feature decreases bankruptcy risk

**For Employee Model:**
- `base_value`: Average attrition probability across training data
- Positive SHAP = feature increases attrition risk
- Negative SHAP = feature decreases attrition risk

### SHAP Waterfall Chart

The frontend displays SHAP values as a waterfall chart:

```
Base Value (0.25)
    ↓
  +0.08 current_ratio
    ↓
  +0.05 net_profit_margin
    ↓
  -0.12 debt_to_equity
    ↓
  -0.11 other features
    ↓
Prediction (0.15)
```

---

## Model Training

### Data Split

Both models use an 80/20 train/test split with stratification:

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y  # Preserve class distribution
)
```

### Class Imbalance Handling

XGBoost's `scale_pos_weight` automatically adjusts for imbalanced classes:

```python
n_negative = (y_train == 0).sum()
n_positive = (y_train == 1).sum()
scale_pos_weight = n_negative / n_positive
```

### Missing Value Handling

Missing values are imputed with column medians:

```python
X = X.fillna(X.median())
```

### Model Persistence

Models are serialized using pickle:

```python
model_data = {
    "model": xgb_model,
    "feature_names": feature_names,
    "metrics": metrics,
    "label_encoders": encoders  # For employee model
}
pickle.dump(model_data, file)
```

---

## Performance Metrics

### Metrics Computed

| Metric | Description |
|--------|-------------|
| **Accuracy** | Overall correct predictions |
| **Precision** | True positives / (True positives + False positives) |
| **Recall** | True positives / (True positives + False negatives) |
| **F1-Score** | Harmonic mean of precision and recall |
| **ROC-AUC** | Area under ROC curve |

### Expected Performance

**Insolvency Predictor:**
| Metric | Target | Notes |
|--------|--------|-------|
| Accuracy | >85% | Overall prediction accuracy |
| Precision | >80% | Avoid false bankruptcy alerts |
| Recall | >75% | Catch actual bankruptcy cases |
| F1-Score | >78% | Balance precision/recall |
| ROC-AUC | >88% | Discrimination ability |

**Employee Scorer:**
| Metric | Target | Notes |
|--------|--------|-------|
| Accuracy | >82% | Overall prediction accuracy |
| Precision | >78% | Avoid false attrition alerts |
| Recall | >75% | Catch actual attrition cases |
| F1-Score | >76% | Balance precision/recall |
| ROC-AUC | >85% | Discrimination ability |

### Accessing Metrics

Via API:
```bash
GET /api/health
GET /api/financial/feature-importance
GET /api/employee/feature-importance
```

Via Code:
```python
predictor = InsolvencyPredictor()
predictor.load_model("path/to/model.pkl")
print(predictor.metrics)
# {'accuracy': 0.89, 'precision': 0.85, 'recall': 0.82, ...}
```

---

## Retraining Models

### Manual Retraining

```python
from ml_models.insolvency_predictor import InsolvencyPredictor
from ml_models.employee_scorer import EmployeeScorer
import pandas as pd

# Insolvency Model
predictor = InsolvencyPredictor(random_state=42)
df = pd.read_csv("data/company_data.csv")
metrics = predictor.train(df, target_col="is_bankrupt")
predictor.save_model("ml_models/trained_models/insolvency_model.pkl")

# Employee Model
scorer = EmployeeScorer(random_state=42)
df = pd.read_csv("data/employee_data.csv")
metrics = scorer.train(df, target_col="attrition")
scorer.save_model("ml_models/trained_models/employee_model.pkl")
```

### Automated Retraining

Models are automatically trained on startup if no saved model exists:

```python
# In main.py lifespan()
if model_path.exists():
    model.load_model(model_path)
else:
    df = pd.read_csv(data_path)
    model.train(df)
    model.save_model(model_path)
```

---

## Best Practices

### Data Quality
- Ensure all required features are present
- Handle outliers before training
- Validate data ranges match expected constraints

### Model Updates
- Retrain periodically with new data
- Monitor performance metrics for drift
- Version control trained model files

### Interpretability
- Always provide SHAP explanations with predictions
- Document feature definitions for end users
- Validate explanations make business sense
