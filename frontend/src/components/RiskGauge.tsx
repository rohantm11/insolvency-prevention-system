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
          return { stroke: '#22c55e', bg: 'rgba(34, 197, 94, 0.1)', glow: 'rgba(34, 197, 94, 0.3)' };
        case 'Medium':
          return { stroke: '#eab308', bg: 'rgba(234, 179, 8, 0.1)', glow: 'rgba(234, 179, 8, 0.3)' };
        case 'High':
          return { stroke: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', glow: 'rgba(239, 68, 68, 0.3)' };
      }
    }
    if (normalizedValue < 30) {
      return { stroke: '#22c55e', bg: 'rgba(34, 197, 94, 0.1)', glow: 'rgba(34, 197, 94, 0.3)' };
    } else if (normalizedValue < 70) {
      return { stroke: '#eab308', bg: 'rgba(234, 179, 8, 0.1)', glow: 'rgba(234, 179, 8, 0.3)' };
    } else {
      return { stroke: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', glow: 'rgba(239, 68, 68, 0.3)' };
    }
  };

  const colors = getColor();
  const progress = (normalizedValue / 100) * circumference;
  // Pulse speed increases with risk level
  const pulseDuration = Math.max(0.8, 2.5 - (normalizedValue / 100) * 1.7);
  const outerR = radius + strokeWidth + 6;
  const outerCirc = 2 * Math.PI * outerR;

  return (
    <motion.div
      className="flex flex-col items-center"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', stiffness: 200, damping: 25 }}
    >
      <div className="relative" style={{ width: width + 16, height: height + 16 }}>
        <svg width={width + 16} height={height + 16} className="transform -rotate-90">
          <defs>
            <filter id={`glow-${label}`}>
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Outer decorative dashed ring — slow rotation */}
          <circle
            cx={(width + 16) / 2}
            cy={(height + 16) / 2}
            r={outerR}
            fill="none"
            stroke={colors.stroke}
            strokeWidth={1}
            strokeDasharray={`${outerCirc / 40} ${outerCirc / 20}`}
            opacity={0.25}
            className="gauge-outer-ring"
            style={{ transformOrigin: 'center' }}
          />

          {/* Background track */}
          <circle
            cx={(width + 16) / 2}
            cy={(height + 16) / 2}
            r={radius}
            fill="none"
            stroke="#1e293b"
            strokeWidth={strokeWidth}
          />

          {/* Pulsing ring behind progress */}
          <motion.circle
            cx={(width + 16) / 2}
            cy={(height + 16) / 2}
            r={radius}
            fill="none"
            stroke={colors.stroke}
            strokeWidth={strokeWidth + 4}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference - progress}
            animate={{ opacity: [0.15, 0.4, 0.15], scale: [0.98, 1.02, 0.98] }}
            transition={{ repeat: Infinity, duration: pulseDuration, ease: 'easeInOut' }}
            style={{ transformOrigin: 'center', filter: `blur(6px)` }}
          />

          {/* Main progress arc */}
          <motion.circle
            cx={(width + 16) / 2}
            cy={(height + 16) / 2}
            r={radius}
            fill="none"
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - progress }}
            transition={{ duration: 1, ease: [0.25, 0.46, 0.45, 0.94] }}
            filter={`url(#glow-${label})`}
            style={{ filter: `drop-shadow(0 0 10px ${colors.glow})` }}
          />
        </svg>

        {/* Center content */}
        <div
          className="absolute inset-2 flex flex-col items-center justify-center transition-colors duration-500 rounded-full"
          style={{ backgroundColor: colors.bg }}
        >
          <motion.span
            key={Math.round(normalizedValue)}
            initial={{ scale: 1.15, opacity: 0.7 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            className={`font-bold text-white ${fontSize}`}
            style={{ fontVariantNumeric: 'tabular-nums', textShadow: `0 0 20px ${colors.glow}` }}
          >
            {showPercentage ? `${Math.round(displayNum)}%` : displayNum.toFixed(1)}
          </motion.span>
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
