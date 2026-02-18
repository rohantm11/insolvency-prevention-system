import { Link, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Activity, Sun, Moon } from 'lucide-react';
import CustomCursor from './CustomCursor';
import FloatingNav from './FloatingNav';
import { useTheme } from '../context/ThemeContext';

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

const pageVariants = {
  initial: { opacity: 1, y: 0, filter: 'blur(0px)' },
  animate: { opacity: 1, y: 0, filter: 'blur(0px)', transition: { duration: 0.2 } },
  exit: { opacity: 0, y: -6, transition: { duration: 0.15 } },
};

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen flex relative" style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #020617 0%, #0f172a 50%, #0e7490 100%)' }}>
      {/* Animated gradient background (theme-aware) */}
      <div className="fixed inset-0 bg-gradient-animated pointer-events-none transition-opacity duration-500" aria-hidden />
      {/* Grid overlay - futuristic */}
      <div className="fixed inset-0 bg-grid-futuristic bg-grid-glow pointer-events-none" aria-hidden />
      {/* Overlay for contrast */}
      <div className="fixed inset-0 bg-white/75 dark:bg-dark-950/85 pointer-events-none transition-colors duration-500" aria-hidden />

      <CustomCursor />

      {/* Full-width main content (no sidebar) */}
      <div className="flex-1 flex flex-col min-h-screen relative w-full">
        {/* Header - logo left, page title + actions right */}
        <header className="h-16 bg-white/80 dark:bg-dark-900/70 border-b border-slate-200/80 dark:border-white/10 backdrop-blur-xl flex items-center justify-between px-4 sm:px-6 sticky top-0 z-30 transition-colors duration-300">
          <Link to="/" className="flex items-center gap-3 hover:opacity-90 transition-opacity shrink-0">
            <motion.div
              className="w-9 h-9 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/25"
              whileHover={{ scale: 1.05, rotate: 5 }}
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
                animate={{ opacity: [1, 0.5, 1] }}
                transition={{ repeat: Infinity, duration: 1.5 }}
              />
              <span className="text-sm text-slate-500 dark:text-dark-400">API Connected</span>
            </div>
          </div>
        </header>

        {/* Page content with transition */}
        <main className="flex-1 p-6 pb-28 overflow-auto">
          <div className="max-w-7xl mx-auto">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                variants={pageVariants}
                initial="initial"
                animate="animate"
                exit="exit"
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
