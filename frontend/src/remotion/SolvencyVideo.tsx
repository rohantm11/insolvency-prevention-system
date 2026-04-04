import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Sequence,
} from 'remotion';

const clamp = (v: number, min: number, max: number) =>
  Math.min(max, Math.max(min, v));

function useSpring(
  frame: number,
  fps: number,
  delay = 0,
  config: { damping?: number; stiffness?: number; mass?: number } = {}
) {
  return spring({
    frame: frame - delay,
    fps,
    config: { damping: 14, stiffness: 120, mass: 1, ...config },
  });
}

const PARTICLES = Array.from({ length: 60 }, (_, i) => ({
  x: (i * 137.508) % 1920,
  speed: 2 + ((i * 31) % 5),
  size: 20 + ((i * 17) % 28),
  opacity: 0.08 + ((i * 7) % 40) / 100,
  char: ['$', '%', '0', '1', '↓', '▲', '−', '+', '8', '3'][i % 10],
  delay: (i * 7) % 90,
}));

const GRID_LINES = Array.from({ length: 8 }, (_, i) => i);

const SceneStorm: React.FC<{ frame: number; fps: number }> = ({ frame }) => {
  const progress = clamp(frame / 90, 0, 1);
  return (
    <AbsoluteFill
      style={{
        background:
          'radial-gradient(ellipse at 50% 60%, #1a0505 0%, #050508 60%, #000000 100%)',
        overflow: 'hidden',
      }}
    >
      <svg
        width="1920"
        height="1080"
        style={{ position: 'absolute', opacity: 0.07 }}
      >
        {GRID_LINES.map((i) => (
          <React.Fragment key={i}>
            <line
              x1={i * 240}
              y1={0}
              x2={i * 240}
              y2={1080}
              stroke="#3b82f6"
              strokeWidth={1}
            />
            <line
              x1={0}
              y1={i * 135}
              x2={1920}
              y2={i * 135}
              stroke="#3b82f6"
              strokeWidth={1}
            />
          </React.Fragment>
        ))}
      </svg>
      {PARTICLES.map((p, i) => {
        const y = ((frame * p.speed + p.delay * 20) % 1200) - 100;
        const flicker = Math.sin(frame * 0.3 + i) > 0.7 ? 0 : 1;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: p.x,
              top: y,
              color: i % 5 === 0 ? '#ef4444' : '#3b82f6',
              fontSize: p.size,
              fontFamily: "'Courier New', monospace",
              opacity: p.opacity * flicker * progress,
              fontWeight: 'bold',
            }}
          >
            {p.char}
          </div>
        );
      })}
      {[0, 1, 2].map((r) => {
        const age = (frame - r * 20 + 90) % 90;
        const scale = age / 90;
        return (
          <div
            key={r}
            style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              width: 600,
              height: 600,
              marginLeft: -300,
              marginTop: -300,
              borderRadius: '50%',
              border: '2px solid #ef4444',
              transform: `scale(${scale * 2})`,
              opacity: (1 - scale) * 0.4 * progress,
            }}
          />
        );
      })}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,0.8) 100%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: '#000',
          opacity: interpolate(frame, [0, 20], [1, 0]),
        }}
      />
    </AbsoluteFill>
  );
};

/** Straight line: green going up (left to peak), red going down (peak to right). One line, two segments. */
function getStockChartPoints(): { green: [number, number][]; red: [number, number][]; crashPoint: [number, number] } {
  const green: [number, number][] = [[100, 580], [900, 380]];
  const red: [number, number][] = [[900, 380], [1600, 680]];
  return { green, red, crashPoint: [900, 380] };
}

const STOCK_CHART = getStockChartPoints();

function pathLengthFromPoints(points: [number, number][]): number {
  let len = 0;
  for (let i = 1; i < points.length; i++) {
    const [x0, y0] = points[i - 1];
    const [x1, y1] = points[i];
    len += Math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2);
  }
  return len;
}

const GREEN_CHART_LENGTH = pathLengthFromPoints(STOCK_CHART.green);
const RED_CHART_LENGTH = pathLengthFromPoints(STOCK_CHART.red);

