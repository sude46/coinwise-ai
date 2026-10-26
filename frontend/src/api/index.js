import axios from 'axios'

// 生成请求追踪 ID
function generateRequestId() {
  return 'req_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36)
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  timeout: 15000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // 注入 X-Request-ID（用于审计追踪）
    config.headers['X-Request-ID'] = generateRequestId()
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const res = await axios.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken
          })
          const { access_token, refresh_token } = res.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          // 同步清除 token，避免后续请求继续带失效凭证
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      }
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken })
}

// Transaction API
export const transactionApi = {
  create: (data) => api.post('/transactions', data),
  list: (params) => api.get('/transactions', { params }),
  get: (id) => api.get(`/transactions/${id}`),
  update: (id, data) => api.put(`/transactions/${id}`, data),
  delete: (id) => api.delete(`/transactions/${id}`)
}

// Category API
export const categoryApi = {
  create: (data) => api.post('/categories', data),
  list: () => api.get('/categories'),
  delete: (id) => api.delete(`/categories/${id}`)
}

// Budget API
export const budgetApi = {
  create: (data) => api.post('/budgets', data),
  list: (params) => api.get('/budgets', { params }),
  get: (id) => api.get(`/budgets/${id}`),
  update: (id, data) => api.put(`/budgets/${id}`, data),
  delete: (id) => api.delete(`/budgets/${id}`)
}

// Account API
export const accountApi = {
  create: (data) => api.post('/accounts', data),
  list: () => api.get('/accounts'),
  get: (id) => api.get(`/accounts/${id}`),
  update: (id, data) => api.put(`/accounts/${id}`, data),
  delete: (id) => api.delete(`/accounts/${id}`)
}

// Dashboard API
export const dashboardApi = {
  get: (yearMonth) => api.get('/dashboard', { params: { year_month: yearMonth } })
}

// Report API
export const reportApi = {
  get: (yearMonth) => api.get(`/reports/${yearMonth}`),
  list: () => api.get('/reports')
}

// Search API
export const searchApi = {
  search: (params) => api.get('/search', { params })
}

// SavingsGoal API（新增）
export const savingsGoalApi = {
  create: (data) => api.post('/savings-goals', data),
  list: (params) => api.get('/savings-goals', { params }),
  get: (id) => api.get(`/savings-goals/${id}`),
  predict: (id) => api.get(`/savings-goals/${id}/predict`),
  update: (id, data) => api.put(`/savings-goals/${id}`, data),
  delete: (id) => api.delete(`/savings-goals/${id}`)
}

// AI Assistant API（新增）
export const aiApi = {
  chat: (data) => api.post('/ai/chat', data)
}

// Import/Export API
export const importExportApi = {
  importFile: (file, accountId) => {
    const formData = new FormData()
    formData.append('file', file)
    const token = localStorage.getItem('access_token')
    return api.post('/import-export/import', formData, {
      params: { account_id: accountId },
      headers: {
        'Content-Type': 'multipart/form-data',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    })
  },
  exportCSV: (params) => api.get('/import-export/export', {
    params,
    responseType: 'blob',
  }),
}

export default api
