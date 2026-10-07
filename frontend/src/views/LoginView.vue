<script setup>
// 登录/注册页：JWT 鉴权入口。默认演示账号 admin / admin123
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, register } from '../api/index.js'

const router = useRouter()
const tab = ref('login')            // login | register
const username = ref('admin')
const password = ref('')
const password2 = ref('')
const loading = ref(false)

function saveSession(data) {
  localStorage.setItem('dxz_token', data.token)
  localStorage.setItem('dxz_username', data.username)
}

async function handleLogin() {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await login(username.value, password.value)
    saveSession(res.data.data)
    ElMessage.success('登录成功')
    router.push({ name: 'home' })
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '登录失败，请检查用户名密码')
  } finally {
    loading.value = false
  }
}

function errText(e, fallback) {
  // 后端正常返回 {detail: "人话"}；422 校验失败时 detail 是数组，取第一条 msg
  const d = e.response?.data
  if (typeof d?.detail === 'string') return d.detail
  if (Array.isArray(d?.detail)) return d.detail[0]?.msg || fallback
  return fallback
}

async function handleRegister() {
  if (!username.value || !password.value || !password2.value) {
    ElMessage.warning('请填写完整')
    return
  }
  if (password.value !== password2.value) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    const res = await register(username.value, password.value)
    saveSession(res.data.data)
    ElMessage.success('注册成功，已自动登录')
    router.push({ name: 'home' })
  } catch (e) {
    ElMessage.error(errText(e, '注册失败，请稍后再试'))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-title">🛍️ 店小智 · 智能客服工作台</div>
      <div class="login-badge">企业级电商智能客服系统</div>
      <el-tabs v-model="tab" stretch>
        <el-tab-pane label="登 录" name="login">
          <div class="pane">
            <el-input v-model="username" placeholder="用户名" size="large" @keyup.enter="handleLogin" />
            <el-input v-model="password" type="password" placeholder="密码" size="large"
                      show-password @keyup.enter="handleLogin" />
            <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleLogin">
              登 录
            </el-button>
            <div class="login-hint">演示账号：admin / admin123</div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="注 册" name="register">
          <div class="pane">
            <el-input v-model="username" placeholder="用户名（3-20 位字母/数字/下划线）" size="large"
                      @keyup.enter="handleRegister" />
            <el-input v-model="password" type="password" placeholder="密码（至少 6 位）" size="large"
                      show-password @keyup.enter="handleRegister" />
            <el-input v-model="password2" type="password" placeholder="确认密码" size="large"
                      show-password @keyup.enter="handleRegister" />
            <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleRegister">
              注册并登录
            </el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style scoped>
/* 拟物 v2 登录页：亚麻底 + 纸面卡 + 金色徽章 + 蓝色光泽主按钮 */
.login-page {
  height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(180deg, #d4c4a8 0%, #c8b898 55%, #b8a888 100%);
  position: relative;
}
.login-page::before {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background-image: var(--sk-linen);
}
.login-card {
  position: relative;
  width: 400px; padding: 40px 36px; border-radius: 16px;
  background-image: var(--sk-weave), linear-gradient(180deg, var(--sk-paper-hi), var(--sk-paper-lo));
  border: 1px solid var(--sk-paper-border);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.9), inset 0 -1px 0 rgba(0, 0, 0, 0.06);
  display: flex; flex-direction: column; gap: 14px;
}
.login-title {
  font-family: var(--sk-font-display);
  font-weight: 900; font-size: 21px; text-align: center; color: var(--sk-ink);
  text-shadow: 0 2px 0 rgba(255, 255, 255, 0.45), 0 4px 12px rgba(0, 0, 0, 0.15);
}
.login-badge {
  align-self: center; margin-bottom: 12px;
  padding: 5px 18px; border-radius: 999px;
  font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.14em;
  color: #fff8e0;
  background-image: linear-gradient(180deg, var(--sk-gold), var(--sk-gold-deep));
  border: 1px solid #806010;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.25), inset 0 -1px 0 rgba(0, 0, 0, 0.2);
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.35);
}
.login-btn { width: 100%; height: 44px; font-size: 15px; letter-spacing: 6px; }
.pane { display: flex; flex-direction: column; gap: 14px; padding-top: 6px; }
.login-hint {
  font-size: 12px; font-weight: 600; color: var(--sk-leather-deep); text-align: center;
  padding: 7px 0; border-radius: 8px;
  background: rgba(139, 115, 85, 0.12);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.4);
}
</style>
