import React, { useMemo } from 'react';
import DashboardCharts from '../components/DashboardCharts';
import { Download, TrendingUp, PieChart as PieIcon, Activity } from 'lucide-react';

const DashboardPage = ({ data }) => {
  const exportToCSV = () => {
    if (data.length === 0) return;
    
    const headers = ['Date', 'Receiver', 'Category', 'Amount (THB)'];
    const rows = data.map(row => [
      `"${row.date || ''}"`,
      `"${row.receiver || ''}"`,
      `"${row.category || 'Uncategorized'}"`,
      row.amount || 0
    ]);
    
    const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "finance_report.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const metrics = useMemo(() => {
    let total = 0;
    const categoryTotals = {};

    data.forEach(item => {
      // Exclude credit card settlements from actual spending totals
      if (item.category !== 'Credit Card Settlement') {
        total += item.amount;
        const cat = item.category || 'Uncategorized';
        categoryTotals[cat] = (categoryTotals[cat] || 0) + item.amount;
      }
    });

    const categoryCount = Object.keys(categoryTotals).length || 1;
    const averageCategory = total / categoryCount;

    let highestCategory = 'None';
    let maxVal = 0;
    for (const [cat, val] of Object.entries(categoryTotals)) {
      if (val > maxVal) {
        maxVal = val;
        highestCategory = cat;
      }
    }

    return {
      total,
      averageCategory,
      highestCategory,
      maxVal
    };
  }, [data]);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Bar with Export */}
      <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-slate-100">
        <h2 className="text-xl font-bold text-slate-800">Financial Overview</h2>
        <button 
          onClick={exportToCSV}
          disabled={data.length === 0}
          className="flex items-center space-x-2 bg-slate-800 text-white px-4 py-2 rounded-lg hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          <span>Export CSV</span>
        </button>
      </div>

      {data.length === 0 ? (
        <div className="text-center p-12 bg-white rounded-xl border border-slate-100">
          <p className="text-slate-500 font-medium">No data available. Please upload slips first.</p>
        </div>
      ) : (
        <>
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start space-x-4">
              <div className="bg-blue-100 p-3 rounded-lg text-blue-600">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-slate-500 font-medium mb-1">Total Spending</p>
                <h3 className="text-2xl font-bold text-slate-800">{metrics.total.toLocaleString(undefined, {minimumFractionDigits: 2})} <span className="text-sm font-normal text-slate-500">THB</span></h3>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start space-x-4">
              <div className="bg-green-100 p-3 rounded-lg text-green-600">
                <PieIcon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-slate-500 font-medium mb-1">Avg per Category</p>
                <h3 className="text-2xl font-bold text-slate-800">{metrics.averageCategory.toLocaleString(undefined, {minimumFractionDigits: 2})} <span className="text-sm font-normal text-slate-500">THB</span></h3>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start space-x-4">
              <div className="bg-orange-100 p-3 rounded-lg text-orange-600">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-slate-500 font-medium mb-1">Top Category</p>
                <h3 className="text-xl font-bold text-slate-800 truncate" title={metrics.highestCategory}>{metrics.highestCategory}</h3>
                <p className="text-sm text-slate-500 mt-1">{metrics.maxVal.toLocaleString(undefined, {minimumFractionDigits: 2})} THB</p>
              </div>
            </div>
          </div>

          {/* Charts */}
          <DashboardCharts data={data} />
        </>
      )}
    </div>
  );
};

export default DashboardPage;
