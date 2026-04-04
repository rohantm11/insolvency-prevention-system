/**
 * @fileoverview Dashboard page component for the Insolvency Prevention System.
 * Displays key metrics, risk distribution charts, and recent activity from API.
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
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
  Legend,
} from 'recharts';
import { Link } from 'react-router-dom';
import {
  Building2,
  Users,
  AlertTriangle,
  Scissors,
  Clock,
  TrendingUp,
  TrendingDown,
  FileSpreadsheet,
  ArrowRight,
} from 'lucide-react';
import { getRecentAnalyses, getMarketIntelligence } from '../services/api';
import type { AnalysisHistoryEntry, MarketIntelligenceResponse } from '../types';
import { CHART_TOOLTIP_CONTENT_STYLE, CHART_TOOLTIP_ITEM_STYLE } from '../constants/chartStyles';
import { getTrackedCompanies, type TrackedCompany } from '../constants/watchlist';
import { CountUp, LoadingSpinner } from '../components';
import { BarChart3, Bookmark } from 'lucide-react';

/** Sample risk distribution data for pie chart visualization */
const riskDistributionData = [
  { name: 'Low Risk', value: 45, color: '#22c55e' },
  { name: 'Medium Risk', value: 32, color: '#eab308' },
  { name: 'High Risk', value: 23, color: '#ef4444' },
];

const departmentAttritionData = [
  { department: 'Sales', risk: 42 },
  { department: 'Engineering', risk: 28 },
  { department: 'Marketing', risk: 35 },
  { department: 'Finance', risk: 18 },
  { department: 'HR', risk: 22 },
  { department: 'Operations', risk: 31 },
];

