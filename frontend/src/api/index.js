import axios from 'axios'

// 创建 axios 实例：相对路径（开发走 Vite 代理，部署走 Nginx 反代）
const request = axios.create({
  baseURL: '',
  timeout: 60000,   // 智能体要多轮往返，超时放宽到 60 秒
})

// 请求拦截器：自动携带 JWT（localStorage 中保存登录凭证）
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('dxz_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截器：401 统一跳回登录页
request.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('dxz_token')
      localStorage.removeItem('dxz_username')
      if (!location.hash.includes('/login')) location.hash = '#/login'
    }
    return Promise.reject(err)
  },
)

// ===== 认证 =====
export function login(username, password) {
  return request.post('/api/auth/login', { username, password })
}

// ===== 会话管理 =====
export function listSessions() {
  return request.get('/api/sessions')
}

export function createSession() {
  return request.post('/api/sessions')
}

export function deleteSession(id) {
  return request.delete(`/api/sessions/${id}`)
}

export function getMessages(id) {
  return request.get(`/api/sessions/${id}/messages`)
}

// ===== 对话 =====
export function sendChat(message, sessionId) {
  return request.post('/api/chat', { message, session_id: sessionId })
}

export function sendAgentChat(message, sessionId) {
  return request.post('/api/agent/chat', { message, session_id: sessionId })
}

// 统一入口：后端意图识别后自动路由到普通对话或智能体
export function sendSmartChat(message, sessionId) {
  return request.post('/api/smart/chat', { message, session_id: sessionId })
}

// ===== 业务数据中心：订单 =====
export function listOrders() {
  return request.get('/api/orders')
}

export function saveOrder(order) {
  return request.post('/api/orders', order)
}

export function deleteOrder(orderId) {
  return request.delete(`/api/orders/${orderId}`)
}

// ===== 业务数据中心：优惠券 =====
export function listCoupons() {
  return request.get('/api/coupons')
}

export function saveCoupon(coupon) {
  return request.post('/api/coupons', coupon)
}

export function deleteCoupon(code) {
  return request.delete(`/api/coupons/${code}`)
}

// ===== 知识库 =====
export function listKnowledge() {
  return request.get('/api/knowledge')
}

export function addKnowledge(item) {
  return request.post('/api/knowledge', item)
}

export function updateKnowledge(id, item) {
  return request.put(`/api/knowledge/${id}`, item)
}

export function deleteKnowledge(id) {
  return request.delete(`/api/knowledge/${id}`)
}

// ===== 统计 =====
export function getStatsOverview() {
  return request.get('/api/stats/overview')
}
