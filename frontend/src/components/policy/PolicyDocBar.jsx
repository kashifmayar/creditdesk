import { useRef } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { FileUp, FileText } from 'lucide-react';
import { fetchPolicyStatus, uploadPolicy } from '../../api/policy';
import { useUiStore } from '../../store/uiStore';
import LoadingSpinner from '../shared/LoadingSpinner';

export default function PolicyDocBar() {
  const inputRef = useRef(null);
  const queryClient = useQueryClient();
  const addToast = useUiStore((s) => s.addToast);

  const { data: status, isLoading } = useQuery({
    queryKey: ['policy-status'],
    queryFn: fetchPolicyStatus,
  });

  const uploadMutation = useMutation({
    mutationFn: uploadPolicy,
    onSuccess: (data) => {
      addToast(`Policy updated: ${data.filename || 'document'} (${data.chunks_ingested} sections indexed)`);
      queryClient.invalidateQueries({ queryKey: ['policy-status'] });
    },
    onError: (err) => {
      addToast(err.response?.data?.detail || 'Upload failed', 'error');
    },
  });

  const onFile = (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      addToast('Only PDF files are supported', 'error');
      return;
    }
    uploadMutation.mutate(file);
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-line bg-white px-4 py-3">
      <div className="flex items-start gap-3 min-w-0">
        <div className="mt-0.5 rounded-md bg-surface p-2 text-accent">
          <FileText className="h-4 w-4" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-medium text-ink">Policy manual</p>
          {isLoading ? (
            <p className="text-xs text-gray-500">Checking document…</p>
          ) : status?.loaded ? (
            <p className="text-xs text-gray-500 truncate">
              {status.filename}
              {status.chunks_ingested ? ` · ${status.chunks_ingested} sections` : ''}
            </p>
          ) : (
            <p className="text-xs text-amber-700">No PDF on file — upload to enable retrieval</p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => onFile(e.target.files?.[0])}
        />
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={uploadMutation.isPending}
          className="inline-flex items-center gap-2 rounded-md border border-line bg-white px-3 py-2 text-sm text-ink hover:bg-surface transition-colors disabled:opacity-60"
        >
          {uploadMutation.isPending ? <LoadingSpinner size="sm" /> : <FileUp className="h-4 w-4" />}
          Replace PDF
        </button>
      </div>
    </div>
  );
}
