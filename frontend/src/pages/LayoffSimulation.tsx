/**
 * @fileoverview Layoff Simulation page component.
 * Provides workforce optimization simulation based on budget constraints and retention scores.
 */

import { useState, useMemo } from 'react';
import {
  Scissors,
  AlertTriangle,
  DollarSign,
  Users,
  Building,
  Download,
  FileSpreadsheet,
  RefreshCw,
  Shield,
  TrendingDown,
  ChevronDown,
  ChevronUp,
  Check,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { simulateLayoffs, generateLayoffReport, downloadBlob } from '../services/api';
import type { LayoffSimulationResponse, LayoffRecommendation } from '../types';
import { FileUpload, LoadingSpinner } from '../components';
import { CHART_TOOLTIP_CONTENT_STYLE } from '../constants/chartStyles';
import { useToast } from '../context/ToastContext';

/** Color palette for department charts */
const COLORS = ['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#22c55e', '#ef4444', '#64748b'];

/**
 * LayoffSimulation component for simulating workforce reduction scenarios.
 * Allows configuration of budget cut percentage and minimum employees per department.
 * Displays recommendations with cost analysis and department breakdown.
 * @returns {JSX.Element} The rendered layoff simulation page
 */
export default function LayoffSimulation() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [budgetCutPercent, setBudgetCutPercent] = useState(15);
  const [minPerDept, setMinPerDept] = useState(1);
  const [protectCritical, setProtectCritical] = useState(false);
  const [result, setResult] = useState<LayoffSimulationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [excludedEmployees, setExcludedEmployees] = useState<Set<string>>(new Set());
  const [downloadingReport, setDownloadingReport] = useState(false);
  const toast = useToast();

  const handleSimulation = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    setExcludedEmployees(new Set());
    try {
      const response = await simulateLayoffs(selectedFile, budgetCutPercent, minPerDept);
      setResult(response);
      toast.success(
        'Simulation Complete',
        `${response.employees_affected} employees affected, saving $${response.actual_monthly_savings.toLocaleString()}/month`
      );
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Simulation failed';
      setError(errorMessage);
      toast.error('Simulation Failed', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!selectedFile || !result) return;
    setDownloadingReport(true);
    try {
      const blob = await generateLayoffReport(selectedFile, budgetCutPercent, minPerDept);
      const timestamp = new Date().toISOString().split('T')[0];
      downloadBlob(blob, `layoff_simulation_report_${timestamp}.pdf`);
      toast.success('Report Downloaded', 'PDF report has been generated and downloaded');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate report';
      setError(errorMessage);
      toast.error('Report Generation Failed', errorMessage);
    } finally {
      setDownloadingReport(false);
    }
  };

  const handleExportCSV = () => {
    if (!result) return;

    const layoffList = result.recommendations.filter(
      (r) => r.layoff_recommended && !excludedEmployees.has(r.employee_id)
    );

    const headers = ['Employee ID', 'Name', 'Department', 'Monthly Income', 'Retention Score', 'Layoff Reason'];
    const csvContent = [
      headers.join(','),
      ...layoffList.map((emp) =>
        [
          emp.employee_id,
          `"${emp.name}"`,
          `"${emp.department}"`,
          emp.monthly_income,
          emp.retention_score.toFixed(2),
          `"${emp.layoff_reason}"`,
        ].join(',')
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const timestamp = new Date().toISOString().split('T')[0];
    downloadBlob(blob, `layoff_list_${timestamp}.csv`);
    toast.success('CSV Exported', `Exported ${layoffList.length} employees to CSV`);
  };

  const toggleExcludeEmployee = (employeeId: string) => {
    setExcludedEmployees((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(employeeId)) {
        newSet.delete(employeeId);
      } else {
        newSet.add(employeeId);
      }
      return newSet;
    });
  };

  // Calculate adjusted metrics based on exclusions
  const adjustedMetrics = useMemo(() => {
    if (!result) return null;

    const originalLayoffs = result.recommendations.filter((r) => r.layoff_recommended);
    const adjustedLayoffs = originalLayoffs.filter((r) => !excludedEmployees.has(r.employee_id));
    const retainedEmployees = result.recommendations.filter(
      (r) => !r.layoff_recommended || excludedEmployees.has(r.employee_id)
    );

    const adjustedSavings = adjustedLayoffs.reduce((sum, emp) => sum + emp.monthly_income, 0);
    const originalTotalSalary = result.recommendations.reduce((sum, emp) => sum + emp.monthly_income, 0);
    const adjustedSavingsPercent = originalTotalSalary > 0 ? (adjustedSavings / originalTotalSalary) * 100 : 0;

    // Calculate average retention scores
    const avgRetentionLaidOff = adjustedLayoffs.length > 0
      ? adjustedLayoffs.reduce((sum, emp) => sum + emp.retention_score, 0) / adjustedLayoffs.length
      : 0;
    const avgRetentionRetained = retainedEmployees.length > 0
      ? retainedEmployees.reduce((sum, emp) => sum + emp.retention_score, 0) / retainedEmployees.length
      : 0;

    // Get unique departments affected
    const departmentsAffected = new Set(adjustedLayoffs.map((emp) => emp.department)).size;

    return {
      employeesToLayoff: adjustedLayoffs.length,
      totalEmployees: result.recommendations.length,
      annualSavings: adjustedSavings * 12,
      monthlySavings: adjustedSavings,
      savingsPercent: adjustedSavingsPercent,
      departmentsAffected,
      avgRetentionLaidOff,
      avgRetentionRetained,
      adjustedLayoffs,
      retainedEmployees,
    };
  }, [result, excludedEmployees]);

  const departmentChartData = result
    ? Object.entries(result.department_breakdown).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  // Comparison chart data
  const comparisonChartData = adjustedMetrics
    ? [
        { name: 'Laid Off', score: adjustedMetrics.avgRetentionLaidOff, fill: '#ef4444' },
        { name: 'Retained', score: adjustedMetrics.avgRetentionRetained, fill: '#22c55e' },
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center gap-4">
          <Scissors className="w-6 h-6 text-primary-400" />
          <h2 className="text-xl font-semibold text-white">Layoff Simulation</h2>
        </div>
        <p className="text-dark-400 mt-2">
          Upload employee data and simulate layoff scenarios based on budget constraints.
          The system will recommend layoffs based on retention scores while respecting department minimums.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex flex-wrap items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <p className="text-red-400 flex-1 min-w-0">{error}</p>
          <button
            onClick={() => setError(null)}
            className="btn btn-ghost btn-sm text-red-400 hover:text-red-300"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* File Upload */}
        <div className="card lg:col-span-2">
          <h3 className="card-header">Upload Employee Data</h3>
          <FileUpload
            onFileSelect={setSelectedFile}
            selectedFile={selectedFile}
            onClear={() => {
              setSelectedFile(null);
              setResult(null);
              setExcludedEmployees(new Set());
            }}
            disabled={loading}
          />
          <p className="text-sm text-dark-500 mt-2">
            CSV must contain: employee_id, name, department, monthly_income, and all performance metrics
          </p>
        </div>

        {/* Parameters */}
        <div className="card">
          <h3 className="card-header">Simulation Parameters</h3>
          <div className="space-y-4">
            {/* Budget Cut Slider */}
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
              <div className="flex justify-between text-xs text-dark-500 mt-1">
                <span>5%</span>
                <span>50%</span>
              </div>
            </div>

            {/* Minimum per Department */}
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
              <p className="text-xs text-dark-500 mt-1">
                Minimum employees to retain per department
              </p>
            </div>

            {/* Protect Critical Roles */}
            <div>
              <label className="flex items-center gap-3 cursor-pointer group">
                <div
                  className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                    protectCritical
                      ? 'bg-primary-500 border-primary-500'
                      : 'border-dark-500 group-hover:border-dark-400'
                  }`}
                  onClick={() => setProtectCritical(!protectCritical)}
                >
                  {protectCritical && <Check className="w-3 h-3 text-white" />}
                </div>
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-dark-400" />
                  <span className="text-dark-300 text-sm">Protect Critical Roles</span>
                </div>
              </label>
              <p className="text-xs text-dark-500 mt-1 ml-8">
                Exclude employees marked as critical from layoff recommendations
              </p>
            </div>

            <button
              onClick={handleSimulation}
              disabled={!selectedFile || loading}
              className="btn btn-danger w-full"
            >
              {loading ? 'Simulating...' : 'Run Simulation'}
            </button>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && <LoadingSpinner message="Running layoff simulation..." />}

      {/* Empty state: no simulation result yet */}
      {!result && !loading && (
        <div className="bg-dark-900 border border-dark-700 rounded-xl p-8 text-center">
          <Scissors className="w-12 h-12 text-dark-500 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-white mb-2">No simulation results yet</h3>
          <p className="text-dark-400 text-sm max-w-md mx-auto mb-4">
            Upload an employee CSV file, set your budget cut percentage and parameters, then click &quot;Run Simulation&quot; to see layoff recommendations and cost savings.
          </p>
          <p className="text-dark-500 text-xs">
            CSV must include department and monthly_income. Consider further review for any recommended layoffs.
          </p>
        </div>
      )}

      {/* Results */}
      {result && !loading && adjustedMetrics && (
        <div className="space-y-6 animate-fade-in">
          {/* Results Dashboard Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <ResultCard
              icon={Users}
              label="Employees to Lay Off"
              value={`${adjustedMetrics.employeesToLayoff} / ${adjustedMetrics.totalEmployees}`}
              subtext={`${((adjustedMetrics.employeesToLayoff / adjustedMetrics.totalEmployees) * 100).toFixed(1)}% of workforce`}
              color="red"
            />
            <ResultCard
              icon={DollarSign}
              label="Annual Cost Savings"
              value={`$${adjustedMetrics.annualSavings.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
              subtext={`$${adjustedMetrics.monthlySavings.toLocaleString(undefined, { maximumFractionDigits: 0 })}/month`}
              color="green"
            />
            <ResultCard
              icon={Building}
              label="Departments Affected"
              value={adjustedMetrics.departmentsAffected.toString()}
              subtext={`out of ${departmentChartData.length} departments`}
              color="purple"
            />
            <ResultCard
              icon={TrendingDown}
              label="Savings Achieved"
              value={`${adjustedMetrics.savingsPercent.toFixed(1)}%`}
              subtext={`Target: ${budgetCutPercent}%`}
              color={adjustedMetrics.savingsPercent >= budgetCutPercent ? 'green' : 'yellow'}
            />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Comparison Chart: Avg Retention Score */}
            <div className="card">
              <h3 className="card-header">Average Retention Score Comparison</h3>
              <p className="text-dark-400 text-sm mb-4">
                Compare average retention scores between laid off and retained employees
              </p>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={comparisonChartData} layout="vertical">
                    <XAxis
                      type="number"
                      domain={[0, 100]}
                      tick={{ fill: '#94a3b8', fontSize: 12 }}
                      axisLine={{ stroke: '#334155' }}
                      tickLine={{ stroke: '#334155' }}
                    />
                    <YAxis
                      type="category"
                      dataKey="name"
                      tick={{ fill: '#94a3b8', fontSize: 14 }}
                      width={80}
                      axisLine={{ stroke: '#334155' }}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={CHART_TOOLTIP_CONTENT_STYLE}
                      formatter={(value) => [`${(value as number).toFixed(1)}`, 'Avg. Retention Score']}
                    />
                    <Bar dataKey="score" radius={[0, 8, 8, 0]} maxBarSize={50}>
                      {comparisonChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 p-3 bg-dark-800/50 rounded-lg">
                <p className="text-dark-300 text-sm">
                  <span className="text-red-400 font-medium">Laid off employees</span> have an average
                  retention score of <span className="text-white font-medium">{adjustedMetrics.avgRetentionLaidOff.toFixed(1)}</span>,
                  while <span className="text-green-400 font-medium">retained employees</span> average{' '}
                  <span className="text-white font-medium">{adjustedMetrics.avgRetentionRetained.toFixed(1)}</span>.
                </p>
              </div>
            </div>

            {/* Department Distribution */}
            <div className="card">
              <h3 className="card-header">Layoffs by Department</h3>
              <div className="h-64 flex items-center justify-center">
                {departmentChartData.length > 0 ? (
                  <div className="flex items-center gap-6 w-full">
                    <div className="w-48 h-48 flex-shrink-0">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={departmentChartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={40}
                            outerRadius={80}
                            dataKey="value"
                            label={({ value }) => `${value}`}
                            labelLine={false}
                          >
                            {departmentChartData.map((_, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                              />
                            ))}
                          </Pie>
                          <Tooltip
                            contentStyle={CHART_TOOLTIP_CONTENT_STYLE}
                            formatter={(value) => [`${value} employees`, 'Layoffs']}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="space-y-2 overflow-y-auto max-h-48">
                      {departmentChartData.map((item, index) => (
                        <div key={item.name} className="flex items-center gap-2 text-sm">
                          <div
                            className="w-3 h-3 rounded flex-shrink-0"
                            style={{ backgroundColor: COLORS[index % COLORS.length] }}
                          />
                          <span className="text-dark-300 truncate">{item.name}</span>
                          <span className="text-white font-medium ml-auto">{item.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-dark-400">No data available</p>
                )}
              </div>
            </div>
          </div>

          {/* Savings Progress */}
          <div className="card">
            <h3 className="card-header">Budget Cut Progress</h3>
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-dark-400">Target: {budgetCutPercent}%</span>
                <span className="text-dark-400">
                  Achieved: {adjustedMetrics.savingsPercent.toFixed(1)}%
                </span>
              </div>
              <div className="h-4 bg-dark-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-1000 ${
                    adjustedMetrics.savingsPercent >= budgetCutPercent
                      ? 'bg-green-500'
                      : 'bg-yellow-500'
                  }`}
                  style={{
                    width: `${Math.min(
                      (adjustedMetrics.savingsPercent / budgetCutPercent) * 100,
                      100
                    )}%`,
                  }}
                />
              </div>
              <p
                className={`text-sm ${
                  adjustedMetrics.savingsPercent >= budgetCutPercent
                    ? 'text-green-400'
                    : 'text-yellow-400'
                }`}
              >
                {adjustedMetrics.savingsPercent >= budgetCutPercent
                  ? 'Target achieved!'
                  : `${(budgetCutPercent - adjustedMetrics.savingsPercent).toFixed(1)}% more needed to reach target`}
              </p>
            </div>
          </div>

          {/* Layoff List Table with Exclusions */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white">
                  Layoff List ({adjustedMetrics.adjustedLayoffs.length} employees)
                </h3>
                <p className="text-dark-400 text-sm">
                  Uncheck employees to exclude them from the layoff list
                </p>
              </div>
              <div className="flex gap-2">
                {excludedEmployees.size > 0 && (
                  <button
                    onClick={() => setExcludedEmployees(new Set())}
                    className="btn btn-secondary btn-sm"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Reset Exclusions ({excludedEmployees.size})
                  </button>
                )}
              </div>
            </div>
            <LayoffTable
              data={result.recommendations.filter((r) => r.layoff_recommended)}
              excludedEmployees={excludedEmployees}
              onToggleExclude={toggleExcludeEmployee}
            />
          </div>

          {/* Actions */}
          <div className="card">
            <h3 className="card-header">Actions</h3>
            <div className="flex flex-wrap gap-4">
              <button
                onClick={handleDownloadReport}
                disabled={downloadingReport}
                className="btn btn-primary"
              >
                {downloadingReport ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Download Layoff Report (PDF)
                  </>
                )}
              </button>
              <button onClick={handleExportCSV} className="btn btn-secondary">
                <FileSpreadsheet className="w-4 h-4 mr-2" />
                Export to CSV
              </button>
            </div>
            <p className="text-dark-500 text-sm mt-3">
              The PDF report includes executive summary, department breakdown, and complete employee list.
              CSV export includes only the layoff list with retention scores.
            </p>
          </div>

          {/* All Employees Table */}
          <div className="card">
            <h3 className="card-header">All Employees ({result.recommendations.length})</h3>
            <AllEmployeesTable
              data={result.recommendations}
              excludedEmployees={excludedEmployees}
            />
          </div>
        </div>
      )}
    </div>
  );
}

// Result Card Component
interface ResultCardProps {
  icon: React.ElementType;
  label: string;
  value: string;
  subtext: string;
  color: 'cyan' | 'green' | 'red' | 'purple' | 'yellow';
}

function ResultCard({ icon: Icon, label, value, subtext, color }: ResultCardProps) {
  const colorClasses = {
    cyan: 'bg-cyan-500/10 border-cyan-500/20',
    green: 'bg-green-500/10 border-green-500/20',
    red: 'bg-red-500/10 border-red-500/20',
    purple: 'bg-purple-500/10 border-purple-500/20',
    yellow: 'bg-yellow-500/10 border-yellow-500/20',
  };

  const iconClasses = {
    cyan: 'text-cyan-400',
    green: 'text-green-400',
    red: 'text-red-400',
    purple: 'text-purple-400',
    yellow: 'text-yellow-400',
  };

  return (
    <div className={`rounded-xl border p-5 ${colorClasses[color]}`}>
      <div className="flex items-center gap-2 mb-3">
        <Icon className={`w-5 h-5 ${iconClasses[color]}`} />
        <span className="text-dark-400 text-sm">{label}</span>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-dark-500 text-sm mt-1">{subtext}</p>
    </div>
  );
}

// Layoff Table with Checkboxes
interface LayoffTableProps {
  data: LayoffRecommendation[];
  excludedEmployees: Set<string>;
  onToggleExclude: (employeeId: string) => void;
}

function LayoffTable({ data, excludedEmployees, onToggleExclude }: LayoffTableProps) {
  const [sortKey, setSortKey] = useState<keyof LayoffRecommendation>('retention_score');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 15;

  const handleSort = (key: keyof LayoffRecommendation) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const filteredData = useMemo(() => {
    let filtered = [...data];

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (emp) =>
          emp.name.toLowerCase().includes(query) ||
          emp.employee_id.toLowerCase().includes(query) ||
          emp.department.toLowerCase().includes(query)
      );
    }

    filtered.sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      return 0;
    });

    return filtered;
  }, [data, searchQuery, sortKey, sortDirection]);

  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredData.slice(start, start + pageSize);
  }, [filteredData, currentPage]);

  const totalPages = Math.ceil(filteredData.length / pageSize);

  const SortIcon = ({ column }: { column: keyof LayoffRecommendation }) => {
    if (sortKey !== column) return <ChevronDown className="w-4 h-4 text-dark-600" />;
    return sortDirection === 'asc' ? (
      <ChevronUp className="w-4 h-4 text-primary-400" />
    ) : (
      <ChevronDown className="w-4 h-4 text-primary-400" />
    );
  };

  return (
    <div>
      {/* Search */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search by name, ID, or department..."
          className="input max-w-md"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setCurrentPage(1);
          }}
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-dark-700">
              <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider w-12">
                Include
              </th>
              <th
                className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('name')}
              >
                <div className="flex items-center gap-1">
                  Name <SortIcon column="name" />
                </div>
              </th>
              <th
                className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('department')}
              >
                <div className="flex items-center gap-1">
                  Department <SortIcon column="department" />
                </div>
              </th>
              <th
                className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('retention_score')}
              >
                <div className="flex items-center gap-1">
                  Retention Score <SortIcon column="retention_score" />
                </div>
              </th>
              <th
                className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('monthly_income')}
              >
                <div className="flex items-center gap-1">
                  Monthly Salary <SortIcon column="monthly_income" />
                </div>
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">
                Reason
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((employee) => {
              const isExcluded = excludedEmployees.has(employee.employee_id);
              return (
                <tr
                  key={employee.employee_id}
                  className={`border-b border-dark-800 transition-colors ${
                    isExcluded ? 'opacity-50 bg-dark-800/30' : 'hover:bg-dark-800/50'
                  }`}
                >
                  <td className="py-3 px-4">
                    <button
                      onClick={() => onToggleExclude(employee.employee_id)}
                      className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                        !isExcluded
                          ? 'bg-red-500 border-red-500'
                          : 'border-dark-500 hover:border-dark-400'
                      }`}
                    >
                      {!isExcluded && <Check className="w-3 h-3 text-white" />}
                    </button>
                  </td>
                  <td className="py-3 px-4">
                    <div>
                      <p className={`font-medium ${isExcluded ? 'text-dark-400 line-through' : 'text-white'}`}>
                        {employee.name}
                      </p>
                      <p className="text-dark-500 text-xs">{employee.employee_id}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-dark-300">{employee.department}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-dark-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            employee.retention_score >= 50
                              ? 'bg-green-500'
                              : employee.retention_score >= 30
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                          style={{ width: `${employee.retention_score}%` }}
                        />
                      </div>
                      <span className={`text-sm font-medium ${
                        employee.retention_score >= 50
                          ? 'text-green-400'
                          : employee.retention_score >= 30
                          ? 'text-yellow-400'
                          : 'text-red-400'
                      }`}>
                        {employee.retention_score.toFixed(1)}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-dark-300">
                    ${employee.monthly_income.toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-dark-400 text-sm">{employee.layoff_reason}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-dark-400 text-sm">
            Showing {(currentPage - 1) * pageSize + 1} to{' '}
            {Math.min(currentPage * pageSize, filteredData.length)} of {filteredData.length} employees
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="btn btn-secondary btn-sm"
            >
              Previous
            </button>
            <span className="text-dark-300 px-3 py-1">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="btn btn-secondary btn-sm"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// All Employees Table
interface AllEmployeesTableProps {
  data: LayoffRecommendation[];
  excludedEmployees: Set<string>;
}

function AllEmployeesTable({ data, excludedEmployees }: AllEmployeesTableProps) {
  const [sortKey, setSortKey] = useState<keyof LayoffRecommendation>('retention_score');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const handleSort = (key: keyof LayoffRecommendation) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const filteredData = useMemo(() => {
    let filtered = [...data];

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (emp) =>
          emp.name.toLowerCase().includes(query) ||
          emp.employee_id.toLowerCase().includes(query) ||
          emp.department.toLowerCase().includes(query)
      );
    }

    filtered.sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      return 0;
    });

    return filtered;
  }, [data, searchQuery, sortKey, sortDirection]);

  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredData.slice(start, start + pageSize);
  }, [filteredData, currentPage]);

  const totalPages = Math.ceil(filteredData.length / pageSize);

  const SortIcon = ({ column }: { column: keyof LayoffRecommendation }) => {
    if (sortKey !== column) return <ChevronDown className="w-4 h-4 text-dark-600" />;
    return sortDirection === 'asc' ? (
      <ChevronUp className="w-4 h-4 text-primary-400" />
    ) : (
      <ChevronDown className="w-4 h-4 text-primary-400" />
    );
  };

  return (
    <div>
      {/* Search */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search all employees..."
          className="input max-w-md"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setCurrentPage(1);
          }}
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-dark-700">
              <th
                className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('employee_id')}
              >
                <div className="flex items-center gap-1">
                  ID <SortIcon column="employee_id" />
                </div>
              </th>
              <th
                className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('name')}
              >
                <div className="flex items-center gap-1">
                  Name <SortIcon column="name" />
                </div>
              </th>
              <th
                className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('department')}
              >
                <div className="flex items-center gap-1">
                  Department <SortIcon column="department" />
                </div>
              </th>
              <th
                className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('monthly_income')}
              >
                <div className="flex items-center gap-1">
                  Salary <SortIcon column="monthly_income" />
                </div>
              </th>
              <th
                className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('retention_score')}
              >
                <div className="flex items-center gap-1">
                  Retention <SortIcon column="retention_score" />
                </div>
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((employee) => {
              const isExcluded = excludedEmployees.has(employee.employee_id);
              const shouldLayoff = employee.layoff_recommended && !isExcluded;

              return (
                <tr
                  key={employee.employee_id}
                  className="border-b border-dark-800 hover:bg-dark-800/50 transition-colors"
                >
                  <td className="py-3 px-4 text-dark-300 text-sm">{employee.employee_id}</td>
                  <td className="py-3 px-4 text-white font-medium">{employee.name}</td>
                  <td className="py-3 px-4 text-dark-300">{employee.department}</td>
                  <td className="py-3 px-4 text-dark-300">${employee.monthly_income.toLocaleString()}</td>
                  <td className="py-3 px-4 text-dark-300">{employee.retention_score.toFixed(1)}</td>
                  <td className="py-3 px-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${
                        shouldLayoff
                          ? 'bg-red-500/20 text-red-400 border-red-500/30'
                          : 'bg-green-500/20 text-green-400 border-green-500/30'
                      }`}
                    >
                      {shouldLayoff ? 'Layoff' : 'Retain'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-dark-400 text-sm">
            Showing {(currentPage - 1) * pageSize + 1} to{' '}
            {Math.min(currentPage * pageSize, filteredData.length)} of {filteredData.length} employees
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="btn btn-secondary btn-sm"
            >
              Previous
            </button>
            <span className="text-dark-300 px-3 py-1">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="btn btn-secondary btn-sm"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
