import { createRouter, createWebHashHistory } from 'vue-router'

// 路由守卫依赖的登录态存放在 localStorage
import AppLayout from '../layouts/AppLayout.vue'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', name: 'home', component: () => import('../views/DashboardView.vue') },
      { path: 'chat', name: 'chat', component: () => import('../views/ChatView.vue') },
      { path: 'data', name: 'data', component: () => import('../views/DataCenterView.vue') },
      { path: 'knowledge', name: 'knowledge', component: () => import('../views/KnowledgeView.vue') },
      { path: 'stats', name: 'stats', component: () => import('../views/StatsView.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// 全局守卫：未登录一律跳转登录页
router.beforeEach((to) => {
  const token = localStorage.getItem('dxz_token')
  if (to.name !== 'login' && !token) return { name: 'login' }
  if (to.name === 'login' && token) return { name: 'home' }
  return true
})

export default router
