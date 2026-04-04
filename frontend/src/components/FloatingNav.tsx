/**
 * Floating bottom menu: compact pill that expands when opened.
 * Icons only in bar; label appears on hover (tooltip / slide-in).
 * Enhanced glassmorphism + shared layout animation for active indicator.
 */
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion';
import { preloadRoute } from '../routes';
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

const iconVariants = {
  hidden: { scale: 0, opacity: 0 },
  visible: (i: number) => ({
    scale: 1,
    opacity: 1,
    transition: { delay: i * 0.04, type: 'spring' as const, stiffness: 400, damping: 22 },
  }),
};

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
            initial={{ opacity: 0, y: 6, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.95 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="absolute bottom-full mb-2 px-3 py-1.5 rounded-lg bg-slate-800/95 dark:bg-dark-800/95 text-white text-sm font-medium whitespace-nowrap shadow-xl border border-white/10 backdrop-blur-sm"
          >
            {navItems[hoveredIndex].label}
            <span className="absolute left-1/2 -translate-x-1/2 -bottom-1 w-2 h-2 rotate-45 bg-slate-800 dark:bg-dark-800 border-r border-b border-white/10" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating pill — expands horizontally when open */}
      <motion.div
        className="flex items-center overflow-hidden rounded-full max-w-[95vw]"
        style={{
          background: 'rgba(15, 23, 42, 0.7)',
          backdropFilter: 'blur(24px) saturate(1.5)',
          WebkitBackdropFilter: 'blur(24px) saturate(1.5)',
          border: '1px solid rgba(255,255,255,0.08)',
          boxShadow: '0 0 50px rgba(6,182,212,0.08), 0 30px 60px -15px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.06)',
        }}
        initial={false}
        animate={{
          width: expanded ? 'auto' : 56,
          minHeight: 56,
        }}
        transition={{ type: 'spring', stiffness: 260, damping: 26 }}
      >
        <LayoutGroup>
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
                      onMouseEnter={() => {
                        setHoveredIndex(index);
                        preloadRoute(item.path);
                      }}
                      onMouseLeave={() => setHoveredIndex(null)}
                      className="relative flex items-center justify-center w-10 h-10 rounded-full transition-colors duration-200"
                      title={item.label}
                      aria-label={item.label}
                    >
                      {/* Shared layout active indicator */}
                      {isActive && (
                        <motion.div
                          layoutId="nav-active-indicator"
                          className="absolute inset-0 rounded-full bg-primary-500"
                          style={{ boxShadow: '0 0 20px rgba(6,182,212,0.5)' }}
                          transition={{ type: 'spring', stiffness: 380, damping: 28 }}
                        />
                      )}
                      <motion.div
                        custom={index}
                        variants={iconVariants}
                        initial="hidden"
                        animate="visible"
                        className={`relative z-10 ${
                          isActive
                            ? 'text-white'
                            : 'text-slate-400 hover:text-white'
                        }`}
                      >
                        <Icon className="w-5 h-5 shrink-0" />
                      </motion.div>
                    </Link>
                  );
                })}
              </div>
              <button
                type="button"
                onClick={() => setExpanded(false)}
                className="flex items-center justify-center w-10 h-10 rounded-full mr-2 text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                aria-label="Close menu"
              >
                <ChevronUp className="w-5 h-5" />
              </button>
            </>
          ) : (
            <motion.button
              type="button"
              onClick={() => setExpanded(true)}
              className="flex items-center justify-center w-full h-full gap-2 rounded-full text-slate-400 hover:text-primary-400 transition-colors group"
              aria-label="Open menu"
              aria-expanded={expanded}
              /* Gentle floating when collapsed */
              animate={{ y: [0, -3, 0] }}
              transition={{ repeat: Infinity, duration: 3, ease: 'easeInOut' }}
            >
              <Menu className="w-6 h-6 text-primary-400" />
            </motion.button>
          )}
        </LayoutGroup>
      </motion.div>

      {/* Collapsed state: show current page hint */}
      {!expanded && (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          className="text-xs text-dark-400 font-mono"
        >
          {currentLabel}
        </motion.span>
      )}
    </nav>
  );
}
