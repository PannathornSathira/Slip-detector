import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import DashboardPage from './pages/DashboardPage';
import CategoriesPage from './pages/CategoriesPage';
import { Wallet, UploadCloud, PieChart, Tag, Settings, X } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from './config';

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

  const [settings, setSettings] = useState({ processing_mode: 'lite', llm_provider: 'local' });
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/settings/`).then(res => setSettings(res.data)).catch(console.error);
  }, []);

  const saveSettings = async () => {
    try {
      await axios.post(`${API_BASE_URL}/settings/`, settings);
      setShowSettings(false);
    } catch (e) {
      console.error(e);
    }
  };

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
          <nav className="flex items-center space-x-2">
            <NavLink to="/" icon={UploadCloud}>Upload & Edit</NavLink>
            <NavLink to="/dashboard" icon={PieChart}>Dashboard</NavLink>
            <NavLink to="/categories" icon={Tag}>Manage Labels</NavLink>
            <button onClick={() => setShowSettings(true)} className="p-2 text-slate-500 hover:bg-slate-100 rounded-lg ml-2 transition-colors">
              <Settings className="w-5 h-5" />
            </button>
          </nav>
        </header>

        {/* Route Content */}
        <Routes>
          <Route path="/" element={<UploadPage data={data} setData={setData} />} />
          <Route path="/dashboard" element={<DashboardPage data={data} />} />
          <Route path="/categories" element={<CategoriesPage />} />
        </Routes>

        {/* Settings Modal */}
        {showSettings && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-2xl w-full max-w-md shadow-lg space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-slate-800">Application Settings</h2>
                <button onClick={() => setShowSettings(false)} className="text-slate-500 hover:text-slate-800"><X className="w-5 h-5"/></button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">OCR Processing Mode</label>
                  <select 
                    value={settings.processing_mode}
                    onChange={(e) => setSettings({...settings, processing_mode: e.target.value})}
                    className="w-full border border-slate-300 rounded-lg p-2 bg-white"
                  >
                    <option value="lite">Lite (EasyOCR + Rules)</option>
                    <option value="local">Powerful Local (Typhoon OCR via Ollama)</option>
                  </select>
                  <p className="text-xs text-slate-500 mt-1">Local mode requires Ollama and scb10x/typhoon-ocr-3b.</p>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Categorization LLM</label>
                  <select 
                    value={settings.llm_provider}
                    onChange={(e) => setSettings({...settings, llm_provider: e.target.value})}
                    className="w-full border border-slate-300 rounded-lg p-2 bg-white"
                  >
                    <option value="">Rules Only (No LLM)</option>
                    <option value="local">Local (Typhoon2 via Ollama)</option>
                    <option value="gemini">Google Gemini</option>
                    <option value="openai">OpenAI</option>
                  </select>
                </div>
              </div>
              
              <div className="flex justify-end pt-2">
                <button onClick={saveSettings} className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        )}

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
