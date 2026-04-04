import { Link, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Player } from '@remotion/player';
import { Activity, Sun, Moon } from 'lucide-react';
import AnimatedBackground from './AnimatedBackground';
import CustomCursor from './CustomCursor';
import FloatingNav from './FloatingNav';
import { useTheme } from '../context/ThemeContext';
import { preloadRoute } from '../routes';
import { BackgroundVideo } from '../remotion';

interface LayoutProps {
  children: React.ReactNode;
}

const navItems = [
  { path: '/', label: 'Home' },
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/insolvency', label: 'Insolvency Analysis' },
  { path: '/compare', label: 'Compare Companies' },
  { path: '/employees', label: 'Employee Scoring' },
  { path: '/layoffs', label: 'Layoff Simulation' },
  { path: '/reports', label: 'Reports' },
];

const cinematicEase = [0.22, 1, 0.36, 1] as const;

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: cinematicEase },
  },
  exit: {
    opacity: 0,
    y: -8,
    transition: { duration: 0.15, ease: cinematicEase },
  },
};

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const isHome = location.pathname === '/';

  return (
    <div className="min-h-screen flex relative">
      <AnimatedBackground />
      {/* Non-home: ambient background video + overlay (smooth fade-in) */}
      {!isHome && (
        <>
          <motion.div
            className="fixed inset-0 z-[-1] overflow-hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, ease: [0.33, 1, 0.68, 1] }}
            aria-hidden
          >
            <Player
              component={BackgroundVideo}
              durationInFrames={900}
              fps={30}
              inputProps={{}}
              compositionWidth={1920}
              compositionHeight={1080}
              style={{ width: '100%', height: '100%' }}
              loop
              autoPlay
              controls={false}
            />
          </motion.div>
          <motion.div
            className="fixed inset-0 z-0 pointer-events-none"
            style={{ backgroundColor: 'rgba(2, 8, 24, 0.75)' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, ease: [0.33, 1, 0.68, 1] }}
            aria-hidden
          />
        </>
      )}

      {/* Home: gradient + grid */}
      {isHome && (
        <>
          <div className="fixed inset-0 z-0 bg-gradient-animated pointer-events-none transition-opacity duration-500" aria-hidden />
          <div className="fixed inset-0 z-0 bg-grid-futuristic bg-grid-glow pointer-events-none" aria-hidden />
          <div className="fixed inset-0 z-0 bg-white/40 dark:bg-dark-950/50 pointer-events-none transition-colors duration-500" aria-hidden />
        </>
      )}

      <CustomCursor />

      {/* Full-width main content (no sidebar) - above backgrounds */}
      <div className="flex-1 flex flex-col min-h-screen relative z-10 w-full">
        {/* Header - logo left, page title + actions right */}
        <header className="h-16 bg-white/80 dark:bg-dark-900/60 border-b border-slate-200/80 dark:border-white/[0.07] backdrop-blur-2xl flex items-center justify-between px-4 sm:px-6 sticky top-0 z-30 transition-colors duration-400 ease-out" style={{ boxShadow: '0 4px 30px rgba(0,0,0,0.1), inset 0 -1px 0 rgba(255,255,255,0.04)' }}>
          <Link to="/" className="flex items-center gap-3 hover:opacity-90 transition-opacity shrink-0" onMouseEnter={() => preloadRoute('/')}>
            <motion.div
              className="w-9 h-9 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/25"
              whileHover={{ scale: 1.05, rotate: 5 }}
              transition={{ type: 'tween', duration: 0.28, ease: [0.33, 1, 0.68, 1] }}
            >
              <Activity className="w-5 h-5 text-white" />
            </motion.div>
            <span className="font-semibold text-slate-800 dark:text-white hidden sm:inline">SolvencyInsight</span>
          </Link>

          <div className="flex-1 flex justify-center min-w-0">
            <h1 className="text-base sm:text-lg font-semibold text-slate-800 dark:text-white truncate">
              {navItems.find((item) => item.path === location.pathname)?.label || 'Dashboard'}
            </h1>
          </div>

          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-200/80 dark:text-dark-400 dark:hover:text-white dark:hover:bg-dark-700 transition-colors"
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <div className="flex items-center gap-2">
              <motion.div
                className="w-2 h-2 rounded-full bg-green-500"
                animate={{ opacity: [1, 0.55, 1] }}
                transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
              />
              <span className="text-sm text-slate-500 dark:text-dark-400">API Connected</span>
            </div>
          </div>
        </header>

        {/* Page content — smooth flow transition between routes */}
        <main className={`flex-1 min-h-0 pb-28 overflow-auto relative pt-2 ${isHome ? 'px-0 pb-6' : 'px-6 pb-6'}`} style={{ willChange: 'scroll-position', WebkitOverflowScrolling: 'touch' }}>
          <div className={isHome ? 'min-h-full w-full' : 'max-w-7xl mx-auto min-h-full'}>
            <AnimatePresence mode="sync" initial={false}>
              <motion.div
                key={location.pathname}
                variants={pageVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="min-h-full"
              >
                {children}
                {/* Footer at very end of page */}
                <footer className="mt-16 pt-8 border-t border-slate-200 dark:border-dark-800 text-center">
                  <div className="text-xs text-slate-500 dark:text-dark-500">
                    SolvencyInsight
                    <br />
                    v1.0.0
                  </div>
                </footer>
              </motion.div>
            </AnimatePresence>
          </div>
        </main>

        {/* Floating bottom menu — expands when opened, labels on hover */}
        <FloatingNav />
      </div>
    </div>
  );
}
