import client from './client';

export async function previewReminder(payload) {
  const { data } = await client.post('/reminders/preview', payload);
  return data;
}

export async function sendBulkReminders(loan_ids) {
  const { data } = await client.post('/reminders/send', { loan_ids });
  return data;
}
