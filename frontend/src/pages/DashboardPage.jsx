import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import Sidebar from '../components/layout/Sidebar';
import TopBar from '../components/layout/TopBar';
import MetricCards from '../components/metrics/MetricCards';
import PolicyChat from '../components/policy/PolicyChat';
import BorrowerTable from '../components/reminders/BorrowerTable';
import PolicyUpload from '../components/policy/PolicyUpload';
import Toast from '../components/shared/Toast';
import { fetchMetrics } from '../api/borrowers';
import { useUiStore } from '../store/uiStore';
import { TABS } from '../utils/constants';

export default function DashboardPage() {
  const activeTab = useUiStore((s) => s.activeTab);
  const setRemindersSentToday = useUiStore((s) => s.setRemindersSentToday);

  const { data: metrics, isLoading: metricsLoading, refetch } = useQuery({
    queryKey: ['metrics'],
    queryFn: fetchMetrics,
    refetchInterval: 60_000,
  });

  useEffect(() => {
    if (metrics?.reminders_sent_today != null) {
      setRemindersSentToday(metrics.reminders_sent_today);
    }
  }, [metrics, setRemindersSentToday]);

  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-[220px]">
        <TopBar activeLoans={metrics?.active_loans} />
        <main className="flex-1 p-6 overflow-auto">
          <MetricCards metrics={metrics} isLoading={metricsLoading} />
          <div className="mt-6 bg-white rounded-xl border border-gray-100 shadow-sm p-6 min-h-[500px]">
            {activeTab === TABS.POLICY && <PolicyChat />}
            {activeTab === TABS.REMINDERS && (
              <BorrowerTable onRemindersSent={() => refetch()} />
            )}
            {activeTab === TABS.UPLOAD && <PolicyUpload />}
          </div>
        </main>
      </div>
      <Toast />
    </div>
  );
}
