import { defineStore } from 'pinia'
import http from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('auth_user') || 'null'),
    accessToken: localStorage.getItem('access_token') || '',
    refreshToken: localStorage.getItem('refresh_token') || '',
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken && state.user),
    role: (state) => state.user?.role || '',
  },
  actions: {
    async login(email, password) {
      this.loading = true
      try {
        const response = await http.post('/api/v1/auth/login', { email, password })
        this.setSession(response.data.user, response.data.access_token, response.data.refresh_token)
        return response.data.user
      } finally {
        this.loading = false
      }
    },
    async restoreSession() {
      if (!this.accessToken) return null
      try {
        const response = await http.get('/api/v1/auth/me')
        this.user = response.data.user
        localStorage.setItem('auth_user', JSON.stringify(this.user))
        return this.user
      } catch {
        this.logout()
        return null
      }
    },
    setSession(user, accessToken, refreshToken) {
      this.user = user
      this.accessToken = accessToken
      this.refreshToken = refreshToken
      localStorage.setItem('auth_user', JSON.stringify(user))
      localStorage.setItem('access_token', accessToken)
      localStorage.setItem('refresh_token', refreshToken)
      http.defaults.headers.common.Authorization = `Bearer ${accessToken}`
    },
    logout() {
      this.user = null
      this.accessToken = ''
      this.refreshToken = ''
      localStorage.removeItem('auth_user')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      delete http.defaults.headers.common.Authorization
    },
  },
})
