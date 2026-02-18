import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components';
import { ToastProvider } from './context/ToastContext';
import { ThemeProvider } from './context/ThemeContext';
import {
  Landing,
  Dashboard,
  InsolvencyAnalysis,
  EmployeeScoring,
  LayoffSimulation,
  Reports,
  Compare,
} from './pages';

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/insolvency" element={<InsolvencyAnalysis />} />
            <Route path="/employees" element={<EmployeeScoring />} />
            <Route path="/layoffs" element={<LayoffSimulation />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/compare" element={<Compare />} />
          </Routes>
          </Layout>
        </Router>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
