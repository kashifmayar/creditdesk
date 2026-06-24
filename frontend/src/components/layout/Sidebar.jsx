import { MessageSquare, Send, Upload } from 'lucide-react';
import { LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUiStore } from '../../store/uiStore';
import { TABS } from '../../utils/constants';

const NAV_ITEMS = [
  { id: TABS.POLICY, label: 'Policy Assistant', icon: MessageSquare },
  { id: TABS.REMINDERS, label: 'Payment Reminders', icon: Send },
  { id: TABS.UPLOAD, label: 'Upload Policy', icon: Upload, adminOnly: true },
];

export default function Sidebar() {
  const activeTab = useUiStore((s) => s.activeTab);
  const setActiveTab = useUiStore((s) => s.setActiveTab);
  const remindersSentToday = useUiStore((s) => s.remindersSentToday);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  return (
    <aside className="fixed left-0 top-0 h-full w-[220px] bg-navy text-white flex flex-col z-10">
      <div className="p-5 border-b border-white/10">
        <h1 className="text-sm font-medium tracking-wide">Credit Analyst</h1>
        <p className="text-xs text-white/60 mt-0.5">AI Workspace</p>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {NAV_ITEMS.map(({ id, label, icon: Icon, adminOnly }) => {
          if (adminOnly && user?.role !== 'admin') return null;
          const active = activeTab === id;
          return (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                active
                  ? 'bg-white/15 text-white font-medium'
                  : 'text-white/70 hover:bg-white/10 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/10 space-y-3">
        <div>
          <p className="text-xs text-white/50 mb-1">Reminders sent today</p>
          <p className="text-2xl font-medium text-teal-400">{remindersSentToday}</p>
        </div>
        <button
          onClick={() => { logout(); navigate('/login'); }}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-white/70 hover:bg-white/10 hover:text-white transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
