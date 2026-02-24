import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import SignalAnalysis from './pages/SignalAnalysis';
import VehicleDetection from './pages/VehicleDetection';
import AiPerformance from './pages/AiPerformance';
import Simulation from './pages/Simulation';
import LiveDashboard from './pages/LiveDashboard';
import Comparison from './pages/Comparison';

export default function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/live" element={<LiveDashboard />} />
            <Route path="/simulation" element={<Simulation />} />
            <Route path="/signals" element={<SignalAnalysis />} />
            <Route path="/detection" element={<VehicleDetection />} />
            <Route path="/ai" element={<AiPerformance />} />
            <Route path="/comparison" element={<Comparison />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
