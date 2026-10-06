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
      <div class="hero-badge">企业级电商智能客服系统</div>
      <h1 class="hero-title">店小智为你服务 🛍️</h1>
      <p class="hero-sub">多轮对话 · 智能体工具调用 · 意图路由 · 知识库检索 · 数据看板</p>
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

    <section class="entry-panel">
      <div class="entry-stitch entry-stitch-top"></div>
      <div class="entry-stitch entry-stitch-bottom"></div>
      <div class="entry-grid">
        <router-link v-for="e in entries" :key="e.name" :to="{ name: e.name }" class="entry-card">
          <div class="entry-icon">{{ e.icon }}</div>
          <div class="entry-title">{{ e.title }}</div>
          <div class="entry-desc">{{ e.desc }}</div>
          <div class="entry-go">进入 →</div>
        </router-link>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* 拟物 v2 主页：标题区直接铺在亚麻底上整体居中（showcase hero 同款），
   入口卡片收进皮革面板，纸面统计卡居中衔接，整页撑满视口 */
.page {
  max-width: 1100px; margin: 0 auto; padding: 16px 24px 24px;
  min-height: calc(100vh - 56px); box-sizing: border-box;
  display: flex; flex-direction: column; justify-content: center;
}
.hero {
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  text-align: center; padding: 8px 12px 34px;
}
.hero-badge {
  display: inline-block; padding: 7px 24px; border-radius: 999px; margin-bottom: 18px;
  font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.16em;
  color: #fff8e0;
  background-image: linear-gradient(180deg, var(--sk-gold), var(--sk-gold-deep));
  border: 1px solid #806010;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.25), inset 0 -1px 0 rgba(0, 0, 0, 0.2);
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.35);
}
.hero-title {
  font-family: var(--sk-font-display);
  font-weight: 900; font-size: clamp(40px, 5.5vw, 62px); line-height: 1.1;
  margin: 0 0 14px; color: var(--sk-ink);
  text-shadow: 0 2px 0 rgba(255, 255, 255, 0.45), 0 4px 12px rgba(0, 0, 0, 0.2);
}
.hero-sub {
  font-size: 16px; margin: 0; max-width: 640px; line-height: 1.7; color: var(--sk-body);
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5);
}
.stat-row { display: flex; gap: 20px; margin-bottom: 24px; }
.stat-card {
  flex: 1; border-radius: 12px; padding: 18px; text-align: center;
  background-image: var(--sk-weave), linear-gradient(180deg, var(--sk-paper-hi), var(--sk-paper-lo));
  border: 1px solid var(--sk-paper-border);
  box-shadow: var(--sk-shadow-card);
}
.stat-num {
  font-family: var(--sk-font-display);
  font-size: 27px; font-weight: 900; color: var(--sk-ink);
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.55);
}
.stat-label {
  font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.12em;
  color: var(--sk-label); margin-top: 5px;
}
/* 入口皮革面板（showcase 按钮容器同款：缝线 + 织纹） */
.entry-panel {
  position: relative; padding: 20px; border-radius: 16px;
  background-image: var(--sk-weave), linear-gradient(180deg, #a0855e 0%, #7a6045 100%);
  border: 2px solid #6a5238;
  box-shadow: var(--sk-shadow-leather-panel);
}
.entry-stitch {
  position: absolute; left: 0; right: 0; height: 1px; pointer-events: none;
  background: var(--sk-stitch-h);
}
.entry-stitch-top { top: 8px; }
.entry-stitch-bottom { bottom: 8px; }
.entry-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.entry-card {
  background-image: var(--sk-weave), linear-gradient(180deg, var(--sk-paper-hi), var(--sk-paper-lo));
  border: 1px solid rgba(0, 0, 0, 0.2); border-radius: 12px; padding: 20px 16px;
  text-decoration: none; color: var(--sk-ink);
  box-shadow: var(--sk-shadow-chip);
  transition: all 0.2s ease-out;
  display: flex; flex-direction: column; gap: 8px;
}
.entry-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3), inset 0 -1px 0 rgba(0, 0, 0, 0.15);
}
.entry-card:active { transform: translateY(1px); box-shadow: var(--sk-press); }
.entry-icon { font-size: 30px; filter: drop-shadow(0 2px 2px rgba(0, 0, 0, 0.25)); }
.entry-title {
  font-family: var(--sk-font-display);
  font-size: 16px; font-weight: 900; color: var(--sk-ink);
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5);
}
.entry-desc { font-size: 12px; color: var(--sk-body); line-height: 1.6; flex: 1; }
.entry-go { font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.12em; color: var(--sk-gold-deep); }
</style>
