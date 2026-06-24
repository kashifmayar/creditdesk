import { X } from 'lucide-react';
import Badge from '../shared/Badge';

export default function ReminderPreview({ message, onClose }) {
  return (
    <div className="mt-4 p-4 rounded-xl border border-gray-200 bg-gray-50">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-ink">Message Preview</h3>
          <Badge variant="ai">✦ AI generated</Badge>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
      <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{message}</p>
    </div>
  );
}
