import api from './api.js';

export const authService = {
  async login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password });
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    return data.user;
  },
  async logout() {
    const refresh = localStorage.getItem('refresh_token');
    if (refresh) {
      await api.post('/auth/logout/', { refresh });
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
  async profile() {
    const { data } = await api.get('/auth/profile/');
    return data;
  },
  async changePassword(payload) {
    const { data } = await api.post('/auth/change-password/', payload);
    return data;
  },
};
