/**
 * Landing page: Remotion hero video, intro to insolvency, why SolvencyInsight, rotating parameters cube, CTA to app.
 */
import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Player, type PlayerRef } from '@remotion/player';
import {
  Shield,
  TrendingUp,
  Building2,
  ArrowLeftRight,
  Users,
  Scissors,
  FileText,
  ArrowRight,
  Upload,
  Cpu,
  Play,
} from 'lucide-react';
import { SolvencyVideo } from '../remotion';
import { RotatingCube, TerminalBlock, CountUp } from '../components';
import LandingBackground from '../components/LandingBackground';

const features = [
  { path: '/insolvency', icon: Building2, label: 'Insolvency Analysis', desc: 'Company risk & Z-Score' },
  { path: '/compare', icon: ArrowLeftRight, label: 'Compare Companies', desc: 'Side-by-side analysis' },
  { path: '/employees', icon: Users, label: 'Employee Scoring', desc: 'Retention & attrition risk' },
  { path: '/layoffs', icon: Scissors, label: 'Layoff Simulation', desc: 'Budget-driven scenarios' },
  { path: '/reports', icon: FileText, label: 'Reports', desc: 'PDF reports' },
];

/** Animated stats: count up on scroll. One real number we stand behind (12 ratios). */
const stats = [
  { to: 12, suffix: '', label: 'Financial ratios analyzed per company' },
  { to: 6, suffix: '+', label: 'Key metrics' },
  { to: 100, suffix: '%', label: 'SHAP explainability on every prediction' },
];

const howItWorksSteps = [
  { icon: Upload, title: 'Upload data', desc: 'CSV with company financials or employee data' },
  { icon: Cpu, title: 'AI analyzes', desc: 'Z-Score, ML risk model, and SHAP explanations' },
  { icon: FileText, title: 'Get actionable report', desc: 'PDF reports and recommendations' },
];

const REMOTION_FPS = 30;
const REMOTION_DURATION = 630;
const REMOTION_WIDTH = 1920;
const REMOTION_HEIGHT = 1080;

