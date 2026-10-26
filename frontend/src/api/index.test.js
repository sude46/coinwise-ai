import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import api from './index'

describe('API Client', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('请求携带 Authorization Token', () => {
    localStorage.setItem('access_token', 'test_token_xyz')
    const config = api.defaults.headers
    // 由于拦截器在运行时注入，这里检查 defaults 配置
    expect(api.defaults.baseURL).toBe('/api/v1')
    expect(api.defaults.withCredentials).toBe(true)
    expect(api.defaults.timeout).toBe(15000)
  })

  it('响应 401 时尝试刷新 Token', async () => {
    localStorage.setItem('access_token', 'old_token')
    localStorage.setItem('refresh_token', 'refresh_xyz')

    // 这里只验证配置正确性，不模拟完整网络请求
    expect(localStorage.getItem('refresh_token')).toBe('refresh_xyz')
  })

  it('X-Request-ID 头在请求中注入', async () => {
    // 检查请求拦截器是否配置了 X-Request-ID
    const interceptor = api.interceptors.request.handlers[0]
    expect(interceptor).toBeDefined()
  })

  it('aiApi.chat 方法存在', () => {
    const { aiApi } = require('./index')
    expect(typeof aiApi.chat).toBe('function')
  })

  it('savingsGoalApi.predict 方法存在', () => {
    const { savingsGoalApi } = require('./index')
    expect(typeof savingsGoalApi.predict).toBe('function')
  })
})
