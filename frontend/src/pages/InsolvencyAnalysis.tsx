/**
 * @fileoverview Insolvency Analysis page component.
 * Provides single company and bulk CSV analysis for bankruptcy risk prediction.
 */

import { useState } from 'react';
import {
  Building2,
  Upload,
  AlertTriangle,
  Download,
  RefreshCw,
  Clock,
  TrendingUp,
  Info,
  Users,
  ArrowRight,
  UserX,
  UserCheck,
  X,
} from 'lucide-react';
import { analyzeCompany, uploadSingleCompany, uploadFinancialData, generateInsolvencyReport, downloadBlob, downloadCompanyTemplate, uploadEmployeeWithHealth } from '../services/api';
import type { CompanyFinancialData, InsolvencyAnalysisResponse, InsolvencyBulkResponse, EmployeeBulkResponse, EmployeePrediction } from '../types';
import { RiskGauge, DataTable, FileUpload, LoadingSpinner, Skeleton, AnimatedButton, Tooltip as InfoTooltip, ShapChart } from '../components';
import { useToast } from '../context/ToastContext';
import { TOOLTIP_COPY } from '../constants/tooltipCopy';
import { addTrackedCompany } from '../constants/watchlist';

/** Analysis mode - single company or bulk CSV upload */
type Mode = 'single' | 'bulk';

const defaultFormData: CompanyFinancialData = {
  company_id: '',
  company_name: '',
  working_capital_to_total_assets: 0.2,
  retained_earnings_to_total_assets: 0.3,
  ebit_to_total_assets: 0.1,
  market_value_equity_to_total_liabilities: 2.0,
  sales_to_total_assets: 1.0,
  current_ratio: 1.5,
  quick_ratio: 1.0,
  debt_to_equity: 1.0,
  interest_coverage: 3.0,
  net_profit_margin: 0.05,
  return_on_assets: 0.05,
  return_on_equity: 0.1,
};

/**
 * InsolvencyAnalysis component for analyzing company bankruptcy risk.
 * Supports single company form input and bulk CSV upload.
 * Uses Altman Z-Score and XGBoost ML model for predictions with SHAP explanations.
 * @returns {JSX.Element} The rendered insolvency analysis page
 */
