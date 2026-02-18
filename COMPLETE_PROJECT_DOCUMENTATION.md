# SolvencyInsight: Complete Technical Documentation

## AI-Powered Financial Distress Prediction System

---

# Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Architecture](#2-project-architecture)
3. [Data Layer](#3-data-layer)
4. [Machine Learning Module](#4-machine-learning-module)
5. [Backend API](#5-backend-api)
6. [Frontend Application](#6-frontend-application)
7. [Model Comparison Analysis](#7-model-comparison-analysis)
8. [Feature Engineering Deep Dive](#8-feature-engineering-deep-dive)
9. [API Reference](#9-api-reference)
10. [Deployment Guide](#10-deployment-guide)
11. [Team Contributions](#11-team-contributions)

---

# 1. Executive Summary

## 1.1 What is SolvencyInsight?

SolvencyInsight is an enterprise-grade financial distress prediction platform that combines **traditional financial analysis** (Altman Z-Score) with **modern machine learning** (XGBoost with SHAP explainability) to predict corporate bankruptcy risk.

## 1.2 Problem Statement

Corporate bankruptcy can devastate stakeholders - employees lose jobs, investors lose capital, and suppliers lose revenue. Early detection of financial distress allows:
- **Investors** to divest before losses
- **Creditors** to adjust lending terms
- **Management** to take corrective action
- **Regulators** to intervene proactively

## 1.3 Solution Overview

SolvencyInsight analyzes **12 financial ratios** and engineers **41 derived features** to predict bankruptcy probability with **97.97% ROC-AUC accuracy**.

### Key Capabilities:
| Feature | Description |
|---------|-------------|
| **Single Company Analysis** | Upload CSV or enter data manually for instant risk assessment |
| **Bulk Analysis** | Process hundreds of companies simultaneously |
| **SHAP Explanations** | Understand WHY a company is flagged as high-risk |
| **Altman Z-Score** | Classic bankruptcy predictor with zone classification |
| **PDF Reports** | Generate professional reports for stakeholders |
| **Market Intelligence** | Real-time news sentiment and sector analysis |

## 1.4 Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│  React 18 + TypeScript + TailwindCSS + Recharts + Vite          │
├─────────────────────────────────────────────────────────────────┤
│                        BACKEND                                   │
│  FastAPI + Pydantic + Uvicorn + Python 3.11+                    │
├─────────────────────────────────────────────────────────────────┤
│                     MACHINE LEARNING                             │
│  XGBoost + SHAP + Scikit-learn + Pandas + NumPy                 │
├─────────────────────────────────────────────────────────────────┤
│                         DATA                                     │
│  10,000 Company Dataset + 30 Industries + 5 Company Sizes       │
└─────────────────────────────────────────────────────────────────┘
```

---

# 2. Project Architecture

## 2.1 Directory Structure

```
insolvency-prevention-system/
│
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # API endpoints & app initialization
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic request/response models
│   │   └── services/
│   │       ├── market_intelligence.py  # News & sector analysis
│   │       └── report_generator.py     # PDF report generation
│   └── requirements.txt
│
├── frontend/                     # React Frontend
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── DataTable.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── RiskGauge.tsx
│   │   │   └── index.ts
│   │   ├── pages/               # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── InsolvencyAnalysis.tsx
│   │   │   └── EmployeeAnalysis.tsx
│   │   ├── services/
│   │   │   └── api.ts           # Axios API client
│   │   ├── context/
│   │   │   └── ToastContext.tsx # Notification system
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── vite.config.ts           # Vite configuration with proxy
│   ├── tailwind.config.js
│   └── package.json
│
├── ml_models/                    # Machine Learning Module
│   ├── insolvency_predictor.py      # Original predictor
│   ├── insolvency_predictor_v2.py   # Enhanced with feature engineering
│   ├── employee_predictor.py
│   └── saved_models/            # Serialized trained models
│       ├── insolvency_model_v2.pkl
│       └── employee_model.pkl
│
├── data/                         # Training Data
│   ├── training_companies/       # 500 company dataset
│   └── training_companies_10k/   # 10,000 company dataset
│       ├── _combined_training_data_10k.csv
│       └── _company_index_10k.csv
│
├── model_comparison_v2.py        # Model comparison script
├── generate_large_dataset.py     # Dataset generation script
├── train_model_v2.py             # Model training script
│
└── Documentation & Reports
    ├── model_comparison_report.txt
    ├── model_comparison_*.png    # Comparison charts
    └── SolvencyInsight_Team_Documentation.pdf
```

## 2.2 Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                  │
│                    (React + TypeScript + TailwindCSS)                    │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                            API LAYER                                      │
│                    (Axios HTTP Client - api.ts)                          │
│                                                                           │
│  Functions:                                                               │
│  • analyzeCompany()     → POST /api/financial/analyze                    │
│  • uploadSingleCompany() → POST /api/financial/upload-single             │
│  • uploadFinancialData() → POST /api/financial/upload                    │
│  • generateInsolvencyReport() → POST /api/reports/insolvency             │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         VITE DEV SERVER                                   │
│                    (Proxy: /api → localhost:8001)                        │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                                   │
│                         (main.py - Port 8001)                            │
│                                                                           │
│  Endpoints:                                                               │
│  • /api/financial/analyze        - Single company prediction             │
│  • /api/financial/upload         - Bulk CSV processing                   │
│  • /api/financial/upload-single  - Single CSV with full SHAP            │
│  • /api/reports/insolvency       - PDF report generation                 │
│  • /health                       - System health check                   │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      MACHINE LEARNING ENGINE                              │
│                    (insolvency_predictor_v2.py)                          │
│                                                                           │
│  Pipeline:                                                                │
│  1. Receive 12 base financial ratios                                     │
│  2. Engineer 41 total features                                           │
│  3. XGBoost prediction → probability                                     │
│  4. SHAP TreeExplainer → feature contributions                          │
│  5. Altman Z-Score calculation → zone classification                    │
│  6. Return: probability, risk_category, z_score, SHAP values            │
└──────────────────────────────────────────────────────────────────────────┘
```

## 2.3 Request-Response Flow Example

```
User clicks "Analyze Company"
         │
         ▼
┌─────────────────────────────────────┐
│ Frontend: InsolvencyAnalysis.tsx    │
│ handleSingleAnalysis() called       │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ API Client: api.ts                  │
│ uploadSingleCompany(file)           │
│ POST /api/financial/upload-single   │
│ Content-Type: multipart/form-data   │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ Backend: main.py                    │
│ @app.post("/api/financial/upload-   │
│           single")                  │
│ 1. Read CSV with pandas             │
│ 2. Validate columns                 │
│ 3. Call predictor.predict()         │
│ 4. Call predictor.explain_          │
│    prediction()                     │
│ 5. Calculate Z-Score                │
│ 6. Return InsolvencyAnalysis-       │
│    Response                         │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ Response JSON:                      │
│ {                                   │
│   "prediction": {                   │
│     "probability_of_distress": 0.85,│
│     "risk_category": "High",        │
│     "z_score": 1.23,                │
│     "z_score_zone": "Distress"      │
│   },                                │
│   "explanation": {                  │
│     "shap_values": {...},           │
│     "top_risk_drivers": [...]       │
│   }                                 │
│ }                                   │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ Frontend renders:                   │
│ • RiskGauge (85% probability)       │
│ • Z-Score visualization             │
│ • SHAP bar chart (top 10 drivers)   │
│ • Key metrics cards                 │
└─────────────────────────────────────┘
```

---

# 3. Data Layer

## 3.1 Dataset Overview

The model is trained on **10,000 synthetic companies** generated with realistic financial characteristics based on industry research and domain expertise.

### Dataset Statistics:
| Metric | Value |
|--------|-------|
| Total Companies | 10,000 |
| Healthy Companies | 5,302 (53.0%) |
| Distressed Companies | 4,698 (47.0%) |
| Industries | 30 |
| Company Sizes | 5 categories |
| Economic Cycles | 4 phases |

## 3.2 Input Features (12 Base Ratios)

### 3.2.1 Altman Z-Score Components (5 ratios)

| Feature | Formula | Interpretation |
|---------|---------|----------------|
| `working_capital_to_total_assets` | (Current Assets - Current Liabilities) / Total Assets | Measures short-term liquidity; negative values indicate distress |
| `retained_earnings_to_total_assets` | Retained Earnings / Total Assets | Measures cumulative profitability; young/loss-making firms have low values |
| `ebit_to_total_assets` | EBIT / Total Assets | Measures operating efficiency; shows true productivity of assets |
| `market_value_equity_to_total_liabilities` | Market Cap / Total Liabilities | Measures solvency; how much assets can decline before insolvency |
| `sales_to_total_assets` | Revenue / Total Assets | Measures asset turnover; ability to generate sales from assets |

### 3.2.2 Additional Financial Ratios (7 ratios)

| Feature | Formula | Healthy Range | Distressed Range |
|---------|---------|---------------|------------------|
| `current_ratio` | Current Assets / Current Liabilities | > 1.5 | < 1.0 |
| `quick_ratio` | (Current Assets - Inventory) / Current Liabilities | > 1.0 | < 0.5 |
| `debt_to_equity` | Total Debt / Total Equity | < 1.0 | > 2.5 |
| `interest_coverage` | EBIT / Interest Expense | > 3.0 | < 1.5 |
| `net_profit_margin` | Net Income / Revenue | > 5% | < 0% |
| `return_on_assets` | Net Income / Total Assets | > 5% | < 0% |
| `return_on_equity` | Net Income / Shareholders Equity | > 10% | < 0% |

## 3.3 Data Generation Logic

### 3.3.1 Healthy Company Generation

```python
def generate_healthy_company(industry_chars, size_chars, economic_cycle):
    # Base financial health factor (0.6 to 1.0 for healthy)
    base_strength = np.random.uniform(0.65, 1.0)

    # Size affects stability
    stability = size_chars['stability'] * base_strength

    # Industry affects margins and leverage
    margin_mult = industry_chars['margin']
    leverage_mult = industry_chars['leverage']

    data = {
        'working_capital_to_total_assets': np.clip(
            np.random.normal(0.22 * stability, 0.06), -0.1, 0.5
        ),
        'current_ratio': np.clip(
            np.random.normal(1.9 * stability, 0.35), 0.9, 4.0
        ),
        'debt_to_equity': np.clip(
            np.random.normal(0.65 * leverage_mult / stability, 0.2), 0.1, 2.5
        ),
        # ... other ratios
        'is_insolvent': 0
    }
    return data
```

### 3.3.2 Distressed Company Generation

```python
def generate_distressed_company(industry_chars, size_chars, economic_cycle):
    # Distress severity (0.2 to 0.7, lower = more distressed)
    distress_level = np.random.uniform(0.2, 0.7)

    data = {
        'working_capital_to_total_assets': np.clip(
            np.random.normal(-0.08 + 0.15 * distress_level, 0.08), -0.35, 0.12
        ),
        'current_ratio': np.clip(
            np.random.normal(0.7 + 0.4 * distress_level, 0.25), 0.2, 1.4
        ),
        'debt_to_equity': np.clip(
            np.random.normal(3.5 - distress_level * 1.5, 0.8), 1.2, 8.0
        ),
        # ... other ratios
        'is_insolvent': 1
    }
    return data
```

### 3.3.3 Industry Adjustments

Different industries have different typical financial characteristics:

```python
INDUSTRIES = {
    "Technology": {"volatility": 1.3, "growth": 1.2, "leverage": 0.6, "margin": 1.4},
    "Banking": {"volatility": 1.1, "growth": 0.9, "leverage": 3.0, "margin": 0.9},
    "Retail": {"volatility": 1.0, "growth": 0.95, "leverage": 1.1, "margin": 0.5},
    "Airlines": {"volatility": 1.8, "growth": 0.8, "leverage": 1.5, "margin": 0.3},
    "Utilities": {"volatility": 0.5, "growth": 0.7, "leverage": 1.6, "margin": 0.8},
    # ... 25 more industries
}
```

### 3.3.4 Economic Cycle Effects

```python
ECONOMIC_CYCLES = {
    "expansion": {"profit": 1.15, "liquidity": 1.1, "leverage": 0.95},
    "peak": {"profit": 1.2, "liquidity": 1.05, "leverage": 1.0},
    "contraction": {"profit": 0.8, "liquidity": 0.9, "leverage": 1.1},
    "trough": {"profit": 0.7, "liquidity": 0.85, "leverage": 1.15},
}
```

## 3.4 CSV File Format

### Single Company CSV:
```csv
company_id,company_name,working_capital_to_total_assets,retained_earnings_to_total_assets,ebit_to_total_assets,market_value_equity_to_total_liabilities,sales_to_total_assets,current_ratio,quick_ratio,debt_to_equity,interest_coverage,net_profit_margin,return_on_assets,return_on_equity
COMP_001,Acme Corp,0.25,0.35,0.12,2.5,1.2,2.0,1.5,0.8,5.0,0.10,0.08,0.15
```

### Bulk Upload CSV:
```csv
company_id,company_name,working_capital_to_total_assets,...,is_insolvent
COMP_001,Company A,0.25,...,0
COMP_002,Company B,-0.05,...,1
COMP_003,Company C,0.15,...,0
```

---

# 4. Machine Learning Module

## 4.1 Model Selection Rationale

### Why XGBoost?

We evaluated three models and chose XGBoost for production:

| Criterion | XGBoost V2 | Random Forest | Logistic Regression |
|-----------|------------|---------------|---------------------|
| ROC-AUC | **97.97%** | 97.60% | 97.30% |
| Handles Non-linearity | Excellent | Good | Limited |
| Feature Interactions | Automatic | Automatic | Manual only |
| Regularization | L1 + L2 + gamma | Tree constraints | L2 only |
| Explainability | SHAP native | SHAP supported | Coefficients |
| Overfitting Risk | Low | Moderate | Low |

### XGBoost Advantages for Financial Data:

1. **Gradient Boosting**: Each tree corrects errors from previous trees, capturing nuanced patterns
2. **Regularization**: Built-in L1/L2 prevents overfitting on noisy financial data
3. **Non-linearity**: Captures thresholds (e.g., debt_to_equity > 3.0 = danger zone)
4. **Missing Values**: Native handling of missing data (common in financial datasets)
5. **SHAP Integration**: TreeExplainer provides fast, accurate feature attributions

## 4.2 Model Architecture (InsolvencyPredictorV2)

### 4.2.1 Class Structure

```python
class InsolvencyPredictorV2:
    """
    Enhanced XGBoost-based model for predicting company insolvency/bankruptcy risk.

    Features:
    - Advanced feature engineering with derived financial metrics
    - Fine-tuned XGBoost parameters for high accuracy
    - Cross-validation for robust performance estimation
    - SHAP-based explanations for interpretability
    """

    # 12 base features from input data
    BASE_FEATURES = [
        "working_capital_to_total_assets",
        "retained_earnings_to_total_assets",
        "ebit_to_total_assets",
        "market_value_equity_to_total_liabilities",
        "sales_to_total_assets",
        "current_ratio",
        "quick_ratio",
        "debt_to_equity",
        "interest_coverage",
        "net_profit_margin",
        "return_on_assets",
        "return_on_equity",
    ]

    def __init__(self, random_state=42):
        self.model = None           # XGBClassifier
        self.explainer = None       # SHAP TreeExplainer
        self.is_fitted = False
        self.metrics = {}
        self.feature_names = []     # 41 features after engineering
        self.cv_scores = []

    def _engineer_features(self, df): ...
    def train(self, df, target_col, test_size, use_cv): ...
    def predict(self, df): ...
    def explain_prediction(self, df, index): ...
    def get_feature_importance(self): ...
```

### 4.2.2 XGBoost Hyperparameters

```python
self.model = xgb.XGBClassifier(
    # Tree Structure
    n_estimators=200,          # Number of boosting rounds
    max_depth=6,               # Maximum tree depth (captures interactions)
    min_child_weight=5,        # Minimum samples per leaf (prevents overfitting)
    gamma=0.1,                 # Minimum loss reduction for split

    # Learning Rate
    learning_rate=0.05,        # Step size shrinkage (lower = more trees needed)

    # Sampling (introduces randomness)
    subsample=0.8,             # Use 80% of rows per tree
    colsample_bytree=0.8,      # Use 80% of features per tree
    colsample_bylevel=0.8,     # Use 80% of features per level

    # Regularization (prevents overfitting)
    reg_alpha=0.5,             # L1 regularization (Lasso)
    reg_lambda=2.0,            # L2 regularization (Ridge)

    # Class Imbalance
    scale_pos_weight=1.13,     # n_negative / n_positive

    # Training Control
    early_stopping_rounds=20,  # Stop if no improvement for 20 rounds
    eval_metric='logloss',     # Optimization metric

    random_state=42,
    n_jobs=-1,                 # Use all CPU cores
)
```

### 4.2.3 Hyperparameter Explanations

| Parameter | Value | Why This Value |
|-----------|-------|----------------|
| `n_estimators=200` | 200 trees | Enough capacity for complex patterns; early stopping prevents overuse |
| `max_depth=6` | 6 levels | Captures feature interactions (e.g., leverage × liquidity); not too deep to overfit |
| `learning_rate=0.05` | Small steps | Allows fine-grained optimization; more trees compensate |
| `reg_alpha=0.5` | L1 penalty | Encourages sparse solutions; zeroes out irrelevant features |
| `reg_lambda=2.0` | L2 penalty | Prevents any single feature from dominating |
| `subsample=0.8` | 80% rows | Introduces randomness; reduces variance |
| `colsample_bytree=0.8` | 80% features | Forces model to not rely on any single feature |
| `min_child_weight=5` | 5 samples minimum | Prevents splits on very small subsets |
| `gamma=0.1` | Minimum gain | Only make splits that significantly improve model |

## 4.3 Training Pipeline

```python
def train(self, df, target_col='is_insolvent', test_size=0.2, use_cv=True):
    """
    Training Pipeline:
    1. Extract base features
    2. Engineer 41 total features
    3. Split into train/test (80/20, stratified)
    4. Train XGBoost with early stopping
    5. Create SHAP explainer
    6. Calculate metrics
    7. Perform 5-fold cross-validation
    8. Save model
    """

    # Step 1: Get available features
    available_features = [col for col in self.BASE_FEATURES if col in df.columns]
    X_base = df[available_features].copy()
    y = df[target_col].copy()

    # Step 2: Engineer features (12 → 41)
    X = self._engineer_features(X_base)
    self.feature_names = list(X.columns)

    # Step 3: Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Step 4: Train model
    self.model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )

    # Step 5: Create SHAP explainer
    self.explainer = shap.TreeExplainer(self.model)

    # Step 6: Calculate metrics
    y_pred = self.model.predict(X_test)
    y_prob = self.model.predict_proba(X_test)[:, 1]

    self.metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_prob),
    }

    # Step 7: Cross-validation
    if use_cv:
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        self.cv_scores = cross_val_score(cv_model, X, y, cv=cv, scoring='roc_auc')

    # Step 8: Save model
    self._save_model()

    return self.metrics
```

## 4.4 Prediction Pipeline

```python
def predict(self, df):
    """
    Prediction Pipeline:
    1. Engineer features from input
    2. Get raw probability from XGBoost
    3. Apply probability smoothing (avoid 0% or 100%)
    4. Calculate Altman Z-Score
    5. Categorize risk level
    6. Estimate time to potential event
    7. Return structured results
    """

    # Step 1: Engineer features
    X_base = df[self.BASE_FEATURES].copy()
    X = self._engineer_features(X_base)

    # Step 2: Get raw probability
    raw_probabilities = self.model.predict_proba(X)[:, 1]

    # Step 3: Probability smoothing
    # Maps [0, 1] → [0.02, 0.98] to avoid unrealistic extremes
    probabilities = 0.02 + 0.96 * raw_probabilities

    # Step 4: Calculate Z-Score
    z_scores = (
        1.2 * X_base['working_capital_to_total_assets'] +
        1.4 * X_base['retained_earnings_to_total_assets'] +
        3.3 * X_base['ebit_to_total_assets'] +
        0.6 * X_base['market_value_equity_to_total_liabilities'] +
        1.0 * X_base['sales_to_total_assets']
    )

    # Step 5: Categorize risk
    risk_categories = []
    for prob in probabilities:
        if prob < 0.25:
            risk_categories.append("Low")
        elif prob < 0.55:
            risk_categories.append("Medium")
        else:
            risk_categories.append("High")

    # Step 6: Z-Score zones
    z_zones = []
    for z in z_scores:
        if z > 2.99:
            z_zones.append("Safe")
        elif z >= 1.81:
            z_zones.append("Grey")
        else:
            z_zones.append("Distress")

    # Step 7: Return results
    return pd.DataFrame({
        "probability_of_distress": probabilities,
        "risk_category": risk_categories,
        "z_score": z_scores,
        "z_score_zone": z_zones,
    })
```

## 4.5 SHAP Explainability

### What is SHAP?

SHAP (SHapley Additive exPlanations) values are based on cooperative game theory. For each prediction, SHAP calculates how much each feature contributed to moving the prediction away from the baseline (average prediction).

```
Prediction = Base Value + SHAP(feature_1) + SHAP(feature_2) + ... + SHAP(feature_n)
```

### SHAP Implementation

```python
def explain_prediction(self, df, index=0):
    """
    Generate SHAP-based explanation for a single prediction.

    Returns:
    - shap_values: Contribution of each feature
    - top_risk_drivers: Top 15 features sorted by |SHAP|
    - base_value: Expected model output (average)
    - prediction_value: Actual prediction for this sample
    """

    # Engineer features
    X_base = df[self.BASE_FEATURES].copy()
    X = self._engineer_features(X_base)

    # Get single sample
    sample = X.iloc[[index]]

    # Calculate SHAP values
    shap_values = self.explainer.shap_values(sample)

    # Handle binary classification output
    if isinstance(shap_values, list):
        shap_values = shap_values[1]  # Class 1 (distressed)

    shap_values = shap_values.flatten()

    # Create feature importance dictionary
    shap_dict = dict(zip(self.feature_names, shap_values))

    # Sort by absolute importance
    sorted_features = sorted(
        shap_dict.items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )

    # Build top drivers list
    top_drivers = []
    for feature, shap_val in sorted_features[:15]:
        original_value = sample[feature].values[0]
        impact = "increases_risk" if shap_val > 0 else "decreases_risk"

        top_drivers.append({
            "feature": feature,
            "shap_value": float(shap_val),
            "original_value": float(original_value),
            "impact": impact,
        })

    return {
        "shap_values": shap_dict,
        "top_risk_drivers": top_drivers,
        "base_value": float(self.explainer.expected_value),
        "prediction_value": float(self.model.predict_proba(sample)[0, 1]),
    }
```

### Interpreting SHAP Values

| SHAP Value | Meaning | Example |
|------------|---------|---------|
| Positive (+0.5) | Feature INCREASES bankruptcy risk | High debt_to_equity pushes prediction toward distress |
| Negative (-0.3) | Feature DECREASES bankruptcy risk | High current_ratio pushes prediction toward healthy |
| Near Zero (0.01) | Feature has minimal impact | Feature value is close to average |

### Example SHAP Output

```json
{
  "base_value": 0.47,
  "prediction_value": 0.92,
  "top_risk_drivers": [
    {"feature": "profitability_score", "shap_value": +0.18, "impact": "increases_risk"},
    {"feature": "financial_distress_score", "shap_value": +0.12, "impact": "increases_risk"},
    {"feature": "current_ratio", "shap_value": +0.08, "impact": "increases_risk"},
    {"feature": "interest_coverage_safe", "shap_value": -0.05, "impact": "decreases_risk"}
  ]
}
```

Interpretation: This company has a 92% distress probability (vs 47% baseline) primarily because of poor profitability and high distress indicators.

## 4.6 Altman Z-Score

### The Formula

Developed by Edward Altman in 1968, the Z-Score is still the gold standard for bankruptcy prediction:

```
Z = 1.2×X1 + 1.4×X2 + 3.3×X3 + 0.6×X4 + 1.0×X5

Where:
X1 = Working Capital / Total Assets
X2 = Retained Earnings / Total Assets
X3 = EBIT / Total Assets
X4 = Market Value of Equity / Total Liabilities
X5 = Sales / Total Assets
```

### Zone Classification

| Zone | Z-Score Range | Interpretation | Action |
|------|---------------|----------------|--------|
| **Safe** | Z > 2.99 | Low bankruptcy probability | Continue monitoring |
| **Grey** | 1.81 ≤ Z ≤ 2.99 | Uncertain, caution needed | Increase monitoring frequency |
| **Distress** | Z < 1.81 | High bankruptcy probability | Immediate attention required |

### Coefficient Meanings

| Coefficient | Feature | Weight | Why This Weight |
|-------------|---------|--------|-----------------|
| 1.2 | Working Capital/TA | Moderate | Liquidity is important but not decisive |
| 1.4 | Retained Earnings/TA | Moderate | Accumulated profits show long-term viability |
| **3.3** | EBIT/TA | **Highest** | Operating profitability is most predictive |
| 0.6 | Market Value/TL | Lower | Market perceptions can be volatile |
| 1.0 | Sales/TA | Baseline | Asset efficiency is foundational |

### Implementation

```python
def calculate_z_score(self, df):
    """Calculate Altman Z-Score for each company."""

    z_score = (
        1.2 * df['working_capital_to_total_assets'] +
        1.4 * df['retained_earnings_to_total_assets'] +
        3.3 * df['ebit_to_total_assets'] +
        0.6 * df['market_value_equity_to_total_liabilities'] +
        1.0 * df['sales_to_total_assets']
    )

    # Classify zones
    zones = []
    for z in z_score:
        if z > 2.99:
            zones.append("Safe")
        elif z >= 1.81:
            zones.append("Grey")
        else:
            zones.append("Distress")

    return z_score, zones
```

---

# 5. Backend API

## 5.1 FastAPI Application Structure

### main.py Overview

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from app.models.schemas import (
    CompanyFinancialData,
    InsolvencyAnalysisResponse,
    InsolvencyBulkResponse,
    InsolvencyReportRequest,
)

# Initialize FastAPI app
app = FastAPI(
    title="SolvencyInsight API",
    description="AI-powered financial distress prediction",
    version="2.0.0"
)

# CORS middleware (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML models on startup
@app.on_event("startup")
async def load_models():
    global insolvency_predictor
    insolvency_predictor = InsolvencyPredictorV2()
    if not insolvency_predictor.load_model():
        # Train if no saved model exists
        df = pd.read_csv("data/training_companies_10k/_combined_training_data_10k.csv")
        insolvency_predictor.train(df)
```

## 5.2 API Endpoints

### 5.2.1 Health Check

```python
@app.get("/api/health")
async def health_check():
    """
    System health check endpoint.
    Returns model status and metrics.
    """
    return {
        "status": "healthy",
        "models_loaded": insolvency_predictor.is_fitted,
        "insolvency_model_metrics": insolvency_predictor.metrics,
    }
```

### 5.2.2 Single Company Analysis

```python
@app.post("/api/financial/analyze", response_model=InsolvencyAnalysisResponse)
async def analyze_company(data: CompanyFinancialData):
    """
    Analyze a single company from form data.

    Input: CompanyFinancialData (12 financial ratios)
    Output: InsolvencyAnalysisResponse (prediction + SHAP explanation)
    """

    # Convert to DataFrame
    df = pd.DataFrame([data.dict()])

    # Get prediction
    prediction = insolvency_predictor.predict(df)

    # Get SHAP explanation
    explanation = insolvency_predictor.explain_prediction(df, index=0)

    # Calculate Z-Score
    z_score = calculate_altman_z_score(data)
    z_zone = classify_z_score_zone(z_score)

    return InsolvencyAnalysisResponse(
        prediction=InsolvencyPrediction(
            company_id=data.company_id,
            company_name=data.company_name,
            probability_of_distress=prediction['probability_of_distress'].iloc[0],
            risk_category=prediction['risk_category'].iloc[0],
            z_score=z_score,
            z_score_zone=z_zone,
        ),
        explanation=InsolvencyExplanation(
            shap_values=explanation['shap_values'],
            top_risk_drivers=explanation['top_risk_drivers'],
            base_value=explanation['base_value'],
            prediction_value=explanation['prediction_value'],
        )
    )
```

### 5.2.3 Single Company CSV Upload

```python
@app.post("/api/financial/upload-single", response_model=InsolvencyAnalysisResponse)
async def upload_single_company(file: UploadFile = File(...)):
    """
    Upload a CSV file containing ONE company's financial data.
    Returns full analysis with SHAP explanation.

    This endpoint is used when user uploads a CSV instead of
    filling the form manually.
    """

    # Read CSV
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

    # Validate columns
    required_cols = InsolvencyPredictorV2.BASE_FEATURES
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise HTTPException(400, f"Missing columns: {missing}")

    # Take first row if multiple
    row = df.iloc[[0]]

    # Get prediction
    prediction = insolvency_predictor.predict(row)

    # Get SHAP explanation
    explanation = insolvency_predictor.explain_prediction(row, index=0)

    # Build response
    return InsolvencyAnalysisResponse(
        prediction=InsolvencyPrediction(
            company_id=row.get('company_id', ['UNKNOWN'])[0],
            company_name=row.get('company_name', ['Unknown Company'])[0],
            probability_of_distress=prediction['probability_of_distress'].iloc[0],
            risk_category=prediction['risk_category'].iloc[0],
            z_score=prediction['z_score'].iloc[0],
            z_score_zone=prediction['z_score_zone'].iloc[0],
        ),
        explanation=InsolvencyExplanation(
            shap_values=explanation['shap_values'],
            top_risk_drivers=explanation['top_risk_drivers'],
            base_value=explanation['base_value'],
            prediction_value=explanation['prediction_value'],
        )
    )
```

### 5.2.4 Bulk Upload

```python
@app.post("/api/financial/upload", response_model=InsolvencyBulkResponse)
async def upload_financial_data(file: UploadFile = File(...)):
    """
    Upload a CSV file containing MULTIPLE companies.
    Returns predictions for all companies (without individual SHAP).
    """

    # Read CSV
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

    # Validate
    if len(df) == 0:
        raise HTTPException(400, "Empty file")

    # Get predictions for all rows
    predictions = insolvency_predictor.predict(df)

    # Build response
    results = []
    for i, row in df.iterrows():
        results.append(InsolvencyPrediction(
            company_id=row.get('company_id', f'ROW_{i}'),
            company_name=row.get('company_name', f'Company {i}'),
            probability_of_distress=predictions['probability_of_distress'].iloc[i],
            risk_category=predictions['risk_category'].iloc[i],
            z_score=predictions['z_score'].iloc[i],
            z_score_zone=predictions['z_score_zone'].iloc[i],
        ))

    # Calculate summary statistics
    probs = predictions['probability_of_distress']
    summary = {
        'high_risk_count': sum(predictions['risk_category'] == 'High'),
        'medium_risk_count': sum(predictions['risk_category'] == 'Medium'),
        'low_risk_count': sum(predictions['risk_category'] == 'Low'),
        'avg_probability': float(probs.mean()),
        'max_probability': float(probs.max()),
        'min_probability': float(probs.min()),
    }

    return InsolvencyBulkResponse(
        total_companies=len(df),
        predictions=results,
        summary=summary,
    )
```

### 5.2.5 PDF Report Generation

```python
@app.post("/api/reports/insolvency")
async def generate_insolvency_report(request: InsolvencyReportRequest):
    """
    Generate a PDF report for a single company analysis.
    """

    from app.services.report_generator import generate_insolvency_pdf

    # Get prediction and explanation
    df = pd.DataFrame([request.company_data.dict()])
    prediction = insolvency_predictor.predict(df)
    explanation = insolvency_predictor.explain_prediction(df)

    # Generate PDF
    pdf_buffer = generate_insolvency_pdf(
        company_id=request.company_id,
        company_name=request.company_name,
        prediction=prediction,
        explanation=explanation,
    )

    # Return as streaming response
    return StreamingResponse(
        io.BytesIO(pdf_buffer),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report_{request.company_id}.pdf"
        }
    )
```

## 5.3 Pydantic Schemas

### schemas.py

```python
from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional

# ============================================================
# Input Schemas
# ============================================================

class CompanyFinancialData(BaseModel):
    """Input data for a single company financial analysis."""

    company_id: Optional[str] = None
    company_name: Optional[str] = None

    # Altman Z-score components
    working_capital_to_total_assets: float = Field(
        ..., description="Working Capital / Total Assets"
    )
    retained_earnings_to_total_assets: float = Field(
        ..., description="Retained Earnings / Total Assets"
    )
    ebit_to_total_assets: float = Field(
        ..., description="EBIT / Total Assets"
    )
    market_value_equity_to_total_liabilities: float = Field(
        ..., description="Market Value of Equity / Total Liabilities"
    )
    sales_to_total_assets: float = Field(
        ..., description="Sales / Total Assets"
    )

    # Additional ratios
    current_ratio: float = Field(..., description="Current Assets / Current Liabilities")
    quick_ratio: float = Field(..., description="Quick Assets / Current Liabilities")
    debt_to_equity: float = Field(..., description="Total Debt / Total Equity")
    interest_coverage: float = Field(..., description="EBIT / Interest Expense")
    net_profit_margin: float = Field(..., description="Net Income / Revenue")
    return_on_assets: float = Field(..., description="Net Income / Total Assets")
    return_on_equity: float = Field(..., description="Net Income / Shareholders Equity")

    class Config:
        json_schema_extra = {
            "example": {
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
        }

# ============================================================
# Output Schemas
# ============================================================

class InsolvencyPrediction(BaseModel):
    """Single company insolvency prediction result."""

    company_id: Optional[str] = None
    company_name: Optional[str] = None
    probability_of_distress: float = Field(..., ge=0, le=1)
    risk_category: str = Field(..., description="Low, Medium, or High")
    estimated_time_to_event: Optional[int] = Field(
        None, description="Estimated years to potential bankruptcy"
    )
    z_score: float = Field(..., description="Altman Z-Score")
    z_score_zone: str = Field(..., description="Safe, Grey, or Distress")


class InsolvencyExplanation(BaseModel):
    """SHAP-based explanation for insolvency prediction."""

    shap_values: Dict[str, float]
    top_risk_drivers: List[Dict[str, Any]]
    base_value: float
    prediction_value: float


class InsolvencyAnalysisResponse(BaseModel):
    """Complete response for single company analysis."""

    prediction: InsolvencyPrediction
    explanation: InsolvencyExplanation


class InsolvencyBulkResponse(BaseModel):
    """Response for bulk company analysis."""

    total_companies: int
    predictions: List[InsolvencyPrediction]
    summary: Dict[str, Any]
```

---

# 6. Frontend Application

## 6.1 Technology Stack

| Technology | Purpose |
|------------|---------|
| **React 18** | Component-based UI framework |
| **TypeScript** | Static typing for reliability |
| **TailwindCSS** | Utility-first CSS styling |
| **Recharts** | React charting library for SHAP visualization |
| **Vite** | Fast build tool with HMR |
| **Axios** | HTTP client for API calls |
| **Lucide React** | Icon library |

## 6.2 Component Architecture

```
src/
├── components/           # Reusable UI components
│   ├── DataTable.tsx     # Sortable, searchable table
│   ├── FileUpload.tsx    # Drag-and-drop CSV upload
│   ├── LoadingSpinner.tsx # Loading indicator
│   ├── RiskGauge.tsx     # Circular risk visualization
│   └── index.ts          # Barrel exports
│
├── pages/                # Page-level components
│   ├── Dashboard.tsx     # Main dashboard
│   ├── InsolvencyAnalysis.tsx  # Main analysis page
│   └── EmployeeAnalysis.tsx
│
├── services/
│   └── api.ts            # Axios API client
│
├── context/
│   └── ToastContext.tsx  # Notification system
│
├── types/
│   └── index.ts          # TypeScript interfaces
│
├── App.tsx               # Root component with routing
└── main.tsx              # Entry point
```

## 6.3 Key Components

### 6.3.1 InsolvencyAnalysis.tsx

This is the main page component handling both single company and bulk analysis.

```typescript
/**
 * InsolvencyAnalysis component for analyzing company bankruptcy risk.
 * Supports single company form input and bulk CSV upload.
 * Uses Altman Z-Score and XGBoost ML model for predictions with SHAP explanations.
 */
export default function InsolvencyAnalysis() {
  // State management
  const [mode, setMode] = useState<'single' | 'bulk'>('single');
  const [formData, setFormData] = useState<CompanyFinancialData>(defaultFormData);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [singleResult, setSingleResult] = useState<InsolvencyAnalysisResponse | null>(null);
  const [bulkResult, setBulkResult] = useState<InsolvencyBulkResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handle single company analysis.
   * If a file is selected, upload it. Otherwise, use form data.
   */
  const handleSingleAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      let result: InsolvencyAnalysisResponse;

      if (selectedFile) {
        // Use CSV upload endpoint (returns full SHAP analysis)
        result = await uploadSingleCompany(selectedFile);

        // Update form with company info from CSV
        setFormData(prev => ({
          ...prev,
          company_id: result.prediction.company_id,
          company_name: result.prediction.company_name,
        }));
      } else {
        // Use manual form data endpoint
        result = await analyzeCompany(formData);
      }

      setSingleResult(result);
      toast.success('Analysis Complete',
        `Risk: ${result.prediction.risk_category} (Z-Score: ${result.prediction.z_score.toFixed(2)})`
      );
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
      toast.error('Analysis Failed', err.message);
    } finally {
      setLoading(false);
    }
  };

  // ... render method with conditional display based on mode and results
}
```

### 6.3.2 RiskGauge.tsx

A circular gauge visualization showing the probability of distress.

```typescript
interface RiskGaugeProps {
  value: number;          // 0-1 probability
  label: string;
  size?: 'sm' | 'md' | 'lg';
  riskCategory: 'Low' | 'Medium' | 'High';
}

export function RiskGauge({ value, label, size = 'md', riskCategory }: RiskGaugeProps) {
  // Calculate gauge parameters
  const percentage = value * 100;
  const rotation = (value * 180) - 90;  // -90 to 90 degrees

  // Color based on risk category
  const colors = {
    Low: 'text-green-500',
    Medium: 'text-yellow-500',
    High: 'text-red-500',
  };

  return (
    <div className="flex flex-col items-center">
      {/* SVG gauge arc */}
      <svg viewBox="0 0 100 60" className={sizeClasses[size]}>
        {/* Background arc */}
        <path d="M 10 50 A 40 40 0 0 1 90 50"
              fill="none" stroke="#374151" strokeWidth="8" />

        {/* Colored arc based on value */}
        <path d="M 10 50 A 40 40 0 0 1 90 50"
              fill="none"
              stroke={gradientColors[riskCategory]}
              strokeWidth="8"
              strokeDasharray={`${value * 126} 126`} />

        {/* Needle indicator */}
        <line x1="50" y1="50" x2="50" y2="15"
              transform={`rotate(${rotation} 50 50)`}
              stroke="white" strokeWidth="2" />
      </svg>

      {/* Value display */}
      <div className={`text-2xl font-bold ${colors[riskCategory]}`}>
        {percentage.toFixed(1)}%
      </div>
      <div className="text-gray-400 text-sm">{label}</div>
    </div>
  );
}
```

### 6.3.3 FileUpload.tsx

Drag-and-drop CSV upload component with validation.

```typescript
interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
  disabled?: boolean;
  accept?: string;
}

export function FileUpload({
  onFileSelect,
  selectedFile,
  onClear,
  disabled,
  accept = '.csv'
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) {
      onFileSelect(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`
        border-2 border-dashed rounded-xl p-6 text-center
        transition-colors cursor-pointer
        ${isDragging ? 'border-primary-500 bg-primary-500/10' : 'border-dark-600'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary-400'}
      `}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleFileChange}
        className="hidden"
        disabled={disabled}
      />

      {selectedFile ? (
        <div className="flex items-center justify-center gap-3">
          <FileText className="w-8 h-8 text-primary-400" />
          <div>
            <p className="text-white font-medium">{selectedFile.name}</p>
            <p className="text-dark-400 text-sm">
              {(selectedFile.size / 1024).toFixed(1)} KB
            </p>
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); onClear(); }}
            className="ml-4 text-dark-400 hover:text-red-400"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      ) : (
        <>
          <Upload className="w-10 h-10 text-dark-500 mx-auto mb-3" />
          <p className="text-white font-medium">
            Drop CSV file here or click to browse
          </p>
          <p className="text-dark-500 text-sm mt-1">
            Supports .csv files up to 10MB
          </p>
        </>
      )}
    </div>
  );
}
```

### 6.3.4 SHAP Chart (in InsolvencyAnalysis.tsx)

Horizontal bar chart showing top 10 risk drivers:

```typescript
// Prepare SHAP chart data
const shapChartData = singleResult
  ? singleResult.explanation.top_risk_drivers.slice(0, 10).map((item) => ({
      name: formatFeatureName(item.feature),
      value: item.shap_value,
      originalValue: item.original_value,
      impact: item.impact,
      fullName: item.feature,
    }))
  : [];

// Render chart
<ResponsiveContainer width="100%" height={400}>
  <BarChart
    data={shapChartData}
    layout="vertical"
    margin={{ top: 5, right: 30, left: 150, bottom: 5 }}
  >
    <XAxis type="number" />
    <YAxis type="category" dataKey="name" width={140} />
    <Tooltip content={<ShapTooltip />} />
    <ReferenceLine x={0} stroke="#475569" />
    <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={24}>
      {shapChartData.map((entry, index) => (
        <Cell
          key={`cell-${index}`}
          fill={entry.value >= 0 ? '#ef4444' : '#22c55e'}  // Red = risk, Green = safe
        />
      ))}
    </Bar>
  </BarChart>
</ResponsiveContainer>
```

## 6.4 API Service Layer (api.ts)

```typescript
import axios from 'axios';
import type {
  CompanyFinancialData,
  InsolvencyAnalysisResponse,
  InsolvencyBulkResponse
} from '../types';

// Base URL - empty string uses Vite proxy in development
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

/**
 * Analyze a single company using form data.
 */
export const analyzeCompany = async (
  data: CompanyFinancialData
): Promise<InsolvencyAnalysisResponse> => {
  const response = await api.post<InsolvencyAnalysisResponse>(
    '/api/financial/analyze',
    data
  );
  return response.data;
};

/**
 * Upload a single company CSV file for analysis.
 * Returns full response with SHAP explanation.
 */
export const uploadSingleCompany = async (
  file: File
): Promise<InsolvencyAnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<InsolvencyAnalysisResponse>(
    '/api/financial/upload-single',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return response.data;
};

/**
 * Upload bulk CSV for multiple companies.
 */
export const uploadFinancialData = async (
  file: File
): Promise<InsolvencyBulkResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<InsolvencyBulkResponse>(
    '/api/financial/upload',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return response.data;
};

/**
 * Generate PDF report for a company.
 */
export const generateInsolvencyReport = async (
  companyId: string,
  companyName: string,
  companyData: CompanyFinancialData
): Promise<Blob> => {
  const response = await api.post(
    '/api/reports/insolvency',
    { company_id: companyId, company_name: companyName, company_data: companyData },
    { responseType: 'blob' }
  );
  return response.data;
};

/**
 * Helper to download blob as file.
 */
export const downloadBlob = (blob: Blob, filename: string): void => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
};
```

## 6.5 Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward API requests to backend
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
});
```

---

# 7. Model Comparison Analysis

## 7.1 Models Compared

| Model | Type | Description |
|-------|------|-------------|
| **XGBoost V2** | Gradient Boosting | Sequential ensemble with feature engineering |
| **Random Forest** | Bagging Ensemble | Parallel ensemble of decision trees |
| **Logistic Regression** | Linear Model | Weighted sum with sigmoid activation |

## 7.2 Performance Results

### Test Set Performance (2,000 samples)

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| **XGBoost V2** | **91.15%** | 93.01% | **87.77%** | **90.31%** | **97.97%** |
| Random Forest | 90.55% | **93.51%** | 85.85% | 89.52% | 97.60% |
| Logistic Regression | 90.15% | 91.42% | 87.23% | 89.28% | 97.30% |

### Cross-Validation Results (5-Fold)

| Model | CV Mean | CV Std | 95% CI |
|-------|---------|--------|--------|
| **XGBoost V2** | **98.14%** | 0.17% | [97.80%, 98.48%] |
| Random Forest | 97.61% | 0.28% | [97.06%, 98.17%] |
| Logistic Regression | 97.32% | 0.27% | [96.79%, 97.85%] |

## 7.3 Confusion Matrix Analysis

### XGBoost V2
```
                 Predicted
              Healthy  Distressed
Actual  Healthy   998       62
        Distressed 115      825

Specificity: 94.15%
Sensitivity: 87.77%
```

### Interpretation
- **True Negatives (998)**: Healthy companies correctly identified as healthy
- **True Positives (825)**: Distressed companies correctly identified as distressed
- **False Positives (62)**: Healthy companies incorrectly flagged (Type I error)
- **False Negatives (115)**: Distressed companies missed (Type II error - more costly)

## 7.4 Why XGBoost V2 is Best

### Advantage 1: Highest ROC-AUC (97.97%)

ROC-AUC measures the model's ability to distinguish between classes across ALL thresholds. XGBoost achieves the highest, meaning it best separates healthy from distressed companies.

### Advantage 2: Feature Engineering + Gradient Boosting

- **41 engineered features** capture complex relationships
- **Composite scores** (financial_distress_score) combine multiple indicators
- **Interaction terms** capture non-additive effects
- **Sequential boosting** learns from errors of previous trees

### Advantage 3: Built-in Regularization

```python
reg_alpha=0.5   # L1 regularization (Lasso) - sparse features
reg_lambda=2.0  # L2 regularization (Ridge) - small weights
gamma=0.1       # Minimum loss reduction for splits
```

This prevents overfitting on the 10,000 sample dataset.

### Advantage 4: Non-linear Pattern Capture

Financial distress follows non-linear patterns:
- A company with `debt_to_equity = 1.5` may be fine
- A company with `debt_to_equity = 3.0` is in danger
- A company with `debt_to_equity = 5.0` is in severe danger

XGBoost's decision trees capture these thresholds naturally.

### Advantage 5: SHAP Explainability

TreeExplainer provides:
- Fast computation (polynomial time)
- Accurate attributions
- Consistent explanations
- Audit-ready output for financial regulators

## 7.5 Model Comparison Charts

The comparison generates 6 charts:

1. **model_comparison_metrics.png**: Bar chart of all metrics + radar chart
2. **model_comparison_roc_pr.png**: ROC curves and Precision-Recall curves
3. **model_comparison_confusion.png**: Side-by-side confusion matrices
4. **model_comparison_features.png**: Feature importance for XGBoost and RF
5. **model_comparison_calibration.png**: Probability calibration curves
6. **model_comparison_cv.png**: Cross-validation score distributions

---

# 8. Feature Engineering Deep Dive

## 8.1 Overview

Feature engineering transforms **12 base features** into **41 total features** by creating derived metrics, indicators, and interaction terms.

## 8.2 Engineered Features

### 8.2.1 Altman Z-Score and Zone Indicators

```python
# Altman Z-Score (continuous)
X['altman_z_score'] = (
    1.2 * X['working_capital_to_total_assets'] +
    1.4 * X['retained_earnings_to_total_assets'] +
    3.3 * X['ebit_to_total_assets'] +
    0.6 * X['market_value_equity_to_total_liabilities'] +
    1.0 * X['sales_to_total_assets']
)

# Zone indicators (binary)
X['z_score_safe'] = (X['altman_z_score'] > 2.99).astype(float)      # 1 if safe
X['z_score_grey'] = ((X['altman_z_score'] >= 1.81) &
                     (X['altman_z_score'] <= 2.99)).astype(float)   # 1 if grey
X['z_score_distress'] = (X['altman_z_score'] < 1.81).astype(float)  # 1 if distress
```

### 8.2.2 Liquidity Stress Indicators

```python
# Liquidity gap (inventory dependence)
X['liquidity_gap'] = X['current_ratio'] - X['quick_ratio']

# Stress flags
X['severe_liquidity_stress'] = (X['current_ratio'] < 1.0).astype(float)
X['moderate_liquidity_stress'] = ((X['current_ratio'] >= 1.0) &
                                   (X['current_ratio'] < 1.5)).astype(float)
```

**Why These Matter:**
- `liquidity_gap`: Large gap means company relies heavily on inventory (risky if inventory can't be sold)
- `severe_liquidity_stress`: Current ratio < 1.0 means company can't pay short-term obligations

### 8.2.3 Leverage Risk Indicators

```python
X['high_leverage'] = (X['debt_to_equity'] > 2.0).astype(float)
X['extreme_leverage'] = (X['debt_to_equity'] > 4.0).astype(float)
X['leverage_coverage_ratio'] = X['interest_coverage'] / (X['debt_to_equity'] + 0.1)
```

**Why These Matter:**
- High leverage amplifies risk during downturns
- `leverage_coverage_ratio`: Combines two key metrics into one signal

### 8.2.4 Profitability Indicators

```python
# Negative profit flags
X['negative_profit'] = (X['net_profit_margin'] < 0).astype(float)
X['negative_roa'] = (X['return_on_assets'] < 0).astype(float)
X['negative_roe'] = (X['return_on_equity'] < 0).astype(float)

# Aggregate profitability score
X['profitability_score'] = (
    X['net_profit_margin'] + X['return_on_assets'] + X['return_on_equity']
) / 3
```

**Why These Matter:**
- Negative profits indicate operational problems
- `profitability_score`: Single metric capturing overall profitability health

### 8.2.5 Working Capital Health

```python
X['negative_working_capital'] = (X['working_capital_to_total_assets'] < 0).astype(float)
X['working_capital_trend'] = X['working_capital_to_total_assets'] * X['sales_to_total_assets']
```

### 8.2.6 Asset Efficiency

```python
X['asset_utilization'] = X['sales_to_total_assets'] * X['ebit_to_total_assets']
X['capital_efficiency'] = X['return_on_assets'] / (X['debt_to_equity'] + 0.5)
```

### 8.2.7 Interest Coverage Indicators

```python
X['interest_coverage_safe'] = (X['interest_coverage'] > 3.0).astype(float)
X['interest_coverage_danger'] = (X['interest_coverage'] < 1.5).astype(float)
```

### 8.2.8 Interaction Features

```python
# Leverage × Liquidity (dangerous combination)
X['leverage_liquidity_interaction'] = X['debt_to_equity'] * (1 / (X['current_ratio'] + 0.1))

# Profit × Leverage (profit cushion against debt)
X['profit_leverage_interaction'] = X['net_profit_margin'] * (1 / (X['debt_to_equity'] + 0.1))

# Z-Score adjusted for leverage
X['z_score_leverage_interaction'] = X['altman_z_score'] / (X['debt_to_equity'] + 0.5)
```

**Why Interactions Matter:**
- A company with high leverage AND low liquidity is in worse shape than either alone
- Interactions capture non-additive effects that linear models miss

### 8.2.9 Composite Risk Scores

```python
# Financial Distress Score (0-5, higher = worse)
X['financial_distress_score'] = (
    X['negative_working_capital'] +
    X['severe_liquidity_stress'] +
    X['high_leverage'] +
    X['negative_profit'] +
    X['interest_coverage_danger']
)

# Financial Health Score (0-5, higher = better)
X['financial_health_score'] = (
    X['z_score_safe'] +
    X['interest_coverage_safe'] +
    (X['current_ratio'] > 2.0).astype(float) +
    (X['debt_to_equity'] < 1.0).astype(float) +
    (X['net_profit_margin'] > 0.05).astype(float)
)
```

**Why These Matter:**
- `financial_distress_score` is the **#1 most important feature** (40.3% importance)
- Combines 5 key warning signs into single metric
- Easy to interpret: 0 = no red flags, 5 = severe distress

### 8.2.10 Retained Earnings and Market Value Indicators

```python
X['negative_retained_earnings'] = (X['retained_earnings_to_total_assets'] < 0).astype(float)
X['strong_retained_earnings'] = (X['retained_earnings_to_total_assets'] > 0.3).astype(float)

X['low_market_value'] = (X['market_value_equity_to_total_liabilities'] < 1.0).astype(float)
X['strong_market_value'] = (X['market_value_equity_to_total_liabilities'] > 2.0).astype(float)
```

## 8.3 Feature Importance Rankings

Based on XGBoost's feature importance:

| Rank | Feature | Importance | Description |
|------|---------|------------|-------------|
| 1 | `financial_distress_score` | 40.29% | Composite of 5 warning signs |
| 2 | `profitability_score` | 13.79% | Average of profit margins |
| 3 | `z_score_leverage_interaction` | 5.89% | Z-Score adjusted for debt |
| 4 | `z_score_grey` | 4.55% | In grey zone indicator |
| 5 | `negative_retained_earnings` | 2.65% | Accumulated losses flag |
| 6 | `financial_health_score` | 2.55% | Composite of 5 health indicators |
| 7 | `retained_earnings_to_total_assets` | 2.40% | Original Altman component |
| 8 | `interest_coverage_safe` | 2.12% | Coverage > 3x indicator |
| 9 | `altman_z_score` | 1.81% | Continuous Z-Score |
| 10 | `interest_coverage_danger` | 1.54% | Coverage < 1.5x indicator |

---

# 9. API Reference

## 9.1 Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | System health check |
| POST | `/api/financial/analyze` | Single company analysis (form data) |
| POST | `/api/financial/upload-single` | Single company analysis (CSV upload) |
| POST | `/api/financial/upload` | Bulk analysis (multiple companies) |
| GET | `/api/financial/feature-importance` | Get model feature weights |
| POST | `/api/reports/insolvency` | Generate PDF report |

## 9.2 Request/Response Examples

### POST /api/financial/analyze

**Request:**
```json
{
  "company_id": "COMP_001",
  "company_name": "Acme Corporation",
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

**Response:**
```json
{
  "prediction": {
    "company_id": "COMP_001",
    "company_name": "Acme Corporation",
    "probability_of_distress": 0.0523,
    "risk_category": "Low",
    "estimated_time_to_event": null,
    "z_score": 4.23,
    "z_score_zone": "Safe"
  },
  "explanation": {
    "shap_values": {
      "financial_distress_score": -0.1523,
      "profitability_score": -0.0892,
      "z_score_safe": -0.0654,
      "current_ratio": -0.0421,
      ...
    },
    "top_risk_drivers": [
      {
        "feature": "financial_distress_score",
        "shap_value": -0.1523,
        "original_value": 0.0,
        "impact": "decreases_risk"
      },
      {
        "feature": "profitability_score",
        "shap_value": -0.0892,
        "original_value": 0.11,
        "impact": "decreases_risk"
      }
    ],
    "base_value": 0.47,
    "prediction_value": 0.0523
  }
}
```

### POST /api/financial/upload (Bulk)

**Request:** Multipart form data with CSV file

**Response:**
```json
{
  "total_companies": 50,
  "predictions": [
    {
      "company_id": "COMP_001",
      "company_name": "Company A",
      "probability_of_distress": 0.12,
      "risk_category": "Low",
      "z_score": 3.45,
      "z_score_zone": "Safe"
    },
    {
      "company_id": "COMP_002",
      "company_name": "Company B",
      "probability_of_distress": 0.78,
      "risk_category": "High",
      "z_score": 1.23,
      "z_score_zone": "Distress"
    }
  ],
  "summary": {
    "high_risk_count": 12,
    "medium_risk_count": 18,
    "low_risk_count": 20,
    "avg_probability": 0.42,
    "max_probability": 0.95,
    "min_probability": 0.03
  }
}
```

---

# 10. Deployment Guide

## 10.1 Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- pip and npm

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## 10.2 Production Deployment

### Docker Compose (Recommended)

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8001:8001"
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./ml_models:/app/ml_models
      - ./data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://backend:8001
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | production/development | development |
| `VITE_API_URL` | Backend API URL | (empty for proxy) |
| `MODEL_PATH` | Path to saved models | ml_models/saved_models |

---

# 11. Team Contributions

## Rohan & Jonathan: Machine Learning Module & Backend

### Responsibilities:
- XGBoost model architecture and hyperparameter tuning
- Feature engineering (41 derived features)
- SHAP explainability integration
- Altman Z-Score calculation
- FastAPI backend development
- Pydantic schema validation
- Model training and evaluation pipeline

### Key Files:
- `ml_models/insolvency_predictor_v2.py`
- `backend/app/main.py`
- `backend/app/models/schemas.py`
- `train_model_v2.py`
- `model_comparison_v2.py`

## Neha: Data Preparation & Frontend

### Responsibilities:
- Dataset generation (10,000 companies)
- Industry-specific financial characteristics
- Economic cycle simulation
- CSV parsing and validation
- API service layer (api.ts)
- FileUpload component
- DataTable component

### Key Files:
- `generate_large_dataset.py`
- `data/training_companies_10k/`
- `frontend/src/services/api.ts`
- `frontend/src/components/FileUpload.tsx`
- `frontend/src/components/DataTable.tsx`

## Mariya: Frontend Development & UI/UX

### Responsibilities:
- React page components
- InsolvencyAnalysis page
- SHAP visualization (Recharts)
- RiskGauge component
- TailwindCSS styling
- Responsive design
- Toast notification system

### Key Files:
- `frontend/src/pages/InsolvencyAnalysis.tsx`
- `frontend/src/components/RiskGauge.tsx`
- `frontend/src/context/ToastContext.tsx`
- `frontend/tailwind.config.js`

## All Team Members: Integration & Testing

### Joint Responsibilities:
- Frontend-backend integration
- Vite proxy configuration
- End-to-end testing
- Error handling
- Performance optimization
- Documentation

---

# Appendix A: Glossary

| Term | Definition |
|------|------------|
| **ROC-AUC** | Receiver Operating Characteristic - Area Under Curve; measures classifier's ability to distinguish classes |
| **SHAP** | SHapley Additive exPlanations; game-theoretic approach to explain ML predictions |
| **XGBoost** | Extreme Gradient Boosting; ensemble learning algorithm using decision trees |
| **Altman Z-Score** | Bankruptcy prediction formula developed by Edward Altman in 1968 |
| **Regularization** | Technique to prevent overfitting by penalizing model complexity |
| **Feature Engineering** | Creating new features from existing data to improve model performance |
| **Cross-Validation** | Technique to assess model generalization by training on different data subsets |

---

# Appendix B: References

1. Altman, E. I. (1968). "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy"
2. Chen, T., & Guestrin, C. (2016). "XGBoost: A Scalable Tree Boosting System"
3. Lundberg, S. M., & Lee, S. I. (2017). "A Unified Approach to Interpreting Model Predictions" (SHAP)
4. FastAPI Documentation: https://fastapi.tiangolo.com
5. XGBoost Documentation: https://xgboost.readthedocs.io
6. SHAP Documentation: https://shap.readthedocs.io

---

**Document Version:** 2.0
**Last Updated:** 2024
**Total Pages:** ~60
