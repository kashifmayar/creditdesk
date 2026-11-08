function extractCitations(text) {
  const citationRegex = /\[§[\d.]+\s*[^\]]*\]/g;
  const citations = text.match(citationRegex) || [];
  const cleanText = text.replace(citationRegex, '').trim();
  return { cleanText, citations };
}

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const { cleanText, citations } = isUser
    ? { cleanText: message.text, citations: [] }
    : extractCitations(message.text);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[88%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-navy text-white rounded-br-md'
            : message.isError
              ? 'bg-red-50 text-red-800 border border-red-100 rounded-bl-md'
              : 'bg-surface text-ink border border-line rounded-bl-md'
        }`}
      >
        <p className="whitespace-pre-wrap">{cleanText || message.text}</p>
        {citations.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {citations.map((c, i) => (
              <span
                key={i}
                className="inline-block rounded-md bg-white px-2 py-0.5 text-[11px] font-medium text-accent ring-1 ring-line"
              >
                {c.replace(/[\[\]]/g, '')}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
