import client from './client';
import { isDemoMode } from './demo';

export async function previewReminder(payload) {
  if (isDemoMode()) {
    const { demoDelay, getDemoReminderPreview } = await import('./demoData');
    await demoDelay();
    return getDemoReminderPreview(payload);
  }
  const { data } = await client.post('/reminders/preview', payload);
  return data;
}

export async function sendBulkReminders(loan_ids) {
  if (isDemoMode()) {
    const { demoDelay, getDemoReminderSend } = await import('./demoData');
    await demoDelay(700);
    return getDemoReminderSend(loan_ids);
  }
  const { data } = await client.post('/reminders/send', { loan_ids });
  return data;
}

export async function uploadReminderList(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await client.post('/reminders/upload-list', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}