function pointsToPathD(points: [number, number][]): string {
  if (points.length === 0) return '';
  const [x0, y0] = points[0];
  let d = `M ${x0} ${y0}`;
  for (let i = 1; i < points.length; i++) {
    d += ` L ${points[i][0]} ${points[i][1]}`;
  }
  return d;
}

const SceneSignal: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const textSpring = useSpring(frame, fps, 10);
  const subSpring = useSpring(frame, fps, 30);
  const sceneOpacity = Math.min(
    interpolate(frame, [0, 15], [0, 1]),
    interpolate(frame, [75, 90], [1, 0])
  );

  const greenOffset = interpolate(frame, [0, 70], [GREEN_CHART_LENGTH, 0]);
  const redOffset = interpolate(frame, [70, 105], [RED_CHART_LENGTH, 0]);
  const crashMarkerOpacity = interpolate(frame, [68, 78], [0, 1]);
  const greenD = pointsToPathD(STOCK_CHART.green);
  const redD = pointsToPathD(STOCK_CHART.red);
  const [crashX, crashY] = STOCK_CHART.crashPoint;

  return (
    <AbsoluteFill
      style={{
        background:
          'radial-gradient(ellipse at 50% 40%, #0d0d1a 0%, #050508 100%)',
        overflow: 'hidden',
        opacity: sceneOpacity,
      }}
    >
      <svg width="1920" height="1080" style={{ position: 'absolute' }}>
        <defs>
          <filter id="greenGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx={0} dy={0} stdDeviation={3} floodColor="#22c55e" floodOpacity={0.9} />
          </filter>
          <filter id="redGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx={0} dy={0} stdDeviation={4} floodColor="#ef4444" floodOpacity={0.9} />
          </filter>
        </defs>
        <path
          d={greenD}
          fill="none"
          stroke="#22c55e"
          strokeWidth={3}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={GREEN_CHART_LENGTH}
          strokeDashoffset={greenOffset}
          filter="url(#greenGlow)"
        />
        <path
          d={redD}
          fill="none"
          stroke="#ef4444"
          strokeWidth={3}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={RED_CHART_LENGTH}
          strokeDashoffset={redOffset}
          filter="url(#redGlow)"
        />
        <text
          x={crashX}
          y={crashY - 14}
          textAnchor="middle"
          fill="#ef4444"
          fontSize={20}
          fontWeight="bold"
          opacity={crashMarkerOpacity}
          filter="url(#redGlow)"
        >
          ▼
        </text>
      </svg>
      <div
        style={{
          position: 'absolute',
          top: '28%',
          left: 0,
          right: 0,
          textAlign: 'center',
          transform: `translateY(${interpolate(textSpring, [0, 1], [60, 0])}px)`,
          opacity: textSpring,
        }}
      >
        <div
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 192,
            fontWeight: 900,
            color: '#ffffff',
            letterSpacing: '-4px',
            lineHeight: 1.05,
            textShadow: '0 0 120px rgba(239,68,68,0.5), 0 2px 4px rgba(0,0,0,0.3)',
            WebkitFontSmoothing: 'antialiased',
          }}
        >
          Most businesses
          <br />
          <span style={{ color: '#ef4444' }}>don't see it coming.</span>
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          top: '62%',
          left: 0,
          right: 0,
          textAlign: 'center',
          opacity: subSpring,
          transform: `translateY(${interpolate(subSpring, [0, 1], [30, 0])}px)`,
        }}
      >
        <div
          style={{
            fontFamily: "'Courier New', monospace",
            fontSize: 52,
            color: '#9ca3af',
            letterSpacing: '8px',
            textTransform: 'uppercase',
            WebkitFontSmoothing: 'antialiased',
          }}
        >
          Financial distress signals are there — if you know where to look
        </div>
      </div>
    </AbsoluteFill>
  );
};

