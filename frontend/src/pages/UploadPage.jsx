import React, { useState } from 'react';
import axios from 'axios';
import UploadZone from '../components/UploadZone';
import DataTable from '../components/DataTable';

const UploadPage = ({ data, setData }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const handleUpload = async (files) => {
    setIsUploading(true);
    setProgress(0);
    setError(null);

    const newExtractedData = [];
    const totalFiles = files.length;
    let successCount = 0;

    for (let i = 0; i < totalFiles; i++) {
      const file = files[i];
      const formData = new FormData();
      formData.append('files', file);

      try {
        const response = await axios.post('http://localhost:8000/upload-slips/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        newExtractedData.push(...response.data.data);
        successCount++;
      } catch (err) {
        console.error("Error uploading file", file.name, err);
      }
      
      setProgress(Math.round(((i + 1) / totalFiles) * 100));
    }

    if (successCount < totalFiles) {
      setError(`Processed ${successCount} of ${totalFiles} slips successfully.`);
    }

    // Append new data to existing data
    setData(prevData => [...prevData, ...newExtractedData]);
    setIsUploading(false);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <UploadZone onUpload={handleUpload} isUploading={isUploading} progress={progress} />
        {error && <p className="text-red-500 mt-4 font-medium text-center">{error}</p>}
      </section>

      {data.length > 0 && (
        <section className="animate-fade-in">
          <div className="flex justify-between items-end mb-4 px-1">
            <h2 className="text-xl font-bold text-slate-800">Extracted Transactions</h2>
            <button 
              onClick={() => setData([])}
              className="text-sm text-red-500 hover:text-red-700 transition-colors"
            >
              Clear Data
            </button>
          </div>
          <DataTable data={data} setData={setData} />
        </section>
      )}
    </div>
  );
};

export default UploadPage;
