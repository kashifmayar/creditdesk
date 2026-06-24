import client from './client';

export async function askPolicy(question) {
  const { data } = await client.post('/policy/ask', { question });
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
