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
        className={`max-w-[92%] text-sm leading-relaxed sm:max-w-[85%] ${
          isUser
            ? 'user-bubble rounded-2xl rounded-br-md px-4 py-3 text-white shadow-lg'
            : message.isError
              ? 'rounded-2xl rounded-bl-md border border-red-200/80 bg-red-50/90 px-4 py-3 text-red-800 backdrop-blur-sm'
              : 'ai-bubble rounded-2xl rounded-bl-md px-4 py-3 text-ink shadow-md'
        }`}
      >
        {message.isExcerpt && !message.isError && (
          <p className="mb-2 text-[11px] font-medium uppercase tracking-wide text-indigo-600/80">
            Excerpt from manual (AI unavailable)
          </p>
        )}
        <p className="whitespace-pre-wrap">{cleanText || message.text}</p>
        {citations.length > 0 && (
          <div className="mt-2.5 flex flex-wrap gap-1.5">
            {citations.map((c, i) => (
              <span
                key={i}
                className="inline-block rounded-lg bg-white/70 px-2 py-0.5 text-[11px] font-medium text-indigo-700 ring-1 ring-indigo-100"
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
