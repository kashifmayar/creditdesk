import Badge from '../shared/Badge';

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
        className={`max-w-[85%] rounded-xl px-4 py-2.5 text-sm ${
          isUser
            ? 'bg-blue-700 text-white'
            : message.isError
              ? 'bg-red-50 text-red-700 border border-red-100'
              : 'bg-gray-50 text-ink border border-gray-100'
        }`}
      >
        {!isUser && !message.isError && (
          <Badge variant="ai" className="mb-1.5">✦ AI generated</Badge>
        )}
        <p className="whitespace-pre-wrap">{cleanText || message.text}</p>
        {citations.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {citations.map((c, i) => (
              <span
                key={i}
                className="inline-block text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700"
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
