import React, { useState } from 'react';
import axios from 'axios';
import UploadZone from '../components/UploadZone';
import DataTable from '../components/DataTable';
import { CheckCircle2, AlertTriangle, FileText, XCircle } from 'lucide-react';
import { API_BASE_URL } from '../config';

const UploadPage = ({ data, setData }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [sessionStats, setSessionStats] = useState(null);

  const handleUpload = async (files) => {
    setIsUploading(true);
    setProgress(0);
    setError(null);
    setSessionStats(null);

    const newExtractedData = [];
    const totalFiles = files.length;
    let successCount = 0;
    const failedFiles = [];

    for (let i = 0; i < totalFiles; i++) {
      const file = files[i];
      const formData = new FormData();
      formData.append('files', file);

      try {
        const response = await axios.post(`${API_BASE_URL}/upload-slips/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        const fileResults = response.data.data;
        let fileHasError = false;
        
        for (const res of fileResults) {
          if (res.error) {
            fileHasError = true;
            failedFiles.push(`${file.name} (${res.error})`);
          } else {
            newExtractedData.push(res);
          }
        }
        
        if (!fileHasError) {
          successCount++;
        }
      } catch (err) {
        console.error("Error uploading file", file.name, err);
        failedFiles.push(`${file.name} (Connection or Server Error)`);
      }
      
      setProgress(Math.round(((i + 1) / totalFiles) * 100));
    }

    setSessionStats({
      totalFiles,
      successCount,
      failedCount: failedFiles.length,
      failedFiles
    });

    if (successCount < totalFiles) {
      setError(`Processed ${successCount} of ${totalFiles} slips successfully.`);
    }

    // Append new data to existing data
    setData(prevData => [...prevData, ...newExtractedData]);
    setIsUploading(false);
  };

  const handleUpdateCategory = async (receiver, category) => {
    try {
      await axios.post(`${API_BASE_URL}/update-category/`, { receiver, category });
      
      // Update category for all transactions with the same receiver
      setData(prevData => prevData.map(item => 
        item.receiver === receiver ? { ...item, category } : item
      ));
    } catch (err) {
      console.error("Failed to update category on backend", err);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <UploadZone onUpload={handleUpload} isUploading={isUploading} progress={progress} />
        {error && <p className="text-red-500 mt-4 font-medium text-center">{error}</p>}
      </section>

      {/* Upload Summary Cards */}
      {sessionStats && (
        <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 space-y-4 animate-fade-in">
          <h3 className="text-md font-bold text-slate-800 flex items-center space-x-2">
            <FileText className="w-5 h-5 text-slate-500" />
            <span>Upload Summary</span>
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Success Card */}
            <div className={`p-4 rounded-xl border flex items-start space-x-3 
              ${sessionStats.failedCount === 0 ? 'bg-green-50/50 border-green-100 text-green-800' : 'bg-slate-50 border-slate-100 text-slate-700'}`}>
              <CheckCircle2 className={`w-5 h-5 mt-0.5 flex-shrink-0 ${sessionStats.failedCount === 0 ? 'text-green-600' : 'text-slate-500'}`} />
              <div>
                <p className="text-sm font-semibold">Success Count</p>
                <p className="text-2xl font-bold mt-1">
                  {sessionStats.successCount} / {sessionStats.totalFiles} <span className="text-xs font-normal text-slate-500">slips parsed</span>
                </p>
              </div>
            </div>

            {/* Failed Card */}
            <div className={`p-4 rounded-xl border flex items-start space-x-3 
              ${sessionStats.failedCount > 0 ? 'bg-amber-50/50 border-amber-100 text-amber-800' : 'bg-slate-50 border-slate-100 text-slate-700'}`}>
              {sessionStats.failedCount > 0 ? (
                <AlertTriangle className="w-5 h-5 mt-0.5 text-amber-600 flex-shrink-0" />
              ) : (
                <CheckCircle2 className="w-5 h-5 mt-0.5 text-green-600 flex-shrink-0" />
              )}
              <div className="w-full">
                <p className="text-sm font-semibold">Failed Count</p>
                <p className="text-2xl font-bold mt-1">
                  {sessionStats.failedCount} <span className="text-xs font-normal text-slate-500">failed</span>
                </p>
                {sessionStats.failedFiles.length > 0 && (
                  <div className="mt-2 text-xs bg-white/70 p-2 rounded border border-amber-100/50 space-y-1">
                    <p className="font-semibold text-amber-900 mb-1">Failed Files Details:</p>
                    <ul className="list-disc list-inside text-amber-700 space-y-0.5 max-h-24 overflow-y-auto">
                      {sessionStats.failedFiles.map((fname, idx) => (
                        <li key={idx} className="truncate" title={fname}>{fname}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>
      )}

      {data.length > 0 && (
        <section className="animate-fade-in">
          <div className="flex justify-between items-end mb-4 px-1">
            <h2 className="text-xl font-bold text-slate-800">Extracted Transactions</h2>
            <button 
              onClick={() => {
                setData([]);
                setSessionStats(null);
              }}
              className="text-sm text-red-500 hover:text-red-700 transition-colors cursor-pointer font-medium"
            >
              Clear Data
            </button>
          </div>
          <DataTable data={data} setData={setData} onUpdateCategory={handleUpdateCategory} />
        </section>
      )}
    </div>
  );
};

export default UploadPage;

