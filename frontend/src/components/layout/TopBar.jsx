import { useAuthStore } from '../../store/authStore';
import Avatar from '../shared/Avatar';
import { formatToday } from '../../utils/formatters';

export default function TopBar({ activeLoans = 0 }) {
  const user = useAuthStore((s) => s.user);

  return (
    <header className="h-14 bg-white border-b border-gray-100 flex items-center justify-between px-6 sticky top-0 z-10">
      <div>
        <p className="text-xs text-gray-400">{formatToday()}</p>
        <p className="text-sm text-gray-600">
          <span className="font-medium text-ink">{activeLoans ?? 0}</span> active loans
        </p>
      </div>
      <div className="flex items-center gap-3">
        <Avatar name={user?.full_name || user?.email} />
        <div className="text-right">
          <p className="text-sm font-medium text-ink">{user?.full_name}</p>
          <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
        </div>
      </div>
    </header>
  );
}
