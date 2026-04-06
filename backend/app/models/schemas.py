"""
Pydantic models for request/response validation.
"""

from typing import Any, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Health Check
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    insolvency_model_metrics: dict[str, float] | None = None
    employee_model_metrics: dict[str, float] | None = None


# ============================================================================
# Financial Analysis Models
# ============================================================================

class CompanyFinancialData(BaseModel):
    """Input data for a single company financial analysis.

    For better insolvency modelling and explainability, ratios should be codependent
    where applicable: e.g. quick_ratio <= current_ratio; ROA = net_profit_margin * sales_to_total_assets;
    ROE ≈ ROA * (1 + debt_to_equity); interest_coverage consistent with EBIT and leverage.
    """
    company_id: str | None = None
    company_name: str | None = None

    # Altman Z-score components
    working_capital_to_total_assets: float = Field(..., ge=-1.0, le=1.0, description="Working Capital / Total Assets")
    retained_earnings_to_total_assets: float = Field(..., ge=-2.0, le=1.0, description="Retained Earnings / Total Assets. Negative indicates accumulated losses.")
    ebit_to_total_assets: float = Field(..., ge=-1.0, le=1.0, description="EBIT / Total Assets")
    market_value_equity_to_total_liabilities: float = Field(..., ge=0.0, le=100.0, description="Market Value of Equity / Total Liabilities")
    sales_to_total_assets: float = Field(..., ge=0.0, le=10.0, description="Sales / Total Assets (asset turnover)")

    # Additional financial ratios
    current_ratio: float = Field(..., ge=0.0, le=30.0, description="Current Assets / Current Liabilities")
    quick_ratio: float = Field(..., ge=0.0, le=30.0, description="(Current Assets - Inventory) / Current Liabilities")
    debt_to_equity: float = Field(..., ge=-10.0, le=50.0, description="Total Debt / Total Equity. Negative indicates negative equity.")
    interest_coverage: float = Field(..., ge=-50.0, le=100.0, description="EBIT / Interest Expense. Negative means EBIT does not cover interest.")
    net_profit_margin: float = Field(..., ge=-2.0, le=1.0, description="Net Income / Revenue")
    return_on_assets: float = Field(..., ge=-1.0, le=1.0, description="Net Income / Total Assets")
    return_on_equity: float = Field(..., ge=-5.0, le=5.0, description="Net Income / Shareholders Equity. Extreme values indicate near-zero equity.")

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


class InsolvencyPrediction(BaseModel):
    """Single company insolvency prediction result."""
    company_id: str | None = None
    company_name: str | None = None
    probability_of_distress: float = Field(..., ge=0, le=1)
    risk_category: str = Field(..., description="Low, Medium, or High")
    estimated_time_to_event: int | None = Field(None, description="Estimated years to potential bankruptcy")
    z_score: float = Field(..., description="Altman Z-Score")
    z_score_zone: str = Field(..., description="Safe, Grey, or Distress")
    executive_summary: str | None = Field(None, description="Plain-language narrative summary")
    input_warnings: list[str] = Field(default_factory=list, description="Warnings about input data inconsistencies")


class InsolvencyExplanation(BaseModel):
    """SHAP-based explanation for insolvency prediction."""
    shap_values: dict[str, float]
    top_risk_drivers: list[dict[str, Any]]
    base_value: float
    prediction_value: float


class InsolvencyAnalysisResponse(BaseModel):
    """Response for single company analysis."""
    prediction: InsolvencyPrediction
    explanation: InsolvencyExplanation


class InsolvencyBulkResponse(BaseModel):
    """Response for bulk company analysis."""
    total_companies: int
    predictions: list[InsolvencyPrediction]
    summary: dict[str, Any]


class FeatureImportanceResponse(BaseModel):
    """Feature importance from trained model."""
    feature_importance: dict[str, float]
    model_metrics: dict[str, float]


# ============================================================================
# Analysis History (for Dashboard and saved analyses)
# ============================================================================

class AnalysisHistoryEntry(BaseModel):
    """Single entry in recent analyses list."""
    id: str
    type: Literal["Company Analysis", "Employee Scoring", "Layoff Simulation"]
    name: str
    result: str
    score: str | None = None
    timestamp: str
    payload: dict[str, Any] | None = None


class RecentAnalysesResponse(BaseModel):
    """Response for recent analyses (Dashboard)."""
    entries: list[AnalysisHistoryEntry]
    total: int


# ============================================================================
# Employee Analysis Models
# ============================================================================

