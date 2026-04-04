/**
 * Looping ambient background: dark financial trading aesthetic with neon chart lines,
 * candlesticks, grid floor, and floating labels. Seamless 30s loop (900 frames @ 30fps).
 */
import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';

const W = 1920;
const H = 1080;

const cycle = (frame: number, period: number, offset = 0) =>
  Math.sin((2 * Math.PI * frame) / period + offset);

export const BackgroundVideo: React.FC = () => {
  const frame = useCurrentFrame();

  const bgStyle: React.CSSProperties = { background: '#020818' };
  const radialStyle: React.CSSProperties = {
    position: 'absolute',
    inset: 0,
    background: 'radial-gradient(circle at 50% 50%, rgba(6,182,212,0.06) 0%, transparent 55%, transparent 100%)',
    pointerEvents: 'none',
  };

  const vanishingX = W / 2;
  const vanishingY = H;
  const floorLineCount = 18;
  const floorLines = Array.from({ length: floorLineCount }, (_, i) => {
    const t = (i + 1) / (floorLineCount + 1);
    const topY = 320 + (1 - t) * 380;
    const leftX = vanishingX - (vanishingX * (1 - t));
    const rightX = vanishingX + (vanishingX * (1 - t));
    return { leftX, rightX, topY };
  });

  const amp1 = 80;
  const amp2 = 70;
  const amp2Var = 25;
  const y1 = H * 0.32 + amp1 * cycle(frame, 450, 0);
  const y2 = H * 0.52 + (amp2 + amp2Var * cycle(frame, 900, 1)) * cycle(frame, 300, 0.5);

  const linePath = (getY: (x: number) => number) => {
    let d = '';
    for (let i = 0; i <= 80; i++) {
      const x = (i / 80) * W;
      const y = getY(x);
      if (i === 0) d += `M ${x} ${y}`;
      else d += ` L ${x} ${y}`;
    }
    return d;
  };
  const line1Y = (x: number) => y1 + 30 * Math.sin((2 * Math.PI * frame) / 450 + (2 * Math.PI * x) / W);
  const line2Y = (x: number) => y2 + 25 * Math.sin((2 * Math.PI * frame) / 300 + (2 * Math.PI * x) / (W * 0.8));

  const horizonY = 520;
  const reflectedPath = (getY: (x: number) => number) => {
    let d = '';
    for (let i = 0; i <= 60; i++) {
      const x = (i / 60) * W;
      const yOrig = getY(x);
      const yReflect = Math.min(H - 2, Math.max(horizonY + 2, horizonY + (horizonY - yOrig) * 0.55));
      if (d === '') d += `M ${x} ${yReflect}`;
      else d += ` L ${x} ${yReflect}`;
    }
    return d;
  };

  const candlesticks = [
    { x: 180, wickH: 140, bodyH: 50, bodyY: 380, green: true },
    { x: 320, wickH: 100, bodyH: 45, bodyY: 420, green: false },
    { x: 480, wickH: 180, bodyH: 55, bodyY: 340, green: true },
    { x: 620, wickH: 80, bodyH: 40, bodyY: 450, green: false },
    { x: 780, wickH: 160, bodyH: 52, bodyY: 360, green: true },
    { x: 920, wickH: 120, bodyH: 48, bodyY: 400, green: false },
    { x: 1080, wickH: 90, bodyH: 42, bodyY: 435, green: true },
    { x: 1240, wickH: 150, bodyH: 50, bodyY: 370, green: false },
    { x: 1420, wickH: 110, bodyH: 46, bodyY: 410, green: true },
    { x: 1620, wickH: 130, bodyH: 44, bodyY: 395, green: false },
  ];

  const neonBars = [
    { x: 200, h: 420 }, { x: 420, h: 380 }, { x: 640, h: 460 },
    { x: 860, h: 340 }, { x: 1080, h: 400 }, { x: 1300, h: 360 },
  ];

  const labels = [
    { x: 220, y: 280, value: '2,765.31', up: true },
    { x: 580, y: 250, value: '3,010.93', up: false },
    { x: 980, y: 260, value: '4,096.56', up: true },
    { x: 1320, y: 270, value: '4,333.55', up: false },
  ];

  const gridSpacing = 120;

  return (
    <AbsoluteFill style={bgStyle}>
      <div style={radialStyle} />

      <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
        {floorLines.map(({ leftX, rightX, topY }, i) => {
          const opacity = 0.2 + (1 - (topY - 320) / 400) * 0.35;
          return (
            <React.Fragment key={i}>
              <line x1={vanishingX} y1={vanishingY} x2={leftX} y2={topY} stroke="#06b6d4" strokeWidth={1.5} opacity={opacity} />
              <line x1={vanishingX} y1={vanishingY} x2={rightX} y2={topY} stroke="#06b6d4" strokeWidth={1.5} opacity={opacity} />
            </React.Fragment>
          );
        })}
      </svg>

      <svg width={W} height={H} style={{ position: 'absolute', inset: 0, opacity: 0.12 }}>
        {neonBars.map(({ x, h }, i) => (
          <rect key={i} x={x} y={H - h} width={80} height={h} fill="none" stroke="#06b6d4" strokeWidth={2} />
        ))}
      </svg>

      <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
        <defs>
          <filter id="candleGlowGreen" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feFlood floodColor="#22c55e" floodOpacity="0.6" result="color" />
            <feComposite in="color" in2="blur" operator="in" result="glow" />
            <feMerge><feMergeNode in="glow" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
          <filter id="candleGlowRed" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feFlood floodColor="#ef4444" floodOpacity="0.6" result="color" />
            <feComposite in="color" in2="blur" operator="in" result="glow" />
            <feMerge><feMergeNode in="glow" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>
        {candlesticks.map((c, i) => {
          const opacity = 0.75 + 0.2 * cycle(frame, 90, i);
          const fill = c.green ? '#22c55e' : '#ef4444';
          const filter = c.green ? 'url(#candleGlowGreen)' : 'url(#candleGlowRed)';
          return (
            <g key={i} opacity={Math.max(0.6, Math.min(1, opacity))} filter={filter}>
              <line x1={c.x} y1={c.bodyY + c.bodyH} x2={c.x} y2={c.bodyY + c.bodyH + c.wickH} stroke={fill} strokeWidth={2} />
              <rect x={c.x - 14} y={c.bodyY} width={28} height={c.bodyH} fill={fill} stroke={fill} strokeWidth={1} opacity={0.95} />
            </g>
          );
        })}
      </svg>

      <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
        <defs><clipPath id="floorClip"><rect x={0} y={horizonY} width={W} height={H - horizonY} /></clipPath></defs>
        <g clipPath="url(#floorClip)" opacity={0.2}>
          <path d={reflectedPath(line1Y)} fill="none" stroke="#22c55e" strokeWidth={3} />
          <path d={reflectedPath(line2Y)} fill="none" stroke="#ef4444" strokeWidth={3} />
        </g>
      </svg>

      <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
        <defs>
          <filter id="glowGreen" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="10" result="blur" />
            <feFlood floodColor="#22c55e" floodOpacity="0.85" result="color" />
            <feComposite in="color" in2="blur" operator="in" result="glow" />
            <feMerge><feMergeNode in="glow" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
          <filter id="glowRed" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="10" result="blur" />
            <feFlood floodColor="#ef4444" floodOpacity="0.85" result="color" />
            <feComposite in="color" in2="blur" operator="in" result="glow" />
            <feMerge><feMergeNode in="glow" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>
        <path d={linePath(line1Y)} fill="none" stroke="#22c55e" strokeWidth={3} filter="url(#glowGreen)" />
        <path d={linePath(line2Y)} fill="none" stroke="#ef4444" strokeWidth={3} filter="url(#glowRed)" />
      </svg>

      {labels.map((lb, i) => {
        const dy = 8 * cycle(frame, 900, i * 2);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: lb.x,
              top: lb.y + dy,
              fontFamily: "'Courier New', monospace",
              fontSize: 13,
              color: 'rgba(255,255,255,0.5)',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <span style={{ color: lb.up ? '#22c55e' : '#ef4444', fontSize: 10 }}>{lb.up ? '▲' : '▼'}</span>
            <span>{lb.value}</span>
          </div>
        );
      })}

      <svg width={W} height={H} style={{ position: 'absolute', inset: 0, opacity: 0.05, pointerEvents: 'none' }}>
        {Array.from({ length: Math.ceil(W / gridSpacing) + 1 }, (_, i) => (
          <line key={`v${i}`} x1={i * gridSpacing} y1={0} x2={i * gridSpacing} y2={H} stroke="#06b6d4" strokeWidth={1} />
        ))}
        {Array.from({ length: Math.ceil(H / gridSpacing) + 1 }, (_, i) => (
          <line key={`h${i}`} x1={0} y1={i * gridSpacing} x2={W} y2={i * gridSpacing} stroke="#06b6d4" strokeWidth={1} />
        ))}
      </svg>
    </AbsoluteFill>
  );
};
