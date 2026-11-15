import { useRef } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { FileUp, LogOut, MessageCircle, Send } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { fetchPolicyStatus, uploadPolicy } from '../../api/policy';
import { useAuthStore } from '../../store/authStore';
import { useUiStore } from '../../store/uiStore';
import { TABS } from '../../utils/constants';
import LoadingSpinner from '../shared/LoadingSpinner';

export default function ChatHeader() {
  const inputRef = useRef(null);
  const queryClient = useQueryClient();
  const activeTab = useUiStore((s) => s.activeTab);
  const setActiveTab = useUiStore((s) => s.setActiveTab);
  const addToast = useUiStore((s) => s.addToast);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  const { data: status } = useQuery({
    queryKey: ['policy-status'],
    queryFn: fetchPolicyStatus,
    enabled: activeTab === TABS.POLICY,
  });

  const uploadMutation = useMutation({
    mutationFn: uploadPolicy,
    onSuccess: (data) => {
      addToast(`Policy updated (${data.chunks_ingested} sections)`);
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
    <header className="sticky top-0 z-30 border-b border-white/40 bg-white/70 px-3 py-3 backdrop-blur-xl sm:px-5">
      <div className="mx-auto flex max-w-4xl items-center gap-2 sm:gap-4">
        <div className="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-300/40">
            <MessageCircle className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-ink sm:text-base">Credit Desk</p>
            {activeTab === TABS.POLICY && status?.loaded && (
              <p className="hidden truncate text-[11px] text-gray-500 sm:block">{status.filename}</p>
            )}
          </div>
        </div>

        <nav className="flex items-center rounded-full bg-surface/80 p-0.5 ring-1 ring-line/80">
          <button
            type="button"
            onClick={() => setActiveTab(TABS.POLICY)}
            className={`rounded-full px-2.5 py-1.5 text-xs font-medium transition sm:px-3.5 ${
              activeTab === TABS.POLICY
                ? 'bg-white text-indigo-700 shadow-sm'
                : 'text-gray-600 hover:text-ink'
            }`}
          >
            Chat
          </button>
          <button
            type="button"
            onClick={() => setActiveTab(TABS.REMINDERS)}
            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1.5 text-xs font-medium transition sm:px-3.5 ${
              activeTab === TABS.REMINDERS
                ? 'bg-white text-indigo-700 shadow-sm'
                : 'text-gray-600 hover:text-ink'
            }`}
          >
            <Send className="h-3 w-3 sm:hidden" />
            <span className="hidden sm:inline">Reminders</span>
            <span className="sm:hidden">Alerts</span>
          </button>
        </nav>

        {activeTab === TABS.POLICY && (
          <>
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
              title="Upload policy PDF"
              className="inline-flex shrink-0 items-center gap-1.5 rounded-xl border border-line/80 bg-white px-2.5 py-2 text-xs font-medium text-gray-700 shadow-sm transition hover:border-indigo-200 hover:text-indigo-700 disabled:opacity-60 sm:px-3"
            >
              {uploadMutation.isPending ? (
                <LoadingSpinner size="sm" />
              ) : (
                <FileUp className="h-4 w-4" />
              )}
              <span className="hidden sm:inline">PDF</span>
            </button>
          </>
        )}

        <div className="flex shrink-0 items-center gap-1">
          <span className="hidden max-w-[7rem] truncate text-xs text-gray-500 md:inline">
            {user?.full_name?.split(' ')[0]}
          </span>
          <button
            type="button"
            onClick={() => {
              logout();
              navigate('/login');
            }}
            className="rounded-xl p-2 text-gray-500 transition hover:bg-surface hover:text-ink"
            aria-label="Sign out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
