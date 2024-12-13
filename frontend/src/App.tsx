import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import Navbar from '@/components/layout/Navbar';
import ConfigPage from '@/pages/ConfigPage';
import AnalysisPage from '@/pages/AnalysisPage';
import BacktestPage from '@/pages/BacktestPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/backtest" element={<BacktestPage />} />
            <Route path="/config" element={<ConfigPage />} />
            <Route path="/" element={<Navigate to="/analysis" replace />} />
          </Routes>
        </main>
        <Toaster />
      </div>
    </Router>
  );
}

export default App;
