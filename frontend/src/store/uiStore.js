import { create } from 'zustand';
import { TABS } from '../utils/constants';

export const useUiStore = create((set) => ({
  activeTab: TABS.POLICY,
  setActiveTab: (tab) => set({ activeTab: tab }),
  remindersSentToday: 0,
  setRemindersSentToday: (count) => set({ remindersSentToday: count }),
  incrementRemindersSent: (count) =>
    set((state) => ({ remindersSentToday: state.remindersSentToday + count })),
  toasts: [],
  addToast: (message, type = 'success') => {
    const id = Date.now();
    set((state) => ({
      toasts: [...state.toasts, { id, message, type }],
    }));
    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      }));
    }, 4000);
  },
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));
