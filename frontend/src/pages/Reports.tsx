/**
 * @fileoverview Reports page component.
 * Provides PDF report generation for insolvency analysis and layoff simulations.
 */

import { useState, useCallback } from 'react';
import { FileText, Download, Building2, Users, AlertTriangle, CheckCircle, Upload, Edit3 } from 'lucide-react';
import { generateInsolvencyReport, generateLayoffReport, downloadBlob, downloadCompanyTemplate } from '../services/api';
import type { CompanyFinancialData } from '../types';
import { FileUpload, LoadingSpinner } from '../components';

/** Type of report to generate */
type ReportType = 'insolvency' | 'layoff';

/** Input mode for insolvency report: manual form or CSV upload */
type InsolvencyInputMode = 'manual' | 'csv';

const NUMERIC_KEYS: (keyof CompanyFinancialData)[] = [
  'working_capital_to_total_assets',
  'retained_earnings_to_total_assets',
  'ebit_to_total_assets',
  'market_value_equity_to_total_liabilities',
  'sales_to_total_assets',
  'current_ratio',
  'quick_ratio',
  'debt_to_equity',
  'interest_coverage',
  'net_profit_margin',
  'return_on_assets',
  'return_on_equity',
];

/**
 * Parse a single-company CSV file into company id, name, and financial data.
 * Expects one header row and one data row; column names must match schema (snake_case).
 */
