import client from './client';
import { isDemoMode } from './demo';
import { demoDelay, getDemoLogin } from './demoData';

export async function login(email, password) {
  if (isDemoMode()) {
    await demoDelay();
    return getDemoLogin();
  }
  const { data } = await client.post('/auth/login', { email, password });
  return data;
}

export async function fetchMe() {
  if (isDemoMode()) return getDemoLogin().user;
  const { data } = await client.get('/auth/me');
  return data;
}

export async function refreshToken(refresh_token) {
  const { data } = await client.post('/auth/refresh', { refresh_token });
  return data;
}
