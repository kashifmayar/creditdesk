export default function BulkActionBar({
  selectedCount,
  totalCount,
  onSelectAll,
  onPreview,
  onSend,
  isSending,
  isPreviewing,
}) {
  const allSelected = selectedCount === totalCount && totalCount > 0;

  return (
    <div className="flex flex-wrap items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
      <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
        <input
          type="checkbox"
          checked={allSelected}
          onChange={(e) => onSelectAll(e.target.checked)}
          className="w-4 h-4 rounded border-gray-300 text-blue-700 focus:ring-blue-700"
        />
        Select all ({selectedCount}/{totalCount})
      </label>

      <div className="flex-1" />

      <button
        onClick={onPreview}
        disabled={selectedCount === 0 || isPreviewing || isSending}
        className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:border-blue-700 hover:text-blue-700 disabled:opacity-50 transition-colors"
      >
        {isPreviewing ? 'Generating…' : 'Preview'}
      </button>
      <button
        onClick={onSend}
        disabled={selectedCount === 0 || isSending}
        className="px-4 py-1.5 text-sm bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 disabled:opacity-50 transition-colors"
      >
        {isSending ? 'Sending…' : `Send ${selectedCount || ''} Reminder${selectedCount !== 1 ? 's' : ''}`}
      </button>
    </div>
  );
}
