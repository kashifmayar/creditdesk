import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import Sidebar from '../components/layout/Sidebar';
import TopBar from '../components/layout/TopBar';
import MetricCards from '../components/metrics/MetricCards';
import PolicyChat from '../components/policy/PolicyChat';
import BorrowerTable from '../components/reminders/BorrowerTable';
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
    <div className="min-h-screen bg-surface">
      <Sidebar />
      <div className="ml-60 flex min-h-screen flex-col">
        <TopBar activeLoans={metrics?.active_loans} />
        <main className="flex-1 p-6">
          {activeTab === TABS.REMINDERS && (
            <div className="mb-5">
              <MetricCards metrics={metrics} isLoading={metricsLoading} />
            </div>
          )}
          {activeTab === TABS.POLICY && <PolicyChat />}
          {activeTab === TABS.REMINDERS && (
            <div className="rounded-xl border border-line bg-white p-6 shadow-panel">
              <BorrowerTable onRemindersSent={() => refetch()} />
            </div>
          )}
        </main>
      </div>
      <Toast />
    </div>
  );
}
