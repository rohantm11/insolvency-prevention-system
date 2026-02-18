import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
  accept?: Record<string, string[]>;
  disabled?: boolean;
}

export default function FileUpload({
  onFileSelect,
  selectedFile,
  onClear,
  accept = { 'text/csv': ['.csv'] },
  disabled = false,
}: FileUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxFiles: 1,
    disabled,
  });

  if (selectedFile) {
    return (
      <div className="flex items-center gap-3 p-4 bg-dark-800 border border-green-500/30 rounded-lg transition-colors duration-200">
        <div className="w-10 h-10 bg-primary-600/20 rounded-lg flex items-center justify-center">
          <File className="w-5 h-5 text-primary-400" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white truncate">{selectedFile.name}</p>
          <p className="text-xs text-dark-400">
            {(selectedFile.size / 1024).toFixed(1)} KB
          </p>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onClear();
          }}
          className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
          disabled={disabled}
        >
          <X className="w-4 h-4 text-dark-400" />
        </button>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
        ${isDragActive
          ? 'border-primary-500 bg-primary-500/15'
          : 'border-dark-600 hover:border-primary-500 hover:bg-dark-800/50'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input {...getInputProps()} />
      <div className="w-16 h-16 bg-primary-500/20 rounded-full mx-auto mb-4 flex items-center justify-center">
        <Upload className="w-8 h-8 text-primary-400" />
      </div>
      {isDragActive ? (
        <p className="text-primary-400 font-medium text-lg">Drop the file here...</p>
      ) : (
        <>
          <div className="inline-flex items-center px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg font-medium mb-3 transition-colors">
            <Upload className="w-4 h-4 mr-2" />
            Click to Select CSV File
          </div>
          <p className="text-dark-300 font-medium mb-1">
            or drag & drop your file here
          </p>
          <p className="text-dark-500 text-sm">Only CSV files are accepted</p>
        </>
      )}
    </div>
  );
}
