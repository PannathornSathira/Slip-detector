import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#ffc658'];

const DashboardCharts = ({ data }) => {
  // Process data for charts
  const { pieData, barData } = useMemo(() => {
    const categories = {};
    const daily = {};

    data.forEach(item => {
      // Aggregate for Pie Chart (exclude Credit Card Settlement)
      if (item.category !== 'Credit Card Settlement') {
        const cat = item.category || 'Uncategorized';
        categories[cat] = (categories[cat] || 0) + item.amount;
      }

      // Aggregate for Bar Chart
      const dateKey = item.date || 'Unknown';
      daily[dateKey] = (daily[dateKey] || 0) + item.amount;
    });

    const pData = Object.keys(categories).map(key => ({ name: key, value: categories[key] }));
    const bData = Object.keys(daily).map(key => ({ date: key, amount: daily[key] }));

    // Sort bar data by date simple string sort for now
    bData.sort((a, b) => a.date.localeCompare(b.date));

    return { pieData: pData, barData: bData };
  }, [data]);

  if (data.length === 0) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
      {/* Category Pie Chart */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Spending by Category</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <RechartsTooltip formatter={(value) => `${value.toFixed(2)} THB`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Daily Bar Chart */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Daily Spending</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
              <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} />
              <YAxis axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} />
              <RechartsTooltip 
                cursor={{fill: '#F3F4F6'}}
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                formatter={(value) => [`${value.toFixed(2)} THB`, 'Amount']}
              />
              <Bar dataKey="amount" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default DashboardCharts;
