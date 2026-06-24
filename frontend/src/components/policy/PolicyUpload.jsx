import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadPolicy } from '../../api/policy';
import { useUiStore } from '../../store/uiStore';
import LoadingSpinner from '../shared/LoadingSpinner';

export default function PolicyUpload() {
  const [dragOver, setDragOver] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const addToast = useUiStore((s) => s.addToast);

  const mutation = useMutation({
    mutationFn: uploadPolicy,
    onSuccess: (data) => {
      setLastResult(data);
      addToast(`Policy uploaded: ${data.chunks_ingested} chunks ingested`);
    },
    onError: (err) => {
      const detail = err.response?.data?.detail || 'Upload failed';
      addToast(detail, 'error');
      setLastResult({ status: 'error', detail });
    },
  });

  const handleFile = (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      addToast('Only PDF files are accepted', 'error');
      return;
    }
    mutation.mutate(file);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  };

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-lg font-medium text-ink mb-1">Upload Policy Document</h2>
        <p className="text-sm text-gray-500">
          Replace the credit policy manual. PDF will be chunked and embedded for RAG search.
        </p>
      </div>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
          dragOver ? 'border-blue-700 bg-blue-50' : 'border-gray-200 bg-gray-50'
        }`}
      >
        {mutation.isPending ? (
          <div className="flex flex-col items-center gap-3">
            <LoadingSpinner />
            <p className="text-sm text-gray-500">Processing PDF and generating embeddings…</p>
          </div>
        ) : (
          <>
            <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
            <p className="text-sm text-gray-600 mb-2">
              Drag and drop your policy PDF here, or
            </p>
            <label className="inline-block px-4 py-2 bg-blue-700 text-white rounded-lg text-sm font-medium hover:bg-blue-800 cursor-pointer transition-colors">
              Browse files
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(e) => handleFile(e.target.files[0])}
              />
            </label>
          </>
        )}
      </div>

      {lastResult && !mutation.isPending && (
        <div
          className={`mt-4 flex items-start gap-3 p-4 rounded-lg ${
            lastResult.status === 'error'
              ? 'bg-red-50 border border-red-100'
              : 'bg-teal-50 border border-teal-100'
          }`}
        >
          {lastResult.status === 'error' ? (
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
          ) : (
            <CheckCircle className="w-5 h-5 text-teal-600 shrink-0" />
          )}
          <div>
            <p className="text-sm font-medium text-ink">
              {lastResult.status === 'error' ? 'Upload failed' : 'Upload complete'}
            </p>
            <p className="text-sm text-gray-600 mt-0.5">
              {lastResult.detail ||
                `${lastResult.chunks_ingested} policy chunks ingested successfully.`}
            </p>
          </div>
        </div>
      )}

      <div className="mt-6 flex items-start gap-2 text-xs text-gray-400">
        <FileText className="w-4 h-4 shrink-0 mt-0.5" />
        <p>Admin only. Existing policy chunks will be replaced on upload.</p>
      </div>
    </div>
  );
}
