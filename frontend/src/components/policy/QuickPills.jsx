export default function QuickPills({ questions, onSelect, disabled }) {
  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {questions.map((q) => (
        <button
          key={q}
          onClick={() => onSelect(q)}
          disabled={disabled}
          className="text-xs px-3 py-1.5 rounded-full border border-gray-200 bg-white text-gray-600 hover:border-blue-700 hover:text-blue-700 transition-colors disabled:opacity-50"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
