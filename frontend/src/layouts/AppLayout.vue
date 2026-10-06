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
      <div class="stitch stitch-top"></div>
      <div class="stitch stitch-bottom"></div>
      <div class="brand">
        <span class="brand-plate">🛍️</span>
        <span class="brand-name">店小智 · 智能客服工作台</span>
      </div>
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
/* 拟物 v2：浅米皮革导航条（showcase 配方）+ 缝线 + 金色药丸激活态 */
.layout {
  height: 100vh; display: flex; flex-direction: column;
  background: linear-gradient(180deg, #d4c4a8 0%, #c8b898 55%, #b8a888 100%) fixed;
}
.topbar {
  position: relative;
  height: 56px; flex-shrink: 0; display: flex; align-items: center; gap: 24px;
  padding: 0 24px;
  background-image: linear-gradient(180deg, var(--sk-nav-hi) 0%, var(--sk-nav-lo) 100%);
  border-bottom: 2px solid var(--sk-nav-border);
  box-shadow: var(--sk-shadow-nav);
}
/* 上下两道深色缝线 */
.stitch {
  position: absolute; left: 0; right: 0; height: 1px; pointer-events: none;
  background: var(--sk-stitch-dark);
}
.stitch-top { top: 6px; opacity: 0.6; }
.stitch-bottom { bottom: 6px; }
/* 品牌：方形铭牌 + 衬线字 */
.brand { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.brand-plate {
  width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;
  font-size: 16px; border-radius: 8px;
  background-image: linear-gradient(180deg, #e0d0b0, #c8b890);
  border: 1px solid #a09060;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.6);
}
.brand-name {
  font-family: var(--sk-font-display);
  font-weight: 700; font-size: 15px; color: var(--sk-leather-deep);
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.6);
}
.nav { display: flex; gap: 8px; flex: 1; }
.nav-item {
  padding: 6px 14px; border-radius: 999px; color: var(--sk-leather-deep);
  text-decoration: none; font-size: 14px; font-weight: 600;
  display: flex; align-items: center; gap: 5px;
  border: 1px solid transparent;
  transition: all 0.15s ease-out;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.45);
}
.nav-item:hover {
  color: var(--sk-ink);
  background: rgba(255, 255, 255, 0.35);
  border-color: rgba(176, 160, 128, 0.6);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.6);
}
/* 激活项：金色徽章药丸 */
.nav-item.active {
  color: #fff8e0;
  background-image: linear-gradient(180deg, var(--sk-gold) 0%, var(--sk-gold-deep) 100%);
  border-color: #806010;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.25), inset 0 -1px 0 rgba(0, 0, 0, 0.2);
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.35);
}
.nav-icon { font-size: 13px; }
.user-box { display: flex; align-items: center; gap: 8px; }
.username {
  font-size: 13px; font-weight: 600; color: var(--sk-leather-deep);
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5);
}
.user-box :deep(.el-button.is-text) { color: var(--sk-leather-deep); }
.user-box :deep(.el-button.is-text:hover) { color: var(--sk-ink); background-color: rgba(255, 255, 255, 0.4); }
.content { flex: 1; overflow-y: auto; }
</style>
