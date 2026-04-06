/**
 * @fileoverview API service module for the Insolvency Prevention System.
 * Provides typed functions for all backend API endpoints.
 */

import axios from 'axios';
import type {
  HealthResponse,
  RecentAnalysesResponse,
  CompanyFinancialData,
  InsolvencyAnalysisResponse,
  InsolvencyBulkResponse,
  EmployeeData,
  EmployeeAnalysisResponse,
  EmployeeBulkResponse,
  LayoffSimulationResponse,
  FeatureImportanceResponse,
  MarketIntelligenceRequest,
  MarketIntelligenceResponse,
  CompanyHealthScore,
} from '../types';

/** Base URL for the backend API, configurable via VITE_API_URL environment variable */
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout for large file uploads
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        error.message = 'Request timed out. Please try again.';
      } else if (error.message === 'Network Error') {
        error.message = 'Unable to connect to server. Please check if the backend is running.';
      }
    }
    // Handle specific HTTP errors
    else if (error.response.status === 422) {
      // Validation error - extract detail
      const detail = error.response.data?.detail;
      if (Array.isArray(detail)) {
        error.message = detail.map((d: any) => d.msg).join(', ');
      } else if (typeof detail === 'string') {
        error.message = detail;
      }
    } else if (error.response.status === 500) {
      error.message = 'Server error. Please try again later.';
    }
    return Promise.reject(error);
  }
);

/**
 * Check API health status and model availability.
 * @returns {Promise<HealthResponse>} Health status with model metrics
 */
export const getHealth = async (): Promise<HealthResponse> => {
  const response = await api.get<HealthResponse>('/api/health');
  return response.data;
};

/**
 * Get recent analyses for Dashboard.
 * @param limit - Max entries (default 10, max 50)
 */
export const getRecentAnalyses = async (limit = 10): Promise<RecentAnalysesResponse> => {
  const response = await api.get<RecentAnalysesResponse>('/api/analyses/recent', { params: { limit } });
  return response.data;
};

/**
 * Get market intelligence for a company (news, sector, economic context).
 * @param request - company_name and optional industry, description
 */
export const getMarketIntelligence = async (
  request: MarketIntelligenceRequest
): Promise<MarketIntelligenceResponse> => {
  const response = await api.post<MarketIntelligenceResponse>('/api/market-intelligence', request);
  return response.data;
};

/** Download company CSV template and trigger save */
export const downloadCompanyTemplate = async (): Promise<void> => {
  const res = await api.get('/api/templates/company', { responseType: 'blob' });
  const url = URL.createObjectURL(res.data);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'company_financial_template.csv';
  a.click();
  URL.revokeObjectURL(url);
};

/** Download employee CSV template and trigger save */
export const downloadEmployeeTemplate = async (): Promise<void> => {
  const res = await api.get('/api/templates/employee', { responseType: 'blob' });
  const url = URL.createObjectURL(res.data);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'employee_data_template.csv';
  a.click();
  URL.revokeObjectURL(url);
};

// Financial Analysis

/**
 * Analyze a single company's financial data for insolvency risk.
 * @param {CompanyFinancialData} data - Company financial ratios
 * @returns {Promise<InsolvencyAnalysisResponse>} Prediction with SHAP explanation
 */
export const analyzeCompany = async (
  data: CompanyFinancialData
): Promise<InsolvencyAnalysisResponse> => {
  const response = await api.post<InsolvencyAnalysisResponse>('/api/financial/analyze', data);
  return response.data;
};

/**
 * Upload a CSV file with a single company's financial data.
 * Returns full SHAP analysis like the manual analyze endpoint.
 * @param {File} file - CSV file with single company financial data
 * @returns {Promise<InsolvencyAnalysisResponse>} Prediction with SHAP explanation
 */
