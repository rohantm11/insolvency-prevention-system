# SolvencyInsight - Project Documentation

## Team Members & Contributions

| Team Member | Primary Contributions |
|-------------|----------------------|
| **Rohan** | ML Module & Backend Development |
| **Jonathan** | ML Module & Backend Development |
| **Neha** | Data Preparation & Frontend Development |
| **Mariya** | Frontend Development |
| **All Members** | System Integration & Testing |

---

# Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Data Preparation (Neha)](#3-data-preparation-neha)
4. [Machine Learning Module (Rohan & Jonathan)](#4-machine-learning-module-rohan--jonathan)
5. [Backend Development (Rohan & Jonathan)](#5-backend-development-rohan--jonathan)
6. [Frontend Development (Neha & Mariya)](#6-frontend-development-neha--mariya)
7. [System Integration (All Team Members)](#7-system-integration-all-team-members)
8. [Model Performance Metrics](#8-model-performance-metrics)
9. [API Endpoints Reference](#9-api-endpoints-reference)
10. [How to Run the Project](#10-how-to-run-the-project)

---

# 1. Project Overview

## What is SolvencyInsight?

**SolvencyInsight** is an AI-powered financial risk analysis platform that helps businesses predict:
1. **Company Insolvency Risk** - Will a company go bankrupt?
2. **Employee Attrition Risk** - Which employees are likely to leave?
3. **Layoff Optimization** - If layoffs are needed, who should be let go to minimize impact?

## Why This Project?

- **Problem**: Companies often fail to detect financial distress early enough to take corrective action
- **Solution**: Use machine learning to analyze financial ratios and predict bankruptcy risk before it's too late
- **Bonus**: Also helps HR departments identify flight-risk employees and make data-driven layoff decisions

## Key Features

| Feature | Description |
|---------|-------------|
| Insolvency Prediction | Predicts bankruptcy probability using 12 financial ratios |
| Altman Z-Score | Calculates traditional Z-Score for validation |
| SHAP Explanations | Shows WHY a company is at risk (explainable AI) |
| Employee Scoring | Predicts which employees might leave |
| Layoff Simulation | Recommends optimal layoffs to meet budget cuts |
| PDF Reports | Generates professional risk assessment reports |
| Market Intelligence | Fetches real-time news and sector data |

## Technology Stack

```
Frontend:  React + TypeScript + Vite + TailwindCSS
Backend:   Python + FastAPI + Uvicorn
ML:        XGBoost + SHAP + Scikit-learn + Pandas
Database:  File-based (CSV) - No external DB required
```

---

# 2. System Architecture

## High-Level Architecture

```
+-------------------+     HTTP/REST     +-------------------+
|                   | <---------------> |                   |
|    FRONTEND       |                   |     BACKEND       |
|    (React)        |                   |    (FastAPI)      |
|                   |                   |                   |
|  - Dashboard      |                   |  - API Endpoints  |
|  - Analysis Pages |                   |  - Data Validation|
|  - File Upload    |                   |  - PDF Generation |
|  - Charts/Graphs  |                   |                   |
+-------------------+                   +--------+----------+
                                                 |
                                                 v
                                        +--------+----------+
                                        |                   |
                                        |    ML MODELS      |
                                        |   (XGBoost)       |
                                        |                   |
                                        |  - Insolvency     |
                                        |  - Employee       |
                                        |  - SHAP Explainer |
                                        +-------------------+
```

## Project File Structure

```
insolvency-prevention-system/
|
+-- backend/                    # Backend API (Rohan & Jonathan)
|   +-- app/
|       +-- main.py             # FastAPI application & all endpoints
|       +-- config.py           # Configuration settings
|       +-- models/
|       |   +-- schemas.py      # Pydantic data models
|       +-- services/
|           +-- pdf_generator.py        # PDF report generation
|           +-- market_intelligence.py  # News & sector data
|           +-- enhanced_prediction.py  # Combined predictions
|
+-- ml_models/                  # Machine Learning (Rohan & Jonathan)
|   +-- insolvency_predictor.py # Company bankruptcy prediction
|   +-- employee_scorer.py      # Employee attrition prediction
|   +-- trained_models/         # Saved model files (.pkl)
|
+-- frontend/                   # Frontend UI (Neha & Mariya)
|   +-- src/
|       +-- pages/
|       |   +-- Dashboard.tsx           # Main dashboard
|       |   +-- InsolvencyAnalysis.tsx  # Company analysis
|       |   +-- EmployeeScoring.tsx     # Employee analysis
|       |   +-- LayoffSimulation.tsx    # Layoff planning
|       |   +-- Reports.tsx             # Report generation
|       +-- components/
|       |   +-- FileUpload.tsx          # CSV upload component
|       |   +-- RiskGauge.tsx           # Risk visualization
|       |   +-- DataTable.tsx           # Data display tables
|       |   +-- Layout.tsx              # Page layout
|       +-- services/
|           +-- api.ts                  # API client functions
|
+-- data/                       # Training Data (Neha)
|   +-- company_data.csv        # 100 companies for training
|   +-- employee_data.csv       # 500 employees for training
|   +-- generate_dummy_data.py  # Data generation script
|
+-- test_data/                  # Test Data (Neha)
|   +-- companies/              # 20 test company folders
|       +-- 01_Pioneer_Group_SAFE/
|       +-- 11_Dynasty_Alliance_AT_RISK/
|       +-- ... (20 total)
|
+-- scripts/                    # Utility Scripts
    +-- train_models.py         # Model training script
    +-- generate_test_companies.py  # Test data generator
```

---

# 3. Data Preparation (Neha)

## Overview

Neha was responsible for creating realistic financial datasets for training and testing the ML models.

## Training Data Statistics

| Dataset | Records | Purpose |
|---------|---------|---------|
| Company Data | 100 companies | Train insolvency model |
| Employee Data | 500 employees | Train attrition model |
| Test Companies | 20 folders | Validate predictions |
| Test Employees | 5,780 employees | Validate scoring |

## Company Financial Data

### File: `data/company_data.csv`

This file contains financial ratios for 100 companies, with 20 bankrupt and 80 healthy.

**Columns Explained:**

| Column | Description | Example Value |
|--------|-------------|---------------|
| `company_id` | Unique identifier | COMP_0001 |
| `company_name` | Company name | Pioneer Group |
| `industry` | Business sector | Technology, Healthcare, Retail |
| `working_capital_to_total_assets` | (Current Assets - Current Liabilities) / Total Assets | 0.15 |
| `retained_earnings_to_total_assets` | Accumulated Profits / Total Assets | 0.25 |
| `ebit_to_total_assets` | Earnings Before Interest & Tax / Total Assets | 0.08 |
| `market_value_equity_to_total_liabilities` | Market Cap / Total Debt | 2.5 |
| `sales_to_total_assets` | Revenue / Total Assets | 1.2 |
| `current_ratio` | Current Assets / Current Liabilities | 1.8 |
| `quick_ratio` | (Current Assets - Inventory) / Current Liabilities | 1.2 |
| `debt_to_equity` | Total Debt / Shareholder Equity | 0.8 |
| `interest_coverage` | EBIT / Interest Expense | 5.0 |
| `net_profit_margin` | Net Income / Revenue | 0.05 |
| `return_on_assets` | Net Income / Total Assets | 0.06 |
| `return_on_equity` | Net Income / Shareholder Equity | 0.12 |
| `is_bankrupt` | Target variable (0 = healthy, 1 = bankrupt) | 0 or 1 |

### Code: Data Generation Script

**File: `data/generate_dummy_data.py`**

```python
# Simplified explanation of data generation logic

# For HEALTHY companies (is_bankrupt = 0):
# - Higher positive ratios
# - Current ratio > 1.5 (can pay short-term debts)
# - Low debt-to-equity (not over-leveraged)
# - Positive profit margins

healthy_company = {
    'working_capital_to_total_assets': random.uniform(0.1, 0.3),    # Positive
    'retained_earnings_to_total_assets': random.uniform(0.2, 0.5),  # Strong profits
    'current_ratio': random.uniform(1.5, 3.5),                      # Good liquidity
    'debt_to_equity': random.uniform(0.3, 1.5),                     # Manageable debt
    'net_profit_margin': random.uniform(0.05, 0.25),                # Profitable
}

# For BANKRUPT companies (is_bankrupt = 1):
# - Negative or very low ratios
# - Current ratio < 1 (liquidity crisis)
# - High debt-to-equity (over-leveraged)
# - Negative profit margins (losing money)

bankrupt_company = {
    'working_capital_to_total_assets': random.uniform(-0.2, 0.05),  # Negative/low
    'retained_earnings_to_total_assets': random.uniform(-0.3, 0.1), # Losses
    'current_ratio': random.uniform(0.5, 1.2),                      # Poor liquidity
    'debt_to_equity': random.uniform(2.0, 8.0),                     # High debt
    'net_profit_margin': random.uniform(-0.15, 0.02),               # Losing money
}
```

## Employee Data

### File: `data/employee_data.csv`

Contains 500 employee records with demographics and job details.

**Key Columns:**

| Column | Description | Values |
|--------|-------------|--------|
| `employee_id` | Unique ID | EMP_0001 |
| `age` | Employee age | 22-60 |
| `department` | Work department | Sales, Engineering, HR, etc. |
| `monthly_income` | Salary | 3000-20000 |
| `years_at_company` | Tenure | 0-30 |
| `job_satisfaction` | 1-4 scale | 1=Low, 4=High |
| `work_life_balance` | 1-4 scale | 1=Poor, 4=Excellent |
| `overtime` | Works overtime? | Yes/No |
| `distance_from_home` | Commute distance | 1-30 km |
| `attrition` | Left company? | Yes/No |

### Test Data Generation

**File: `scripts/generate_test_companies.py`**

Creates 20 realistic test companies (10 safe, 10 at-risk) with:
- Industry-specific financial ratios
- 200-400 employees per company
- Correlated employee data (unhappy employees in struggling companies)

```python
# Test company generation logic

INDUSTRIES = {
    'Technology': {
        'safe_ratios': {'net_profit_margin': (0.08, 0.15), ...},
        'risk_ratios': {'net_profit_margin': (-0.10, 0.02), ...},
        'departments': ['Engineering', 'Product', 'Sales', 'Marketing'],
    },
    'Retail': {
        'safe_ratios': {'current_ratio': (1.5, 2.5), ...},
        'risk_ratios': {'current_ratio': (0.6, 1.0), ...},
        'departments': ['Store Operations', 'Logistics', 'Buying'],
    },
    # ... more industries
}
```

---

# 4. Machine Learning Module (Rohan & Jonathan)

## Overview

Rohan and Jonathan built two XGBoost classification models:
1. **Insolvency Predictor** - Predicts company bankruptcy risk
2. **Employee Scorer** - Predicts employee attrition risk

## 4.1 Insolvency Predictor

### File: `ml_models/insolvency_predictor.py`

### What It Does

Takes 12 financial ratios as input and outputs:
- **Probability of Distress** (0-100%)
- **Risk Category** (Low / Medium / High)
- **Altman Z-Score** (traditional bankruptcy indicator)
- **SHAP Explanation** (why this prediction was made)

### The Algorithm: XGBoost

**Why XGBoost?**
- Best for tabular/structured data (like financial ratios)
- Handles missing values automatically
- Fast training and prediction
- Provides feature importance

**Model Configuration:**

```python
self.model = xgb.XGBClassifier(
    n_estimators=50,        # Number of decision trees
    max_depth=3,            # Tree depth (prevents overfitting)
    learning_rate=0.05,     # How fast model learns
    reg_alpha=0.5,          # L1 regularization
    reg_lambda=1.0,         # L2 regularization
    min_child_weight=3,     # Minimum samples per leaf
    subsample=0.8,          # Use 80% of data per tree
    colsample_bytree=0.8,   # Use 80% of features per tree
)
```

### Key Functions Explained

#### 1. `train()` - Training the Model

```python
def train(self, df, target_col='is_bankrupt', test_size=0.2):
    """
    Train the model on company financial data.

    Steps:
    1. Extract feature columns (12 financial ratios)
    2. Split data: 80% training, 20% testing
    3. Handle class imbalance (more healthy than bankrupt)
    4. Train XGBoost classifier
    5. Create SHAP explainer for interpretability
    6. Calculate performance metrics
    """

    # Features used for prediction
    X = df[['working_capital_to_total_assets',
            'retained_earnings_to_total_assets',
            'ebit_to_total_assets',
            # ... 9 more features
           ]]

    # Target: 0 = healthy, 1 = bankrupt
    y = df['is_bankrupt']

    # Split into train/test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y
    )

    # Train the model
    self.model.fit(X_train, y_train)

    # Create SHAP explainer
    self.explainer = shap.TreeExplainer(self.model)
```

#### 2. `predict()` - Making Predictions

```python
def predict(self, df):
    """
    Predict bankruptcy risk for companies.

    Returns DataFrame with:
    - probability_of_distress: 0.0 to 1.0
    - risk_category: 'Low', 'Medium', or 'High'
    - estimated_time_to_event: Years until potential bankruptcy
    """

    # Get raw probabilities from model
    raw_probs = self.model.predict_proba(X)[:, 1]

    # Smooth probabilities (avoid 0% and 100%)
    # Maps to range [2%, 98%] for more realistic predictions
    probabilities = 0.02 + 0.96 * raw_probs

    # Categorize risk
    for prob in probabilities:
        if prob < 0.3:
            category = "Low"      # < 30% = Low risk
        elif prob < 0.7:
            category = "Medium"   # 30-70% = Medium risk
        else:
            category = "High"     # > 70% = High risk
```

#### 3. `calculate_altman_zscore()` - Traditional Z-Score

The **Altman Z-Score** is a famous formula from 1968 that predicts bankruptcy:

```
Z = 1.2×X1 + 1.4×X2 + 3.3×X3 + 0.6×X4 + 1.0×X5

Where:
X1 = Working Capital / Total Assets
X2 = Retained Earnings / Total Assets
X3 = EBIT / Total Assets
X4 = Market Value of Equity / Total Liabilities
X5 = Sales / Total Assets
```

**Interpretation:**
- **Z > 2.99** = Safe Zone (low bankruptcy risk)
- **1.81 < Z < 2.99** = Grey Zone (uncertain)
- **Z < 1.81** = Distress Zone (high bankruptcy risk)

```python
def calculate_altman_zscore(self, df):
    z_score = (
        1.2 * df['working_capital_to_total_assets'] +
        1.4 * df['retained_earnings_to_total_assets'] +
        3.3 * df['ebit_to_total_assets'] +
        0.6 * df['market_value_equity_to_total_liabilities'] +
        1.0 * df['sales_to_total_assets']
    )

    # Determine zone
    if z_score > 2.99:
        zone = "Safe"
    elif z_score > 1.81:
        zone = "Grey"
    else:
        zone = "Distress"
```

#### 4. `explain_prediction()` - SHAP Explanations

**SHAP (SHapley Additive exPlanations)** tells us WHY the model made a prediction.

```python
def explain_prediction(self, df, index=0):
    """
    Explain why a company got its risk score.

    Returns:
    - shap_values: Impact of each feature
    - top_risk_drivers: Top 10 factors affecting risk
    """

    # Calculate SHAP values
    shap_values = self.explainer.shap_values(sample)

    # Example output:
    # {
    #     'feature': 'debt_to_equity',
    #     'shap_value': 0.85,        # Positive = increases risk
    #     'feature_value': 4.2,      # Company's actual value
    #     'impact': 'increases'      # Direction of effect
    # }
```

**Reading SHAP Values:**
- **Positive SHAP** = Feature INCREASES bankruptcy risk
- **Negative SHAP** = Feature DECREASES bankruptcy risk
- **Larger absolute value** = More important feature

## 4.2 Employee Scorer

### File: `ml_models/employee_scorer.py`

### What It Does

Predicts which employees are likely to leave (attrition risk).

### Key Functions

#### `predict()` - Employee Risk Scoring

```python
def predict(self, df):
    """
    Score employees on retention risk.

    Returns:
    - retention_score: 0-100 (higher = more likely to stay)
    - attrition_probability: 0-1 (chance of leaving)
    - attrition_risk: 'Low', 'Medium', 'High'
    - estimated_time_to_leave: Months until potential departure
    """
```

#### `recommend_layoffs()` - Layoff Optimization

```python
def recommend_layoffs(self, df, budget_cut_percent, min_per_dept=1):
    """
    Recommend which employees to lay off to meet budget cuts.

    Logic:
    1. Calculate total salary budget
    2. Determine target reduction amount
    3. Sort employees by retention score (lowest first)
    4. Keep minimum required per department
    5. Select employees until budget target is met

    This minimizes talent loss by letting go of employees
    who were most likely to leave anyway.
    """
```

---

# 5. Backend Development (Rohan & Jonathan)

## Overview

The backend is built with **FastAPI**, a modern Python web framework that:
- Auto-generates API documentation
- Validates request/response data
- Handles async operations efficiently

## Main Application

### File: `backend/app/main.py`

### Application Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="SolvencyInsight API",
    description="AI-powered insolvency prediction and employee risk analysis",
    version="1.0.0",
)

# Enable CORS (allow frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML models on startup
@app.on_event("startup")
async def load_models():
    insolvency_model.load_model("ml_models/trained_models/insolvency_model.pkl")
    employee_model.load_model("ml_models/trained_models/employee_model.pkl")
```

### Key API Endpoints

#### 1. Health Check

```python
@app.get("/api/health")
async def health_check():
    """Check if API is running and models are loaded."""
    return {
        "status": "healthy",
        "models_loaded": True,
        "insolvency_model_metrics": {...},
        "employee_model_metrics": {...}
    }
```

#### 2. Single Company Analysis

```python
@app.post("/api/financial/analyze")
async def analyze_company(data: CompanyFinancialData):
    """
    Analyze a single company's financial data.

    Input: 12 financial ratios (JSON)
    Output: Prediction + SHAP explanation
    """
    # Convert to DataFrame
    df = pd.DataFrame([data.model_dump()])

    # Get prediction
    prediction = insolvency_model.predict(df)
    z_score = insolvency_model.calculate_altman_zscore(df)
    explanation = insolvency_model.explain_prediction(df)

    return {
        "prediction": {
            "probability_of_distress": 0.75,
            "risk_category": "High",
            "z_score": 1.45,
            "z_score_zone": "Distress"
        },
        "explanation": {
            "top_risk_drivers": [
                {"feature": "debt_to_equity", "shap_value": 0.85, ...},
                ...
            ]
        }
    }
```

#### 3. CSV File Upload

```python
@app.post("/api/financial/upload-single")
async def upload_single_company(file: UploadFile):
    """
    Upload CSV file with company financial data.
    Returns prediction with SHAP analysis.
    """
    # Read CSV
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    # Process and return results
    ...
```

#### 4. Employee Analysis

```python
@app.post("/api/employee/upload")
async def upload_employee_data(file: UploadFile):
    """
    Analyze employee attrition risk from CSV.
    """

@app.post("/api/employee/simulate-layoff")
async def simulate_layoffs(
    file: UploadFile,
    budget_cut_percent: float,
    min_per_dept: int = 1
):
    """
    Simulate layoff recommendations.
    """
```

## Data Validation with Pydantic

### File: `backend/app/models/schemas.py`

Pydantic models ensure data is valid before processing:

```python
from pydantic import BaseModel, Field

class CompanyFinancialData(BaseModel):
    """Input data for company analysis."""

    company_id: str = Field(..., description="Unique company identifier")
    company_name: str | None = Field(None, description="Company name")

    # Financial ratios with validation
    working_capital_to_total_assets: float = Field(
        ...,
        ge=-1.0,  # Greater than or equal to -1
        le=1.0,   # Less than or equal to 1
        description="Working Capital / Total Assets"
    )

    current_ratio: float = Field(
        ...,
        ge=0.0,   # Must be positive
        description="Current Assets / Current Liabilities"
    )

    # ... more fields
```

## PDF Report Generation

### File: `backend/app/services/pdf_generator.py`

Generates professional PDF reports using ReportLab:

```python
def generate_insolvency_report(company_data, prediction, explanation):
    """
    Generate a PDF risk assessment report.

    Contents:
    1. Executive Summary
    2. Risk Score & Category
    3. Altman Z-Score Analysis
    4. Top 10 Risk Drivers (SHAP)
    5. Recommendations
    """
```

---

# 6. Frontend Development (Neha & Mariya)

## Overview

The frontend is built with:
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **Recharts** - Chart library

## Page Components

### 6.1 Dashboard

**File: `frontend/src/pages/Dashboard.tsx`**

The main landing page showing system overview.

```tsx
export default function Dashboard() {
    return (
        <div>
            <h1>SolvencyInsight</h1>
            <p>AI-Powered Insolvency Prevention & Risk Analysis Platform</p>

            {/* Feature cards */}
            <FeatureCard
                title="Insolvency Analysis"
                description="Predict bankruptcy risk using ML"
            />
            <FeatureCard
                title="Employee Scoring"
                description="Identify flight-risk employees"
            />
            {/* ... more cards */}
        </div>
    );
}
```

### 6.2 Insolvency Analysis Page

**File: `frontend/src/pages/InsolvencyAnalysis.tsx`**

The main analysis page with two modes:
1. **Single Company** - Upload one company CSV or enter data manually
2. **Bulk Upload** - Upload multiple companies

```tsx
export default function InsolvencyAnalysis() {
    const [mode, setMode] = useState<'single' | 'bulk'>('single');
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [result, setResult] = useState(null);

    const handleAnalysis = async () => {
        if (selectedFile) {
            // Upload CSV and get prediction
            const result = await uploadSingleCompany(selectedFile);
            setResult(result);
        }
    };

    return (
        <div>
            {/* Mode selector */}
            <button onClick={() => setMode('single')}>Single Company</button>
            <button onClick={() => setMode('bulk')}>Bulk Upload</button>

            {/* File upload */}
            <FileUpload onFileSelect={setSelectedFile} />

            {/* Results display */}
            {result && (
                <>
                    <RiskGauge value={result.probability} />
                    <ZScoreDisplay score={result.z_score} />
                    <ShapChart data={result.explanation.top_risk_drivers} />
                </>
            )}
        </div>
    );
}
```

### 6.3 Employee Scoring Page

**File: `frontend/src/pages/EmployeeScoring.tsx`**

Upload employee data to see attrition risk scores.

### 6.4 Layoff Simulation Page

**File: `frontend/src/pages/LayoffSimulation.tsx`**

Simulate budget cuts and get layoff recommendations.

```tsx
export default function LayoffSimulation() {
    const [budgetCut, setBudgetCut] = useState(10); // 10% default
    const [minPerDept, setMinPerDept] = useState(1);

    const handleSimulation = async () => {
        const result = await simulateLayoffs(file, budgetCut, minPerDept);
        // Shows recommended layoffs and savings
    };
}
```

## Reusable Components

### 6.5 FileUpload Component

**File: `frontend/src/components/FileUpload.tsx`**

Drag-and-drop file upload with visual feedback:

```tsx
export default function FileUpload({ onFileSelect, selectedFile }) {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop: (files) => onFileSelect(files[0]),
        accept: { 'text/csv': ['.csv'] },
        maxFiles: 1,
    });

    return (
        <div {...getRootProps()} className="border-dashed border-2 p-8">
            <input {...getInputProps()} />
            {isDragActive ? (
                <p>Drop the file here...</p>
            ) : (
                <p>Click to Select CSV File</p>
            )}
        </div>
    );
}
```

### 6.6 RiskGauge Component

**File: `frontend/src/components/RiskGauge.tsx`**

Visual gauge showing risk level (0-100%):

```tsx
export default function RiskGauge({ value, riskCategory }) {
    // Circular gauge with color coding
    // Green (0-30%) -> Yellow (30-70%) -> Red (70-100%)

    const color = value < 0.3 ? 'green' : value < 0.7 ? 'yellow' : 'red';

    return (
        <div className="gauge">
            <CircularProgress value={value * 100} color={color} />
            <span>{(value * 100).toFixed(1)}%</span>
            <span className={`badge-${riskCategory.toLowerCase()}`}>
                {riskCategory}
            </span>
        </div>
    );
}
```

### 6.7 DataTable Component

**File: `frontend/src/components/DataTable.tsx`**

Sortable, searchable table for displaying results:

```tsx
export default function DataTable({ data, columns }) {
    const [sortColumn, setSortColumn] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    // Filter and sort data
    const filteredData = data
        .filter(row => /* match search term */)
        .sort((a, b) => /* sort by column */);

    return (
        <table>
            <thead>
                {columns.map(col => (
                    <th onClick={() => setSortColumn(col.key)}>
                        {col.header}
                    </th>
                ))}
            </thead>
            <tbody>
                {filteredData.map(row => (
                    <tr>{/* render cells */}</tr>
                ))}
            </tbody>
        </table>
    );
}
```

## API Client

### File: `frontend/src/services/api.ts`

Centralized API calls using Axios:

```typescript
import axios from 'axios';

const api = axios.create({
    baseURL: '',  // Uses Vite proxy
    timeout: 60000,
});

// Company analysis
export const analyzeCompany = async (data) => {
    const response = await api.post('/api/financial/analyze', data);
    return response.data;
};

export const uploadSingleCompany = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/financial/upload-single', formData);
    return response.data;
};

// Employee analysis
export const uploadEmployeeData = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/employee/upload', formData);
    return response.data;
};

export const simulateLayoffs = async (file, budgetCut, minPerDept) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/employee/simulate-layoff', formData, {
        params: { budget_cut_percent: budgetCut, min_per_dept: minPerDept }
    });
    return response.data;
};
```

---

# 7. System Integration (All Team Members)

## How Components Connect

```
User Action                 Frontend                    Backend                  ML Models
-----------                 --------                    -------                  ---------

