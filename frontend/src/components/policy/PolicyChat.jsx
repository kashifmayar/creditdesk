import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { SendHorizontal } from 'lucide-react';
import { askPolicy } from '../../api/policy';
import ChatMessage from './ChatMessage';
import PolicyDocBar from './PolicyDocBar';
import QuickPills from './QuickPills';

const STARTER = [
  'Maximum LTV for commercial loans?',
  'Grace period for late payments?',
  'When to escalate to credit committee?',
];

export default function PolicyChat() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      text: 'Questions are answered from your uploaded credit policy. Answers include the relevant section reference when available.',
    },
  ]);
  const [input, setInput] = useState('');
  const bottomRef = useRef(null);

  const { mutate: send, isPending } = useMutation({
    mutationFn: askPolicy,
    onMutate: (question) => {
      setMessages((prev) => [...prev, { role: 'user', text: question }]);
    },
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { role: 'ai', text: data.answer }]);
    },
    onError: (err) => {
      const detail = err.response?.data?.detail || 'Unable to reach the policy service.';
      setMessages((prev) => [...prev, { role: 'ai', text: detail, isError: true }]);
    },
  });

  const handleSend = (question) => {
    const q = (question ?? input).trim();
    if (!q || isPending) return;
    setInput('');
    send(q);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isPending]);

  return (
    <div className="flex h-[calc(100vh-13rem)] min-h-[520px] flex-col gap-4 fade-in">
      <PolicyDocBar />

      <div className="flex min-h-0 flex-1 flex-col rounded-xl border border-line bg-white shadow-panel">
        <div className="border-b border-line px-5 py-4">
          <h2 className="text-base font-semibold text-ink">Policy assistant</h2>
          <p className="mt-1 text-sm text-gray-500">
            Internal Q&amp;A over the institution policy manual.
          </p>
          <QuickPills questions={STARTER} onSelect={handleSend} disabled={isPending} />
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className="slide-up" style={{ animationDelay: `${Math.min(i, 6) * 40}ms` }}>
              <ChatMessage message={msg} />
            </div>
          ))}
          {isPending && (
            <div className="flex items-center gap-1.5 text-sm text-gray-500 slide-up">
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-gray-400" />
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-gray-400 [animation-delay:150ms]" />
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-gray-400 [animation-delay:300ms]" />
              <span className="ml-2">Searching policy…</span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-line p-4">
          <div className="flex items-center gap-2 rounded-lg border border-line bg-surface px-3 py-2 focus-within:border-accent/40 focus-within:ring-2 focus-within:ring-accent/10">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about collateral, approvals, restructuring…"
              disabled={isPending}
              className="flex-1 bg-transparent text-sm outline-none placeholder:text-gray-400 disabled:opacity-60"
            />
            <button
              onClick={() => handleSend()}
              disabled={isPending || !input.trim()}
              className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-navy text-white transition hover:bg-accent disabled:opacity-40"
              aria-label="Send"
            >
              <SendHorizontal className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
