import { LogOut, MessageSquare, Send } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUiStore } from '../../store/uiStore';
import { TABS } from '../../utils/constants';

const NAV_ITEMS = [
  { id: TABS.POLICY, label: 'Policy', icon: MessageSquare },
  { id: TABS.REMINDERS, label: 'Reminders', icon: Send },
];

export default function Sidebar() {
  const activeTab = useUiStore((s) => s.activeTab);
  const setActiveTab = useUiStore((s) => s.setActiveTab);
  const remindersSentToday = useUiStore((s) => s.remindersSentToday);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  return (
    <aside className="fixed inset-y-0 left-0 z-20 flex w-60 flex-col border-r border-line bg-white">
      <div className="border-b border-line px-5 py-5">
        <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-gray-500">
          Credit Desk
        </p>
        <h1 className="mt-1 text-lg font-semibold text-ink">Analyst workspace</h1>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
          const active = activeTab === id;
          return (
            <button
              key={id}
              type="button"
              onClick={() => setActiveTab(id)}
              className={`flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm transition ${
                active
                  ? 'bg-navy text-white'
                  : 'text-gray-600 hover:bg-surface hover:text-ink'
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </button>
          );
        })}
      </nav>

      <div className="border-t border-line p-4 space-y-3">
        <div>
          <p className="text-xs text-gray-500">Reminders sent today</p>
          <p className="text-2xl font-semibold tabular-nums text-ink">{remindersSentToday}</p>
        </div>
        <div className="text-xs text-gray-500 truncate">{user?.full_name}</div>
        <button
          type="button"
          onClick={() => {
            logout();
            navigate('/login');
          }}
          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-600 transition hover:bg-surface"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
