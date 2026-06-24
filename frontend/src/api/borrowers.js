import client from './client';

export async function fetchDueBorrowers() {
  const { data } = await client.get('/borrowers/due');
  return data;
}

export async function fetchMetrics() {
  const { data } = await client.get('/borrowers/metrics/summary');
  return data;
}
