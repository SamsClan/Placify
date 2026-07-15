import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
})

http.interceptors.request.use((config) => {
  config.headers = config.headers || {}
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (
      error.response?.status === 401 &&
      !originalRequest?._retry &&
      localStorage.getItem('refresh_token')
    ) {
      originalRequest._retry = true
      try {
        const refreshResponse = await axios.post('/api/v1/auth/refresh', {}, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('refresh_token')}`,
          },
        })
        localStorage.setItem('access_token', refreshResponse.data.access_token)
        originalRequest.headers.Authorization = `Bearer ${refreshResponse.data.access_token}`
        return http(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('auth_user')
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export default http
