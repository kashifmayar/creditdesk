import Badge from '../shared/Badge';
import { formatCurrency, formatDate, formatPhone } from '../../utils/formatters';
import { DUE_STATUS_COLORS, DUE_STATUS_LABELS } from '../../utils/constants';

const SEND_STATUS_LABELS = {
  queued: { text: 'Queued', color: 'text-gray-400' },
  sending: { text: 'Sending…', color: 'text-amber-600' },
  sent: { text: 'Sent', color: 'text-teal-600' },
  failed: { text: 'Failed', color: 'text-red-600' },
};

export default function BorrowerRow({ borrower, selected, onToggle, sendStatus }) {
  const statusClass = DUE_STATUS_COLORS[borrower.due_status] || DUE_STATUS_COLORS.current;
  const statusLabel = DUE_STATUS_LABELS[borrower.due_status] || borrower.due_status;
  const progress = sendStatus ? SEND_STATUS_LABELS[sendStatus] : null;

  return (
    <div
      className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
        selected ? 'border-blue-700 bg-blue-50/50' : 'border-gray-100 bg-white hover:border-gray-200'
      }`}
    >
      <input
        type="checkbox"
        checked={selected}
        onChange={onToggle}
        className="w-4 h-4 rounded border-gray-300 text-blue-700 focus:ring-blue-700"
      />
      <div className="flex-1 min-w-0 grid grid-cols-1 sm:grid-cols-4 gap-2 items-center">
        <div>
          <p className="text-sm font-medium text-ink truncate">{borrower.name}</p>
          <p className="text-xs text-gray-400">{formatPhone(borrower.phone)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">{borrower.loan_number}</p>
          <p className="text-xs text-gray-400">{formatCurrency(borrower.installment_amount)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">{formatDate(borrower.next_due_date)}</p>
          {borrower.days_overdue > 0 && (
            <p className="text-xs text-red-500">{borrower.days_overdue} days overdue</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Badge className={statusClass}>{statusLabel}</Badge>
          {progress && (
            <span className={`text-xs ${progress.color}`}>{progress.text}</span>
          )}
        </div>
      </div>
    </div>
  );
}
