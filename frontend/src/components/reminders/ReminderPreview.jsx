import { X } from 'lucide-react';

export default function ReminderPreview({ message, onClose }) {
  return (
    <div className="mt-4 rounded-lg border border-line bg-surface p-4">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-sm font-medium text-ink">Message preview</h3>
        {onClose && (
          <button type="button" onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
      <p className="text-sm leading-relaxed text-gray-700 whitespace-pre-wrap">{message}</p>
    </div>
  );
}
