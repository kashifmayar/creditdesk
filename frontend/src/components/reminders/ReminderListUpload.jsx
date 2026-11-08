import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Upload } from 'lucide-react';
import { uploadReminderList } from '../../api/reminders';
import { useUiStore } from '../../store/uiStore';

export default function ReminderListUpload() {
  const [file, setFile] = useState(null);
  const addToast = useUiStore((s) => s.addToast);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: uploadReminderList,
    onSuccess: (data) => {
      addToast(
        `Uploaded ${data.filename}: ${data.loans_created} loans imported (due date set to 1st of month).`
      );
      setFile(null);
      queryClient.invalidateQueries({ queryKey: ['due-borrowers'] });
      queryClient.invalidateQueries({ queryKey: ['metrics'] });
    },
    onError: (err) => {
      addToast(err.response?.data?.detail || 'Upload failed', 'error');
    },
  });

  return (
    <div className="mb-4 rounded-lg border border-gray-200 bg-gray-50 p-3">
      <div className="flex flex-wrap items-center gap-3">
        <p className="text-sm text-gray-600">
          Upload borrower list (PDF/Excel) for reminders.
        </p>
        <label className="inline-flex items-center gap-2 px-3 py-1.5 text-sm border border-gray-300 rounded-lg bg-white cursor-pointer hover:border-blue-700">
          <Upload className="w-4 h-4" />
          Choose File
          <input
            type="file"
            accept=".pdf,.xlsx,.xls"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </label>
        <button
          onClick={() => file && uploadMutation.mutate(file)}
          disabled={!file || uploadMutation.isPending}
          className="px-3 py-1.5 text-sm bg-blue-700 text-white rounded-lg disabled:opacity-50"
        >
          {uploadMutation.isPending ? 'Uploading…' : 'Upload to backend'}
        </button>
        {file && <span className="text-xs text-gray-500">{file.name}</span>}
      </div>
      <p className="mt-2 text-xs text-gray-500">
        Expected columns: name, phone, loan_number, installment_amount (optional: cnic, email, principal).
      </p>
    </div>
  );
}
