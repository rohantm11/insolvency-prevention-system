/**
 * @fileoverview Compare two company insolvency analyses with SHAP, graphs, and clear visuals.
 */

import { useState, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
  ReferenceLine,
} from 'recharts';
import { Building2, ArrowRightLeft, AlertTriangle, BarChart3, Zap } from 'lucide-react';
import { analyzeCompany, uploadSingleCompany } from '../services/api';
import type { CompanyFinancialData, InsolvencyAnalysisResponse } from '../types';
import { FileUpload, RiskGauge } from '../components';
import { CHART_TOOLTIP_CONTENT_STYLE } from '../constants/chartStyles';

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

function formatFeatureName(name: string): string {
  return name
    .replace(/_/g, ' ')
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
    .trim();
}

export default function Compare() {
  const [resultA, setResultA] = useState<InsolvencyAnalysisResponse | null>(null);
  const [resultB, setResultB] = useState<InsolvencyAnalysisResponse | null>(null);
  const [loadingA, setLoadingA] = useState(false);
  const [loadingB, setLoadingB] = useState(false);
  const [fileA, setFileA] = useState<File | null>(null);
  const [fileB, setFileB] = useState<File | null>(null);
  const [formA, setFormA] = useState<CompanyFinancialData>({ ...defaultFormData, company_id: 'A', company_name: 'Company A' });
  const [formB, setFormB] = useState<CompanyFinancialData>({ ...defaultFormData, company_id: 'B', company_name: 'Company B' });
  const [error, setError] = useState<string | null>(null);

  const runAnalysisA = async () => {
    setLoadingA(true);
    setError(null);
    try {
      const res = fileA ? await uploadSingleCompany(fileA) : await analyzeCompany(formA);
      setResultA(res);
    } catch (e: unknown) {
      setError((e as { message?: string })?.message || 'Analysis A failed');
    } finally {
      setLoadingA(false);
    }
  };

  const runAnalysisB = async () => {
    setLoadingB(true);
    setError(null);
    try {
      const res = fileB ? await uploadSingleCompany(fileB) : await analyzeCompany(formB);
      setResultB(res);
    } catch (e: unknown) {
      setError((e as { message?: string })?.message || 'Analysis B failed');
    } finally {
      setLoadingB(false);
    }
  };

  const riskColor = (risk: string) => {
    if (risk === 'High') return 'text-red-400';
    if (risk === 'Medium') return 'text-yellow-400';
    return 'text-green-400';
  };

  const riskBadgeClass = (risk: string) => {
    if (risk === 'High') return 'bg-red-500/20 text-red-400 border-red-500/30';
    if (risk === 'Medium') return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    return 'bg-green-500/20 text-green-400 border-green-500/30';
  };

  const nameA = resultA?.prediction.company_name || 'Company A';
  const nameB = resultB?.prediction.company_name || 'Company B';

  const metricsComparisonData = useMemo(() => {
    if (!resultA || !resultB) return [];
    return [
      { metric: 'Z-Score', A: resultA.prediction.z_score, B: resultB.prediction.z_score, format: (v: number) => v.toFixed(2) },
      { metric: 'Distress %', A: resultA.prediction.probability_of_distress * 100, B: resultB.prediction.probability_of_distress * 100, format: (v: number) => `${v.toFixed(1)}%` },
    ];
  }, [resultA, resultB]);

  const shapDataA = useMemo(() => {
    if (!resultA?.explanation?.top_risk_drivers) return [];
    return resultA.explanation.top_risk_drivers.slice(0, 8).map((item) => ({
      name: formatFeatureName(item.feature),
      value: item.shap_value,
      fullName: item.feature,
    }));
  }, [resultA]);

  const shapDataB = useMemo(() => {
    if (!resultB?.explanation?.top_risk_drivers) return [];
    return resultB.explanation.top_risk_drivers.slice(0, 8).map((item) => ({
      name: formatFeatureName(item.feature),
      value: item.shap_value,
      fullName: item.feature,
    }));
  }, [resultB]);

  const bothReady = resultA && resultB;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <ArrowRightLeft className="w-6 h-6 text-primary-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">Compare Companies</h1>
          <p className="text-dark-400 text-sm">Run two insolvency analyses and compare risk, Z-Score, and SHAP drivers side-by-side.</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <p className="text-red-400 text-sm">{error}</p>
          <button type="button" onClick={() => setError(null)} className="btn btn-ghost btn-sm text-red-400 ml-auto">Dismiss</button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-dark-900 border border-dark-700 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-primary-400" />
            Company A
          </h2>
          <div className="space-y-3 mb-4">
            <FileUpload onFileSelect={setFileA} selectedFile={fileA} onClear={() => setFileA(null)} disabled={loadingA} />
            <div className="flex gap-2">
              <input type="text" className="input flex-1" placeholder="Company name" value={formA.company_name || ''} onChange={(e) => setFormA((p) => ({ ...p, company_name: e.target.value }))} />
              <button type="button" onClick={runAnalysisA} disabled={loadingA} className="btn btn-primary">{loadingA ? 'Analyzing...' : 'Analyze A'}</button>
            </div>
          </div>
          {resultA && (
            <div className="border-t border-dark-700 pt-4 space-y-2">
              <p className="text-white font-medium">{nameA}</p>
              <p className={`text-lg font-semibold ${riskColor(resultA.prediction.risk_category)}`}>{resultA.prediction.risk_category} Risk</p>
              <p className="text-dark-400 text-sm">Z-Score: {resultA.prediction.z_score.toFixed(2)} ({resultA.prediction.z_score_zone})</p>
              <p className="text-dark-400 text-sm">Distress: {(resultA.prediction.probability_of_distress * 100).toFixed(1)}%</p>
            </div>
          )}
        </div>

        <div className="bg-dark-900 border border-dark-700 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-primary-400" />
            Company B
          </h2>
          <div className="space-y-3 mb-4">
            <FileUpload onFileSelect={setFileB} selectedFile={fileB} onClear={() => setFileB(null)} disabled={loadingB} />
            <div className="flex gap-2">
              <input type="text" className="input flex-1" placeholder="Company name" value={formB.company_name || ''} onChange={(e) => setFormB((p) => ({ ...p, company_name: e.target.value }))} />
              <button type="button" onClick={runAnalysisB} disabled={loadingB} className="btn btn-primary">{loadingB ? 'Analyzing...' : 'Analyze B'}</button>
            </div>
          </div>
          {resultB && (
            <div className="border-t border-dark-700 pt-4 space-y-2">
              <p className="text-white font-medium">{nameB}</p>
              <p className={`text-lg font-semibold ${riskColor(resultB.prediction.risk_category)}`}>{resultB.prediction.risk_category} Risk</p>
              <p className="text-dark-400 text-sm">Z-Score: {resultB.prediction.z_score.toFixed(2)} ({resultB.prediction.z_score_zone})</p>
              <p className="text-dark-400 text-sm">Distress: {(resultB.prediction.probability_of_distress * 100).toFixed(1)}%</p>
            </div>
          )}
        </div>
      </div>

      {bothReady && (
        <div className="space-y-6 animate-fade-in">
          {/* Headline: Gauges + Z-Score bars */}
          <div className="bg-dark-900 border border-dark-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary-400" />
              Risk at a glance
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="flex flex-col items-center">
                <p className="text-dark-300 text-sm font-medium mb-2">{nameA}</p>
                <RiskGauge value={resultA.prediction.probability_of_distress} label="Distress probability" size="md" riskCategory={resultA.prediction.risk_category} />
                <div className="w-full mt-4">
                  <p className="text-xs text-dark-500 mb-1">Z-Score</p>
                  <div className="relative h-3 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-full">
                    <div className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full border-2 border-dark-900 shadow z-10" style={{ left: `${Math.min(Math.max((resultA.prediction.z_score / 5) * 100, 0), 100)}%`, transform: 'translate(-50%, -50%)' }} />
                  </div>
                  <div className="flex justify-between mt-0.5 text-xs text-dark-500"><span>0</span><span>1.81</span><span>2.99</span><span>5+</span></div>
                </div>
              </div>
              <div className="flex flex-col items-center">
                <p className="text-dark-300 text-sm font-medium mb-2">{nameB}</p>
                <RiskGauge value={resultB.prediction.probability_of_distress} label="Distress probability" size="md" riskCategory={resultB.prediction.risk_category} />
                <div className="w-full mt-4">
                  <p className="text-xs text-dark-500 mb-1">Z-Score</p>
                  <div className="relative h-3 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-full">
                    <div className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full border-2 border-dark-900 shadow z-10" style={{ left: `${Math.min(Math.max((resultB.prediction.z_score / 5) * 100, 0), 100)}%`, transform: 'translate(-50%, -50%)' }} />
                  </div>
                  <div className="flex justify-between mt-0.5 text-xs text-dark-500"><span>0</span><span>1.81</span><span>2.99</span><span>5+</span></div>
                </div>
              </div>
            </div>
          </div>

          {/* Bar chart: Z-Score & Distress % comparison */}
          <div className="bg-dark-900 border border-dark-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Metric comparison</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metricsComparisonData} layout="vertical" margin={{ top: 10, right: 30, left: 80, bottom: 10 }}>
                  <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={{ stroke: '#334155' }} tickLine={{ stroke: '#334155' }} />
                  <YAxis type="category" dataKey="metric" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={{ stroke: '#334155' }} tickLine={false} width={70} />
                  <Tooltip contentStyle={CHART_TOOLTIP_CONTENT_STYLE} formatter={(value, _name, props) => (props?.payload?.format ? props.payload.format(Number(value ?? 0)) : String(value ?? 0))} />
                  <Legend />
                  <Bar dataKey="A" name={nameA} fill="#06b6d4" radius={[0, 4, 4, 0]} maxBarSize={28} />
                  <Bar dataKey="B" name={nameB} fill="#8b5cf6" radius={[0, 4, 4, 0]} maxBarSize={28} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* SHAP side by side */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-dark-900 border border-dark-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-1 flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-400" />
                Risk drivers — {nameA}
              </h3>
              <p className="text-dark-500 text-xs mb-4">Red = increases risk, Green = decreases risk</p>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={shapDataA} layout="vertical" margin={{ top: 5, right: 24, left: 100, bottom: 5 }}>
                    <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={{ stroke: '#334155' }} tickLine={{ stroke: '#334155' }} />
                    <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={{ stroke: '#334155' }} tickLine={false} width={95} />
                    <Tooltip contentStyle={CHART_TOOLTIP_CONTENT_STYLE} formatter={(value: number | undefined) => [(value ?? 0).toFixed(4), 'SHAP']} />
                    <ReferenceLine x={0} stroke="#475569" strokeWidth={1} />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={20}>
                      {shapDataA.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.value >= 0 ? '#ef4444' : '#22c55e'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="bg-dark-900 border border-dark-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-1 flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-400" />
                Risk drivers — {nameB}
              </h3>
              <p className="text-dark-500 text-xs mb-4">Red = increases risk, Green = decreases risk</p>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={shapDataB} layout="vertical" margin={{ top: 5, right: 24, left: 100, bottom: 5 }}>
                    <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={{ stroke: '#334155' }} tickLine={{ stroke: '#334155' }} />
                    <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={{ stroke: '#334155' }} tickLine={false} width={95} />
                    <Tooltip contentStyle={CHART_TOOLTIP_CONTENT_STYLE} formatter={(value: number | undefined) => [(value ?? 0).toFixed(4), 'SHAP']} />
                    <ReferenceLine x={0} stroke="#475569" strokeWidth={1} />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={20}>
                      {shapDataB.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.value >= 0 ? '#ef4444' : '#22c55e'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Executive summaries */}
          {(resultA.prediction.executive_summary || resultB.prediction.executive_summary) && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {resultA.prediction.executive_summary && (
                <div className="bg-primary-500/10 border border-primary-500/30 rounded-xl p-5">
                  <h4 className="text-sm font-semibold text-primary-300 mb-2">Summary — {nameA}</h4>
                  <p className="text-dark-200 text-sm leading-relaxed">{resultA.prediction.executive_summary}</p>
                </div>
              )}
              {resultB.prediction.executive_summary && (
                <div className="bg-primary-500/10 border border-primary-500/30 rounded-xl p-5">
                  <h4 className="text-sm font-semibold text-primary-300 mb-2">Summary — {nameB}</h4>
                  <p className="text-dark-200 text-sm leading-relaxed">{resultB.prediction.executive_summary}</p>
                </div>
              )}
            </div>
          )}

          {/* Comparison table */}
          <div className="bg-dark-900 border border-dark-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Side-by-side metrics</h3>
            <div className="overflow-x-auto rounded-lg border border-dark-700">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-dark-800 border-b border-dark-700">
                    <th className="text-left py-3 px-4 text-xs font-semibold text-dark-400 uppercase tracking-wider">Metric</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-cyan-400">{nameA}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-purple-400">{nameB}</th>
                  </tr>
                </thead>
                <tbody className="text-dark-200">
                  <tr className="border-b border-dark-800">
                    <td className="py-3 px-4 text-dark-400">Risk category</td>
                    <td className="py-3 px-4"><span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium border ${riskBadgeClass(resultA.prediction.risk_category)}`}>{resultA.prediction.risk_category}</span></td>
                    <td className="py-3 px-4"><span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium border ${riskBadgeClass(resultB.prediction.risk_category)}`}>{resultB.prediction.risk_category}</span></td>
                  </tr>
                  <tr className="border-b border-dark-800">
                    <td className="py-3 px-4 text-dark-400">Z-Score</td>
                    <td className="py-3 px-4 text-white font-medium">{resultA.prediction.z_score.toFixed(2)}</td>
                    <td className="py-3 px-4 text-white font-medium">{resultB.prediction.z_score.toFixed(2)}</td>
                  </tr>
                  <tr className="border-b border-dark-800">
                    <td className="py-3 px-4 text-dark-400">Z-Score zone</td>
                    <td className="py-3 px-4">{resultA.prediction.z_score_zone}</td>
                    <td className="py-3 px-4">{resultB.prediction.z_score_zone}</td>
                  </tr>
                  <tr className="border-b border-dark-800">
                    <td className="py-3 px-4 text-dark-400">Distress probability</td>
                    <td className="py-3 px-4">{(resultA.prediction.probability_of_distress * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4">{(resultB.prediction.probability_of_distress * 100).toFixed(1)}%</td>
                  </tr>
                  {resultA.prediction.estimated_time_to_event != null || resultB.prediction.estimated_time_to_event != null ? (
                    <tr className="border-b border-dark-800">
                      <td className="py-3 px-4 text-dark-400">Est. years to event</td>
                      <td className="py-3 px-4">{resultA.prediction.estimated_time_to_event ?? '—'}</td>
                      <td className="py-3 px-4">{resultB.prediction.estimated_time_to_event ?? '—'}</td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
