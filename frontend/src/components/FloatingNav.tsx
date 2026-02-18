/**
 * Floating bottom menu: compact pill that expands when opened.
 * Icons only in bar; label appears on hover (tooltip / slide-in).
 * Futuristic glass + glow styling.
 */
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Home,
  LayoutDashboard,
  Building2,
  Users,
  Scissors,
  FileText,
  ArrowLeftRight,
  ChevronUp,
  Menu,
} from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

const navItems = [
  { path: '/', icon: Home, label: 'Home' },
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/insolvency', icon: Building2, label: 'Insolvency Analysis' },
  { path: '/compare', icon: ArrowLeftRight, label: 'Compare Companies' },
  { path: '/employees', icon: Users, label: 'Employee Scoring' },
  { path: '/layoffs', icon: Scissors, label: 'Layoff Simulation' },
  { path: '/reports', icon: FileText, label: 'Reports' },
];

export default function FloatingNav() {
  const location = useLocation();
  const [expanded, setExpanded] = useState(false);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const navRef = useRef<HTMLElement>(null);

  // Close when clicking outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (navRef.current && !navRef.current.contains(e.target as Node)) {
        setExpanded(false);
      }
    }
    if (expanded) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [expanded]);

  const currentLabel = navItems.find((item) => item.path === location.pathname)?.label ?? 'Menu';

  return (
    <nav
      ref={navRef}
      className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex flex-col items-center gap-2"
      aria-label="Main navigation"
    >
      {/* Label on hover — above the bar when expanded */}
      <AnimatePresence>
        {expanded && hoveredIndex !== null && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.2 }}
            className="absolute bottom-full mb-2 px-3 py-1.5 rounded-lg bg-slate-800/95 dark:bg-dark-800/95 text-white text-sm font-medium whitespace-nowrap shadow-xl border border-white/10 backdrop-blur-sm"
          >
            {navItems[hoveredIndex].label}
            <span className="absolute left-1/2 -translate-x-1/2 -bottom-1 w-2 h-2 rotate-45 bg-slate-800 dark:bg-dark-800 border-r border-b border-white/10" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating pill — expands horizontally when open */}
      <motion.div
        className="flex items-center overflow-hidden rounded-full bg-white/90 dark:bg-dark-900/90 border border-slate-200/80 dark:border-white/10 shadow-2xl backdrop-blur-xl max-w-[95vw]"
        style={{
          boxShadow: '0 0 40px rgba(6, 182, 212, 0.12), 0 25px 50px -12px rgba(0, 0, 0, 0.15)',
        }}
        initial={false}
        animate={{
          width: expanded ? 'auto' : 56,
          minHeight: 56,
        }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        {expanded ? (
          <>
            <div className="flex items-center gap-1 py-2 pl-3 pr-2 overflow-x-auto scrollbar-thin">
              {navItems.map((item, index) => {
                const isActive = location.pathname === item.path;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setExpanded(false)}
                    onMouseEnter={() => setHoveredIndex(index)}
                    onMouseLeave={() => setHoveredIndex(null)}
                    className={`relative flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200 ${
                      isActive
                        ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                        : 'text-slate-500 hover:text-slate-800 hover:bg-slate-200/80 dark:text-dark-300 dark:hover:text-white dark:hover:bg-white/10'
                    }`}
                    title={item.label}
                    aria-label={item.label}
                  >
                    <Icon className="w-5 h-5 shrink-0" />
                  </Link>
                );
              })}
            </div>
            <button
              type="button"
              onClick={() => setExpanded(false)}
              className="flex items-center justify-center w-10 h-10 rounded-full mr-2 text-slate-500 hover:bg-slate-200/80 hover:text-slate-800 dark:hover:bg-white/10 dark:hover:text-white transition-colors"
              aria-label="Close menu"
            >
              <ChevronUp className="w-5 h-5" />
            </button>
          </>
        ) : (
          <button
            type="button"
            onClick={() => setExpanded(true)}
            className="flex items-center justify-center w-full h-full gap-2 rounded-full text-slate-600 dark:text-dark-300 hover:text-primary-500 dark:hover:text-primary-400 transition-colors group"
            aria-label="Open menu"
            aria-expanded={expanded}
          >
            <Menu className="w-6 h-6 text-primary-500 dark:text-primary-400" />
          </button>
        )}
      </motion.div>

      {/* Collapsed state: show current page hint */}
      {!expanded && (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xs text-slate-500 dark:text-dark-400 font-mono"
        >
          {currentLabel}
        </motion.span>
      )}
    </nav>
  );
}
