import { useMemo, useEffect, useState } from 'react';
import { motion, useMotionValue, useSpring, useMotionValueEvent } from 'framer-motion';

interface RiskGaugeProps {
  value: number; // 0-100 or 0-1
  label: string;
  size?: 'sm' | 'md' | 'lg';
  showPercentage?: boolean;
  riskCategory?: 'Low' | 'Medium' | 'High' | string;
}

export default function RiskGauge({
  value,
  label,
  size = 'md',
  showPercentage = true,
  riskCategory,
}: RiskGaugeProps) {
  const normalizedValue = value > 1 ? value : value * 100;
  const displayValue = useMotionValue(0);
  const springValue = useSpring(displayValue, { stiffness: 60, damping: 25 });
  const [displayNum, setDisplayNum] = useState(0);

  useEffect(() => {
    displayValue.set(normalizedValue);
  }, [normalizedValue, displayValue]);

  useMotionValueEvent(springValue, 'change', (v) => setDisplayNum(v));

  const dimensions = useMemo(() => {
    switch (size) {
      case 'sm':
        return { width: 120, height: 120, strokeWidth: 8, fontSize: 'text-xl' };
      case 'lg':
        return { width: 200, height: 200, strokeWidth: 14, fontSize: 'text-4xl' };
      default:
        return { width: 160, height: 160, strokeWidth: 12, fontSize: 'text-3xl' };
    }
  }, [size]);

  const { width, height, strokeWidth, fontSize } = dimensions;
  const radius = (width - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  const getColor = () => {
    if (riskCategory) {
      switch (riskCategory) {
        case 'Low':
          return { stroke: '#22c55e', bg: 'rgba(34, 197, 94, 0.1)' };
        case 'Medium':
          return { stroke: '#eab308', bg: 'rgba(234, 179, 8, 0.1)' };
        case 'High':
          return { stroke: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' };
      }
    }

    if (normalizedValue < 30) {
      return { stroke: '#22c55e', bg: 'rgba(34, 197, 94, 0.1)' };
    } else if (normalizedValue < 70) {
      return { stroke: '#eab308', bg: 'rgba(234, 179, 8, 0.1)' };
    } else {
      return { stroke: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' };
    }
  };

  const colors = getColor();
  const progress = (normalizedValue / 100) * circumference;

  return (
    <motion.div
      className="flex flex-col items-center"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', stiffness: 200, damping: 25 }}
    >
      <div className="relative" style={{ width, height }}>
        <svg width={width} height={height} className="transform -rotate-90">
          <circle
            cx={width / 2}
            cy={height / 2}
            r={radius}
            fill="none"
            stroke="#1e293b"
            strokeWidth={strokeWidth}
          />
          <motion.circle
            cx={width / 2}
            cy={height / 2}
            r={radius}
            fill="none"
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - progress }}
            transition={{ duration: 1, ease: [0.25, 0.46, 0.45, 0.94] }}
            style={{ filter: `drop-shadow(0 0 8px ${colors.stroke})` }}
          />
        </svg>

        <div
          className="absolute inset-0 flex flex-col items-center justify-center transition-colors duration-500"
          style={{ backgroundColor: colors.bg, borderRadius: '50%' }}
        >
          <span
            className={`font-bold text-white ${fontSize}`}
            style={{ fontVariantNumeric: 'tabular-nums' }}
          >
            {showPercentage ? `${Math.round(displayNum)}%` : displayNum.toFixed(1)}
          </span>
          {riskCategory && (
            <span className="text-sm font-medium mt-1" style={{ color: colors.stroke }}>
              {riskCategory}
            </span>
          )}
        </div>
      </div>
      <span className="mt-3 text-sm text-dark-400 font-medium">{label}</span>
    </motion.div>
  );
}
