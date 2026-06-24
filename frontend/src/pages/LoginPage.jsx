import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2 } from 'lucide-react';
import { login } from '../api/auth';
import { useAuthStore } from '../store/authStore';
import LoadingSpinner from '../components/shared/LoadingSpinner';

export default function LoginPage() {
  const [email, setEmail] = useState('analyst@bank.pk');
  const [password, setPassword] = useState('analyst123');
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
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg border border-gray-100 p-8">
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-xl bg-navy flex items-center justify-center mb-4">
            <Building2 className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-xl font-medium text-ink">Credit Analyst Workspace</h1>
          <p className="text-sm text-gray-500 mt-1">Sign in to your analyst account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-700 text-sm"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-700 text-sm"
            />
          </div>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-blue-700 text-white rounded-lg text-sm font-medium hover:bg-blue-800 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
          >
            {loading ? <LoadingSpinner size="sm" /> : null}
            Sign in
          </button>
        </form>

        <p className="text-xs text-gray-400 text-center mt-6">
          Demo: analyst@bank.pk / analyst123
        </p>
      </div>
    </div>
  );
}
