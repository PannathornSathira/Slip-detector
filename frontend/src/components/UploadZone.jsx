import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud } from 'lucide-react';

const UploadZone = ({ onUpload, isUploading, progress }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0 && !isUploading) {
      onUpload(acceptedFiles);
    }
  }, [onUpload, isUploading]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: {'image/*': []} });

  return (
    <div 
      {...getRootProps()} 
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors relative overflow-hidden
        ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white hover:bg-gray-50'}`}
    >
      <input {...getInputProps()} />
      <UploadCloud className="mx-auto h-12 w-12 text-gray-400 mb-4 relative z-10" />
      <div className="relative z-10">
        {
          isUploading ? (
            <div className="w-full max-w-xs mx-auto">
              <p className="text-gray-600 font-medium mb-2">Processing slips... {progress}%</p>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
              </div>
            </div>
          ) : isDragActive ? (
            <p className="text-blue-500 font-medium">Drop the slip images here ...</p>
          ) : (
            <p className="text-gray-600 font-medium">Drag & drop some slip images here, or click to select files</p>
          )
        }
      </div>
    </div>
  );
};

export default UploadZone;
