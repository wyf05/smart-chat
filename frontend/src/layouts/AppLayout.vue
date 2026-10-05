<script setup>
// 全局布局：顶部导航栏 + 内容区。所有子页面在此布局下渲染。
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const navs = [
  { name: 'home', label: '首页', icon: '🏠' },
  { name: 'chat', label: '智能对话', icon: '💬' },
  { name: 'data', label: '业务数据', icon: '📦' },
  { name: 'knowledge', label: '知识库', icon: '📚' },
  { name: 'stats', label: '数据统计', icon: '📊' },
]

const username = computed(() => localStorage.getItem('dxz_username') || 'admin')
const activeName = computed(() => (route.name === 'login' ? '' : route.name))

function handleLogout() {
  localStorage.removeItem('dxz_token')
  localStorage.removeItem('dxz_username')
  ElMessage.success('已退出登录')
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="layout">
    <header class="topbar">
      <div class="brand">🛍️ 店小智 · 智能客服工作台</div>
      <nav class="nav">
        <router-link
          v-for="n in navs"
          :key="n.name"
          :to="{ name: n.name }"
          class="nav-item"
          :class="{ active: activeName === n.name }"
        >
          <span class="nav-icon">{{ n.icon }}</span>{{ n.label }}
        </router-link>
      </nav>
      <div class="user-box">
        <span class="username">👤 {{ username }}</span>
        <el-button size="small" text @click="handleLogout">退出登录</el-button>
      </div>
    </header>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.layout { height: 100vh; display: flex; flex-direction: column; background: #f5f7fa; }
.topbar {
  height: 56px; flex-shrink: 0; display: flex; align-items: center; gap: 24px;
  padding: 0 24px; background: #1d1e22; color: #e5eaf3;
}
.brand { font-weight: bold; font-size: 15px; white-space: nowrap; }
.nav { display: flex; gap: 4px; flex: 1; }
.nav-item {
  padding: 6px 14px; border-radius: 6px; color: #cfd3dc;
  text-decoration: none; font-size: 14px; display: flex; align-items: center; gap: 5px;
}
.nav-item:hover { background: #2a2b30; color: #fff; }
.nav-item.active { background: #409eff; color: #fff; }
.nav-icon { font-size: 13px; }
.user-box { display: flex; align-items: center; gap: 8px; }
.username { font-size: 13px; color: #cfd3dc; }
.content { flex: 1; overflow-y: auto; }
</style>