1. Upload CSV    -->    FileUpload.tsx
                              |
2. Click Analyze -->    InsolvencyAnalysis.tsx
                              |
3. API Call      -->    api.ts (uploadSingleCompany)
                              |
                        POST /api/financial/upload-single
                              |                              |
                              +----------------------------> main.py
                                                              |
4. Process CSV                                          Read & validate CSV
                                                              |
5. ML Prediction                                        insolvency_predictor.predict()
                                                              |
6. SHAP Explain                                         insolvency_predictor.explain_prediction()
                                                              |
7. Return JSON   <------------------------------------  Return response
                              |
8. Display       <--    RiskGauge, ShapChart, etc.
```

## Vite Proxy Configuration

**File: `frontend/vite.config.ts`**

The frontend runs on port 5180, backend on port 8001. Vite proxy forwards API calls:

```typescript
export default defineConfig({
    server: {
        port: 5180,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8001',
                changeOrigin: true,
            },
        },
    },
});
```

## Integration Testing

All team members participated in testing the complete flow:

1. **Data Flow Test**: CSV upload -> Backend -> ML Model -> Response
2. **UI/UX Test**: Verify all pages render correctly
3. **Edge Cases**: Empty files, invalid data, large files
4. **Cross-browser**: Chrome, Firefox, Edge

---

# 8. Model Performance Metrics

## Insolvency Prediction Model

| Metric | Value | Meaning |
|--------|-------|---------|
| **Accuracy** | 100% | Correct predictions / Total predictions |
| **Precision** | 100% | True positives / Predicted positives |
| **Recall** | 100% | True positives / Actual positives |
| **F1 Score** | 100% | Harmonic mean of precision & recall |
| **ROC-AUC** | 100% | Area under ROC curve |

> **Note**: High metrics due to clearly separable training data. In production, expect 85-95%.

## Employee Attrition Model

| Metric | Value | Meaning |
|--------|-------|---------|
| **Accuracy** | 89.4% | Correct predictions / Total predictions |
| **Precision** | 81.4% | True positives / Predicted positives |
| **Recall** | 67.6% | True positives / Actual positives |
| **F1 Score** | 73.8% | Harmonic mean of precision & recall |
| **ROC-AUC** | 92.7% | Area under ROC curve |

## Data Statistics

| Dataset | Count |
|---------|-------|
| Training Companies | 100 |
| - Bankrupt | 20 (20%) |
| - Healthy | 80 (80%) |
| Training Employees | 500 |
| - Attrition | 80 (16%) |
| - Retained | 420 (84%) |
| Test Companies | 20 |
| - Safe | 10 |
| - At-Risk | 10 |
| Test Employees | 5,780 |

## Sample Predictions

| Company Type | Probability | Z-Score | Zone |
|--------------|-------------|---------|------|
| SAFE company | ~8% | 5.1+ | Safe |
| AT_RISK company | ~92% | 0.8-1.5 | Distress |

---

# 9. API Endpoints Reference

## Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Check API status and model metrics |

## Financial Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/financial/analyze` | Analyze single company (JSON) |
| POST | `/api/financial/upload-single` | Upload single company CSV |
| POST | `/api/financial/upload` | Upload multiple companies CSV |
| GET | `/api/financial/feature-importance` | Get model feature importance |

