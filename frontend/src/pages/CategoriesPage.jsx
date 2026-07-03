import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Plus, Trash2, Edit2, Save, X, Tag, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '../config';

const CategoriesPage = () => {
  const [categories, setCategories] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [newReceiver, setNewReceiver] = useState('');
  const [newCategory, setNewCategory] = useState('');
  const [editingKey, setEditingKey] = useState(null);
  const [editingVal, setEditingVal] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/categories/`);
      setCategories(response.data);
      setError(null);
    } catch (err) {
      console.error("Error fetching categories", err);
      setError("Failed to load categories. Please make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!newReceiver.trim() || !newCategory.trim()) return;

    try {
      await axios.post(`${API_BASE_URL}/update-category/`, {
        receiver: newReceiver.trim(),
        category: newCategory.trim()
      });
      
      setCategories(prev => ({
        ...prev,
        [newReceiver.trim()]: newCategory.trim()
      }));
      setNewReceiver('');
      setNewCategory('');
    } catch (err) {
      console.error("Error adding category mapping", err);
      setError("Failed to add mapping rule.");
    }
  };

  const handleDelete = async (receiver) => {
    try {
      await axios.delete(`${API_BASE_URL}/categories/?receiver=${encodeURIComponent(receiver)}`);
      setCategories(prev => {
        const copy = { ...prev };
        delete copy[receiver];
        return copy;
      });
    } catch (err) {
      console.error("Error deleting category", err);
      setError("Failed to delete mapping rule.");
    }
  };

  const handleStartEdit = (key, val) => {
    setEditingKey(key);
    setEditingVal(val);
  };

  const handleSaveEdit = async (key) => {
    if (!editingVal.trim()) return;
    try {
      await axios.post(`${API_BASE_URL}/update-category/`, {
        receiver: key,
        category: editingVal.trim()
      });
      setCategories(prev => ({
        ...prev,
        [key]: editingVal.trim()
      }));
      setEditingKey(null);
    } catch (err) {
      console.error("Error updating category", err);
      setError("Failed to update mapping rule.");
    }
  };

  const filteredMappings = Object.entries(categories).filter(([key, val]) => 
    key.toLowerCase().includes(searchQuery.toLowerCase()) || 
    val.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page Header */}
      <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-slate-100">
        <div className="flex items-center space-x-3">
          <div className="bg-indigo-100 p-2.5 rounded-xl text-indigo-600">
            <Tag className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-800">Category Labels Manager</h2>
            <p className="text-xs text-slate-500">Configure how recognized merchants are automatically categorized</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="font-medium text-sm">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Side: Add Mapping Form */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 h-fit space-y-6">
          <h3 className="text-lg font-bold text-slate-800">Add Label Rule</h3>
          <form onSubmit={handleAdd} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Merchant / Contact Name</label>
              <input 
                type="text" 
                placeholder="e.g., KFC, แฟลช คอฟฟี่ ทีเอช" 
                value={newReceiver}
                onChange={(e) => setNewReceiver(e.target.value)}
                required
                className="w-full border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-slate-50/50"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Category Label</label>
              <input 
                type="text" 
                placeholder="e.g., Dining, Groceries" 
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                required
                className="w-full border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-slate-50/50"
              />
            </div>
            <button 
              type="submit" 
              className="w-full flex items-center justify-center space-x-2 bg-indigo-600 text-white rounded-lg p-2.5 font-medium hover:bg-indigo-700 transition-colors shadow-sm cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Add Mapping</span>
            </button>
          </form>
        </div>

        {/* Right Side: Mapping Rules List */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h3 className="text-lg font-bold text-slate-800">Mapping Rules ({filteredMappings.length})</h3>
            
            {/* Search Input */}
            <div className="relative max-w-xs w-full">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Search className="w-4 h-4" />
              </span>
              <input 
                type="text" 
                placeholder="Search merchant or category..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-1.5 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
              <p className="text-sm text-slate-500 mt-2 font-medium">Loading labeling rules...</p>
            </div>
          ) : filteredMappings.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-slate-100 rounded-xl">
              <p className="text-slate-500 font-medium">No label mappings found.</p>
            </div>
          ) : (
            <div className="overflow-x-auto border border-slate-100 rounded-xl">
              <table className="min-w-full divide-y divide-slate-100">
                <thead className="bg-slate-50/70">
                  <tr>
                    <th className="px-6 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Merchant / Contact</th>
                    <th className="px-6 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Category Label</th>
                    <th className="px-6 py-3.5 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider w-32">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-100">
                  {filteredMappings.map(([key, val]) => (
                    <tr key={key} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-slate-800">
                        {key}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {editingKey === key ? (
                          <input 
                            type="text" 
                            value={editingVal} 
                            onChange={(e) => setEditingVal(e.target.value)}
                            className="border border-indigo-200 rounded px-2 py-1 text-sm bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                          />
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100">
                            {val}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                        {editingKey === key ? (
                          <div className="flex justify-center space-x-2">
                            <button 
                              onClick={() => handleSaveEdit(key)}
                              className="text-green-600 hover:text-green-800 transition-colors p-1"
                              title="Save Changes"
                            >
                              <Save className="w-4 h-4" />
                            </button>
                            <button 
                              onClick={() => setEditingKey(null)}
                              className="text-slate-400 hover:text-slate-600 transition-colors p-1"
                              title="Cancel"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <div className="flex justify-center space-x-2">
                            <button 
                              onClick={() => handleStartEdit(key, val)}
                              className="text-slate-500 hover:text-indigo-600 transition-colors p-1"
                              title="Edit Label"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button 
                              onClick={() => handleDelete(key)}
                              className="text-slate-500 hover:text-red-600 transition-colors p-1"
                              title="Delete Label"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default CategoriesPage;
