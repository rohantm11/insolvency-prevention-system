/**
 * Landing page: intro to insolvency, why SolvencyInsight, rotating parameters cube, CTA to app.
 */
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Activity,
  Shield,
  TrendingUp,
  Building2,
  ArrowLeftRight,
  Users,
  Scissors,
  FileText,
  ArrowRight,
} from 'lucide-react';
import { RotatingCube, TerminalBlock } from '../components';

const features = [
  { path: '/insolvency', icon: Building2, label: 'Insolvency Analysis', desc: 'Company risk & Z-Score' },
  { path: '/compare', icon: ArrowLeftRight, label: 'Compare Companies', desc: 'Side-by-side analysis' },
  { path: '/employees', icon: Users, label: 'Employee Scoring', desc: 'Retention & attrition risk' },
  { path: '/layoffs', icon: Scissors, label: 'Layoff Simulation', desc: 'Budget-driven scenarios' },
  { path: '/reports', icon: FileText, label: 'Reports', desc: 'PDF reports' },
];

const stats = [
  { value: 'Z-Score', label: 'Risk model' },
  { value: '6+', label: 'Key metrics' },
  { value: 'Reports', label: 'PDF export' },
];

export default function Landing() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <motion.section
        className="relative py-16 md:py-24 text-center"
        initial={{ opacity: 1, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex justify-center mb-4">
          <motion.div
            className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-primary-glow"
            initial={{ scale: 1, opacity: 1 }}
            animate={{ scale: 1, opacity: 1 }}
          >
            <Activity className="w-8 h-8 text-white" />
          </motion.div>
        </div>
        <h1 className="text-4xl md:text-6xl font-bold text-slate-800 dark:text-white mb-4 font-heading">
          <span className="text-slate-800 dark:text-white">SolvencyInsight — </span>
          <span className="text-highlight-500">Prevent</span>
          <span className="text-slate-800 dark:text-white"> before it’s too late</span>
        </h1>
        <p className="text-lg text-slate-600 dark:text-dark-300 max-w-2xl mx-auto mb-6">
          AI-powered insolvency prevention and risk analysis. Detect early warning signs and protect your business.
        </p>
        <motion.div className="flex flex-wrap justify-center gap-4" initial={{ opacity: 1 }} animate={{ opacity: 1 }}>
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-highlight-500 hover:bg-highlight-400 text-white font-semibold shadow-highlight-glow transition-colors"
          >
            Open Dashboard
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/insolvency"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border-2 border-primary-500 text-primary-600 dark:text-primary-400 hover:bg-primary-500/10 font-semibold transition-colors"
          >
            Run analysis
            <ArrowRight className="w-5 h-5" />
          </Link>
        </motion.div>
        <motion.div className="flex flex-wrap justify-center gap-8 md:gap-12 mt-12" initial={{ opacity: 1 }} animate={{ opacity: 1 }}>
          {stats.map((s, i) => (
            <div key={i} className="text-center">
              <div className="text-2xl md:text-3xl font-bold text-highlight-500 dark:text-highlight-400 font-mono">{s.value}</div>
              <div className="text-sm text-slate-500 dark:text-dark-400 mt-0.5">{s.label}</div>
            </div>
          ))}
        </motion.div>
      </motion.section>

      {/* What is insolvency */}
      <motion.section
        className="py-12 md:py-16 border-t border-slate-200 dark:border-white/10"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.5 }}
      >
        <div className="max-w-3xl mx-auto px-4">
          <p className="section-title">// What is insolvency</p>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
            <Shield className="w-6 h-6 text-primary-500" />
            What is insolvency?
          </h2>
          <p className="text-slate-600 dark:text-dark-300 leading-relaxed mb-4">
            Insolvency means a company cannot pay its debts when they fall due. It often leads to bankruptcy or restructuring.
            Early detection helps management, investors, and creditors take action before it’s too late.
          </p>
          <p className="text-slate-500 dark:text-dark-400 text-sm leading-relaxed">
            SolvencyInsight uses the <strong className="text-slate-700 dark:text-dark-200">Altman Z-Score</strong> and machine
            learning to predict distress risk from financial ratios—so you can spot warning signs and act in time.
          </p>
        </div>
      </motion.section>

      {/* Terminal block */}
      <motion.section
        className="py-8 border-t border-slate-200 dark:border-white/10"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.4 }}
      >
        <div className="max-w-md mx-auto px-4">
          <TerminalBlock />
        </div>
      </motion.section>

      {/* Why SolvencyInsight + cube */}
      <motion.section
        className="py-12 md:py-16 border-t border-slate-200 dark:border-white/10"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.5 }}
      >
        <div className="max-w-4xl mx-auto px-4">
          <p className="section-title text-center">// Why SolvencyInsight</p>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-2 text-center">Why SolvencyInsight?</h2>
          <ul className="flex flex-wrap justify-center gap-4 mb-10 text-slate-600 dark:text-dark-300 text-sm">
            <li className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-primary-500" /> Early warning of distress risk</li>
            <li className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-primary-500" /> Altman Z-Score + ML models</li>
            <li className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-primary-500" /> Employee & layoff impact</li>
            <li className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-primary-500" /> Actionable PDF reports</li>
          </ul>
          <p className="text-center text-slate-500 dark:text-dark-400 text-sm mb-6">The metrics that power our model (each face of the cube):</p>
          <RotatingCube />
        </div>
      </motion.section>

      {/* What you can do */}
      <motion.section
        className="py-12 md:py-16 border-t border-slate-200 dark:border-white/10"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.5 }}
      >
        <div className="max-w-4xl mx-auto px-4">
          <p className="section-title text-center">// What you can do</p>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-6 text-center flex items-center justify-center gap-2">
            <TrendingUp className="w-6 h-6 text-primary-500" />
            What you can do
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map((f, i) => {
              const Icon = f.icon;
              return (
                <motion.div key={f.path} initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.06 }}>
                  <div className="card flex flex-col gap-2 hover:border-primary-500/40 transition-colors">
                    <Icon className="w-6 h-6 text-primary-500" />
                    <span className="font-semibold text-slate-800 dark:text-white">{f.label}</span>
                    <span className="text-sm text-slate-500 dark:text-dark-400 flex-1">{f.desc}</span>
                    <Link to={f.path} className="card-action highlight mt-1">
                      Open tool
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                </motion.div>
              );
            })}
          </div>
          <div className="text-center mt-8">
            <Link to="/dashboard" className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 font-medium">
              Open full dashboard
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </motion.section>
    </div>
  );
}