export const uploadSingleCompany = async (
  file: File
): Promise<InsolvencyAnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<InsolvencyAnalysisResponse>('/api/financial/upload-single', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Upload a CSV file with multiple companies' financial data.
 * @param {File} file - CSV file with company financial data
 * @returns {Promise<InsolvencyBulkResponse>} Predictions for all companies
 */
export const uploadFinancialData = async (
  file: File
): Promise<InsolvencyBulkResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<InsolvencyBulkResponse>('/api/financial/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Get prediction + SHAP explanation for one row from a bulk financial CSV.
 * Use after bulk upload to explain a single row without re-uploading.
 * @param {File} file - Same CSV file used for bulk upload
 * @param {number} rowIndex - 0-based row index
 * @returns {Promise<InsolvencyAnalysisResponse>} Prediction with SHAP for that row
 */
export const explainFinancialRow = async (
  file: File,
  rowIndex: number = 0
): Promise<InsolvencyAnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<InsolvencyAnalysisResponse>(
    '/api/financial/explain-row',
    formData,
    {
      params: { row_index: rowIndex },
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  );
  return response.data;
};

/**
 * Get feature importance from the insolvency prediction model.
 * @returns {Promise<FeatureImportanceResponse>} Feature importance rankings
 */
export const getFinancialFeatureImportance = async (): Promise<FeatureImportanceResponse> => {
  const response = await api.get<FeatureImportanceResponse>('/api/financial/feature-importance');
  return response.data;
};

// Model Bridge: Company Health Score

/**
 * Compute company_health_score from financial data.
 * Bridges the insolvency model to the employee model.
 * Formula: health_score = 100 * (1 - probability_of_distress)
 * @param {CompanyFinancialData} data - Company financial ratios
 * @returns {Promise<CompanyHealthScore>} Health score with distress details
 */
export const getCompanyHealthScore = async (
  data: CompanyFinancialData
): Promise<CompanyHealthScore> => {
  const response = await api.post<CompanyHealthScore>('/api/bridge/company-health-score', data);
  return response.data;
};

/**
 * Upload employee CSV with company_health_score auto-injected into every row.
 * Bridges insolvency analysis to employee scoring in one step.
 * @param {File} file - CSV file with employee data
 * @param {number} companyHealthScore - Health score from insolvency analysis (0-100)
 * @returns {Promise<EmployeeBulkResponse>} Predictions with health score applied
 */
export const uploadEmployeeWithHealth = async (
  file: File,
  companyHealthScore: number
): Promise<EmployeeBulkResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<EmployeeBulkResponse>(
    '/api/employee/upload-with-health',
    formData,
    {
      params: { company_health_score: companyHealthScore },
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  );
  return response.data;
};

// Employee Analysis

/**
 * Analyze a single employee's data for attrition risk.
 * @param {EmployeeData} data - Employee data
 * @returns {Promise<EmployeeAnalysisResponse>} Prediction with SHAP explanation
 */
export const analyzeEmployee = async (
  data: EmployeeData
): Promise<EmployeeAnalysisResponse> => {
  const response = await api.post<EmployeeAnalysisResponse>('/api/employee/analyze', data);
  return response.data;
};

/**
 * Upload a CSV file with multiple employees' data.
 * @param {File} file - CSV file with employee data
 * @returns {Promise<EmployeeBulkResponse>} Predictions for all employees
 */
export const uploadEmployeeData = async (
  file: File
): Promise<EmployeeBulkResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<EmployeeBulkResponse>('/api/employee/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Simulate layoff recommendations based on budget constraints.
 * @param {File} file - CSV file with employee data
 * @param {number} budgetCutPercent - Target budget reduction percentage
 * @param {number} minPerDept - Minimum employees to retain per department
 * @returns {Promise<LayoffSimulationResponse>} Layoff recommendations
 */
export const simulateLayoffs = async (
  file: File,
  budgetCutPercent: number,
  minPerDept: number = 1
): Promise<LayoffSimulationResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<LayoffSimulationResponse>(
    '/api/employee/simulate-layoff',
    formData,
    {
      params: {
        budget_cut_percent: budgetCutPercent,
        min_per_dept: minPerDept,
      },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

/**
 * Get prediction + SHAP explanation for one row from a bulk employee CSV.
 * Use after bulk upload to explain a single row without re-uploading.
 * @param {File} file - Same CSV file used for bulk upload
 * @param {number} rowIndex - 0-based row index
 * @returns {Promise<EmployeeAnalysisResponse>} Prediction with SHAP for that row
 */
export const explainEmployeeRow = async (
  file: File,
  rowIndex: number = 0
): Promise<EmployeeAnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<EmployeeAnalysisResponse>(
    '/api/employee/explain-row',
    formData,
    {
      params: { row_index: rowIndex },
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  );
  return response.data;
};

/**
 * Get feature importance from the employee scoring model.
 * @returns {Promise<FeatureImportanceResponse>} Feature importance rankings
 */
export const getEmployeeFeatureImportance = async (): Promise<FeatureImportanceResponse> => {
  const response = await api.get<FeatureImportanceResponse>('/api/employee/feature-importance');
  return response.data;
};

// Report Generation

/**
 * Generate an insolvency risk assessment PDF report.
 * @param {string} companyId - Company identifier
 * @param {string} companyName - Company name
 * @param {CompanyFinancialData} companyData - Financial data for analysis
 * @returns {Promise<Blob>} PDF file as blob
 */
export const generateInsolvencyReport = async (
  companyId: string,
  companyName: string,
  companyData: CompanyFinancialData
): Promise<Blob> => {
  const response = await api.post(
    '/api/reports/insolvency',
    {
      company_id: companyId,
      company_name: companyName,
      company_data: companyData,
    },
    {
      responseType: 'blob',
    }
  );
  return response.data;
};

/**
 * Generate a layoff simulation PDF report.
 * @param {File} file - CSV file with employee data
 * @param {number} budgetCutPercent - Target budget reduction percentage
 * @param {number} minPerDept - Minimum employees per department
 * @returns {Promise<Blob>} PDF file as blob
 */
export const generateLayoffReport = async (
  file: File,
  budgetCutPercent: number,
  minPerDept: number = 1
): Promise<Blob> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/reports/layoff', formData, {
    params: {
      budget_cut_percent: budgetCutPercent,
      min_per_dept: minPerDept,
    },
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    responseType: 'blob',
  });
  return response.data;
};

/**
 * Download a blob as a file in the browser.
 * @param {Blob} blob - File content as blob
 * @param {string} filename - Name for the downloaded file
 */
export const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
};

export default api;
