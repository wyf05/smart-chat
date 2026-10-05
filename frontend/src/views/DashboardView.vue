<script setup>
// 首页仪表盘：核心指标 + 各子页面入口卡片
import { ref, onMounted } from 'vue'
import { getStatsOverview } from '../api/index.js'

const stats = ref(null)

const entries = [
  { name: 'chat', icon: '💬', title: '智能对话', desc: '多轮对话 / 智能体工具调用 / 流式输出，支持意图路由自动分流' },
  { name: 'data', icon: '📦', title: '业务数据中心', desc: '订单与优惠券管理，数据实时同步给智能体工具查询' },
  { name: 'knowledge', icon: '📚', title: '智能知识库', desc: '维护店铺 FAQ，智能体自动检索并引用知识库回答' },
  { name: 'stats', icon: '📊', title: '数据统计', desc: '工具调用分布、意图路由占比、响应耗时等可视化看板' },
]

onMounted(async () => {
  try {
    const res = await getStatsOverview()
    stats.value = res.data
  } catch (e) {
    console.error('加载统计失败', e)
  }
})
</script>

<template>
  <div class="page">
    <section class="hero">
      <h1>欢迎回来，店小智为你服务 🛍️</h1>
      <p>企业级电商智能客服系统：多轮对话 · 智能体工具调用 · 意图路由 · 知识库检索 · 数据看板</p>
    </section>

    <section v-if="stats" class="stat-row">
      <div class="stat-card">
        <div class="stat-num">{{ stats.total_sessions }}</div>
        <div class="stat-label">会话总数</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{{ stats.total_messages }}</div>
        <div class="stat-label">用户消息数</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{{ stats.tool_calls_total }}</div>
        <div class="stat-label">工具调用次数</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{{ (stats.avg_duration_ms / 1000).toFixed(1) }}s</div>
        <div class="stat-label">平均响应耗时</div>
      </div>
    </section>

    <section class="entry-grid">
      <router-link v-for="e in entries" :key="e.name" :to="{ name: e.name }" class="entry-card">
        <div class="entry-icon">{{ e.icon }}</div>
        <div class="entry-title">{{ e.title }}</div>
        <div class="entry-desc">{{ e.desc }}</div>
        <div class="entry-go">进入 →</div>
      </router-link>
    </section>
  </div>
</template>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 28px 24px; }
.hero h1 { font-size: 24px; margin: 0 0 8px; }
.hero p { color: #909399; font-size: 14px; margin: 0 0 24px; }
.stat-row { display: flex; gap: 16px; margin-bottom: 28px; }
.stat-card {
  flex: 1; background: #fff; border-radius: 10px; padding: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); text-align: center;
}
.stat-num { font-size: 26px; font-weight: bold; color: #409eff; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
.entry-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.entry-card {
  background: #fff; border-radius: 10px; padding: 22px 18px; text-decoration: none;
  color: inherit; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); transition: all 0.2s;
  display: flex; flex-direction: column; gap: 8px;
}
.entry-card:hover { transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1); }
.entry-icon { font-size: 30px; }
.entry-title { font-size: 16px; font-weight: bold; }
.entry-desc { font-size: 12px; color: #909399; line-height: 1.6; flex: 1; }
.entry-go { font-size: 13px; color: #409eff; }
</style>
