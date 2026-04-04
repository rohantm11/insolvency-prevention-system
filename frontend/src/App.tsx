import { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Layout, LoadingSpinner } from './components';
import { ToastProvider } from './context/ToastContext';
import { ThemeProvider } from './context/ThemeContext';
import { Landing } from './pages';

// Lazy-load only non-home routes so first paint is never blank
const Dashboard = lazy(() => import('./pages/Dashboard'));
const InsolvencyAnalysis = lazy(() => import('./pages/InsolvencyAnalysis'));
const EmployeeScoring = lazy(() => import('./pages/EmployeeScoring'));
const LayoffSimulation = lazy(() => import('./pages/LayoffSimulation'));
const Reports = lazy(() => import('./pages/Reports'));
const Compare = lazy(() => import('./pages/Compare'));

function PageFallback() {
  return (
    <motion.div
      className="flex items-center justify-center min-h-[70vh] w-full"
      aria-label="Loading page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3, ease: [0.33, 1, 0.68, 1] }}
    >
      <LoadingSpinner size="lg" />
    </motion.div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/dashboard" element={<Suspense fallback={<PageFallback />}><Dashboard /></Suspense>} />
              <Route path="/insolvency" element={<Suspense fallback={<PageFallback />}><InsolvencyAnalysis /></Suspense>} />
              <Route path="/employees" element={<Suspense fallback={<PageFallback />}><EmployeeScoring /></Suspense>} />
              <Route path="/layoffs" element={<Suspense fallback={<PageFallback />}><LayoffSimulation /></Suspense>} />
              <Route path="/reports" element={<Suspense fallback={<PageFallback />}><Reports /></Suspense>} />
              <Route path="/compare" element={<Suspense fallback={<PageFallback />}><Compare /></Suspense>} />
            </Routes>
          </Layout>
        </Router>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
