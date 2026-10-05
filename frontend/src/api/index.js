import axios from 'axios'

// 创建 axios 实例：相对路径（开发走 Vite 代理，部署走 Nginx 反代）
const request = axios.create({
  baseURL: '',
  timeout: 60000,   // 智能体要多轮往返，超时放宽到 60 秒
})

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
