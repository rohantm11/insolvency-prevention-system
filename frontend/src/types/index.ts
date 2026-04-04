// Health Check
export interface HealthResponse {
  status: string;
  models_loaded: boolean;
  insolvency_model_metrics: Record<string, number> | null;
  employee_model_metrics: Record<string, number> | null;
}

// Financial Analysis Types
export interface CompanyFinancialData {
  company_id?: string;
  company_name?: string;
  working_capital_to_total_assets: number;
  retained_earnings_to_total_assets: number;
  ebit_to_total_assets: number;
  market_value_equity_to_total_liabilities: number;
  sales_to_total_assets: number;
  current_ratio: number;
  quick_ratio: number;
  debt_to_equity: number;
  interest_coverage: number;
  net_profit_margin: number;
  return_on_assets: number;
  return_on_equity: number;
}

export interface InsolvencyPrediction {
  company_id: string | null;
  company_name: string | null;
  probability_of_distress: number;
  risk_category: 'Low' | 'Medium' | 'High';
  estimated_time_to_event: number | null;
  z_score: number;
  z_score_zone: 'Safe' | 'Grey' | 'Distress';
  executive_summary?: string | null;
}

export type AnalysisType = 'Company Analysis' | 'Employee Scoring' | 'Layoff Simulation';

export interface AnalysisHistoryEntry {
  id: string;
  type: AnalysisType;
  name: string;
  result: string;
  score: string | null;
  timestamp: string;
  payload?: Record<string, unknown>;
}

export interface RecentAnalysesResponse {
  entries: AnalysisHistoryEntry[];
  total: number;
}

export interface InsolvencyExplanation {
  shap_values: Record<string, number>;
  top_risk_drivers: Array<{
    feature: string;
    shap_value: number;
    original_value: number;
    impact: string;
  }>;
  base_value: number;
  prediction_value: number;
}

export interface InsolvencyAnalysisResponse {
  prediction: InsolvencyPrediction;
  explanation: InsolvencyExplanation;
}

export interface InsolvencyBulkResponse {
  total_companies: number;
  predictions: InsolvencyPrediction[];
  summary: {
    high_risk_count: number;
    medium_risk_count: number;
    low_risk_count: number;
    avg_probability: number;
    z_score_distress_count: number;
  };
}

// Employee Analysis Types
export interface EmployeeData {
  employee_id?: string;
  name?: string;
  age: number;
  gender: string;
  department: string;
  job_role: string;
  job_level: number;
  performance_rating: number;
  job_satisfaction: number;
  job_involvement: number;
  environment_satisfaction: number;
  monthly_income: number;
  percent_salary_hike: number;
  stock_option_level: number;
  years_at_company: number;
  years_in_current_role: number;
  total_working_years: number;
  distance_from_home: number;
  business_travel: string;
  over_time: string;
}

export interface EmployeePrediction {
  employee_id: string | null;
  name: string | null;
  department: string | null;
  retention_score: number;
  attrition_probability: number;
  attrition_risk: 'Low' | 'Medium' | 'High';
  layoff_priority: 'Low' | 'Medium' | 'High';
}

export interface EmployeeExplanation {
  shap_values: Record<string, number>;
  top_factors: Array<{
    feature: string;
    shap_value: number;
    original_value: number | string;
    impact: string;
  }>;
  base_value: number;
  prediction_value: number;
}

export interface EmployeeAnalysisResponse {
  prediction: EmployeePrediction;
  explanation: EmployeeExplanation;
}

export interface EmployeeBulkResponse {
  total_employees: number;
  predictions: EmployeePrediction[];
  summary: {
    high_attrition_risk_count: number;
    medium_attrition_risk_count: number;
    low_attrition_risk_count: number;
    avg_retention_score: number;
    avg_attrition_probability: number;
    high_layoff_priority_count: number;
  };
}

// Layoff Simulation Types
export interface LayoffRecommendation {
  employee_id: string;
  name: string;
  department: string;
  monthly_income: number;
  retention_score: number;
  layoff_recommended: boolean;
  layoff_reason: string;
}

export interface LayoffSimulationResponse {
  target_budget_cut: number;
  target_monthly_savings: number;
  actual_monthly_savings: number;
  employees_affected: number;
  savings_achieved_percent: number;
  recommendations: LayoffRecommendation[];
  department_breakdown: Record<string, number>;
}

// Feature Importance
export interface FeatureImportanceResponse {
  feature_importance: Record<string, number>;
  model_metrics: Record<string, number>;
}

// Market Intelligence
export interface MarketIntelligenceRequest {
  company_name: string;
  industry?: string | null;
  description?: string | null;
}

export interface NewsArticleResponse {
  title: string;
  source: string;
  url: string;
  published_at: string;
  summary: string;
  sentiment_score: number;
  relevance_score: number;
}

export interface SectorDataResponse {
  sector: string;
  performance_1d: number;
  performance_1w: number;
  performance_1m: number;
  performance_ytd: number;
  trend: string;
}

export interface EconomicIndicatorsResponse {
  gdp_growth?: number | null;
  unemployment_rate?: number | null;
  inflation_rate?: number | null;
  interest_rate?: number | null;
  consumer_confidence?: number | null;
}

export interface MarketIntelligenceResponse {
  company_name: string;
  industry: string;
  sector: string;
  generated_at: string;
  news_articles: NewsArticleResponse[];
  overall_news_sentiment: number;
  sector_data: SectorDataResponse | null;
  economic_indicators: EconomicIndicatorsResponse | null;
  risk_adjustment: number;
  market_summary: string;
}
