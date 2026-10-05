<script setup>
// 登录页：JWT 鉴权入口。默认演示账号 admin / admin123
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/index.js'

const router = useRouter()
const username = ref('admin')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await login(username.value, password.value)
    localStorage.setItem('dxz_token', res.data.data.token)
    localStorage.setItem('dxz_username', res.data.data.username)
    ElMessage.success('登录成功')
    router.push({ name: 'home' })
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '登录失败，请检查用户名密码')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-title">🛍️ 店小智 · 智能客服工作台</div>
      <div class="login-sub">企业级电商智能客服系统</div>
      <el-input v-model="username" placeholder="用户名" size="large" @keyup.enter="handleLogin" />
      <el-input v-model="password" type="password" placeholder="密码" size="large"
                show-password @keyup.enter="handleLogin" />
      <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleLogin">
        登 录
      </el-button>
      <div class="login-hint">演示账号：admin / admin123</div>
    </div>
  </div>
</template>

<style scoped>
/* 拟物登录页：皮革门面 + 缝线 + 纸面卡片 */
.login-page {
  height: 100vh; display: flex; align-items: center; justify-content: center;
  background-image: var(--sk-noise), var(--sk-wood-grain),
    linear-gradient(180deg, #8b7355 0%, #6b5b45 60%, #55483a 100%);
  box-shadow: inset 0 0 120px rgba(0, 0, 0, 0.35);
}
.login-card {
  position: relative;
  width: 380px; padding: 36px 32px; border-radius: 12px;
  background-image: var(--sk-noise), linear-gradient(180deg, #f0e9da, var(--sk-wood));
  border: 1px solid var(--sk-border);
  box-shadow: var(--sk-shadow-lg), inset 0 1px 0 rgba(255, 255, 255, 0.8), inset 0 -1px 0 rgba(0, 0, 0, 0.1);
  display: flex; flex-direction: column; gap: 14px;
}
/* 卡片内圈皮革缝线 */
.login-card::before {
  content: ""; position: absolute; inset: 8px; border-radius: 9px;
  border: 1px dashed rgba(139, 115, 85, 0.5); pointer-events: none;
}
.login-title {
  font-size: 20px; font-weight: bold; text-align: center; color: var(--sk-ink);
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.65);
}
.login-sub { font-size: 13px; color: var(--sk-ink-2); text-align: center; margin-bottom: 10px; }
.login-btn { width: 100%; height: 42px; font-size: 15px; letter-spacing: 6px; }
.login-hint {
  font-size: 12px; color: var(--sk-ink-3); text-align: center;
  padding: 6px 0; border-radius: 8px;
  background: rgba(139, 115, 85, 0.1);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.08);
}
</style>
