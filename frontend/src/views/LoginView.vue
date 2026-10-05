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
.login-page {
  height: 100vh; display: flex; align-items: center; justify-content: center;
  background: #f5f7fa;
}
.login-card {
  width: 360px; padding: 36px 32px; background: #fff; border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08); display: flex; flex-direction: column; gap: 14px;
}
.login-title { font-size: 20px; font-weight: bold; text-align: center; }
.login-sub { font-size: 13px; color: #909399; text-align: center; margin-bottom: 10px; }
.login-btn { width: 100%; }
.login-hint { font-size: 12px; color: #b0b3ba; text-align: center; }
</style>
