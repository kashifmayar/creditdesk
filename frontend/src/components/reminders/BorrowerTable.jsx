import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchDueBorrowers } from '../../api/borrowers';
import { previewReminder, sendBulkReminders } from '../../api/reminders';
import BorrowerRow from './BorrowerRow';
import ReminderPreview from './ReminderPreview';
import BulkActionBar from './BulkActionBar';
import LoadingSpinner from '../shared/LoadingSpinner';
import { useUiStore } from '../../store/uiStore';
import { formatCurrency } from '../../utils/formatters';

export default function BorrowerTable({ onRemindersSent }) {
  const [selected, setSelected] = useState(new Set());
  const [preview, setPreview] = useState(null);
  const [sendProgress, setSendProgress] = useState({});
  const queryClient = useQueryClient();
  const addToast = useUiStore((s) => s.addToast);
  const incrementRemindersSent = useUiStore((s) => s.incrementRemindersSent);

  const { data: borrowers = [], isLoading, isError, error } = useQuery({
    queryKey: ['due-borrowers'],
    queryFn: fetchDueBorrowers,
    refetchInterval: 60_000,
  });

  const previewMutation = useMutation({
    mutationFn: previewReminder,
    onSuccess: (data) => setPreview(data.message),
    onError: (err) => {
      addToast(err.response?.data?.detail || 'Preview failed', 'error');
    },
  });

  const sendMutation = useMutation({
    mutationFn: async (loanIds) => {
      const progress = {};
      loanIds.forEach((id) => { progress[id] = 'queued'; });
      setSendProgress({ ...progress });

      for (const id of loanIds) {
        setSendProgress((p) => ({ ...p, [id]: 'sending' }));
        await new Promise((r) => setTimeout(r, 300));
      }

      const result = await sendBulkReminders(loanIds);

      result.results.forEach((r) => {
        setSendProgress((p) => ({ ...p, [r.loan_id]: r.status }));
      });

      return result;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['due-borrowers'] });
      queryClient.invalidateQueries({ queryKey: ['metrics'] });
      incrementRemindersSent(data.sent);
      onRemindersSent?.();
      setSelected(new Set());
      setPreview(null);
      addToast(`Sent ${data.sent} of ${data.total} reminders`);
      setTimeout(() => setSendProgress({}), 3000);
    },
    onError: (err) => {
      addToast(err.response?.data?.detail || 'Send failed', 'error');
      setSendProgress({});
    },
  });

  const toggleSelect = (id) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleAll = (checked) => {
    setSelected(checked ? new Set(borrowers.map((b) => b.loan_id)) : new Set());
  };

  const handlePreview = () => {
    const firstId = [...selected][0];
    const borrower = borrowers.find((b) => b.loan_id === firstId);
    if (borrower) {
      previewMutation.mutate({
        borrower_name: borrower.name,
        amount: formatCurrency(borrower.installment_amount),
        loan_number: borrower.loan_number,
        due_status: borrower.due_status,
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner />
        <span className="ml-2 text-sm text-gray-400">Loading borrowers…</span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-center py-12 text-red-600 text-sm">
        {error?.response?.data?.detail || 'Failed to load borrowers'}
      </div>
    );
  }

  if (borrowers.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-sm text-gray-500">No borrowers due today — check back tomorrow</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-lg font-medium text-ink mb-1">Payment Reminders</h2>
        <p className="text-sm text-gray-500">
          Select borrowers with upcoming or overdue installments and send AI-generated reminders.
        </p>
      </div>

      <div className="space-y-2 mb-4">
        {borrowers.map((b) => (
          <BorrowerRow
            key={b.loan_id}
            borrower={b}
            selected={selected.has(b.loan_id)}
            onToggle={() => toggleSelect(b.loan_id)}
            sendStatus={sendProgress[b.loan_id]}
          />
        ))}
      </div>

      <BulkActionBar
        selectedCount={selected.size}
        totalCount={borrowers.length}
        onSelectAll={toggleAll}
        onPreview={handlePreview}
        onSend={() => sendMutation.mutate([...selected])}
        isSending={sendMutation.isPending}
        isPreviewing={previewMutation.isPending}
      />

      {preview && <ReminderPreview message={preview} onClose={() => setPreview(null)} />}
    </div>
  );
}