class EmployeeData(BaseModel):
    """Input data for a single employee analysis."""
    employee_id: str | None = None
    name: str | None = None

    # Demographics
    age: int = Field(..., ge=18, le=70)
    gender: str = Field(..., description="Male or Female")

    # Job info
    department: str
    job_role: str
    job_level: int = Field(..., ge=1, le=5)

    # Performance metrics (1-4 scale)
    performance_rating: int = Field(..., ge=1, le=4)
    job_satisfaction: int = Field(..., ge=1, le=4)
    job_involvement: int = Field(..., ge=1, le=4)
    environment_satisfaction: int = Field(..., ge=1, le=4)

    # Compensation
    monthly_income: float = Field(..., ge=1000, le=200000)
    percent_salary_hike: int = Field(..., ge=0, le=100)
    stock_option_level: int = Field(..., ge=0, le=3)

    # Work history
    years_at_company: int = Field(..., ge=0, le=50)
    years_in_current_role: int = Field(..., ge=0, le=50)
    total_working_years: int = Field(..., ge=0, le=50)

    # Other factors
    distance_from_home: int = Field(..., ge=0, le=100)
    business_travel: str = Field(..., description="Non-Travel, Travel_Rarely, or Travel_Frequently")
    over_time: str = Field(..., description="Yes or No")

    # Company financial health integration
    company_health_score: float = Field(
        default=50.0, ge=0, le=100,
        description="Company financial health score (0-100). Derived from insolvency model: 100*(1 - probability_of_distress). Default 50 (neutral) when unknown."
    )

    class Config:
        json_schema_extra = {
            "example": {
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
                "over_time": "No",
                "company_health_score": 72.5
            }
        }


class EmployeePrediction(BaseModel):
    """Single employee prediction result."""
    employee_id: str | None = None
    name: str | None = None
    department: str | None = None
    retention_score: float = Field(..., ge=0, le=100)
    attrition_probability: float = Field(..., ge=0, le=1)
    attrition_risk: str = Field(..., description="Low, Medium, or High")
    layoff_priority: str = Field(..., description="Low, Medium, or High")
    company_health_score: float = Field(default=50.0, ge=0, le=100, description="Company health score used for this prediction")


class EmployeeExplanation(BaseModel):
    """SHAP-based explanation for employee prediction."""
    shap_values: dict[str, float]
    top_factors: list[dict[str, Any]]
    base_value: float
    prediction_value: float


class EmployeeAnalysisResponse(BaseModel):
    """Response for single employee analysis."""
    prediction: EmployeePrediction
    explanation: EmployeeExplanation


class EmployeeBulkResponse(BaseModel):
    """Response for bulk employee analysis."""
    total_employees: int
    predictions: list[EmployeePrediction]
    summary: dict[str, Any]


class LayoffSimulationRequest(BaseModel):
    """Request for layoff simulation."""
    budget_cut_percent: float = Field(..., gt=0, le=100, description="Target budget reduction percentage")
    min_per_dept: int = Field(default=1, ge=1, description="Minimum employees to retain per department")


class LayoffRecommendation(BaseModel):
    """Single layoff recommendation."""
    employee_id: str
    name: str
    department: str
    monthly_income: int
    retention_score: float
    layoff_recommended: bool
    layoff_reason: str


class LayoffSimulationResponse(BaseModel):
    """Response for layoff simulation."""
    target_budget_cut: float
    target_monthly_savings: float
    actual_monthly_savings: float
    employees_affected: int
    savings_achieved_percent: float
    recommendations: list[LayoffRecommendation]
    department_breakdown: dict[str, int]


# ============================================================================
# Report Generation Models
# ============================================================================

class InsolvencyReportRequest(BaseModel):
    """Request for insolvency PDF report generation."""
    company_id: str = Field(..., description="Company identifier")
    company_name: str = Field(default="Unknown Company", description="Company name")
    company_data: CompanyFinancialData = Field(..., description="Financial data for analysis")

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class LayoffReportRequest(BaseModel):
    """Request for layoff simulation PDF report generation."""
    budget_cut_percent: float = Field(..., gt=0, le=100, description="Target budget reduction percentage")
    min_per_dept: int = Field(default=1, ge=1, description="Minimum employees to retain per department")

    class Config:
        json_schema_extra = {
            "example": {
                "budget_cut_percent": 10.0,
                "min_per_dept": 2
            }
        }


# ============================================================================
# Market Intelligence Models
# ============================================================================

class NewsArticleResponse(BaseModel):
    """Single news article with sentiment."""
    title: str
    source: str
    url: str
    published_at: str
    summary: str
    sentiment_score: float = Field(..., ge=-1, le=1, description="Sentiment from -1 (negative) to 1 (positive)")
    relevance_score: float = Field(..., ge=0, le=1)


class SectorDataResponse(BaseModel):
    """Sector performance data."""
    sector: str
    performance_1d: float
    performance_1w: float
    performance_1m: float
    performance_ytd: float
    trend: str = Field(..., description="bullish, bearish, or neutral")


