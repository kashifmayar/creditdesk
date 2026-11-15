import { useState, useRef, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Sparkles, SendHorizontal } from 'lucide-react';
import { askPolicy, fetchPolicyStatus } from '../../api/policy';
import ChatMessage from './ChatMessage';
import QuickPills from './QuickPills';

const STARTER = [
  'Maximum LTV for commercial loans?',
  'Grace period for late payments?',
  'When to escalate to credit committee?',
];

export default function PolicyChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const bottomRef = useRef(null);

  const { data: policyStatus } = useQuery({
    queryKey: ['policy-status'],
    queryFn: fetchPolicyStatus,
  });

  const { mutate: send, isPending } = useMutation({
    mutationFn: askPolicy,
    onMutate: (question) => {
      setMessages((prev) => [...prev, { role: 'user', text: question }]);
    },
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          text: data.answer,
          isExcerpt: data.answer_mode === 'excerpt',
        },
      ]);
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

  const isEmpty = messages.length === 0;

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col px-1 pb-4 pt-2 sm:px-2 sm:pb-6 sm:pt-4 fade-in">
      <div className="chat-panel flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl sm:rounded-3xl sm:min-h-[min(720px,calc(100dvh-6.5rem))]">
        {policyStatus && !policyStatus.ai_key_format_ok && (
          <div className="border-b border-amber-200/80 bg-amber-50/95 px-4 py-2.5 text-xs leading-relaxed text-amber-950 sm:px-5">
            AI is off. Use a free <strong>gsk_</strong> key from{' '}
            <a
              href="https://console.groq.com/keys"
              target="_blank"
              rel="noreferrer"
              className="font-medium text-indigo-700 underline"
            >
              Groq
            </a>{' '}
            (set <code className="text-[10px]">AI_PROVIDER=groq</code> in .env) or an{' '}
            <strong>AIza</strong> key from{' '}
            <a
              href="https://aistudio.google.com/apikey"
              target="_blank"
              rel="noreferrer"
              className="font-medium text-indigo-700 underline"
            >
              Google AI Studio
            </a>
            . Then restart the backend.
          </div>
        )}
        <div className="flex-1 overflow-y-auto px-3 py-4 sm:px-5 sm:py-6">
          {isEmpty ? (
            <div className="flex h-full min-h-[280px] flex-col items-center justify-center px-4 text-center sm:min-h-[360px]">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-400/35">
                <Sparkles className="h-7 w-7" />
              </div>
              <h2 className="text-lg font-semibold text-ink sm:text-xl">Ask your credit policy</h2>
              <p className="mt-2 max-w-sm text-sm leading-relaxed text-gray-600">
                Get answers grounded in your uploaded procedure manual — with section references when
                available.
              </p>
              <QuickPills
                questions={STARTER}
                onSelect={handleSend}
                disabled={isPending}
                className="mt-6 justify-center"
              />
            </div>
          ) : (
            <div className="space-y-4 sm:space-y-5">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className="slide-up"
                  style={{ animationDelay: `${Math.min(i, 6) * 40}ms` }}
                >
                  <ChatMessage message={msg} />
                </div>
              ))}
              {isPending && (
                <div className="flex items-center gap-2 pl-1 text-sm text-indigo-600/80 slide-up">
                  <span className="typing-dot h-2 w-2 rounded-full bg-indigo-400" />
                  <span className="typing-dot h-2 w-2 rounded-full bg-violet-400 [animation-delay:150ms]" />
                  <span className="typing-dot h-2 w-2 rounded-full bg-indigo-400 [animation-delay:300ms]" />
                  <span className="ml-1">Thinking…</span>
                </div>
              )}
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {!isEmpty && (
          <div className="hidden border-t border-white/50 px-4 py-2 sm:block">
            <QuickPills questions={STARTER} onSelect={handleSend} disabled={isPending} />
          </div>
        )}

        <div className="border-t border-white/50 p-3 sm:p-4">
          <div className="chat-input flex items-end gap-2 rounded-2xl p-2 sm:gap-3 sm:p-2.5">
            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask about collateral, approvals, restructuring…"
              disabled={isPending}
              className="max-h-32 min-h-[2.5rem] flex-1 resize-none bg-transparent px-2 py-2 text-sm leading-snug text-ink outline-none placeholder:text-gray-400 disabled:opacity-60"
            />
            <button
              onClick={() => handleSend()}
              disabled={isPending || !input.trim()}
              className="send-btn inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-white transition disabled:opacity-40 sm:h-10 sm:w-10"
              aria-label="Send"
            >
              <SendHorizontal className="h-5 w-5" />
            </button>
          </div>
          <p className="mt-2 hidden text-center text-[10px] text-gray-500 sm:block">
            Enter to send · Shift+Enter for a new line
          </p>
        </div>
      </div>
    </div>
  );
}