const RiskMeter: React.FC<{
  value: number;
  label: string;
  color: string;
  delay: number;
  frame: number;
  fps: number;
}> = ({ value, label, color, delay, frame, fps }) => {
  const s = useSpring(frame, fps, delay, { damping: 18, stiffness: 80 });
  const bar = value * s;
  return (
    <div style={{ marginBottom: 18 }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: 6,
        }}
      >
        <span
          style={{
            fontFamily: "'Courier New', monospace",
            fontSize: 26,
            color: '#cbd5e1',
            letterSpacing: 3,
            textTransform: 'uppercase',
            WebkitFontSmoothing: 'antialiased',
          }}
        >
          {label}
        </span>
        <span
          style={{
            fontFamily: "'Courier New', monospace",
            fontSize: 26,
            color,
            fontWeight: 600,
          }}
        >
          {Math.round(bar * 100)}%
        </span>
      </div>
      <div
        style={{
          height: 6,
          background: 'rgba(255,255,255,0.08)',
          borderRadius: 3,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${bar * 100}%`,
            background: `linear-gradient(90deg, ${color}88, ${color})`,
            borderRadius: 3,
            boxShadow: `0 0 12px ${color}`,
          }}
        />
      </div>
    </div>
  );
};

const QuarterlyBar: React.FC<{
  frame: number;
  fps: number;
  delay: number;
  height: number;
  isLast: boolean;
  index: number;
}> = ({ frame, fps, delay, height, isLast, index }) => {
  const barSpring = useSpring(frame, fps, delay, { damping: 20, stiffness: 20 });
  const barH = height * barSpring * 120;
  return (
    <div
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'flex-end',
        height: '100%',
      }}
    >
      <div
        style={{
          width: '100%',
          height: barH,
          background: isLast
            ? 'linear-gradient(180deg, #22c55e, #16a34a)'
            : index < 3
              ? 'linear-gradient(180deg, #ef444488, #ef444444)'
              : 'linear-gradient(180deg, #3b82f688, #3b82f644)',
          borderRadius: '4px 4px 0 0',
          boxShadow: isLast ? '0 0 16px rgba(34,197,94,0.4)' : 'none',
        }}
      />
    </div>
  );
};

const SceneProduct: React.FC<{ frame: number; fps: number }> = ({
  frame,
  fps,
}) => {
  const dashboardSpring = useSpring(frame, fps, 5, {
    damping: 20,
    stiffness: 60,
  });
  const sceneOpacity = Math.min(
    interpolate(frame, [0, 20], [0, 1]),
    interpolate(frame, [100, 120], [1, 0])
  );
  const scoreSpring = useSpring(frame, fps, 10, { damping: 22, stiffness: 50 });
  const score = Math.round(interpolate(scoreSpring, [0, 1], [22, 87]));
  const scoreColor =
    score > 70 ? '#22c55e' : score > 40 ? '#f59e0b' : '#ef4444';
  const bars = [0.72, 0.45, 0.81, 0.38, 0.91, 0.62, 0.78];
  return (
    <AbsoluteFill
      style={{
        background:
          'radial-gradient(ellipse at 30% 50%, #060818 0%, #020204 100%)',
        overflow: 'hidden',
        opacity: sceneOpacity,
      }}
    >
      <div
        style={{
          position: 'absolute',
          left: '5%',
          top: '10%',
          width: 700,
          height: 700,
          borderRadius: '50%',
          background:
            'radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: '8%',
          top: '10%',
          width: '84%',
          height: '80%',
          background: 'rgba(10,14,28,0.95)',
          border: '1px solid rgba(59,130,246,0.25)',
          borderRadius: 16,
          padding: 48,
          transform: `scale(${interpolate(dashboardSpring, [0, 1], [0.92, 1])}) translateY(${interpolate(dashboardSpring, [0, 1], [40, 0])}px)`,
          boxShadow:
            '0 0 80px rgba(59,130,246,0.12), 0 40px 120px rgba(0,0,0,0.8)',
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 40,
          }}
        >
          <div>
            <div
              style={{
                fontFamily: "'Georgia', serif",
                fontSize: 36,
                color: '#3b82f6',
                letterSpacing: 10,
                textTransform: 'uppercase',
                marginBottom: 8,
                WebkitFontSmoothing: 'antialiased',
              }}
            >
              SolvencyInsight
            </div>
            <div
              style={{
                fontFamily: "'Courier New', monospace",
                fontSize: 24,
                color: '#64748b',
                letterSpacing: 4,
                WebkitFontSmoothing: 'antialiased',
              }}
            >
              RISK INTELLIGENCE DASHBOARD — LIVE
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            {['ANALYZING', 'AI MODEL v3.2', 'REAL-TIME'].map((tag) => (
              <div
                key={tag}
                style={{
                  padding: '10px 20px',
                  background: 'rgba(59,130,246,0.1)',
                  border: '1px solid rgba(59,130,246,0.3)',
                  borderRadius: 6,
                  fontFamily: "'Courier New', monospace",
                  fontSize: 20,
                  color: '#3b82f6',
                  letterSpacing: 4,
                  WebkitFontSmoothing: 'antialiased',
                }}
              >
                {tag}
              </div>
            ))}
          </div>
        </div>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 1fr',
            gap: 32,
          }}
        >
          <div
            style={{
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: 12,
              padding: 28,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <div
              style={{
                fontFamily: "'Courier New', monospace",
                fontSize: 22,
                color: '#9ca3af',
                letterSpacing: 5,
                marginBottom: 24,
                textTransform: 'uppercase',
                WebkitFontSmoothing: 'antialiased',
              }}
            >
              Solvency Score
            </div>
            <div
              style={{
                fontSize: 176,
                fontWeight: 900,
                fontFamily: "'Georgia', serif",
                color: scoreColor,
                lineHeight: 1,
                textShadow: `0 0 60px ${scoreColor}88, 0 2px 4px rgba(0,0,0,0.3)`,
                WebkitFontSmoothing: 'antialiased',
              }}
            >
              {score}
            </div>
            <div
              style={{
                fontFamily: "'Courier New', monospace",
                fontSize: 22,
                color: scoreColor,
                marginTop: 12,
                letterSpacing: 4,
                fontWeight: 600,
                WebkitFontSmoothing: 'antialiased',
              }}
            >
              {score > 70
                ? '▲ LOW RISK'
                : score > 40
                  ? '● MODERATE'
                  : '▼ HIGH RISK'}
            </div>
          </div>
          <div
            style={{
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: 12,
              padding: 28,
            }}
          >
            <div
              style={{
                fontFamily: "'Courier New', monospace",
                fontSize: 22,
                color: '#9ca3af',
                letterSpacing: 5,
                marginBottom: 28,
                textTransform: 'uppercase',
                WebkitFontSmoothing: 'antialiased',
              }}
            >
              Risk Indicators
            </div>
            <RiskMeter
              value={0.82}
              label="Liquidity"
              color="#22c55e"
              delay={20}
              frame={frame}
              fps={fps}
            />
            <RiskMeter
              value={0.61}
              label="Leverage"
              color="#f59e0b"
              delay={35}
              frame={frame}
              fps={fps}
            />
            <RiskMeter
              value={0.23}
              label="Distress"
              color="#ef4444"
              delay={50}
              frame={frame}
              fps={fps}
            />
            <RiskMeter
              value={0.91}
              label="Coverage"
              color="#22c55e"
              delay={65}
              frame={frame}
              fps={fps}
            />
          </div>
          <div
            style={{
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: 12,
              padding: 28,
            }}
          >
            <div
              style={{
                fontFamily: "'Courier New', monospace",
                fontSize: 22,
                color: '#9ca3af',
                letterSpacing: 5,
                marginBottom: 28,
                textTransform: 'uppercase',
                WebkitFontSmoothing: 'antialiased',
              }}
            >
              Quarterly Trend
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'flex-end',
                gap: 12,
                height: 140,
              }}
            >
              {bars.map((h, i) => (
                <QuarterlyBar
                  key={i}
                  frame={frame}
                  fps={fps}
                  delay={i * 8 + 15}
                  height={h}
                  isLast={i === bars.length - 1}
                  index={i}
                />
              ))}
            </div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: 8,
              }}
            >
              {['Q1', 'Q2', 'Q3', 'Q4', 'Q1', 'Q2', 'Q3'].map((q, i) => (
                <div
                  key={i}
                  style={{
                    fontFamily: "'Courier New', monospace",
                    fontSize: 20,
                    color: '#64748b',
                    textAlign: 'center',
                    flex: 1,
                    WebkitFontSmoothing: 'antialiased',
                  }}
                >
                  {q}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Feature names for the SHAP waterfall (visual only) */
const SHAP_FEATURE_NAMES = [
  'Debt to equity',
  'Profit margin',
  'Current ratio',
  'Interest coverage',
  'Retained earnings',
  'Working capital',
  'EBIT margin',
  'Sales to assets',
];

/** Per-bar max length (0–1). All different so bars don't hit the end at the same time. */
const BAR_MAX_FACTORS = [0.28, 0.95, 0.52, 0.38, 0.72, 0.45, 0.61, 0.88];

/** Per-bar side bias: +1 = mostly red (right), -1 = mostly green (left). Half each, mixed order. */
const BAR_SIDE_BIAS = [1, -1, -1, 1, -1, 1, 1, -1];

/**
 * Ever-changing SHAP waterfall scene: procedural values, clean modern card.
 * Lasts longer than other scenes; visually attractive, not accurate SHAP.
 */
const SceneShapWaterfall: React.FC<{ frame: number; fps: number }> = ({
  frame,
  fps,
}) => {
  const cardSpring = useSpring(frame, fps, 0, { damping: 20, stiffness: 100 });
  const fadeIn = interpolate(frame, [0, 12], [0, 1]);

  // Procedural values: half bars biased to red (positive), half to green (negative), mixed order
  const bars = SHAP_FEATURE_NAMES.map((name, i) => {
    const speed1 = 0.015 + (i * 0.007) % 0.03;
    const speed2 = 0.04 + (i * 0.013) % 0.05;
    const speed3 = 0.022 + (i * 0.011) % 0.04;
    const phase1 = i * 1.2 + (i % 5) * 0.8;
    const phase2 = i * 2.1 + (i % 4) * 1.5;
    const phase3 = i * 0.7 - (i % 3);
    const t = frame * speed1 + phase1;
    const u = frame * speed2 + phase2;
    const v = frame * speed3 + phase3;
    const wobble =
      0.05 * Math.sin(t) +
      0.04 * Math.sin(u * 1.3) +
      0.03 * Math.cos(v) +
      0.015 * Math.sin(t + u) +
      0.01 * Math.cos(v * 0.5 - frame * 0.01);
    const bias = (BAR_SIDE_BIAS[i] ?? 1) * 0.048;
    const value = wobble + bias;
    return { name, value };
  });

  const maxAbs = Math.max(...bars.map((b) => Math.abs(b.value)), 0.01);
  const barScale = Math.min(320 / maxAbs, 4200);

  return (
    <AbsoluteFill
      style={{
        background:
          'radial-gradient(ellipse at 50% 50%, #0a0e1c 0%, #030508 60%, #000 100%)',
        overflow: 'hidden',
        opacity: fadeIn,
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 48,
        }}
      >
        <div
          style={{
            width: '100%',
            maxWidth: 1550,
            background: 'rgba(10, 14, 28, 0.92)',
            border: '1px solid rgba(6, 182, 212, 0.25)',
            borderRadius: 20,
            padding: '52px 64px',
            boxShadow:
              '0 0 80px rgba(6, 182, 212, 0.08), 0 40px 100px rgba(0,0,0,0.5)',
            transform: `scale(${interpolate(cardSpring, [0, 1], [0.92, 1])})`,
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 36,
            }}
          >
            <div>
              <div
                style={{
                  fontFamily: "'Georgia', serif",
                  fontSize: 44,
                  color: '#06b6d4',
                  letterSpacing: 10,
                  textTransform: 'uppercase',
                  marginBottom: 8,
                  WebkitFontSmoothing: 'antialiased',
                  fontWeight: 700,
                }}
              >
                SHAP · Feature impact
              </div>
              <div
                style={{
                  fontFamily: "'Courier New', monospace",
                  fontSize: 22,
                  color: '#94a3b8',
                  letterSpacing: 4,
                  WebkitFontSmoothing: 'antialiased',
                }}
              >
                Risk drivers — explainable AI
              </div>
            </div>
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: '#22c55e',
                boxShadow: `0 0 20px rgba(34, 197, 94, ${0.4 + Math.sin(frame * 0.2) * 0.3})`,
              }}
            />
          </div>

          {/* Baseline */}
          <div
            style={{
              height: 1,
              background: 'rgba(255,255,255,0.12)',
              marginBottom: 28,
            }}
          />

          {/* Waterfall bars */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {bars.map((bar, i) => {
              const barEntrance = interpolate(
                frame,
                [4 + i * 2, 18 + i * 2],
                [0, 1]
              );
              const maxLen = 480 * (BAR_MAX_FACTORS[i] ?? 0.7);
              const width = Math.min(Math.abs(bar.value) * barScale * barEntrance, maxLen);
              const isPositive = bar.value >= 0;
              return (
                <div
                  key={bar.name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 24,
                    minHeight: 36,
                  }}
                >
                  <div
                    style={{
                      width: 220,
                      flexShrink: 0,
                      fontFamily: "'Courier New', monospace",
                      fontSize: 26,
                      color: '#cbd5e1',
                      letterSpacing: 2,
                      WebkitFontSmoothing: 'antialiased',
                    }}
                  >
                    {bar.name}
                  </div>
                  <div
                    style={{
                      flex: 1,
                      height: 28,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative',
                    }}
                  >
                    <div
                      style={{
                        position: 'absolute',
                        left: '50%',
                        top: 0,
                        bottom: 0,
                        width: 2,
                        background: 'rgba(255,255,255,0.2)',
                        marginLeft: -1,
                      }}
                    />
                    <div
                      style={{
                        position: 'absolute',
                        left: isPositive ? '50%' : undefined,
                        right: isPositive ? undefined : '50%',
                        height: 28,
                        width: Math.max(width, 4),
                        background: isPositive
                          ? 'linear-gradient(90deg, rgba(239,68,68,0.9), rgba(239,68,68,0.5))'
                          : 'linear-gradient(90deg, rgba(34,197,94,0.5), rgba(34,197,94,0.9))',
                        borderRadius: 6,
                        boxShadow: isPositive
                          ? '0 0 24px rgba(239, 68, 68, 0.4)'
                          : '0 0 20px rgba(34, 197, 94, 0.3)',
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div
            style={{
              marginTop: 32,
              fontFamily: "'Courier New', monospace",
              fontSize: 20,
              color: '#64748b',
              letterSpacing: 5,
              textTransform: 'uppercase',
              WebkitFontSmoothing: 'antialiased',
            }}
          >
            Values update in real time · SolvencyInsight
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const SceneTagline: React.FC<{ frame: number; fps: number }> = ({
  frame,
  fps,
}) => {
  const line1 = useSpring(frame, fps, 5);
  const line2 = useSpring(frame, fps, 25, { damping: 16 });
  const line3 = useSpring(frame, fps, 45);
  const fadeOut = interpolate(frame, [75, 90], [1, 0]);
  return (
    <AbsoluteFill
      style={{ background: '#000000', overflow: 'hidden', opacity: fadeOut }}
    >
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '10%',
          height: 1,
          width: `${interpolate(frame, [0, 40], [0, 80])}%`,
          background: 'linear-gradient(90deg, #3b82f6, transparent)',
          opacity: 0.4,
        }}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          paddingLeft: '10%',
        }}
      >
        <div
          style={{
            fontFamily: "'Courier New', monospace",
            fontSize: 36,
            color: '#3b82f6',
            letterSpacing: 12,
            textTransform: 'uppercase',
            marginBottom: 36,
            opacity: line1,
            transform: `translateX(${interpolate(line1, [0, 1], [-40, 0])}px)`,
            WebkitFontSmoothing: 'antialiased',
          }}
        >
          SolvencyInsight
        </div>
        <div
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 224,
            fontWeight: 900,
            color: '#ffffff',
            lineHeight: 0.95,
            letterSpacing: '-6px',
            opacity: line2,
            transform: `translateY(${interpolate(line2, [0, 1], [50, 0])}px)`,
            textShadow: '0 2px 8px rgba(0,0,0,0.4)',
            WebkitFontSmoothing: 'antialiased',
          }}
        >
          Know before
          <br />
          <span
            style={{
              WebkitTextStroke: '4px #ef4444',
              color: 'transparent',
            }}
          >
            it's too late.
          </span>
        </div>
        <div
          style={{
            fontFamily: "'Courier New', monospace",
            fontSize: 40,
            color: '#6b7280',
            letterSpacing: 6,
            marginTop: 48,
            opacity: line3,
            transform: `translateY(${interpolate(line3, [0, 1], [20, 0])}px)`,
            WebkitFontSmoothing: 'antialiased',
          }}
        >
          AI-powered insolvency prediction for modern business
        </div>
      </div>
    </AbsoluteFill>
  );
};

const SceneCTA: React.FC<{ frame: number; fps: number }> = ({ frame }) => {
  const fadeIn = interpolate(frame, [0, 20], [0, 1]);
  const pulse = Math.sin(frame * 0.15) * 0.5 + 0.5;
  return (
    <AbsoluteFill
      style={{ background: '#000000', overflow: 'hidden', opacity: fadeIn }}
    >
      <svg
        width="1920"
        height="1080"
        style={{ position: 'absolute', opacity: 0.04 }}
      >
        {GRID_LINES.map((i) => (
          <React.Fragment key={i}>
            <line
              x1={i * 240}
              y1={0}
              x2={i * 240}
              y2={1080}
              stroke="#3b82f6"
              strokeWidth={1}
            />
            <line
              x1={0}
              y1={i * 135}
              x2={1920}
              y2={i * 135}
              stroke="#3b82f6"
              strokeWidth={1}
            />
          </React.Fragment>
        ))}
      </svg>
      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: '50%',
          width: 600,
          height: 600,
          marginLeft: -300,
          marginTop: -300,
          borderRadius: '50%',
          background: `radial-gradient(circle, rgba(59,130,246,${0.06 + pulse * 0.04}) 0%, transparent 70%)`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 56,
            color: '#3b82f6',
            letterSpacing: 16,
            textTransform: 'uppercase',
            textShadow: '0 0 60px rgba(59,130,246,0.4), 0 2px 4px rgba(0,0,0,0.3)',
            WebkitFontSmoothing: 'antialiased',
            fontWeight: 700,
          }}
        >
          SolvencyInsight
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const SolvencyVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: '#000' }}>
      {frame < 100 && (
        <Sequence from={0} durationInFrames={100}>
          <SceneStorm frame={frame} fps={fps} />
        </Sequence>
      )}
      {frame >= 85 && frame < 190 && (
        <Sequence from={85} durationInFrames={105}>
          <SceneSignal frame={frame - 85} fps={fps} />
        </Sequence>
      )}
      {frame >= 175 && frame < 310 && (
        <Sequence from={175} durationInFrames={135}>
          <SceneProduct frame={frame - 175} fps={fps} />
        </Sequence>
      )}
      {frame >= 310 && frame < 410 && (
        <Sequence from={310} durationInFrames={100}>
          <SceneShapWaterfall frame={frame - 310} fps={fps} />
        </Sequence>
      )}
      {frame >= 395 && frame < 500 && (
        <Sequence from={395} durationInFrames={105}>
          <SceneTagline frame={frame - 395} fps={fps} />
        </Sequence>
      )}
      {frame >= 490 && (
        <Sequence from={490} durationInFrames={140}>
          <SceneCTA frame={frame - 490} fps={fps} />
        </Sequence>
      )}
    </AbsoluteFill>
  );
};
