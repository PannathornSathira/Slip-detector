import React, { useState } from 'react';
import { Bug, ChevronDown, ChevronUp } from 'lucide-react';

const DataTable = ({ data, setData, onUpdateCategory }) => {
  const [expandedRows, setExpandedRows] = useState({});

  const toggleRow = (index) => {
    setExpandedRows(prev => ({ ...prev, [index]: !prev[index] }));
  };

  const handleChange = (index, field, value) => {
    const newData = [...data];
    newData[index][field] = field === 'amount' ? parseFloat(value) || 0 : value;
    setData(newData);
  };

  if (data.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Receiver</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Amount (THB)</th>
            <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Debug</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, idx) => (
            <React.Fragment key={idx}>
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <input 
                    type="text" 
                    value={row.date || ''} 
                    onChange={(e) => handleChange(idx, 'date', e.target.value)}
                    className="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-1 w-full"
                  />
                </td>
                <td className="px-6 py-4">
                  <input 
                    type="text" 
                    value={row.receiver || ''} 
                    onChange={(e) => handleChange(idx, 'receiver', e.target.value)}
                    className="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-1 w-full"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <input 
                    type="text" 
                    value={row.category || ''} 
                    onChange={(e) => handleChange(idx, 'category', e.target.value)}
                    onBlur={() => onUpdateCategory && onUpdateCategory(row.receiver, row.category)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.target.blur();
                      }
                    }}
                    className="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-1 w-full"
                  />
                </td>

                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <input 
                    type="number" 
                    value={row.amount} 
                    onChange={(e) => handleChange(idx, 'amount', e.target.value)}
                    className="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-1 w-24 text-right"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <button onClick={() => toggleRow(idx)} className="text-gray-400 hover:text-blue-500 transition-colors">
                    <Bug className="w-5 h-5 inline-block" />
                    {expandedRows[idx] ? <ChevronUp className="w-4 h-4 inline-block ml-1" /> : <ChevronDown className="w-4 h-4 inline-block ml-1" />}
                  </button>
                </td>
              </tr>
              {expandedRows[idx] && row.debug_info && (
                <tr className="bg-gray-50">
                  <td colSpan="5" className="px-6 py-4 text-sm text-gray-700">
                    <div className="bg-gray-800 text-green-400 p-4 rounded-md font-mono text-xs overflow-x-auto">
                      <strong>Raw OCR Output:</strong>
                      <pre className="mt-2">{JSON.stringify(row.debug_info.raw_texts, null, 2)}</pre>
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
