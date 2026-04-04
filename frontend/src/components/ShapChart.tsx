import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';

interface ShapChartProps {
  data: Array<{
    feature: string;
    shap_value: number;
    original_value: number | string;
    impact: string;
  }>;
  title?: string;
  maxItems?: number;
}

export default function ShapChart({
  data,
  title = 'Feature Impact (SHAP Values)',
  maxItems = 10,
}: ShapChartProps) {
  const chartData = data.slice(0, maxItems).map((item) => ({
    name: formatFeatureName(item.feature),
    value: item.shap_value,
    originalValue: item.original_value,
    impact: item.impact,
    fullName: item.feature,
  }));

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 24, scale: 0.98 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
    >
      <h3 className="card-header">{title}</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
          >
            <defs>
              <linearGradient id="shap-red" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#ef4444" />
                <stop offset="100%" stopColor="#f87171" />
              </linearGradient>
              <linearGradient id="shap-green" x1="1" y1="0" x2="0" y2="0">
                <stop offset="0%" stopColor="#22c55e" />
                <stop offset="100%" stopColor="#4ade80" />
              </linearGradient>
            </defs>
            <XAxis
              type="number"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              axisLine={{ stroke: '#334155' }}
              tickLine={{ stroke: '#334155' }}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              axisLine={{ stroke: '#334155' }}
              tickLine={false}
              width={110}
            />
            <Tooltip
              content={<CustomTooltip />}
              cursor={{ fill: 'rgba(6, 182, 212, 0.08)' }}
            />
            <ReferenceLine x={0} stroke="#475569" strokeWidth={1} />
            <Bar
              dataKey="value"
              radius={[0, 4, 4, 0]}
              maxBarSize={24}
              animationBegin={0}
              animationDuration={800}
              animationEasing="ease-out"
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.value >= 0 ? 'url(#shap-red)' : 'url(#shap-green)'}
                  style={{ filter: `drop-shadow(0 0 4px ${entry.value >= 0 ? 'rgba(239,68,68,0.3)' : 'rgba(34,197,94,0.3)'})` }}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-gradient-to-r from-red-500 to-red-400" />
          <span className="text-dark-400">Increases Risk</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-gradient-to-r from-green-500 to-green-400" />
          <span className="text-dark-400">Decreases Risk</span>
        </div>
      </div>
    </motion.div>
  );
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;

  const data = payload[0].payload;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.15 }}
      className="bg-dark-900/95 border rounded-lg p-3 shadow-xl backdrop-blur-sm"
      style={{
        borderColor: 'rgba(6,182,212,0.25)',
        boxShadow: '0 0 20px rgba(6,182,212,0.1), 0 10px 30px rgba(0,0,0,0.3)',
      }}
    >
      <p className="text-white font-medium mb-1">{data.fullName}</p>
      <p className="text-dark-300 text-sm">
        Value: <span className="text-white">{data.originalValue}</span>
      </p>
      <p className="text-dark-300 text-sm">
        SHAP:{' '}
        <span className={data.value >= 0 ? 'text-red-400' : 'text-green-400'}>
          {data.value >= 0 ? '+' : ''}
          {data.value.toFixed(4)}
        </span>
      </p>
      <p className="text-dark-400 text-xs mt-1 capitalize">{data.impact}</p>
    </motion.div>
  );
}

function formatFeatureName(name: string): string {
  return name
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
    .trim();
}
