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
/* 拟物：内容区是纸面，顶栏是一条皮革腰带，导航项是缝在带上的小皮牌 */
.layout {
  height: 100vh; display: flex; flex-direction: column;
  background: linear-gradient(180deg, var(--sk-bg-from), var(--sk-bg-to)) fixed;
}
.topbar {
  height: 56px; flex-shrink: 0; display: flex; align-items: center; gap: 24px;
  padding: 0 24px;
  background-image: var(--sk-noise), linear-gradient(180deg, #8b7355 0%, #6b5b45 100%);
  border-bottom: 2px solid #4a3f30;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.25);
}
/* 皮革缝线 */
.topbar::after {
  content: ""; position: absolute; left: 0; right: 0; top: 50px; height: 0;
  border-top: 1px dashed rgba(233, 221, 196, 0.35);
  pointer-events: none;
}
.topbar { position: relative; }
/* 黄铜铭牌 */
.brand {
  font-weight: bold; font-size: 14px; white-space: nowrap;
  color: #3a2f22; padding: 5px 14px; border-radius: 8px;
  background-image: var(--sk-noise), linear-gradient(180deg, #e3d3a8, #b89f6e);
  border: 1px solid #8a744c;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.4);
}
.nav { display: flex; gap: 6px; flex: 1; }
.nav-item {
  padding: 6px 14px; border-radius: 8px; color: #efe6d4;
  text-decoration: none; font-size: 14px; display: flex; align-items: center; gap: 5px;
  border: 1px solid rgba(74, 63, 48, 0.8);
  background-image: var(--sk-noise), linear-gradient(180deg, #7c684c, #66563f);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.18);
  transition: all 0.2s ease-out;
}
.nav-item:hover {
  color: #fff; transform: translateY(-1px);
  background-image: var(--sk-noise), linear-gradient(180deg, #8a745a, #71614a);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.22);
}
/* 激活项：黄铜牌按下嵌入皮带 */
.nav-item.active {
  color: #3a2f22; font-weight: 700; text-shadow: 0 1px 0 rgba(255, 255, 255, 0.4);
  background-image: var(--sk-noise), linear-gradient(180deg, #e3d3a8, #c2a878);
  border-color: #8a744c;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2), inset 0 -1px 0 rgba(255, 255, 255, 0.3);
  transform: translateY(1px);
}
.nav-icon { font-size: 13px; }
.user-box { display: flex; align-items: center; gap: 8px; }
.username { font-size: 13px; color: #efe6d4; text-shadow: 0 1px 0 rgba(0, 0, 0, 0.3); }
.user-box :deep(.el-button.is-text) { color: #e3d3a8; }
.user-box :deep(.el-button.is-text:hover) { color: #fff; background-color: rgba(0, 0, 0, 0.2); }
.content { flex: 1; overflow-y: auto; }
</style>
