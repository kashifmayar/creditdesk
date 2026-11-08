import client from './client';
import { isDemoMode } from './demo';
import { demoDelay, getDemoBorrowers, getDemoMetrics } from './demoData';

export async function fetchDueBorrowers() {
  if (isDemoMode()) {
    await demoDelay();
    return getDemoBorrowers();
  }
  const { data } = await client.get('/borrowers/due');
  return data;
}

export async function fetchMetrics() {
  if (isDemoMode()) {
    await demoDelay(200);
    return getDemoMetrics();
  }
  const { data } = await client.get('/borrowers/metrics/summary');
  return data;
}