export default function InsolvencyAnalysis() {
  const [mode, setMode] = useState<Mode>('single');
  const [formData, setFormData] = useState<CompanyFinancialData>(defaultFormData);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [singleResult, setSingleResult] = useState<InsolvencyAnalysisResponse | null>(null);
  const [bulkResult, setBulkResult] = useState<InsolvencyBulkResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloadingReport, setDownloadingReport] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Workforce Impact state
  const [employeeFile, setEmployeeFile] = useState<File | null>(null);
  const [employeeResult, setEmployeeResult] = useState<EmployeeBulkResponse | null>(null);
  const [employeeLoading, setEmployeeLoading] = useState(false);
  const [selectedWorkforceEmployee, setSelectedWorkforceEmployee] = useState<EmployeePrediction | null>(null);
  const toast = useToast();

  const handleInputChange = (field: keyof CompanyFinancialData, value: string | number) => {
    setFormData((prev) => ({
      ...prev,
      [field]: typeof defaultFormData[field] === 'number' ? Number(value) : value,
    }));
  };

  const handleSingleAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      let result: InsolvencyAnalysisResponse;

      if (selectedFile) {
        // Use single company upload endpoint - returns full SHAP analysis
        result = await uploadSingleCompany(selectedFile);
        // Update formData with the company info from CSV
        setFormData(prev => ({
          ...prev,
          company_id: result.prediction.company_id ?? undefined,
          company_name: result.prediction.company_name ?? undefined,
        }));
      } else {
        // Use manual form data
        result = await analyzeCompany(formData);
      }

      setSingleResult(result);
      addTrackedCompany({
        company_id: result.prediction.company_id ?? null,
        company_name: result.prediction.company_name ?? null,
        risk_category: result.prediction.risk_category,
        z_score: result.prediction.z_score,
      });
      const isFirstAnalysis = typeof window !== 'undefined' && !localStorage.getItem('solvency-insight-first-analysis-done');
      if (isFirstAnalysis) {
        toast.addToast({
          type: 'success',
          title: 'Risk analysis complete — here\'s what the model found.',
          message: `Risk category: ${result.prediction.risk_category}. Z-Score: ${result.prediction.z_score.toFixed(2)}. Check the risk drivers below for details.`,
          duration: 8000,
        });
        localStorage.setItem('solvency-insight-first-analysis-done', 'true');
      } else {
        toast.success(
          'Analysis Complete',
          `Risk category: ${result.prediction.risk_category} (Z-Score: ${result.prediction.z_score.toFixed(2)})`
        );
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Analysis failed';
      setError(errorMessage);
      toast.error('Analysis Failed', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleBulkAnalysis = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    try {
      const result = await uploadFinancialData(selectedFile);
      setBulkResult(result);
      toast.success(
        'Bulk Analysis Complete',
        `Analyzed ${result.total_companies} companies: ${result.summary.high_risk_count} high risk, ${result.summary.medium_risk_count} medium, ${result.summary.low_risk_count} low`
      );
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Upload failed';
      setError(errorMessage);
      toast.error('Upload Failed', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!singleResult) return;
    setDownloadingReport(true);
    try {
      const blob = await generateInsolvencyReport(
        formData.company_id || 'UNKNOWN',
        formData.company_name || 'Unknown Company',
        formData
      );
      const timestamp = new Date().toISOString().split('T')[0];
      downloadBlob(blob, `insolvency_report_${formData.company_id || 'company'}_${timestamp}.pdf`);
      toast.success('Report Downloaded', 'PDF report has been generated and downloaded');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate report';
      setError(errorMessage);
      toast.error('Report Generation Failed', errorMessage);
    } finally {
      setDownloadingReport(false);
    }
  };

  const handleReset = () => {
    setFormData(defaultFormData);
    setSingleResult(null);
    setBulkResult(null);
    setSelectedFile(null);
    setError(null);
    setEmployeeFile(null);
    setEmployeeResult(null);
    setSelectedWorkforceEmployee(null);
  };

  // Derived company health score from insolvency result
  const companyHealthScore = singleResult
    ? Math.round(100 * (1 - singleResult.prediction.probability_of_distress) * 100) / 100
    : null;

  const handleWorkforceAnalysis = async () => {
    if (!employeeFile || companyHealthScore === null) return;
    setEmployeeLoading(true);
    try {
      const result = await uploadEmployeeWithHealth(employeeFile, companyHealthScore);
      setEmployeeResult(result);
      // Store health context for Employee Scoring page
      localStorage.setItem('solvency-insight-health-context', JSON.stringify({
        company_health_score: companyHealthScore,
        company_name: singleResult?.prediction.company_name || 'Unknown',
        timestamp: Date.now(),
      }));
      toast.success(
        'Workforce Impact Complete',
        `Analyzed ${result.total_employees} employees with company health score ${companyHealthScore.toFixed(1)}`
      );
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Workforce analysis failed';
      setError(msg);
      toast.error('Workforce Analysis Failed', msg);
    } finally {
      setEmployeeLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-dark-900 border border-dark-700 rounded-xl p-6 shadow-lg">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-primary-500/20 rounded-xl flex items-center justify-center">
              <Building2 className="w-6 h-6 text-primary-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Insolvency Risk Analysis</h1>
              <p className="text-dark-400 mt-1">
                Analyze company financial data using Altman Z-Score and ML models
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {
                setMode('single');
                setBulkResult(null);
              }}
              className={`btn ${mode === 'single' ? 'btn-primary' : 'btn-secondary'}`}
            >
              Single Company
            </button>
            <button
              onClick={() => {
                setMode('bulk');
                setSingleResult(null);
              }}
              className={`btn ${mode === 'bulk' ? 'btn-primary' : 'btn-secondary'}`}
            >
              <Upload className="w-4 h-4 mr-2" />
              Bulk Upload
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex flex-wrap items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <p className="text-red-400 flex-1 min-w-0">{error}</p>
          <div className="flex gap-2">
            <button
              onClick={() => setError(null)}
              className="btn btn-ghost btn-sm text-red-400 hover:text-red-300"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Single Company Mode */}
      {mode === 'single' && !singleResult && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* File Upload or Manual Entry */}
          <div className="bg-dark-900 border border-dark-700 rounded-xl p-6 shadow-lg">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Upload className="w-5 h-5 text-primary-400" />
              Upload CSV (Optional)
            </h2>
            <FileUpload
              onFileSelect={setSelectedFile}
              selectedFile={selectedFile}
              onClear={() => setSelectedFile(null)}
              disabled={loading}
            />
            <p className="text-sm text-dark-500 mt-3">
              Or fill in the form below for manual entry
            </p>

            <div className="mt-6 border-t border-dark-700 pt-6">
              <h3 className="text-sm font-medium text-white mb-4">Company Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Company ID</label>
                  <input
                    type="text"
                    className={`input ${error ? 'input-error' : ''}`}
                    value={formData.company_id || ''}
                    onChange={(e) => handleInputChange('company_id', e.target.value)}
                    placeholder="COMP_001"
                  />
                </div>
                <div>
                  <label className="label">Company Name</label>
                  <input
                    type="text"
                    className="input"
                    value={formData.company_name || ''}
                    onChange={(e) => handleInputChange('company_name', e.target.value)}
                    placeholder="Example Corp"
                  />
                </div>
              </div>
            </div>

            <div className="mt-6 border-t border-dark-700 pt-6">
              <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
                Altman Z-Score Components
                <InfoTooltip content={TOOLTIP_COPY.ALTMAN_Z_SCORE} title="Altman Z-Score" />
                <span className="text-xs text-dark-500 font-normal">(Required)</span>
              </h3>
              <div className="space-y-4">
                <NumberInput
                  label="Working Capital / Total Assets"
                  value={formData.working_capital_to_total_assets}
                  onChange={(v) => handleInputChange('working_capital_to_total_assets', v)}
                  tooltip="(Current Assets - Current Liabilities) / Total Assets"
                />
                <NumberInput
                  label="Retained Earnings / Total Assets"
                  value={formData.retained_earnings_to_total_assets}
                  onChange={(v) => handleInputChange('retained_earnings_to_total_assets', v)}
                  tooltip="Accumulated retained earnings divided by total assets"
                />
                <NumberInput
                  label="EBIT / Total Assets"
                  value={formData.ebit_to_total_assets}
                  onChange={(v) => handleInputChange('ebit_to_total_assets', v)}
                  tooltip="Earnings Before Interest and Taxes / Total Assets"
                />
                <NumberInput
                  label="Market Value Equity / Total Liabilities"
                  value={formData.market_value_equity_to_total_liabilities}
                  onChange={(v) => handleInputChange('market_value_equity_to_total_liabilities', v)}
                  tooltip="Market cap (or book value for private) / Total Liabilities"
                />
                <NumberInput
                  label="Sales / Total Assets"
                  value={formData.sales_to_total_assets}
                  onChange={(v) => handleInputChange('sales_to_total_assets', v)}
                  tooltip="Total Revenue / Total Assets"
                />
              </div>
            </div>
          </div>

          {/* Additional Ratios */}
          <div className="bg-dark-900 border border-dark-700 rounded-xl p-6 shadow-lg">
            <h2 className="text-lg font-semibold text-white mb-4">Additional Financial Ratios</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <NumberInput
                  label="Current Ratio"
                  value={formData.current_ratio}
                  onChange={(v) => handleInputChange('current_ratio', v)}
                  tooltip="Current Assets / Current Liabilities"
                />
                <NumberInput
                  label="Quick Ratio"
                  value={formData.quick_ratio}
                  onChange={(v) => handleInputChange('quick_ratio', v)}
                  tooltip="(Current Assets - Inventory) / Current Liabilities"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <NumberInput
                  label="Debt to Equity"
                  value={formData.debt_to_equity}
                  onChange={(v) => handleInputChange('debt_to_equity', v)}
                  tooltip="Total Debt / Total Equity"
                />
                <NumberInput
                  label="Interest Coverage"
                  value={formData.interest_coverage}
                  onChange={(v) => handleInputChange('interest_coverage', v)}
                  tooltip="EBIT / Interest Expense"
                />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <NumberInput
                  label="Net Profit Margin"
                  value={formData.net_profit_margin}
                  onChange={(v) => handleInputChange('net_profit_margin', v)}
                  tooltip="Net Income / Revenue"
                />
                <NumberInput
                  label="Return on Assets"
                  value={formData.return_on_assets}
                  onChange={(v) => handleInputChange('return_on_assets', v)}
                  tooltip="Net Income / Total Assets"
                />
                <NumberInput
                  label="Return on Equity"
                  value={formData.return_on_equity}
                  onChange={(v) => handleInputChange('return_on_equity', v)}
                  tooltip="Net Income / Shareholders Equity"
                />
              </div>
            </div>

            {/* Z-Score Info */}
            <div className="mt-6 p-4 bg-dark-800/50 rounded-lg border border-dark-700">
              <div className="flex items-start gap-3">
                <Info className="w-5 h-5 text-primary-400 mt-0.5" />
                <div>
                  <h4 className="text-sm font-medium text-white">Altman Z-Score Zones</h4>
                  <div className="mt-2 flex flex-wrap gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-green-500" />
                      <span className="text-dark-300">Safe Zone (&gt;2.99)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-yellow-500" />
                      <span className="text-dark-300">Grey Zone (1.81-2.99)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-red-500" />
                      <span className="text-dark-300">Distress Zone (&lt;1.81)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <AnimatedButton
              onClick={handleSingleAnalysis}
              disabled={loading}
              loading={loading}
              className="w-full mt-6 py-3 text-lg inline-flex items-center justify-center gap-2"
            >
              <TrendingUp className="w-5 h-5" />
              {selectedFile ? `Analyze ${selectedFile.name}` : 'Analyze Company'}
            </AnimatedButton>
          </div>
        </div>
      )}

      {/* Bulk Upload Mode */}
      {mode === 'bulk' && !bulkResult && (
        <div className="bg-dark-900 border border-dark-700 rounded-xl p-6 shadow-lg">
          <h2 className="text-lg font-semibold text-white mb-4">Upload Company Data (CSV)</h2>
          <FileUpload
            onFileSelect={setSelectedFile}
            selectedFile={selectedFile}
            onClear={() => setSelectedFile(null)}
            disabled={loading}
          />
          <p className="text-sm text-dark-500 mt-3">
            CSV must include company_id, company_name, and financial ratio columns.
          </p>
          <div className="flex flex-wrap gap-2 mt-4">
            <button
              onClick={handleBulkAnalysis}
              disabled={!selectedFile || loading}
              className="btn btn-primary"
            >
              {loading ? 'Processing...' : 'Analyze All Companies'}
            </button>
            <button
              type="button"
              onClick={() => downloadCompanyTemplate()}
              className="btn btn-secondary"
            >
              <Download className="w-4 h-4 mr-2" />
              Download CSV template
            </button>
          </div>
        </div>
      )}

      {/* Bulk mode empty state: no result yet */}
      {mode === 'bulk' && !loading && !bulkResult && (
        <div className="bg-dark-900 border border-dark-700 rounded-xl p-8 text-center">
          <Building2 className="w-12 h-12 text-dark-500 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-white mb-2">No bulk results yet</h3>
          <p className="text-dark-400 text-sm max-w-md mx-auto mb-4">
            Upload a CSV file with company financial data above, then click &quot;Analyze All Companies&quot; to see risk predictions for each company.
          </p>
          <p className="text-dark-500 text-xs">
            CSV must include company_id, company_name, and required financial ratio columns.
          </p>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="space-y-4">
          <LoadingSpinner message="Analyzing financial data..." />
          <div className="card flex flex-col sm:flex-row gap-6">
            <Skeleton className="h-40 w-40 rounded-full shrink-0" variant="circle" />
            <div className="flex-1 space-y-3">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          </div>
        </div>
      )}

      {/* Single Result Display */}
      {singleResult && !loading && (
        <div className="space-y-6 animate-fade-in">
          {/* Results Header with Actions */}
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h2 className="text-xl font-semibold text-white">
                Analysis Results: {formData.company_name || formData.company_id || 'Company'}
              </h2>
              <p className="text-dark-400 text-sm mt-1">
                Analysis completed at {new Date().toLocaleString()}
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleDownloadReport}
                disabled={downloadingReport}
                className="btn btn-primary"
              >
                {downloadingReport ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span className="ml-2">Generating...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Download Report
                  </>
                )}
              </button>
              <button onClick={handleReset} className="btn btn-secondary">
                <RefreshCw className="w-4 h-4 mr-2" />
                Analyze Another
              </button>
            </div>
          </div>

          {/* Main Results Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Risk Gauge */}
            <div className="bg-dark-900 border border-dark-700 rounded-xl p-6 shadow-lg flex flex-col items-center justify-center">
              <RiskGauge
                value={singleResult.prediction.probability_of_distress}
                label="Probability of Distress"
                size="lg"
                riskCategory={singleResult.prediction.risk_category}
              />
            </div>

            {/* Key Metrics */}
            <div className="bg-dark-900 border border-dark-700 rounded-xl p-6 shadow-lg lg:col-span-2">
              <h3 className="text-lg font-semibold text-white mb-4">Key Metrics</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <MetricCard
                  label="Risk Category"
                  badge={singleResult.prediction.risk_category}
                  tooltipContent={TOOLTIP_COPY.RISK_CATEGORY}
                />
                <MetricCard
                  label="Altman Z-Score"
                  value={singleResult.prediction.z_score.toFixed(2)}
                  subValue={singleResult.prediction.z_score_zone}
                  tooltipContent={TOOLTIP_COPY.Z_SCORE}
                />
                <MetricCard
                  label="Est. Time to Event"
                  value={
                    singleResult.prediction.estimated_time_to_event !== null
                      ? `${singleResult.prediction.estimated_time_to_event}`
                      : 'N/A'
                  }
                  subValue={singleResult.prediction.estimated_time_to_event !== null ? 'years' : ''}
                  icon={Clock}
                />
                <MetricCard
                  label="Distress Probability"
                  value={`${(singleResult.prediction.probability_of_distress * 100).toFixed(1)}%`}
                  tooltipContent={TOOLTIP_COPY.DISTRESS_PROBABILITY}
                />
              </div>

              {/* Z-Score Visual - scale 0 to 5 with ticks at 0, 1.81, 2.99, 5 */}
              <div className="mt-6 p-4 bg-dark-800/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-dark-400">Z-Score Position</span>
                  <span className="text-sm font-medium text-white">
                    {singleResult.prediction.z_score.toFixed(2)}
                  </span>
                </div>
                <div className="relative h-4 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-full">
                  <div
                    className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full border-2 border-dark-900 shadow-lg z-10"
                    style={{
                      left: `${Math.min(Math.max((singleResult.prediction.z_score / 5) * 100, 0), 100)}%`,
                      transform: 'translate(-50%, -50%)',
                    }}
                  />
                </div>
                <div className="relative mt-1 h-5 text-xs text-dark-500">
                  <span className="absolute left-0" style={{ transform: 'translateX(0)' }}>0</span>
                  <span className="absolute" style={{ left: `${(1.81 / 5) * 100}%`, transform: 'translateX(-50%)' }}>1.81</span>
                  <span className="absolute" style={{ left: `${(2.99 / 5) * 100}%`, transform: 'translateX(-50%)' }}>2.99</span>
                  <span className="absolute right-0" style={{ transform: 'translateX(0)' }}>5+</span>
                </div>
                <div className="flex justify-between mt-0.5 text-xs text-dark-500">
                  <span>High Risk</span>
                  <span>Safe</span>
                </div>
              </div>
            </div>
          </div>

          {/* Executive Summary */}
          {singleResult.prediction.executive_summary && (
            <div className="bg-primary-500/10 border border-primary-500/30 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-primary-300 mb-2">Executive Summary</h3>
              <p className="text-dark-200 text-sm leading-relaxed">
                {singleResult.prediction.executive_summary}
              </p>
            </div>
          )}

          {/* SHAP Explanation Chart — uses shared ShapChart component */}
          <ShapChart
            data={singleResult.explanation.top_risk_drivers}
            title="Top 10 Risk Drivers (SHAP Analysis)"
          />
        </div>
      )}

      {/* ================================================================ */}
      {/* Workforce Impact Analysis — bridges insolvency → employee models */}
      {/* ================================================================ */}
      {singleResult && !loading && companyHealthScore !== null && (
        <div className="space-y-4 animate-fade-in">
          <div className="bg-dark-900 border border-dark-700 rounded-xl p-6 shadow-lg">
            {/* Header with health score badge */}
            <div className="flex items-center justify-between flex-wrap gap-4 mb-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center">
                  <Users className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    Workforce Impact Analysis
                    <ArrowRight className="w-5 h-5 text-dark-500" />
                    <span className={`text-sm font-medium px-2.5 py-1 rounded-full border ${
                      companyHealthScore >= 70
                        ? 'bg-green-500/20 text-green-400 border-green-500/30'
                        : companyHealthScore >= 40
                        ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                        : 'bg-red-500/20 text-red-400 border-red-500/30'
                    }`}>
                      Health: {companyHealthScore.toFixed(1)}
                    </span>
                  </h2>
                  <p className="text-dark-400 mt-1">
                    Upload employee data to see how{' '}
                    {singleResult.prediction.company_name || 'this company'}&apos;s financial{' '}
                    {singleResult.prediction.risk_category === 'High' ? 'distress' :
                     singleResult.prediction.risk_category === 'Medium' ? 'uncertainty' : 'health'}{' '}
                    affects employee attrition predictions
                  </p>
                </div>
              </div>
            </div>

            {/* Connection explanation */}
            <div className={`rounded-lg p-3 mb-4 border ${
              companyHealthScore < 40
                ? 'bg-red-500/10 border-red-500/20'
                : companyHealthScore < 70
                ? 'bg-yellow-500/10 border-yellow-500/20'
                : 'bg-green-500/10 border-green-500/20'
            }`}>
              <p className="text-sm text-dark-300">
                <span className="font-semibold text-white">Model Integration: </span>
                The insolvency model computed a distress probability of{' '}
                <span className="font-medium text-white">
                  {(singleResult.prediction.probability_of_distress * 100).toFixed(1)}%
                </span>
                , which translates to a company health score of{' '}
                <span className="font-medium text-white">{companyHealthScore.toFixed(1)}/100</span>.
                {companyHealthScore < 40
                  ? ' This score will be injected into every employee record, significantly increasing predicted attrition due to pay uncertainty, potential layoffs, and reduced morale.'
                  : companyHealthScore < 70
                  ? ' This moderate score will influence employee attrition predictions, reflecting some financial uncertainty.'
                  : ' This healthy score will positively influence employee retention predictions.'}
              </p>
            </div>

            {/* Employee file upload */}
            <FileUpload
              onFileSelect={setEmployeeFile}
              selectedFile={employeeFile}
              onClear={() => { setEmployeeFile(null); setEmployeeResult(null); }}
              disabled={employeeLoading}
            />
            <div className="flex flex-wrap gap-2 mt-4">
              <button
                onClick={handleWorkforceAnalysis}
                disabled={!employeeFile || employeeLoading}
                className="btn btn-primary"
              >
                {employeeLoading ? 'Analyzing Workforce...' : 'Analyze Workforce Impact'}
              </button>
            </div>
          </div>

          {/* Employee Loading */}
          {employeeLoading && <LoadingSpinner message="Analyzing workforce with company health context..." />}

          {/* Employee Results */}
          {employeeResult && !employeeLoading && (
            <div className="space-y-4 animate-fade-in">
              {/* Impact banner */}
              <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4">
                <p className="text-purple-300 text-sm font-medium">
                  Company Health Score of {companyHealthScore.toFixed(1)} applied to all{' '}
                  {employeeResult.total_employees} employees from{' '}
                  {singleResult.prediction.company_name || 'the analyzed company'}
                </p>
              </div>

              {/* Summary stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-dark-900 border border-dark-700 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <Users className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs text-dark-400">Total Employees</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{employeeResult.total_employees}</p>
                </div>
                <div className="bg-dark-900 border border-red-500/20 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <UserX className="w-4 h-4 text-red-400" />
                    <span className="text-xs text-dark-400">High Attrition Risk</span>
                  </div>
                  <p className="text-2xl font-bold text-red-400">{employeeResult.summary.high_attrition_risk_count}</p>
                </div>
                <div className="bg-dark-900 border border-yellow-500/20 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle className="w-4 h-4 text-yellow-400" />
                    <span className="text-xs text-dark-400">Medium Risk</span>
                  </div>
                  <p className="text-2xl font-bold text-yellow-400">{employeeResult.summary.medium_attrition_risk_count}</p>
                </div>
                <div className="bg-dark-900 border border-green-500/20 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <UserCheck className="w-4 h-4 text-green-400" />
                    <span className="text-xs text-dark-400">Low Risk</span>
                  </div>
                  <p className="text-2xl font-bold text-green-400">{employeeResult.summary.low_attrition_risk_count}</p>
                </div>
              </div>

              {/* Key metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-dark-900 border border-dark-700 rounded-xl p-4">
                  <p className="text-xs text-dark-400 mb-1">Avg. Retention Score</p>
                  <p className={`text-3xl font-bold ${
                    employeeResult.summary.avg_retention_score >= 70 ? 'text-green-400' :
                    employeeResult.summary.avg_retention_score >= 40 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {employeeResult.summary.avg_retention_score.toFixed(1)}
                  </p>
                </div>
                <div className="bg-dark-900 border border-dark-700 rounded-xl p-4">
                  <p className="text-xs text-dark-400 mb-1">Avg. Attrition Probability</p>
                  <p className={`text-3xl font-bold ${
                    employeeResult.summary.avg_attrition_probability < 0.3 ? 'text-green-400' :
                    employeeResult.summary.avg_attrition_probability < 0.6 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {(employeeResult.summary.avg_attrition_probability * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Employee table */}
              <div className="bg-dark-900 border border-dark-700 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Employee Risk Breakdown ({employeeResult.total_employees} employees)
                  <span className="text-dark-400 text-sm font-normal ml-2">Click a row for details</span>
                </h3>
                <div className="overflow-x-auto max-h-96">
                  <table className="w-full">
                    <thead className="sticky top-0 bg-dark-900">
                      <tr className="border-b border-dark-700">
                        <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase">ID</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase">Name</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase">Department</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase">Retention</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase">Attrition Risk</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase">Co. Health</th>
                      </tr>
                    </thead>
                    <tbody>
                      {employeeResult.predictions.slice(0, 50).map((emp, i) => (
                        <tr key={emp.employee_id || i} className="border-b border-dark-800 hover:bg-dark-800/50 cursor-pointer" onClick={() => setSelectedWorkforceEmployee(emp)}>
                          <td className="py-2 px-4 text-dark-300 text-sm">{emp.employee_id || '-'}</td>
                          <td className="py-2 px-4 text-white text-sm font-medium">{emp.name || 'Unknown'}</td>
                          <td className="py-2 px-4 text-dark-300 text-sm">{emp.department || '-'}</td>
                          <td className="py-2 px-4">
                            <div className="flex items-center gap-2">
                              <div className="w-12 h-1.5 bg-dark-700 rounded-full overflow-hidden">
                                <div
                                  className={`h-full rounded-full ${
                                    emp.retention_score >= 70 ? 'bg-green-500' :
                                    emp.retention_score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                                  }`}
                                  style={{ width: `${emp.retention_score}%` }}
                                />
                              </div>
                              <span className="text-white text-sm">{emp.retention_score.toFixed(1)}</span>
                            </div>
                          </td>
                          <td className="py-2 px-4">
                            <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${
                              emp.attrition_risk === 'High' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                              emp.attrition_risk === 'Medium' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                              'bg-green-500/20 text-green-400 border-green-500/30'
                            }`}>
                              {emp.attrition_risk}
                            </span>
                          </td>
                          <td className="py-2 px-4">
                            <span className={`text-sm font-medium ${
                              (emp.company_health_score ?? 50) >= 70 ? 'text-green-400' :
                              (emp.company_health_score ?? 50) >= 40 ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                              {(emp.company_health_score ?? 50).toFixed(0)}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {employeeResult.predictions.length > 50 && (
                    <p className="text-dark-500 text-sm text-center mt-3">
                      Showing first 50 of {employeeResult.predictions.length} employees.{' '}
                      <a
                        href="/employees"
                        onClick={(e) => {
                          e.preventDefault();
                          // Pass health score context to Employee Scoring page
                          localStorage.setItem('solvency-insight-health-context', JSON.stringify({
                            company_health_score: companyHealthScore,
                            company_name: singleResult?.prediction.company_name || 'Unknown',
                            timestamp: Date.now(),
                          }));
                          window.location.href = '/employees';
                        }}
                        className="text-primary-400 hover:text-primary-300 underline"
                      >
                        Open full Employee Scoring
                      </a>{' '}
                      with health score pre-applied.
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Workforce Employee Detail Modal */}
      {selectedWorkforceEmployee && (
        <WorkforceEmployeeModal
          employee={selectedWorkforceEmployee}
          onClose={() => setSelectedWorkforceEmployee(null)}
        />
      )}

      {/* Bulk Result Display */}
      {bulkResult && !loading && (
        <div className="space-y-6 animate-fade-in">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">Bulk Analysis Results</h2>
            <button onClick={handleReset} className="btn btn-secondary">
              <RefreshCw className="w-4 h-4 mr-2" />
              Start Over
            </button>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <SummaryCard label="Total Companies" value={bulkResult.total_companies} />
            <SummaryCard label="High Risk" value={bulkResult.summary.high_risk_count} color="red" />
            <SummaryCard label="Medium Risk" value={bulkResult.summary.medium_risk_count} color="yellow" />
            <SummaryCard label="Low Risk" value={bulkResult.summary.low_risk_count} color="green" />
            <SummaryCard
              label="Avg. Probability"
              value={`${(bulkResult.summary.avg_probability * 100).toFixed(1)}%`}
            />
          </div>

          {/* Results Table */}
          <div className="bg-dark-900 border border-dark-700 rounded-xl p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-white mb-4">Company Results</h3>
            <DataTable
              data={bulkResult.predictions}
              columns={[
                { key: 'company_id', header: 'ID' },
                { key: 'company_name', header: 'Company' },
                {
                  key: 'probability_of_distress',
                  header: 'Risk Prob.',
                  render: (v) => `${(v * 100).toFixed(1)}%`,
                },
                {
                  key: 'risk_category',
                  header: 'Risk',
                  render: (v) => <RiskBadge risk={v} />,
                },
                {
                  key: 'z_score',
                  header: 'Z-Score',
                  render: (v) => v.toFixed(2),
                },
                {
                  key: 'z_score_zone',
                  header: 'Zone',
                  render: (v) => <ZoneBadge zone={v} />,
                },
              ]}
              searchPlaceholder="Search companies..."
            />
          </div>
        </div>
      )}
    </div>
  );
}

// Helper Components

/**
 * Props for the NumberInput component.
 */
interface NumberInputProps {
  /** Label text for the input field */
  label: string;
  /** Current numeric value */
  value: number;
  /** Callback when value changes */
  onChange: (value: number) => void;
  /** Step increment for number input */
  step?: number;
  /** Tooltip text explaining the metric */
  tooltip?: string;
}

/**
 * NumberInput component for financial ratio input with optional tooltip.
 * @param {NumberInputProps} props - Component props
 * @returns {JSX.Element} Styled number input with label
 */
function NumberInput({ label, value, onChange, step = 0.01, tooltip }: NumberInputProps) {
  return (
    <div>
      <label className="label flex items-center gap-1">
        {label}
        {tooltip && (
          <span className="group relative">
            <Info className="w-3 h-3 text-dark-500 cursor-help" />
            <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-dark-700 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
              {tooltip}
            </span>
          </span>
        )}
      </label>
      <input
        type="number"
        step={step}
        className="input"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
      />
    </div>
  );
}

/**
 * Props for the MetricCard component.
 */
interface MetricCardProps {
  /** Label describing the metric */
  label: string;
  /** Primary value to display */
  value?: string;
  /** Secondary value or unit */
  subValue?: string;
  /** Risk badge to display instead of value */
  badge?: 'Low' | 'Medium' | 'High';
  /** Optional icon component */
  icon?: React.ElementType;
  /** Optional tooltip explanation (plain English) */
  tooltipContent?: string;
}

/**
 * MetricCard component displaying a single metric with optional icon or risk badge.
 * @param {MetricCardProps} props - Component props
 * @returns {JSX.Element} Styled metric card
 */
function MetricCard({ label, value, subValue, badge, icon: Icon, tooltipContent }: MetricCardProps) {
  return (
    <div className="bg-dark-800/50 rounded-lg p-4 border border-dark-700">
      <p className="text-xs text-dark-400 mb-2 flex items-center gap-1">
        {label}
        {tooltipContent && <InfoTooltip content={tooltipContent} />}
      </p>
      {badge ? (
        <RiskBadge risk={badge} large />
      ) : (
        <div className="flex items-center gap-2">
          {Icon && <Icon className="w-5 h-5 text-primary-400" />}
          <div>
            <p className="text-xl font-bold text-white">{value}</p>
            {subValue && <p className="text-xs text-dark-400">{subValue}</p>}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * RiskBadge component displaying a color-coded risk level.
 * @param {{ risk: string; large?: boolean }} props - Risk level and size flag
 * @returns {JSX.Element} Styled risk badge
 */
function RiskBadge({ risk, large = false }: { risk: string; large?: boolean }) {
  const classes = {
    Low: 'bg-green-500/20 text-green-400 border-green-500/30',
    Medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    High: 'bg-red-500/20 text-red-400 border-red-500/30',
  }[risk] || 'bg-dark-700 text-dark-300 border-dark-600';

  return (
    <span
      className={`inline-flex items-center rounded-full border font-medium ${classes} ${
        large ? 'px-4 py-2 text-lg' : 'px-2.5 py-1 text-xs'
      }`}
    >
      {risk}
    </span>
  );
}

/**
 * ZoneBadge component displaying Altman Z-Score zone classification.
 * @param {{ zone: string }} props - Zone classification (Safe, Grey, Distress)
 * @returns {JSX.Element} Styled zone badge
 */
function ZoneBadge({ zone }: { zone: string }) {
  const classes = {
    Safe: 'bg-green-500/20 text-green-400 border-green-500/30',
    Grey: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    Distress: 'bg-red-500/20 text-red-400 border-red-500/30',
  }[zone] || 'bg-dark-700 text-dark-300 border-dark-600';

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${classes}`}>
      {zone}
    </span>
  );
}

/**
 * Props for the SummaryCard component.
 */
interface SummaryCardProps {
  /** Label describing the summary stat */
  label: string;
  /** Value to display */
  value: string | number;
  /** Optional accent color for the card */
  color?: 'red' | 'yellow' | 'green';
}

/**
 * SummaryCard component displaying a bulk analysis summary statistic.
 * @param {SummaryCardProps} props - Component props
 * @returns {JSX.Element} Styled summary card
 */
function SummaryCard({ label, value, color }: SummaryCardProps) {
  const colorClasses = {
    red: 'border-red-500/30 bg-red-500/10',
    yellow: 'border-yellow-500/30 bg-yellow-500/10',
    green: 'border-green-500/30 bg-green-500/10',
  };

  return (
    <div
      className={`rounded-xl border p-4 ${
        color ? colorClasses[color] : 'border-dark-700 bg-dark-800/50'
      }`}
    >
      <p className="text-sm text-dark-400">{label}</p>
      <p className="text-2xl font-bold text-white mt-1">{value}</p>
    </div>
  );
}

function WorkforceEmployeeModal({ employee, onClose }: { employee: EmployeePrediction; onClose: () => void }) {
  const healthScore = employee.company_health_score ?? 50;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-dark-900 border border-dark-700 rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-dark-700">
          <div>
            <h2 className="text-xl font-semibold text-white">
              {employee.name || 'Employee Details'}
            </h2>
            <p className="text-dark-400 text-sm">
              {employee.employee_id} &bull; {employee.department}
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-dark-800 rounded-lg transition-colors">
            <X className="w-5 h-5 text-dark-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="bg-dark-800/50 rounded-lg p-4 border border-dark-700">
                <p className="text-xs text-dark-400 mb-1">Retention Score</p>
                <p className={`text-2xl font-bold ${
                  employee.retention_score >= 70 ? 'text-green-400' :
                  employee.retention_score >= 40 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {employee.retention_score.toFixed(1)}
                </p>
              </div>
              <div className="bg-dark-800/50 rounded-lg p-4 border border-dark-700">
                <p className="text-xs text-dark-400 mb-1">Attrition Probability</p>
                <p className="text-2xl font-bold text-white">
                  {(employee.attrition_probability * 100).toFixed(1)}%
                </p>
              </div>
              <div className="bg-dark-800/50 rounded-lg p-4 border border-dark-700">
                <p className="text-xs text-dark-400 mb-1">Attrition Risk</p>
                <RiskBadge risk={employee.attrition_risk} large />
              </div>
              <div className="bg-dark-800/50 rounded-lg p-4 border border-dark-700">
                <p className="text-xs text-dark-400 mb-1">Layoff Priority</p>
                <RiskBadge risk={employee.layoff_priority} large />
              </div>
              <div className="bg-dark-800/50 rounded-lg p-4 border border-dark-700">
                <p className="text-xs text-dark-400 mb-1">Company Health</p>
                <p className={`text-2xl font-bold ${
                  healthScore >= 70 ? 'text-green-400' :
                  healthScore >= 40 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {healthScore.toFixed(1)}
                </p>
                <p className="text-[10px] text-dark-500 mt-0.5">
                  {healthScore >= 70 ? 'Healthy' : healthScore >= 40 ? 'At Risk' : 'Distressed'}
                </p>
              </div>
            </div>

            {/* Company Health Impact */}
            {healthScore !== 50 && (
              <div className={`rounded-lg p-3 border ${
                healthScore < 40 ? 'bg-red-500/10 border-red-500/20' :
                healthScore < 70 ? 'bg-yellow-500/10 border-yellow-500/20' :
                'bg-green-500/10 border-green-500/20'
              }`}>
                <p className="text-sm text-dark-300">
                  <span className="font-medium text-white">Company Health Factor: </span>
                  {healthScore < 40
                    ? 'This employee\'s company is in financial distress, which significantly increases predicted attrition risk due to pay uncertainty, potential layoffs, and reduced morale.'
                    : healthScore < 70
                    ? 'The company shows moderate financial health. Some financial uncertainty may be contributing to this employee\'s attrition risk.'
                    : 'The company is financially healthy, which contributes positively to employee retention.'}
                </p>
              </div>
            )}

            {/* Retention Gauge */}
            <div className="flex justify-center py-4">
              <RiskGauge
                value={employee.retention_score}
                label="Retention Score"
                size="lg"
                showPercentage={true}
                riskCategory={
                  employee.retention_score >= 70 ? 'Low' :
                  employee.retention_score >= 40 ? 'Medium' : 'High'
                }
              />
            </div>

            {/* Recommendations */}
            <div className="bg-dark-800/30 rounded-lg p-4 border border-dark-700">
              <h3 className="text-lg font-semibold text-white mb-3">Recommendations</h3>
              <div className="space-y-2">
                {employee.attrition_risk === 'High' && (
                  <>
                    <RecommendationItem text="Schedule one-on-one meeting to discuss career goals and concerns" priority="high" />
                    <RecommendationItem text="Review compensation package against market rates" priority="high" />
                    <RecommendationItem text="Explore opportunities for role expansion or project leadership" priority="medium" />
                    {healthScore < 40 && (
                      <RecommendationItem text="Provide transparent communication about company financial recovery plans to reduce uncertainty" priority="high" />
                    )}
                  </>
                )}
                {employee.attrition_risk === 'Medium' && (
                  <>
                    <RecommendationItem text="Check in regularly to monitor job satisfaction" priority="medium" />
                    <RecommendationItem text="Consider professional development opportunities" priority="medium" />
                    {healthScore < 40 && (
                      <RecommendationItem text="Address financial uncertainty concerns proactively to prevent escalation" priority="high" />
                    )}
                  </>
                )}
                {employee.attrition_risk === 'Low' && (
                  <>
                    <RecommendationItem text="Continue current engagement strategies" priority="low" />
                    <RecommendationItem text="Consider for mentorship or leadership roles" priority="low" />
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function RecommendationItem({ text, priority }: { text: string; priority: 'high' | 'medium' | 'low' }) {
  const colors = {
    high: 'border-red-500/30 bg-red-500/10',
    medium: 'border-yellow-500/30 bg-yellow-500/10',
    low: 'border-green-500/30 bg-green-500/10',
  };
  return (
    <div className={`p-3 rounded-lg border ${colors[priority]}`}>
      <p className="text-dark-200 text-sm">{text}</p>
    </div>
  );
}

