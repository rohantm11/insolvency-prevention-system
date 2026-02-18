/**
 * 3D rotating cube showing insolvency / Altman Z-Score parameters on each face.
 * Pure CSS 3D + Framer Motion, no Three.js.
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const CUBE_FACES = [
  { title: 'Working Capital', sub: '/ Total Assets', desc: 'Liquidity vs assets' },
  { title: 'Retained Earnings', sub: '/ Total Assets', desc: 'Accumulated profit' },
  { title: 'EBIT', sub: '/ Total Assets', desc: 'Operating profitability' },
  { title: 'Market Value Equity', sub: '/ Total Liabilities', desc: 'Market vs debt' },
  { title: 'Sales', sub: '/ Total Assets', desc: 'Asset turnover' },
  { title: 'Z-Score & Ratios', sub: 'Current, Quick, D/E, ROA, ROE', desc: 'Key risk metrics' },
];

const FACE_SIZE = 140;

export default function RotatingCube() {
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    const m = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReduceMotion(m.matches);
    const fn = () => setReduceMotion(m.matches);
    m.addEventListener('change', fn);
    return () => m.removeEventListener('change', fn);
  }, []);

  return (
    <div
      className="flex justify-center items-center py-8"
      style={{ perspective: '900px', perspectiveOrigin: '50% 50%' }}
    >
      <motion.div
        className="relative"
        style={{
          width: FACE_SIZE,
          height: FACE_SIZE,
          transformStyle: 'preserve-3d',
        }}
        animate={
          reduceMotion
            ? {}
            : {
                rotateY: [0, 360],
                transition: { duration: 20, repeat: Infinity, ease: 'linear' },
              }
        }
      >
        {CUBE_FACES.map((face, i) => {
          const rotations = [
            { rotateY: 0, rotateX: 0, translateZ: FACE_SIZE / 2 },
            { rotateY: 180, rotateX: 0, translateZ: FACE_SIZE / 2 },
            { rotateY: 90, rotateX: 0, translateZ: FACE_SIZE / 2 },
            { rotateY: -90, rotateX: 0, translateZ: FACE_SIZE / 2 },
            { rotateY: 0, rotateX: 90, translateZ: FACE_SIZE / 2 },
            { rotateY: 0, rotateX: -90, translateZ: FACE_SIZE / 2 },
          ];
          const r = rotations[i];
          return (
            <div
              key={i}
              className="absolute flex flex-col items-center justify-center rounded-xl border border-slate-300/80 dark:border-white/20 bg-white/95 dark:bg-dark-800/90 backdrop-blur-sm p-3 shadow-xl"
              style={{
                width: FACE_SIZE,
                height: FACE_SIZE,
                left: 0,
                top: 0,
                transform: `rotateY(${r.rotateY}deg) rotateX(${r.rotateX}deg) translateZ(${r.translateZ}px)`,
                backfaceVisibility: 'hidden',
              }}
            >
              <p className="text-xs font-semibold text-primary-600 dark:text-primary-300 text-center leading-tight">
                {face.title}
              </p>
              <p className="text-[10px] text-slate-500 dark:text-dark-400 text-center mt-0.5">{face.sub}</p>
              <p className="text-[10px] text-slate-400 dark:text-dark-500 mt-1 hidden sm:block">{face.desc}</p>
            </div>
          );
        })}
      </motion.div>
    </div>
  );
}
