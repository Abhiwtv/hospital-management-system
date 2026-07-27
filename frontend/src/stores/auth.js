import { defineStore } from 'pinia'
import api from '../api/index.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
  user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null,
  access_token: localStorage.getItem('access_token') || null,
  role: localStorage.getItem('role') || null,
}),

  actions: {
    async loginPatient(username, password) {
      const res = await api.post('/api/auth/login/patient', { username, password })
      this.setAuth(res.data.data.patient, res.data.data.access_token, 'patient')
    },

    async loginDoctor(username, password) {
      const res = await api.post('/api/auth/login/doctor', { username, password })
      this.setAuth(res.data.data.doctor, res.data.data.access_token, 'doctor')
    },

    async loginAdmin(username, password) {
      const res = await api.post('/api/auth/login/admin', { username, password })
      this.setAuth({ username }, res.data.data.access_token, 'admin')
    },

    
    async refreshAccessToken() {
      try {
        const res = await api.post('/api/auth/refresh')
        const newAccessToken = res.data.data.access_token
        
        this.access_token = newAccessToken
        localStorage.setItem('access_token', newAccessToken)
        
        return newAccessToken
      } catch (error) {
        await this.logout()
        throw error
      }
    },

    setAuth(user, token, role) {
      this.user         = user
      this.access_token = token
      this.role         = role
      localStorage.setItem('user',         JSON.stringify(user))
      localStorage.setItem('access_token', token)
      localStorage.setItem('role',         role)
    },

    
    async logout() {
      try {
        await api.post('/api/auth/logout') 
      } catch (error) {
        console.error("Backend logout failed, clearing local state anyway", error)
      } finally {
        this.user         = null
        this.access_token = null
        this.role         = null
        localStorage.clear()
      }
    },
  },
})