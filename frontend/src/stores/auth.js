// src/stores/auth.js
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
// In auth.js actions
    setToken(newToken) {
      this.token = newToken;
      localStorage.setItem('access_token', newToken);
      // Force update
      this.router = this.router; // This is a hack to force reactivity
    },
    clearToken() {
      this.token = null;
      localStorage.removeItem('access_token');
    },
  },
});
