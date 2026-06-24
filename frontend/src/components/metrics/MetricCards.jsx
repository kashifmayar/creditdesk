import { AlertTriangle, Calendar, CheckCircle, Send } from 'lucide-react';
import LoadingSpinner from '../shared/LoadingSpinner';

const CARDS = [
  { key: 'active_loans', label: 'Active Loans', icon: CheckCircle, color: 'text-teal-600' },
  { key: 'due_today', label: 'Due Today', icon: Calendar, color: 'text-amber-600' },
  { key: 'overdue', label: 'Overdue', icon: AlertTriangle, color: 'text-red-600' },
  { key: 'reminders_sent_today', label: 'Reminders Sent Today', icon: Send, color: 'text-blue-700' },
];

export default function MetricCards({ metrics, isLoading }) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {CARDS.map(({ key, label, icon: Icon, color }) => (
        <div
          key={key}
          className="bg-white rounded-xl border border-gray-100 p-4 flex items-center gap-4 shadow-sm"
        >
          <div className={`p-2.5 rounded-lg bg-gray-50 ${color}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <p className="text-2xl font-medium text-ink">{metrics?.[key] ?? 0}</p>
            <p className="text-xs text-gray-500">{label}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