class EconomicIndicatorsResponse(BaseModel):
    """Economic indicators."""
    gdp_growth: float | None = None
    unemployment_rate: float | None = None
    inflation_rate: float | None = None
    interest_rate: float | None = None
    consumer_confidence: float | None = None


class RiskFactor(BaseModel):
    """Individual risk factor."""
    type: str = Field(..., description="financial, market, or economic")
    metric: str
    value: float | None = None
    threshold: float | None = None
    message: str
    severity: str = Field(..., description="low, medium, or high")


class MarketIntelligenceResponse(BaseModel):
    """Complete market intelligence report."""
    company_name: str
    industry: str
    sector: str
    generated_at: str
    news_articles: list[NewsArticleResponse]
    overall_news_sentiment: float
    sector_data: SectorDataResponse | None = None
    economic_indicators: EconomicIndicatorsResponse | None = None
    risk_adjustment: float = Field(..., description="Risk adjustment factor from -0.2 to 0.2")
    market_summary: str


class EnhancedAnalysisRequest(BaseModel):
    """Request for enhanced analysis with market intelligence."""
    company_id: str | None = None
    company_name: str | None = Field(default="Unknown Company", description="Company name for news search")
    industry: str | None = Field(default=None, description="Industry (auto-detected if not provided)")
    description: str | None = Field(default="", description="Company description for better industry classification")

    # Altman Z-score components
    working_capital_to_total_assets: float = Field(..., ge=-1.0, le=1.0, description="Working Capital / Total Assets")
    retained_earnings_to_total_assets: float = Field(..., ge=-2.0, le=1.0, description="Retained Earnings / Total Assets")
    ebit_to_total_assets: float = Field(..., ge=-1.0, le=1.0, description="EBIT / Total Assets")
    market_value_equity_to_total_liabilities: float = Field(..., ge=0.0, le=100.0, description="Market Value of Equity / Total Liabilities")
    sales_to_total_assets: float = Field(..., ge=0.0, le=10.0, description="Sales / Total Assets")

    # Additional financial ratios
    current_ratio: float = Field(..., ge=0.0, le=30.0, description="Current Assets / Current Liabilities")
    quick_ratio: float = Field(..., ge=0.0, le=30.0, description="(Current Assets - Inventory) / Current Liabilities")
    debt_to_equity: float = Field(..., ge=-10.0, le=50.0, description="Total Debt / Total Equity")
    interest_coverage: float = Field(..., ge=-50.0, le=100.0, description="EBIT / Interest Expense")
    net_profit_margin: float = Field(..., ge=-2.0, le=1.0, description="Net Income / Revenue")
    return_on_assets: float = Field(..., ge=-1.0, le=1.0, description="Net Income / Total Assets")
    return_on_equity: float = Field(..., ge=-5.0, le=5.0, description="Net Income / Shareholders Equity")

    # Market intelligence options
    include_market_intelligence: bool = Field(default=True, description="Whether to include live market research")

    class Config:
        json_schema_extra = {
            "example": {
                "company_id": "COMP_001",
                "company_name": "Target Corporation",
                "industry": "retail",
                "description": "Major retail chain",
                "working_capital_to_total_assets": 0.15,
                "retained_earnings_to_total_assets": 0.25,
                "ebit_to_total_assets": 0.08,
                "market_value_equity_to_total_liabilities": 1.5,
                "sales_to_total_assets": 1.0,
                "current_ratio": 1.2,
                "quick_ratio": 0.8,
                "debt_to_equity": 1.5,
                "interest_coverage": 3.0,
                "net_profit_margin": 0.04,
                "return_on_assets": 0.05,
                "return_on_equity": 0.12,
                "include_market_intelligence": True
            }
        }


class EnhancedPredictionResponse(BaseModel):
    """Enhanced prediction with market context."""
    # Base model results
    base_probability: float = Field(..., ge=0, le=1)
    base_prediction: str

    # Market-adjusted results
    adjusted_probability: float = Field(..., ge=0, le=1)
    adjusted_prediction: str
    risk_level: str = Field(..., description="LOW, MODERATE, ELEVATED, HIGH, or CRITICAL")

    # Breakdown
    model_contribution: float
    market_contribution: float

    # Risk analysis
    risk_factors: list[RiskFactor]
    recommendations: list[str]

    # Market intelligence (if requested)
    market_intelligence: MarketIntelligenceResponse | None = None


class MarketIntelligenceRequest(BaseModel):
    """Request for market intelligence only (without prediction)."""
    company_name: str = Field(..., description="Company name for news search")
    industry: str | None = Field(default=None, description="Industry (auto-detected if not provided)")
    description: str | None = Field(default="", description="Company description")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Walmart",
                "industry": "retail",
                "description": "Major retail chain operating supercenters"
            }
        }


# ============================================================================
# Error Response
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str | None = None
