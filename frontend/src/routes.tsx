/**
 * Lazy-loaded route components and preload functions.
 * Preload on nav link hover so the page is ready by the time the user clicks.
 */
import { lazy } from 'react';

// Lazy load each page so the initial bundle stays small and other pages load fast
const Landing = lazy(() => import('./pages/Landing'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const InsolvencyAnalysis = lazy(() => import('./pages/InsolvencyAnalysis'));
const EmployeeScoring = lazy(() => import('./pages/EmployeeScoring'));
const LayoffSimulation = lazy(() => import('./pages/LayoffSimulation'));
const Reports = lazy(() => import('./pages/Reports'));
const Compare = lazy(() => import('./pages/Compare'));

export const lazyPages = {
  Landing,
  Dashboard,
  InsolvencyAnalysis,
  EmployeeScoring,
  LayoffSimulation,
  Reports,
  Compare,
};

/** Preload a route chunk so navigation feels instant when the user clicks. */
export const preloadRoute = (path: string) => {
  switch (path) {
    case '/':
      return import('./pages/Landing');
    case '/dashboard':
      return import('./pages/Dashboard');
    case '/insolvency':
      return import('./pages/InsolvencyAnalysis');
    case '/employees':
      return import('./pages/EmployeeScoring');
    case '/layoffs':
      return import('./pages/LayoffSimulation');
    case '/reports':
      return import('./pages/Reports');
    case '/compare':
      return import('./pages/Compare');
    default:
      return Promise.resolve(null);
  }
};
