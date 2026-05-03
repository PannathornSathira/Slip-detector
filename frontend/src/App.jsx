import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import DashboardPage from './pages/DashboardPage';
import { Wallet, UploadCloud, PieChart } from 'lucide-react';

const NavLink = ({ to, icon: Icon, children }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  return (
    <Link 
      to={to} 
      className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors font-medium ${isActive ? 'bg-blue-100 text-blue-700' : 'text-slate-600 hover:bg-slate-100'}`}
    >
      <Icon className="w-5 h-5" />
      <span>{children}</span>
    </Link>
  );
};

function AppContent() {
  const [data, setData] = useState(() => {
    const saved = localStorage.getItem('finance_data');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { return []; }
    }
    return [];
  });

  useEffect(() => {
    localStorage.setItem('finance_data', JSON.stringify(data));
  }, [data]);

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 font-sans p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header & Nav */}
        <header className="flex flex-col md:flex-row md:items-center justify-between space-y-4 md:space-y-0 bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-2 rounded-xl text-white shadow-md shadow-blue-200">
              <Wallet className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-slate-900">Finance OCR</h1>
            </div>
          </div>
          <nav className="flex space-x-2">
            <NavLink to="/" icon={UploadCloud}>Upload & Edit</NavLink>
            <NavLink to="/dashboard" icon={PieChart}>Dashboard</NavLink>
          </nav>
        </header>

        {/* Route Content */}
        <Routes>
          <Route path="/" element={<UploadPage data={data} setData={setData} />} />
          <Route path="/dashboard" element={<DashboardPage data={data} />} />
        </Routes>

      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
