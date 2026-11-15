export default function QuickPills({ questions, onSelect, disabled, className = '' }) {
  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {questions.map((q) => (
        <button
          key={q}
          type="button"
          onClick={() => onSelect(q)}
          disabled={disabled}
          className="rounded-full border border-indigo-100/80 bg-white/80 px-3 py-1.5 text-left text-xs text-gray-700 shadow-sm backdrop-blur-sm transition hover:border-indigo-200 hover:bg-white hover:text-indigo-800 hover:shadow disabled:opacity-50 sm:text-[13px]"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
