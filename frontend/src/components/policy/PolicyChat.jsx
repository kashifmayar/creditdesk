import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { askPolicy } from '../../api/policy';
import ChatMessage from './ChatMessage';
import QuickPills from './QuickPills';

const QUICK_QUESTIONS = [
  'What is the maximum LTV ratio for commercial loans?',
  'What is the grace period for late payments?',
  'What credit score is required for unsecured personal loans?',
  'When must a loan be escalated to the credit committee?',
  'What collateral is accepted for SME loans?',
  'What are the restructuring conditions?',
];

export default function PolicyChat() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      text: "Ask me anything about your credit policy. I'll cite the relevant section.",
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
      const detail = err.response?.data?.detail || 'Something went wrong. Please try again.';
      setMessages((prev) => [
        ...prev,
        { role: 'ai', text: detail, isError: true },
      ]);
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
    <div className="flex flex-col h-full">
      <div className="mb-4">
        <h2 className="text-lg font-medium text-ink mb-1">Policy Assistant</h2>
        <p className="text-sm text-gray-500">
          Instant answers from your credit policy manual with section citations.
        </p>
      </div>

      <QuickPills
        questions={QUICK_QUESTIONS}
        onSelect={(q) => handleSend(q)}
        disabled={isPending}
      />

      <div className="flex-1 overflow-y-auto space-y-3 mb-4 min-h-[280px] max-h-[400px] pr-1">
        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}
        {isPending && (
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span className="animate-spin">⟳</span> Checking policy manual…
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="e.g. What documents are needed for loan restructuring?"
          disabled={isPending}
          className="flex-1 text-sm px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-700 focus:border-transparent disabled:opacity-50"
        />
        <button
          onClick={() => handleSend()}
          disabled={isPending || !input.trim()}
          className="px-4 py-2 bg-blue-700 text-white rounded-lg text-sm font-medium hover:bg-blue-800 disabled:opacity-50 transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
