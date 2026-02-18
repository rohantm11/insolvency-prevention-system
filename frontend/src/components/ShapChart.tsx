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
    <div className="card">
      <h3 className="card-header">{title}</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
          >
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
              cursor={{ fill: 'rgba(6, 182, 212, 0.1)' }}
            />
            <ReferenceLine x={0} stroke="#475569" strokeWidth={1} />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={24}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.value >= 0 ? '#ef4444' : '#22c55e'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-red-500" />
          <span className="text-dark-400">Increases Risk</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-green-500" />
          <span className="text-dark-400">Decreases Risk</span>
        </div>
      </div>
    </div>
  );
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;

  const data = payload[0].payload;

  return (
    <div className="bg-dark-900 border border-dark-700 rounded-lg p-3 shadow-lg">
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
    </div>
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