function parseSingleCompanyCsv(text: string): { companyId: string; companyName: string; companyData: CompanyFinancialData } {
  const lines = text.trim().split(/\r?\n/).filter((line) => line.trim());
  if (lines.length < 2) throw new Error('CSV must have a header row and at least one data row');
  const parseRow = (row: string): string[] =>
    row.split(',').map((cell) => cell.replace(/^"|"$/g, '').trim());
  const headers = parseRow(lines[0]);
  const values = parseRow(lines[1]);
  const record: Record<string, string> = {};
  headers.forEach((h, i) => {
    record[h] = values[i] ?? '';
  });
  const companyId = record.company_id ?? '';
  const companyName = record.company_name ?? '';
  const companyData: CompanyFinancialData = {
    company_id: companyId,
    company_name: companyName,
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
  for (const key of NUMERIC_KEYS) {
    const raw = record[key];
    if (raw !== undefined && raw !== '') {
      const num = parseFloat(raw);
      if (!Number.isNaN(num)) (companyData as unknown as Record<string, number>)[key] = num;
    }
  }
  return { companyId, companyName, companyData };
}

const defaultCompanyData: CompanyFinancialData = {
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
 * Reports component for generating and downloading PDF reports.
 * Supports insolvency risk assessment reports and layoff simulation reports.
 * @returns {JSX.Element} The rendered reports page
 */
export default function Reports() {
  const [reportType, setReportType] = useState<ReportType>('insolvency');

  // Insolvency report state
  const [insolvencyInputMode, setInsolvencyInputMode] = useState<InsolvencyInputMode>('manual');
  const [companyId, setCompanyId] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [companyData, setCompanyData] = useState<CompanyFinancialData>(defaultCompanyData);
  const [insolvencyFile, setInsolvencyFile] = useState<File | null>(null);
  const [parsedInsolvency, setParsedInsolvency] = useState<{
    companyId: string;
    companyName: string;
    companyData: CompanyFinancialData;
  } | null>(null);

  // Layoff report state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [budgetCutPercent, setBudgetCutPercent] = useState(15);
  const [minPerDept, setMinPerDept] = useState(1);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleInsolvencyFileSelect = useCallback((file: File | null) => {
    setInsolvencyFile(file);
    setParsedInsolvency(null);
    setError(null);
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const text = reader.result as string;
        const parsed = parseSingleCompanyCsv(text);
        setParsedInsolvency(parsed);
      } catch (e) {
        setParsedInsolvency(null);
        setError(e instanceof Error ? e.message : 'Invalid CSV format. Use a single-company CSV with header row.');
      }
    };
    reader.onerror = () => setError('Failed to read file');
    reader.readAsText(file, 'UTF-8');
  }, []);

  const handleCompanyDataChange = (field: keyof CompanyFinancialData, value: number) => {
    setCompanyData((prev) => ({ ...prev, [field]: value }));
  };

  const handleGenerateInsolvencyReport = async () => {
    const useCsv = insolvencyInputMode === 'csv' && parsedInsolvency;
    const id = useCsv ? parsedInsolvency.companyId : companyId;
    const name = useCsv ? parsedInsolvency.companyName : companyName;
    const data = useCsv ? parsedInsolvency.companyData : companyData;

    if (!id || !name) {
      setError(useCsv ? 'Upload a valid single-company CSV with company_id and company_name' : 'Please provide company ID and name');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const blob = await generateInsolvencyReport(id, name, data);
      const timestamp = new Date().toISOString().split('T')[0];
      downloadBlob(blob, `insolvency_report_${id}_${timestamp}.pdf`);
      setSuccess('Report generated and downloaded successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const insolvencyCanGenerate =
    insolvencyInputMode === 'csv'
      ? Boolean(parsedInsolvency?.companyId && parsedInsolvency?.companyName)
      : Boolean(companyId && companyName);

  const handleGenerateLayoffReport = async () => {
    if (!selectedFile) {
      setError('Please upload an employee data file');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const blob = await generateLayoffReport(selectedFile, budgetCutPercent, minPerDept);
      const timestamp = new Date().toISOString().split('T')[0];
      downloadBlob(blob, `layoff_report_${timestamp}.pdf`);
      setSuccess('Report generated and downloaded successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center gap-4">
          <FileText className="w-6 h-6 text-primary-400" />
          <h2 className="text-xl font-semibold text-white">Generate Reports</h2>
        </div>
        <p className="text-dark-400 mt-2">
          Generate professional PDF reports for insolvency analysis or layoff simulations.
        </p>

        {/* Report Type Selector */}
        <div className="flex gap-2 mt-4">
          <button
            onClick={() => {
              setReportType('insolvency');
              setError(null);
              setSuccess(null);
            }}
            className={`btn ${reportType === 'insolvency' ? 'btn-primary' : 'btn-secondary'}`}
          >
            <Building2 className="w-4 h-4 mr-2" />
            Insolvency Report
          </button>
          <button
            onClick={() => {
              setReportType('layoff');
              setError(null);
              setSuccess(null);
            }}
            className={`btn ${reportType === 'layoff' ? 'btn-primary' : 'btn-secondary'}`}
          >
            <Users className="w-4 h-4 mr-2" />
            Layoff Report
          </button>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-green-900/20 border border-green-700 rounded-lg p-4 flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
          <p className="text-green-400">{success}</p>
        </div>
      )}

      {/* Insolvency Report Form */}
      {reportType === 'insolvency' && (
        <div className="space-y-6">
          {/* Input mode toggle: Manual vs CSV (same pattern as Layoff upload) */}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => {
                setInsolvencyInputMode('manual');
                setError(null);
              }}
              className={`btn ${insolvencyInputMode === 'manual' ? 'btn-primary' : 'btn-secondary'}`}
            >
              <Edit3 className="w-4 h-4 mr-2" />
              Manual entry
            </button>
            <button
              type="button"
              onClick={() => {
                setInsolvencyInputMode('csv');
                setError(null);
              }}
              className={`btn ${insolvencyInputMode === 'csv' ? 'btn-primary' : 'btn-secondary'}`}
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload CSV
            </button>
          </div>

          {insolvencyInputMode === 'manual' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card">
                <h3 className="card-header">Company Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="label">Company ID *</label>
                    <input
                      type="text"
                      className="input"
                      value={companyId}
                      onChange={(e) => setCompanyId(e.target.value)}
                      placeholder="COMP_001"
                    />
                  </div>
                  <div>
                    <label className="label">Company Name *</label>
                    <input
                      type="text"
                      className="input"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="Example Corp"
                    />
                  </div>
                </div>

                <h4 className="text-sm font-medium text-white mt-6 mb-3">Altman Z-Score Components</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <NumberInput
                    label="Working Capital / Total Assets"
                    value={companyData.working_capital_to_total_assets}
                    onChange={(v) => handleCompanyDataChange('working_capital_to_total_assets', v)}
                  />
                  <NumberInput
                    label="Retained Earnings / Total Assets"
                    value={companyData.retained_earnings_to_total_assets}
                    onChange={(v) => handleCompanyDataChange('retained_earnings_to_total_assets', v)}
                  />
                  <NumberInput
                    label="EBIT / Total Assets"
                    value={companyData.ebit_to_total_assets}
                    onChange={(v) => handleCompanyDataChange('ebit_to_total_assets', v)}
                  />
                  <NumberInput
                    label="Market Equity / Total Liabilities"
                    value={companyData.market_value_equity_to_total_liabilities}
                    onChange={(v) => handleCompanyDataChange('market_value_equity_to_total_liabilities', v)}
                  />
                  <NumberInput
                    label="Sales / Total Assets"
                    value={companyData.sales_to_total_assets}
                    onChange={(v) => handleCompanyDataChange('sales_to_total_assets', v)}
                  />
                </div>
              </div>

              <div className="card">
                <h3 className="card-header">Additional Financial Ratios</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <NumberInput
                    label="Current Ratio"
                    value={companyData.current_ratio}
                    onChange={(v) => handleCompanyDataChange('current_ratio', v)}
                  />
                  <NumberInput
                    label="Quick Ratio"
                    value={companyData.quick_ratio}
                    onChange={(v) => handleCompanyDataChange('quick_ratio', v)}
                  />
                  <NumberInput
                    label="Debt to Equity"
                    value={companyData.debt_to_equity}
                    onChange={(v) => handleCompanyDataChange('debt_to_equity', v)}
                  />
                  <NumberInput
                    label="Interest Coverage"
                    value={companyData.interest_coverage}
                    onChange={(v) => handleCompanyDataChange('interest_coverage', v)}
                  />
                  <NumberInput
                    label="Net Profit Margin"
                    value={companyData.net_profit_margin}
                    onChange={(v) => handleCompanyDataChange('net_profit_margin', v)}
                  />
                  <NumberInput
                    label="Return on Assets"
                    value={companyData.return_on_assets}
                    onChange={(v) => handleCompanyDataChange('return_on_assets', v)}
                  />
                  <NumberInput
                    label="Return on Equity"
                    value={companyData.return_on_equity}
                    onChange={(v) => handleCompanyDataChange('return_on_equity', v)}
                  />
                </div>

                <button
                  onClick={handleGenerateInsolvencyReport}
                  disabled={loading || !insolvencyCanGenerate}
                  className="btn btn-primary w-full mt-6"
                >
                  {loading ? (
                    'Generating...'
                  ) : (
                    <>
                      <Download className="w-4 h-4 mr-2" />
                      Generate PDF Report
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {insolvencyInputMode === 'csv' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="card lg:col-span-2">
                <h3 className="card-header">Upload Company Data (CSV)</h3>
                <FileUpload
                  onFileSelect={handleInsolvencyFileSelect}
                  selectedFile={insolvencyFile}
                  onClear={() => handleInsolvencyFileSelect(null)}
                  disabled={loading}
                />
                <p className="text-sm text-dark-500 mt-2">
                  Single-company CSV with header: company_id, company_name, and financial ratios (e.g. working_capital_to_total_assets, retained_earnings_to_total_assets, etc.).
                </p>
                <button
                  type="button"
                  onClick={downloadCompanyTemplate}
                  className="btn btn-ghost btn-sm mt-2 text-primary-400 hover:text-primary-300"
                >
                  Download CSV template
                </button>
              </div>

              <div className="card">
                <h3 className="card-header">Report</h3>
                {parsedInsolvency ? (
                  <div className="space-y-4">
                    <div>
                      <p className="text-xs text-dark-500">Company</p>
                      <p className="text-white font-medium">{parsedInsolvency.companyName || '—'}</p>
                      <p className="text-dark-400 text-sm">{parsedInsolvency.companyId || '—'}</p>
                    </div>
                    <p className="text-sm text-dark-400">
                      Data loaded from CSV. Generate the PDF report below.
                    </p>
                    <button
                      onClick={handleGenerateInsolvencyReport}
                      disabled={loading || !insolvencyCanGenerate}
                      className="btn btn-primary w-full"
                    >
                      {loading ? (
                        'Generating...'
                      ) : (
                        <>
                          <Download className="w-4 h-4 mr-2" />
                          Generate PDF Report
                        </>
                      )}
                    </button>
                  </div>
                ) : (
                  <p className="text-dark-500 text-sm">
                    Upload a single-company CSV to generate an insolvency report.
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Layoff Report Form */}
      {reportType === 'layoff' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="card lg:col-span-2">
            <h3 className="card-header">Upload Employee Data</h3>
            <FileUpload
              onFileSelect={setSelectedFile}
              selectedFile={selectedFile}
              onClear={() => setSelectedFile(null)}
              disabled={loading}
            />
            <p className="text-sm text-dark-500 mt-2">
              CSV must contain: employee_id, name, department, monthly_income, and performance metrics
            </p>
          </div>

          <div className="card">
            <h3 className="card-header">Simulation Parameters</h3>
            <div className="space-y-4">
              <div>
                <label className="label">Budget Cut Target (%)</label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min={5}
                    max={50}
                    value={budgetCutPercent}
                    onChange={(e) => setBudgetCutPercent(parseInt(e.target.value))}
                    className="flex-1 accent-primary-500"
                  />
                  <span className="text-white font-bold text-xl w-16 text-right">
                    {budgetCutPercent}%
                  </span>
                </div>
              </div>

              <div>
                <label className="label">Minimum per Department</label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  className="input"
                  value={minPerDept}
                  onChange={(e) => setMinPerDept(parseInt(e.target.value) || 1)}
                />
              </div>

              <button
                onClick={handleGenerateLayoffReport}
                disabled={loading || !selectedFile}
                className="btn btn-primary w-full"
              >
                {loading ? (
                  'Generating...'
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Generate PDF Report
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && <LoadingSpinner message="Generating report..." />}

      {/* Report Info */}
      <div className="card">
        <h3 className="card-header">Report Contents</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-white font-medium mb-3 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-primary-400" />
              Insolvency Report Includes:
            </h4>
            <ul className="space-y-2 text-sm text-dark-300">
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Company identification and report date
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Overall risk score with color-coded indicator
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Altman Z-Score analysis and interpretation
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Estimated time to bankruptcy event
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Top 10 risk drivers with SHAP values
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Personalized recommendations
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-medium mb-3 flex items-center gap-2">
              <Users className="w-4 h-4 text-primary-400" />
              Layoff Report Includes:
            </h4>
            <ul className="space-y-2 text-sm text-dark-300">
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Simulation parameters and constraints
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Summary statistics and savings analysis
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Complete list of layoff recommendations
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Retention scores for each employee
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Department-wise impact breakdown
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                Cost savings projections
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

interface NumberInputProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  step?: number;
}

function NumberInput({ label, value, onChange, step = 0.01 }: NumberInputProps) {
  return (
    <div>
      <label className="label">{label}</label>
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
