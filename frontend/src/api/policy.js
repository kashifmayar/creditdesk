import client from './client';
import { isDemoMode } from './demo';

export async function askPolicy(question) {
  if (isDemoMode()) {
    const { demoDelay, getDemoPolicyAnswer } = await import('./demoData');
    await demoDelay(600);
    return getDemoPolicyAnswer(question);
  }
  const { data } = await client.post('/policy/ask', { question });
  return data;
}

export async function fetchPolicyStatus() {
  if (isDemoMode()) {
    return { loaded: true, filename: 'Credit Procedure Manual (demo)', chunks_ingested: 120 };
  }
  const { data } = await client.get('/policy/status');
  return data;
}

export async function uploadPolicy(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await client.post('/policy/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}