function formatTimeAgo(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  if (diffMins < 60) return diffMins <= 1 ? 'Just now' : `${diffMins} minutes ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  return d.toLocaleDateString();
}

/**
 * Dashboard component displaying the main overview of the Insolvency Prevention System.
 * Shows key metrics, risk distribution charts, department attrition data, and recent activity.
 * @returns {JSX.Element} The rendered dashboard component
 */
export default function Dashboard() {
  const [stats] = useState({
    totalCompanies: 127,
    highRiskCompanies: 23,
    totalEmployees: 1842,
    recommendedLayoffs: 156,
  });
  const [recentActivity, setRecentActivity] = useState<AnalysisHistoryEntry[]>([]);
  const [recentLoading, setRecentLoading] = useState(true);
  const [marketIntel, setMarketIntel] = useState<MarketIntelligenceResponse | null>(null);
  const [marketIntelLoading, setMarketIntelLoading] = useState(true);
  const [marketIntelError, setMarketIntelError] = useState<string | null>(null);
  const [trackedCompanies, setTrackedCompanies] = useState<TrackedCompany[]>([]);

  useEffect(() => {
    setTrackedCompanies(getTrackedCompanies());
  }, []);

  useEffect(() => {
    getRecentAnalyses(5)
      .then((res) => setRecentActivity(res.entries))
      .catch(() => setRecentActivity([]))
      .finally(() => setRecentLoading(false));
  }, []);

  useEffect(() => {
    getMarketIntelligence({ company_name: 'Market Overview', industry: 'general' })
      .then((data) => {
        setMarketIntel(data);
        setMarketIntelError(null);
      })
      .catch((err) => {
        setMarketIntelError(err?.message || 'Failed to load market signals');
        setMarketIntel(null);
      })
      .finally(() => setMarketIntelLoading(false));
  }, []);

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.08, delayChildren: 0.15 },
    },
  };
  const item = {
    hidden: { opacity: 0, y: 12 },
    show: {
      opacity: 1,
      y: 0,
      transition: { type: 'spring' as const, stiffness: 200, damping: 24 },
    },
  };

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
    >
      {/* Header */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, delay: 0.05 }}
      >
        <h1 className="text-3xl font-bold text-slate-800 dark:text-white mb-2">
          SolvencyInsight
        </h1>
        <p className="text-slate-500 dark:text-dark-400">
          AI-Powered Insolvency Prevention & Risk Analysis Platform
        </p>
      </motion.div>

      {/* Stat Cards */}
      <motion.div
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
        variants={container}
        initial="hidden"
        animate="show"
      >
        <motion.div variants={item}>
          <StatCard
            icon={Building2}
            label="Total Companies Analyzed"
            value={stats.totalCompanies}
            trend={+12}
            trendLabel="vs last month"
          />
        </motion.div>
        <motion.div variants={item}>
          <StatCard
            icon={AlertTriangle}
            label="High Risk Companies"
            value={stats.highRiskCompanies}
            trend={-3}
            trendLabel="vs last month"
            variant="danger"
          />
        </motion.div>
        <motion.div variants={item}>
          <StatCard
            icon={Users}
            label="Total Employees Scored"
            value={stats.totalEmployees}
            trend={+156}
            trendLabel="vs last month"
            formatNumber
          />
        </motion.div>
        <motion.div variants={item}>
          <StatCard
            icon={Scissors}
            label="Recommended Layoffs"
            value={stats.recommendedLayoffs}
            trend={+8}
            trendLabel="vs last month"
            variant="warning"
          />
        </motion.div>
      </motion.div>

      {/* Market Signals */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.12, duration: 0.4 }}
        className="card"
      >
        <h2 className="text-lg font-semibold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-primary-500" />
          Market Signals
        </h2>
        {marketIntelLoading && (
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner size="md" />
          </div>
        )}
        {marketIntelError && !marketIntelLoading && (
          <p className="text-sm text-amber-600 dark:text-amber-400 py-4">
            {marketIntelError}
          </p>
        )}
        {marketIntel && !marketIntelLoading && (
          <div className="space-y-3">
            {(marketIntel.sector || marketIntel.industry) && (
              <p className="text-xs text-slate-500 dark:text-dark-400">
                {[marketIntel.sector, marketIntel.industry].filter(Boolean).join(' · ')}
              </p>
            )}
            <p className="text-sm text-slate-700 dark:text-dark-300 leading-relaxed whitespace-pre-line">
              {marketIntel.market_summary}
            </p>
          </div>
        )}
      </motion.div>

      {/* Charts Row */}
      <motion.div
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        variants={container}
        initial="hidden"
        animate="show"
      >
        {/* Risk Distribution Pie Chart */}
        <motion.div variants={item} className="card">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-white mb-4">
            Risk Distribution
          </h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={4}
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                  }
                  labelLine={{ stroke: '#64748b', strokeWidth: 1 }}
                >
                  {riskDistributionData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.color}
                      stroke="transparent"
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={CHART_TOOLTIP_CONTENT_STYLE}
                  itemStyle={CHART_TOOLTIP_ITEM_STYLE}
                  formatter={(value) => [`${value} companies`, 'Count']}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  formatter={(value) => (
                    <span className="text-dark-300 text-sm">{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Department Attrition Bar Chart */}
        <motion.div variants={item} className="card">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-white mb-4">
            Department Attrition Risk
          </h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={departmentAttritionData}
                layout="vertical"
                margin={{ left: 20, right: 20 }}
              >
                <XAxis
                  type="number"
                  domain={[0, 50]}
                  tick={{ fill: '#94a3b8', fontSize: 12 }}
                  axisLine={{ stroke: '#334155' }}
                  tickLine={{ stroke: '#334155' }}
                />
                <YAxis
                  type="category"
                  dataKey="department"
                  tick={{ fill: '#94a3b8', fontSize: 12 }}
                  axisLine={{ stroke: '#334155' }}
                  tickLine={false}
                  width={80}
                />
                <Tooltip
                  contentStyle={CHART_TOOLTIP_CONTENT_STYLE}
                  itemStyle={CHART_TOOLTIP_ITEM_STYLE}
                  formatter={(value) => [`${value}%`, 'Attrition Risk']}
                  cursor={{ fill: 'rgba(6, 182, 212, 0.1)' }}
                />
                <Bar
                  dataKey="risk"
                  radius={[0, 4, 4, 0]}
                  maxBarSize={28}
                >
                  {departmentAttritionData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        entry.risk >= 40
                          ? '#ef4444'
                          : entry.risk >= 30
                          ? '#eab308'
                          : '#06b6d4'
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </motion.div>

      {/* Tracked Companies (Recently analyzed) */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.4 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-white">Tracked Companies</h2>
          <span className="text-sm text-slate-500 dark:text-dark-400">Recently analyzed</span>
        </div>
        {trackedCompanies.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-center py-10">
            <div className="w-14 h-14 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center mb-3">
              <Bookmark className="w-7 h-7 text-primary-500" />
            </div>
            <p className="font-medium text-slate-800 dark:text-white mb-1">No companies tracked yet</p>
            <p className="text-slate-500 dark:text-dark-400 text-sm mb-4">
              Run a single-company insolvency analysis to see it here.
            </p>
            <Link
              to="/insolvency"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-400 text-white font-medium text-sm transition-colors"
            >
              Run analysis
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-dark-700">
                  <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">Company</th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">Risk</th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">Z-Score</th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">Time</th>
                </tr>
              </thead>
              <tbody>
                {trackedCompanies.map((c, i) => (
                  <tr key={c.timestamp + (c.company_id ?? c.company_name ?? i)} className="border-b border-dark-800 last:border-b-0 hover:bg-dark-800/50 transition-colors">
                    <td className="py-3 px-4 text-white font-medium">{c.company_name || c.company_id || '—'}</td>
                    <td className="py-3 px-4">
                      <RiskBadge result={`${c.risk_category} Risk`} />
                    </td>
                    <td className="py-3 px-4 text-dark-200">{c.z_score.toFixed(2)}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2 text-dark-400 text-sm">
                        <Clock className="w-4 h-4" />
                        {formatTimeAgo(c.timestamp)}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>

      {/* Recent Activity Table - from API */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25, duration: 0.4 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-white">Recent Activity</h2>
          <span className="text-sm text-slate-500 dark:text-dark-400">Last 5 analyses</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-dark-700">
                <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">
                  Type
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">
                  Name
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">
                  Result
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">
                  Score
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">
                  Time
                </th>
              </tr>
            </thead>
            <tbody>
              {recentLoading ? (
                <tr className="border-b border-dark-800 last:border-b-0">
                  <td colSpan={5} className="py-6 px-4 text-center text-dark-400 text-sm">
                    Loading recent activity...
                  </td>
                </tr>
              ) : recentActivity.length === 0 ? (
                <tr className="border-b border-dark-800 last:border-b-0">
                  <td colSpan={5} className="py-10 px-4">
                    <div className="flex flex-col items-center justify-center text-center max-w-sm mx-auto">
                      <div className="w-16 h-16 rounded-2xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center mb-4">
                        <FileSpreadsheet className="w-8 h-8 text-primary-500" />
                      </div>
                      <p className="font-semibold text-slate-800 dark:text-white mb-1">No analyses yet</p>
                      <p className="text-slate-500 dark:text-dark-400 text-sm mb-4">
                        Upload your first company CSV to see risk analysis and Z-Score results.
                      </p>
                      <Link
                        to="/insolvency"
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-400 text-white font-medium text-sm transition-colors"
                      >
                        Run first analysis
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  </td>
                </tr>
              ) : (
                recentActivity.map((activity) => (
                  <tr
                    key={activity.id}
                    className="border-b border-dark-800 last:border-b-0 hover:bg-dark-800/50 transition-colors"
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <ActivityIcon type={activity.type} />
                        <span className="text-dark-200 text-sm">
                          {activity.type}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-white font-medium">
                      {activity.name}
                    </td>
                    <td className="py-3 px-4">
                      <RiskBadge result={activity.result} />
                    </td>
                    <td className="py-3 px-4 text-dark-200">
                      {activity.score ?? '—'}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2 text-dark-400 text-sm">
                        <Clock className="w-4 h-4" />
                        {formatTimeAgo(activity.timestamp)}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </motion.div>
    </motion.div>
  );
}

/**
 * Props for the StatCard component.
 */
interface StatCardProps {
  /** Icon component to display */
  icon: React.ElementType;
  /** Label text for the stat */
  label: string;
  /** The stat value to display (number animates with CountUp) */
  value: string | number;
  /** Trend value (positive or negative change) */
  trend: number;
  /** Label describing the trend comparison period */
  trendLabel: string;
  /** Visual variant for the card styling */
  variant?: 'default' | 'danger' | 'warning';
  /** Format large numbers with locale (e.g. 1,842) when using CountUp */
  formatNumber?: boolean;
}

/**
 * StatCard component displaying a single metric with trend indicator.
 * @param {StatCardProps} props - Component props
 * @returns {JSX.Element} Styled stat card with icon, value, and trend
 */
function StatCard({
  icon: Icon,
  label,
  value,
  trend,
  trendLabel,
  variant = 'default',
  formatNumber = false,
}: StatCardProps) {
  const variantStyles = {
    default: 'border-slate-200 bg-slate-50/80 dark:border-dark-700 dark:bg-dark-900',
    danger: 'border-red-300 bg-red-50/80 dark:border-red-500/30 dark:bg-red-500/5',
    warning: 'border-amber-300 bg-amber-50/80 dark:border-yellow-500/30 dark:bg-yellow-500/5',
  };

  const iconStyles = {
    default: 'bg-primary-500/20 text-primary-600 dark:text-primary-400',
    danger: 'bg-red-500/20 text-red-600 dark:text-red-400',
    warning: 'bg-amber-500/20 text-amber-600 dark:text-yellow-400',
  };

  return (
    <motion.div
      className={`rounded-xl border p-5 shadow-lg transition-all ${variantStyles[variant]}`}
      whileHover={{ y: -4, boxShadow: '0 20px 40px -15px rgba(0,0,0,0.35)' }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      <div className="flex items-start justify-between">
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center ${iconStyles[variant]}`}
        >
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex items-center gap-1">
          {trend > 0 ? (
            <TrendingUp className="w-4 h-4 text-green-400" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-400" />
          )}
          <span
            className={`text-xs font-medium ${
              trend > 0 ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {trend > 0 ? '+' : ''}
            {trend}
          </span>
        </div>
      </div>
      <div className="mt-4">
        <p className="text-3xl font-bold text-slate-800 dark:text-white">
          {typeof value === 'number' ? (
            <CountUp to={value} formatNumber={formatNumber} duration={1.4} />
          ) : (
            value
          )}
        </p>
        <p className="text-sm text-slate-500 dark:text-dark-400 mt-1">{label}</p>
      </div>
      <p className="text-xs text-slate-400 dark:text-dark-500 mt-2">{trendLabel}</p>
    </motion.div>
  );
}

/**
 * ActivityIcon component that renders an appropriate icon based on activity type.
 * @param {{ type: string }} props - Component props with activity type
 * @returns {JSX.Element} Icon element for the activity type
 */
function ActivityIcon({ type }: { type: string }) {
  const iconMap: Record<string, { icon: React.ElementType; color: string }> = {
    'Company Analysis': { icon: Building2, color: 'text-primary-400' },
    'Employee Scoring': { icon: Users, color: 'text-accent-400' },
    'Layoff Simulation': { icon: Scissors, color: 'text-purple-400' },
  };

  const { icon: Icon, color } = iconMap[type] || {
    icon: Building2,
    color: 'text-dark-400',
  };

  return <Icon className={`w-4 h-4 ${color}`} />;
}

/**
 * RiskBadge component displaying a color-coded risk level badge.
 * @param {{ result: string }} props - Component props with risk result text
 * @returns {JSX.Element} Styled badge indicating risk level
 */
function RiskBadge({ result }: { result: string }) {
  const getBadgeStyle = () => {
    if (result.includes('High')) {
      return 'bg-red-500/20 text-red-400 border-red-500/30';
    }
    if (result.includes('Medium')) {
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    }
    if (result.includes('Low')) {
      return 'bg-green-500/20 text-green-400 border-green-500/30';
    }
    return 'bg-dark-700 text-dark-300 border-dark-600';
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${getBadgeStyle()}`}
    >
      {result}
    </span>
  );
}
