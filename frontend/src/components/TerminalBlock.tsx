/**
 * Small terminal-style block for Landing: monospace lines + subtle glow.
 */
import { motion } from 'framer-motion';

const lines = [
  '> Running risk model...',
  '> Z-Score computed.',
  '> SolvencyInsight ready.',
];

export default function TerminalBlock() {
  return (
    <motion.div
      className="rounded-xl border border-slate-200/80 dark:border-white/10 bg-slate-900/90 dark:bg-dark-950/90 backdrop-blur-sm p-4 font-mono text-sm shadow-lg"
      initial={{ opacity: 0, y: 8 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4 }}
      style={{
        boxShadow: '0 0 24px rgba(6, 182, 212, 0.08), inset 0 1px 0 rgba(255,255,255,0.04)',
      }}
    >
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-700/80">
        <span className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
        <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
        <span className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
        <span className="text-slate-500 dark:text-dark-400 text-xs ml-2">terminal</span>
      </div>
      {lines.map((line, i) => (
        <div
          key={i}
          className="text-slate-300 dark:text-dark-300 tracking-tight"
          style={{ animationDelay: `${i * 0.15}s` }}
        >
          {line}
        </div>
      ))}
      <span className="inline-block w-2 h-4 ml-1 bg-primary-400 dark:bg-primary-500 animate-pulse align-middle" aria-hidden />
    </motion.div>
  );
}
