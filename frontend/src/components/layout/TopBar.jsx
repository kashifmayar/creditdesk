import { useAuthStore } from '../../store/authStore';
import { formatToday } from '../../utils/formatters';

export default function TopBar({ activeLoans = 0 }) {
  const user = useAuthStore((s) => s.user);

  return (
    <header className="sticky top-0 z-10 border-b border-line bg-white/90 px-6 py-4 backdrop-blur">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs text-gray-500">{formatToday()}</p>
          <p className="text-sm text-gray-700">
            <span className="font-semibold text-ink tabular-nums">{activeLoans ?? 0}</span> active loans
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-ink">{user?.full_name}</p>
          <p className="text-xs capitalize text-gray-500">{user?.role}</p>
        </div>
      </div>
    </header>
  );
}
