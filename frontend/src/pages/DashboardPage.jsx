import { useQuery } from '@tanstack/react-query';
import ChatHeader from '../components/layout/ChatHeader';
import PolicyChat from '../components/policy/PolicyChat';
import BorrowerTable from '../components/reminders/BorrowerTable';
import Toast from '../components/shared/Toast';
import { fetchMetrics } from '../api/borrowers';
import { useUiStore } from '../store/uiStore';
import { TABS } from '../utils/constants';

export default function DashboardPage() {
  const activeTab = useUiStore((s) => s.activeTab);

  const { refetch } = useQuery({
    queryKey: ['metrics'],
    queryFn: fetchMetrics,
    refetchInterval: 60_000,
  });

  return (
    <div className="chat-page-bg flex min-h-[100dvh] flex-col">
      <ChatHeader />
      <main className="flex flex-1 flex-col">
        {activeTab === TABS.POLICY && <PolicyChat />}
        {activeTab === TABS.REMINDERS && (
          <div className="mx-auto w-full max-w-5xl flex-1 px-3 py-4 sm:px-5 sm:py-6">
            <div className="rounded-2xl border border-white/60 bg-white/85 p-4 shadow-panel backdrop-blur-sm sm:p-6">
              <BorrowerTable onRemindersSent={() => refetch()} />
            </div>
          </div>
        )}
      </main>
      <Toast />
    </div>
  );
}
