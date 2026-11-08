export default function QuickPills({ questions, onSelect, disabled }) {
  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {questions.map((q) => (
        <button
          key={q}
          type="button"
          onClick={() => onSelect(q)}
          disabled={disabled}
          className="rounded-full border border-line bg-white px-3 py-1 text-xs text-gray-600 transition hover:border-accent/30 hover:text-accent disabled:opacity-50"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