## Employee Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/employee/analyze` | Analyze single employee |
| POST | `/api/employee/upload` | Upload employee CSV |
| POST | `/api/employee/simulate-layoff` | Simulate layoff recommendations |
| GET | `/api/employee/feature-importance` | Get model feature importance |

## Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reports/insolvency` | Generate insolvency PDF report |
| POST | `/api/reports/layoff` | Generate layoff PDF report |

## Market Intelligence

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/market-intelligence` | Get news and sector data |

---

# 10. How to Run the Project

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

## Step 1: Clone and Setup

```bash
cd insolvency-prevention-system

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install Python dependencies
pip install -r requirements.txt
```

## Step 2: Train Models (if needed)

```bash
python scripts/train_models.py
```

## Step 3: Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

## Step 4: Start Frontend

```bash
cd frontend
npm install
npm run dev -- --port 5180
```

## Step 5: Access Application

Open browser: **http://localhost:5180**

---

# Summary

## What Each Team Member Can Talk About

### Rohan & Jonathan (ML & Backend)

1. "We chose XGBoost because it's the best algorithm for tabular financial data"
2. "We used SHAP for explainability - so users know WHY a company is at risk"
3. "The Altman Z-Score validates our ML predictions with a traditional method"
4. "We built a RESTful API with FastAPI for fast, async request handling"
5. "We added regularization to prevent overfitting and get realistic probabilities"

### Neha (Data Preparation)

1. "I generated realistic financial data based on real-world ratio distributions"
2. "Bankrupt companies have negative ratios, high debt, and poor liquidity"
3. "I created 20 test companies with correlated employee data for validation"
4. "The data includes 8 different industries with industry-specific patterns"

### Neha & Mariya (Frontend)

1. "We built a responsive React dashboard with TypeScript for type safety"
2. "The RiskGauge component visualizes probability with intuitive colors"
3. "FileUpload supports drag-and-drop for easy CSV uploads"
4. "SHAP charts show users the top 10 factors driving risk predictions"
5. "We used TailwindCSS for a modern, dark-themed professional UI"

### All Team Members (Integration)

1. "We used Vite proxy to connect frontend (5180) to backend (8001)"
2. "The system flows: Upload -> API -> ML Model -> SHAP -> Display"
3. "We tested with 20 companies and 5,780 employees to validate accuracy"
4. "The models achieve 89-100% accuracy on test data"

---

*Document prepared for SolvencyInsight project presentation*
*Team: Rohan, Jonathan, Neha, Mariya*
