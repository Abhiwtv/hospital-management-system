import axios from 'axios'
import router from '../router/index.js'

const api = axios.create({
  baseURL: 'http://localhost:5000',
})


api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRoute = error.config?.url?.includes('/api/auth/login')
    if (error.response?.status === 401 && !isLoginRoute) {
      
      const role = localStorage.getItem('role')
      localStorage.clear()

      
      if (role === 'doctor')      router.push('/login/doctor')
      else if (role === 'admin')  router.push('/login/admin')
      else                        router.push('/login/patient')
    }
    return Promise.reject(error)
  }
)

export default api