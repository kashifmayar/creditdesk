import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/auth';
import { useAuthStore } from '../store/authStore';
import LoadingSpinner from '../components/shared/LoadingSpinner';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const setAuth = useAuthStore((s) => s.setAuth);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await login(email, password);
      setAuth(data.access_token, data.refresh_token, data.user);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Sign in failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface px-4 flex items-center justify-center fade-in">
      <div className="w-full max-w-md rounded-xl border border-line bg-white p-8 shadow-panel">
        <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-gray-500">
          Credit Desk
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-ink">Sign in</h1>
        <p className="mt-1 text-sm text-gray-500">Analyst access to policy and reminders.</p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div>
            <label htmlFor="email" className="mb-1 block text-sm font-medium text-gray-700">
              Work email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border border-line px-3 py-2 text-sm outline-none focus:border-accent/40 focus:ring-2 focus:ring-accent/10"
            />
          </div>
          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-lg border border-line px-3 py-2 text-sm outline-none focus:border-accent/40 focus:ring-2 focus:ring-accent/10"
            />
          </div>

          {error && (
            <p className="rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-navy py-2.5 text-sm font-medium text-white transition hover:bg-accent disabled:opacity-50"
          >
            {loading ? <LoadingSpinner size="sm" /> : null}
            Continue
          </button>
        </form>
      </div>
    </div>
  );
}