export default function Landing() {
  const [showVideoOverlay, setShowVideoOverlay] = useState(true);
  const playerRef = useRef<PlayerRef>(null);

  const handlePlayIntro = (e: React.MouseEvent) => {
    playerRef.current?.play(e as unknown as React.SyntheticEvent);
    setShowVideoOverlay(false);
  };

  const handlePauseAndShowIntro = () => {
    playerRef.current?.pause();
    setShowVideoOverlay(true);
  };

  return (
    <div className="relative overflow-hidden min-h-screen bg-[#050e1a] w-full max-w-none px-0">
      <LandingBackground />
      {/* Hero: video on top, title + CTAs below (no overlap) */}
      <section className="flex flex-col relative z-[1]">
        {/* Wrapper: padding, transparent bg */}
        <div className="bg-transparent pt-0 px-6 pb-0">
          {/* Video container: max-width, centered, rounded, border, shadow */}
          <div
            className="relative w-full bg-black flex items-center justify-center overflow-hidden mx-auto"
            style={{
              height: 'min(60vh, 100vw * 0.5625)',
              maxWidth: 800,
              borderRadius: 12,
              border: '1px solid rgba(0, 200, 212, 0.2)',
              boxShadow: '0 0 60px rgba(0, 200, 212, 0.08), 0 24px 48px rgba(0,0,0,0.5)',
            }}
          >
            <div
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full"
              style={{
                maxWidth: 'min(100vw, 100vh * 1.7778)',
                maxHeight: 'min(60vh, 100vw * 0.5625)',
              }}
            >
            <Player
              ref={playerRef}
              component={SolvencyVideo}
              inputProps={{}}
              durationInFrames={REMOTION_DURATION}
              compositionWidth={REMOTION_WIDTH}
              compositionHeight={REMOTION_HEIGHT}
              fps={REMOTION_FPS}
              style={{ width: '100%', height: '100%' }}
              loop
              autoPlay={false}
              controls
              className="remotion-player w-full h-full"
            />
            </div>

          {/* Play overlay: click to start video */}
          {showVideoOverlay && (
            <button
              type="button"
              onClick={handlePlayIntro}
              className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-3 bg-black/60 hover:bg-black/50 transition-colors cursor-pointer"
              aria-label="Play intro video"
            >
              <div className="w-20 h-20 rounded-full bg-white/90 flex items-center justify-center shadow-xl pointer-events-none">
                <Play className="w-10 h-10 text-slate-900 ml-1" fill="currentColor" />
              </div>
              <span className="text-white/90 text-sm font-medium pointer-events-none">Watch intro</span>
            </button>
          )}

          {/* When video is playing: click to pause and show Watch intro again */}
          {!showVideoOverlay && (
            <button
              type="button"
              onClick={handlePauseAndShowIntro}
              className="absolute inset-0 z-20 cursor-pointer"
              aria-label="Pause and show intro"
              title="Click to pause"
            />
          )}
          </div>
        </div>

        {/* Title + CTAs below the video */}
        <div className="flex flex-col items-center justify-center px-4 py-8 bg-slate-900/30 border-t border-slate-200 dark:border-white/10">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-slate-800 dark:text-white text-center mb-2">
            SolvencyInsight
          </h1>
          <p className="text-slate-600 dark:text-dark-300 text-base sm:text-lg text-center max-w-md mb-8">
            AI-powered insolvency prevention and risk analysis
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary-500 hover:bg-primary-400 text-white font-semibold shadow-lg transition-colors"
            >
              Open Dashboard
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/insolvency"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border-2 border-primary-500/80 text-primary-600 dark:text-primary-400 hover:bg-primary-500/10 font-semibold transition-colors"
            >
              Run analysis
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Stats strip and rest of content (solid bg so video doesn’t show through) */}
      <div className="relative z-[1] bg-slate-900/30">
      <motion.section
        className="py-8 border-b border-slate-200 dark:border-white/10 relative z-[1]"
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.4 }}
      >
        <div className="flex flex-wrap justify-center gap-8 md:gap-12">
          {stats.map((s, i) => (
            <div key={i} className="text-center">
              <div className="text-2xl md:text-3xl font-bold text-highlight-500 dark:text-highlight-400 font-mono">
                <CountUp to={s.to} suffix={s.suffix} duration={1.2} />
              </div>
              <div className="text-sm text-slate-500 dark:text-dark-400 mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
      </motion.section>

      {/* How it works */}
      <motion.section
        className="py-12 md:py-16 border-t border-slate-200 dark:border-white/10 relative z-[1]"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.5 }}
      >
        <div className="max-w-3xl mx-auto px-4">
          <p className="section-title text-center">// How it works</p>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-8 text-center">How it works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {howItWorksSteps.map((step, i) => {
              const Icon = step.icon;
              return (
                <motion.div
                  key={i}
                  className="text-center"
                  initial={{ opacity: 0, y: 12 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                >
                  <div className="w-14 h-14 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center mx-auto mb-3">
                    <Icon className="w-7 h-7 text-primary-500" />
                  </div>
                  <h3 className="font-semibold text-slate-800 dark:text-white mb-1">{step.title}</h3>
                  <p className="text-sm text-slate-500 dark:text-dark-400">{step.desc}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </motion.section>

      {/* What is insolvency */}
      <motion.section
        className="py-12 md:py-16 border-t border-slate-200 dark:border-white/10 relative z-[1]"
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
            Early detection helps management, investors, and creditors take action before it's too late.
          </p>
          <p className="text-slate-500 dark:text-dark-400 text-sm leading-relaxed">
            SolvencyInsight uses the <strong className="text-slate-700 dark:text-dark-200">Altman Z-Score</strong> and machine
            learning to predict distress risk from financial ratios—so you can spot warning signs and act in time.
          </p>
        </div>
      </motion.section>

      {/* Terminal block */}
      <motion.section
        className="py-8 border-t border-slate-200 dark:border-white/10 relative z-[1]"
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
        className="py-12 md:py-16 border-t border-slate-200 dark:border-white/10 relative z-[1]"
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
          <p className="text-center text-slate-500 dark:text-dark-400 text-sm mb-4">The metrics that power our model (each face of the cube):</p>
          <RotatingCube />
          <p className="text-center text-slate-500 dark:text-dark-500 text-xs mt-4 font-mono">
            The 6 financial signals that power our model
          </p>
        </div>
      </motion.section>

      {/* What you can do */}
      <motion.section
        className="py-12 md:py-16 border-t border-slate-200 dark:border-white/10 relative z-[1]"
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
    </div>
  );
}
