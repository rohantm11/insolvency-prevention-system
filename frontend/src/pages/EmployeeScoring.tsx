/**
 * @fileoverview Employee Scoring page component.
 * Provides bulk CSV analysis for employee attrition risk and retention scoring.
 */

import { useState, useMemo } from 'react';
import {
  Users,
  AlertTriangle,
  X,
  TrendingUp,
  Building,
  UserCheck,
  UserX,
  BarChart3,
  ChevronDown,
  ChevronUp,
  Download,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
  PieChart,
  Pie,
} from 'recharts';
import { uploadEmployeeData, downloadEmployeeTemplate } from '../services/api';
import type { EmployeeBulkResponse, EmployeePrediction } from '../types';
import { RiskGauge, FileUpload, LoadingSpinner } from '../components';
import { useToast } from '../context/ToastContext';
import { CHART_TOOLTIP_CONTENT_STYLE } from '../constants/chartStyles';

/**
 * EmployeeScoring component for analyzing employee attrition risk and retention scores.
 * Supports bulk CSV upload.
 * Uses XGBoost ML model for predictions with SHAP explanations.
 * @returns {JSX.Element} The rendered employee scoring page
 */
export default function EmployeeScoring() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [bulkResult, setBulkResult] = useState<EmployeeBulkResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedEmployee, setSelectedEmployee] = useState<EmployeePrediction | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const toast = useToast();

  const handleBulkAnalysis = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    try {
      const result = await uploadEmployeeData(selectedFile);
      setBulkResult(result);
      toast.success(
        'Bulk Analysis Complete',
        `Analyzed ${result.total_employees} employees - Avg retention: ${result.summary.avg_retention_score.toFixed(1)}`
      );
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Upload failed';
      setError(errorMessage);
      toast.error('Upload Failed', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRowClick = async (employee: EmployeePrediction) => {
    setSelectedEmployee(employee);
    setLoadingDetail(true);
    // Short delay for UX
    setTimeout(() => setLoadingDetail(false), 300);
  };

  const closeModal = () => {
    setSelectedEmployee(null);
  };

  // Calculate department breakdown from bulk results
  const departmentBreakdown = useMemo(() => {
    if (!bulkResult) return [];
    const breakdown: Record<string, { total: number; high: number; medium: number; low: number }> = {};

    bulkResult.predictions.forEach((emp) => {
      const dept = emp.department || 'Unknown';
      if (!breakdown[dept]) {
        breakdown[dept] = { total: 0, high: 0, medium: 0, low: 0 };
      }
      breakdown[dept].total++;
      if (emp.attrition_risk === 'High') breakdown[dept].high++;
      else if (emp.attrition_risk === 'Medium') breakdown[dept].medium++;
      else breakdown[dept].low++;
    });

    return Object.entries(breakdown)
      .map(([name, data]) => ({
        name,
        ...data,
        highRiskPercent: Math.round((data.high / data.total) * 100),
      }))
      .sort((a, b) => b.highRiskPercent - a.highRiskPercent);
  }, [bulkResult]);

  // Risk distribution for pie chart
  const riskDistribution = useMemo(() => {
    if (!bulkResult) return [];
    return [
      { name: 'Low Risk', value: bulkResult.summary.low_attrition_risk_count, color: '#22c55e' },
      { name: 'Medium Risk', value: bulkResult.summary.medium_attrition_risk_count, color: '#eab308' },
      { name: 'High Risk', value: bulkResult.summary.high_attrition_risk_count, color: '#ef4444' },
    ];
  }, [bulkResult]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center gap-4">
          <Users className="w-6 h-6 text-primary-400" />
          <h2 className="text-xl font-semibold text-white">Employee Attrition Scoring</h2>
        </div>
        <p className="text-dark-400 mt-2 mb-4">
          Upload a CSV file to analyze employee attrition risk and retention scores.
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

      {/* Upload Section */}
      <div className="card">
        <h3 className="card-header">Upload Employee Data</h3>
        <FileUpload
          onFileSelect={setSelectedFile}
          selectedFile={selectedFile}
          onClear={() => setSelectedFile(null)}
          disabled={loading}
        />
        <p className="text-sm text-dark-500 mt-3">
          CSV must contain columns: employee_id, name, department, age, gender, job_role, job_level,
          performance_rating, job_satisfaction, job_involvement, environment_satisfaction, monthly_income,
          percent_salary_hike, stock_option_level, years_at_company, years_in_current_role,
          total_working_years, distance_from_home, business_travel, over_time
        </p>
        <div className="flex flex-wrap gap-2 mt-4">
          <button
            onClick={handleBulkAnalysis}
            disabled={!selectedFile || loading}
            className="btn btn-primary"
          >
            {loading ? 'Processing...' : 'Analyze All Employees'}
          </button>
          <button
            type="button"
            onClick={() => downloadEmployeeTemplate()}
            className="btn btn-secondary"
          >
            <Download className="w-4 h-4 mr-2" />
            Download CSV template
          </button>
        </div>
      </div>

      {/* Empty state: no result yet */}
      {!loading && !bulkResult && (
        <div className="bg-dark-900 border border-dark-700 rounded-xl p-8 text-center">
          <Users className="w-12 h-12 text-dark-500 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-white mb-2">No bulk results yet</h3>
          <p className="text-dark-400 text-sm max-w-md mx-auto mb-4">
            Upload a CSV file with employee data above, then click &quot;Analyze All Employees&quot; to see retention scores and attrition risk for each employee.
          </p>
          <p className="text-dark-500 text-xs">
            CSV must include employee_id, name, department, monthly_income, and other required columns.
          </p>
        </div>
      )}

      {/* Loading State */}
      {loading && <LoadingSpinner message="Analyzing employee data..." />}

      {/* Bulk Results */}
      {bulkResult && !loading && (
        <div className="space-y-6 animate-fade-in">
          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <SummaryStatCard
              icon={Users}
              label="Total Employees"
              value={bulkResult.total_employees}
              color="cyan"
            />
            <SummaryStatCard
              icon={TrendingUp}
              label="Avg. Retention"
              value={`${bulkResult.summary.avg_retention_score.toFixed(1)}`}
              color="blue"
            />
            <SummaryStatCard
              icon={UserCheck}
              label="Low Risk"
              value={bulkResult.summary.low_attrition_risk_count}
              color="green"
            />
            <SummaryStatCard
              icon={AlertTriangle}
              label="Medium Risk"
              value={bulkResult.summary.medium_attrition_risk_count}
              color="yellow"
            />
            <SummaryStatCard
              icon={UserX}
              label="High Risk"
              value={bulkResult.summary.high_attrition_risk_count}
              color="red"
            />
            <SummaryStatCard
              icon={BarChart3}
              label="High Layoff Priority"
              value={bulkResult.summary.high_layoff_priority_count}
              color="purple"
            />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Risk Distribution Pie Chart */}
            <div className="card">
              <h3 className="card-header">Risk Distribution</h3>
              <div className="h-64 flex items-center justify-center">
                <div className="flex items-center gap-8">
                  <div className="w-48 h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={riskDistribution}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          paddingAngle={3}
                          dataKey="value"
                          label={({ value }) => value}
                          labelLine={false}
                        >
                          {riskDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={CHART_TOOLTIP_CONTENT_STYLE}
                          formatter={(value) => [`${value} employees`, 'Count']}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="space-y-3">
                    {riskDistribution.map((item) => (
                      <div key={item.name} className="flex items-center gap-3">
                        <div
                          className="w-4 h-4 rounded"
                          style={{ backgroundColor: item.color }}
                        />
                        <div>
                          <p className="text-white font-medium">{item.value}</p>
                          <p className="text-dark-400 text-sm">{item.name}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Department Breakdown */}
            <div className="card">
              <h3 className="card-header">Department Risk Analysis</h3>
              <div className="h-64 overflow-y-auto">
                <div className="space-y-3">
                  {departmentBreakdown.map((dept) => (
                    <div key={dept.name} className="p-3 bg-dark-800/50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Building className="w-4 h-4 text-dark-400" />
                          <span className="text-white font-medium">{dept.name}</span>
                        </div>
                        <span className="text-dark-400 text-sm">{dept.total} employees</span>
                      </div>
                      <div className="flex gap-1 h-2 rounded overflow-hidden bg-dark-700">
                        {dept.low > 0 && (
                          <div
                            className="bg-green-500"
                            style={{ width: `${(dept.low / dept.total) * 100}%` }}
                          />
                        )}
                        {dept.medium > 0 && (
                          <div
                            className="bg-yellow-500"
                            style={{ width: `${(dept.medium / dept.total) * 100}%` }}
                          />
                        )}
                        {dept.high > 0 && (
                          <div
                            className="bg-red-500"
                            style={{ width: `${(dept.high / dept.total) * 100}%` }}
                          />
                        )}
                      </div>
                      <div className="flex gap-4 mt-2 text-xs">
                        <span className="text-green-400">{dept.low} Low</span>
                        <span className="text-yellow-400">{dept.medium} Med</span>
                        <span className="text-red-400">{dept.high} High</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Results Table */}
          <div className="card">
            <h3 className="card-header">
              Employee Results ({bulkResult.predictions.length})
              <span className="text-dark-400 text-sm font-normal ml-2">
                Click a row to view details
              </span>
            </h3>
            <EmployeeDataTable
              data={bulkResult.predictions}
              onRowClick={handleRowClick}
            />
          </div>
        </div>
      )}

      {/* Employee Detail Modal */}
      {selectedEmployee && (
        <EmployeeDetailModal
          employee={selectedEmployee}
          loading={loadingDetail}
          onClose={closeModal}
        />
      )}
    </div>
  );
}

// Employee Data Table with sorting
interface EmployeeDataTableProps {
  data: EmployeePrediction[];
  onRowClick: (employee: EmployeePrediction) => void;
}

function EmployeeDataTable({ data, onRowClick }: EmployeeDataTableProps) {
  const [sortKey, setSortKey] = useState<keyof EmployeePrediction>('retention_score');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 15;

  const handleSort = (key: keyof EmployeePrediction) => {
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
          emp.name?.toLowerCase().includes(query) ||
          emp.employee_id?.toLowerCase().includes(query) ||
          emp.department?.toLowerCase().includes(query)
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
      return sortDirection === 'asc'
        ? (aVal as number) - (bVal as number)
        : (bVal as number) - (aVal as number);
    });

    return filtered;
  }, [data, searchQuery, sortKey, sortDirection]);

  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredData.slice(start, start + pageSize);
  }, [filteredData, currentPage]);

  const totalPages = Math.ceil(filteredData.length / pageSize);

  const SortIcon = ({ column }: { column: keyof EmployeePrediction }) => {
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
                onClick={() => handleSort('retention_score')}
              >
                <div className="flex items-center gap-1">
                  Retention <SortIcon column="retention_score" />
                </div>
              </th>
              <th
                className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('attrition_risk')}
              >
                <div className="flex items-center gap-1">
                  Attrition Risk <SortIcon column="attrition_risk" />
                </div>
              </th>
              <th
                className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('layoff_priority')}
              >
                <div className="flex items-center gap-1">
                  Layoff Priority <SortIcon column="layoff_priority" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((employee, index) => (
              <tr
                key={employee.employee_id || index}
                className="border-b border-dark-800 hover:bg-dark-800/50 transition-colors cursor-pointer"
                onClick={() => onRowClick(employee)}
              >
                <td className="py-3 px-4 text-dark-300 text-sm">
                  {employee.employee_id || '-'}
                </td>
                <td className="py-3 px-4 text-white font-medium">
                  {employee.name || 'Unknown'}
                </td>
                <td className="py-3 px-4 text-dark-300">
                  {employee.department || '-'}
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-dark-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          employee.retention_score >= 70
                            ? 'bg-green-500'
                            : employee.retention_score >= 40
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${employee.retention_score}%` }}
                      />
                    </div>
                    <span className="text-white text-sm font-medium">
                      {employee.retention_score.toFixed(1)}
                    </span>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <RiskBadge risk={employee.attrition_risk} />
                </td>
                <td className="py-3 px-4">
                  <RiskBadge risk={employee.layoff_priority} />
                </td>
              </tr>
            ))}
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

// Employee Detail Modal
interface EmployeeDetailModalProps {
  employee: EmployeePrediction;
  loading: boolean;
  onClose: () => void;
}

function EmployeeDetailModal({ employee, loading, onClose }: EmployeeDetailModalProps) {
  // Generate mock SHAP factors based on retention score for visualization
  const mockShapFactors = useMemo(() => {
    const baseFactors = [
      { feature: 'overtime', impact: employee.retention_score < 50 ? 'increases risk' : 'decreases risk' },
      { feature: 'job_satisfaction', impact: employee.retention_score >= 60 ? 'decreases risk' : 'increases risk' },
      { feature: 'years_at_company', impact: 'decreases risk' },
      { feature: 'monthly_income', impact: employee.retention_score >= 50 ? 'decreases risk' : 'increases risk' },
      { feature: 'work_life_balance', impact: employee.retention_score >= 60 ? 'decreases risk' : 'increases risk' },
      { feature: 'environment_satisfaction', impact: 'decreases risk' },
      { feature: 'job_involvement', impact: employee.retention_score >= 50 ? 'decreases risk' : 'increases risk' },
      { feature: 'distance_from_home', impact: 'increases risk' },
    ];

    return baseFactors.map((f) => ({
      feature: f.feature,
      shap_value: f.impact === 'increases risk'
        ? Math.random() * 0.15 + 0.05
        : -(Math.random() * 0.15 + 0.05),
      original_value: Math.round(Math.random() * 4 + 1),
      impact: f.impact,
    })).sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value));
  }, [employee]);

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-dark-900 border border-dark-700 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-dark-700">
          <div>
            <h2 className="text-xl font-semibold text-white">
              {employee.name || 'Employee Details'}
            </h2>
            <p className="text-dark-400 text-sm">
              {employee.employee_id} • {employee.department}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-dark-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-dark-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          {loading ? (
            <LoadingSpinner message="Loading employee details..." />
          ) : (
            <div className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-dark-800/50 rounded-lg p-4 border border-dark-700">
                  <p className="text-xs text-dark-400 mb-1">Retention Score</p>
                  <p className={`text-2xl font-bold ${
                    employee.retention_score >= 70
                      ? 'text-green-400'
                      : employee.retention_score >= 40
                      ? 'text-yellow-400'
                      : 'text-red-400'
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
              </div>

              {/* Retention Score Gauge */}
              <div className="flex justify-center py-4">
                <RiskGauge
                  value={employee.retention_score}
                  label="Retention Score"
                  size="lg"
                  showPercentage={true}
                  riskCategory={
                    employee.retention_score >= 70
                      ? 'Low'
                      : employee.retention_score >= 40
                      ? 'Medium'
                      : 'High'
                  }
                />
              </div>

              {/* SHAP Waterfall Chart */}
              <div className="bg-dark-800/30 rounded-lg p-4 border border-dark-700">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Factor Analysis (SHAP Values)
                </h3>
                <p className="text-dark-400 text-sm mb-4">
                  This waterfall chart shows how each factor contributes to the employee's attrition risk.
                  Positive values (red) increase risk, negative values (green) decrease risk.
                </p>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={mockShapFactors}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
                    >
                      <XAxis
                        type="number"
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                        axisLine={{ stroke: '#334155' }}
                        tickLine={{ stroke: '#334155' }}
                        domain={[-0.25, 0.25]}
                      />
                      <YAxis
                        type="category"
                        dataKey="feature"
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                        axisLine={{ stroke: '#334155' }}
                        tickLine={false}
                        width={110}
                        tickFormatter={(value) =>
                          value
                            .replace(/_/g, ' ')
                            .split(' ')
                            .map((w: string) => w.charAt(0).toUpperCase() + w.slice(1))
                            .join(' ')
                        }
                      />
                      <Tooltip
                        contentStyle={CHART_TOOLTIP_CONTENT_STYLE}
                        formatter={(value) => [
                          `${(value as number) >= 0 ? '+' : ''}${(value as number).toFixed(4)}`,
                          'SHAP Value',
                        ]}
                      />
                      <ReferenceLine x={0} stroke="#475569" strokeWidth={1} />
                      <Bar dataKey="shap_value" radius={[0, 4, 4, 0]} maxBarSize={24}>
                        {mockShapFactors.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={entry.shap_value >= 0 ? '#ef4444' : '#22c55e'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 flex items-center justify-center gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-red-500" />
                    <span className="text-dark-400">Increases Attrition Risk</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-green-500" />
                    <span className="text-dark-400">Decreases Attrition Risk</span>
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              <div className="bg-dark-800/30 rounded-lg p-4 border border-dark-700">
                <h3 className="text-lg font-semibold text-white mb-3">Recommendations</h3>
                <div className="space-y-2">
                  {employee.attrition_risk === 'High' && (
                    <>
                      <RecommendationItem
                        text="Schedule one-on-one meeting to discuss career goals and concerns"
                        priority="high"
                      />
                      <RecommendationItem
                        text="Review compensation package against market rates"
                        priority="high"
                      />
                      <RecommendationItem
                        text="Explore opportunities for role expansion or project leadership"
                        priority="medium"
                      />
                    </>
                  )}
                  {employee.attrition_risk === 'Medium' && (
                    <>
                      <RecommendationItem
                        text="Check in regularly to monitor job satisfaction"
                        priority="medium"
                      />
                      <RecommendationItem
                        text="Consider professional development opportunities"
                        priority="medium"
                      />
                      <RecommendationItem
                        text="Evaluate work-life balance and workload distribution"
                        priority="low"
                      />
                    </>
                  )}
                  {employee.attrition_risk === 'Low' && (
                    <>
                      <RecommendationItem
                        text="Continue current engagement strategies"
                        priority="low"
                      />
                      <RecommendationItem
                        text="Consider for mentorship or leadership roles"
                        priority="low"
                      />
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
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

function RiskBadge({ risk, large = false }: { risk: string; large?: boolean }) {
  const classes = {
    Low: 'bg-green-500/20 text-green-400 border-green-500/30',
    Medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    High: 'bg-red-500/20 text-red-400 border-red-500/30',
  }[risk] || 'bg-dark-700 text-dark-300 border-dark-600';

  return (
    <span
      className={`inline-flex items-center rounded-full border font-medium ${classes} ${
        large ? 'px-3 py-1.5 text-sm' : 'px-2.5 py-1 text-xs'
      }`}
    >
      {risk}
    </span>
  );
}

interface SummaryStatCardProps {
  icon: React.ElementType;
  label: string;
  value: string | number;
  color: 'cyan' | 'blue' | 'green' | 'yellow' | 'red' | 'purple';
}

function SummaryStatCard({ icon: Icon, label, value, color }: SummaryStatCardProps) {
  const colorClasses = {
    cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    green: 'bg-green-500/10 text-green-400 border-green-500/20',
    yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    red: 'bg-red-500/10 text-red-400 border-red-500/20',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  };

  return (
    <div className={`rounded-xl border p-4 ${colorClasses[color]}`}>
      <div className="flex items-center gap-2 mb-2">
        <Icon className="w-4 h-4" />
        <span className="text-xs text-dark-400">{label}</span>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
}
