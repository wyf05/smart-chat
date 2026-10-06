<script setup>
// 数据统计页：工具调用分布 / 意图路由占比 / 近7日消息量 / 延迟概览（ECharts）
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getStatsOverview } from '../api/index.js'

const s = ref(null)

function initCharts(data) {
  // 拟物 v2 配色（showcase 色板）：光泽蓝 / 皮革棕 / 黄铜金，墨色文字
  const INK = '#3d2010'
  const BODY = '#6b4f35'
  const titleStyle = { fontSize: 14, color: INK, fontWeight: 'bold', fontFamily: '"Playfair Display", Georgia, "STZhongsong", "SimSun", serif' }

  // 工具调用分布（柱状图，光泽蓝三段渐变）
  const toolEl = document.getElementById('chart-tools')
  const tools = Object.entries(data.tool_counter || {})
  echarts.init(toolEl).setOption({
    title: { text: '工具调用分布', left: 'center', textStyle: titleStyle },
    tooltip: {},
    grid: { left: 40, right: 20, bottom: 30, top: 40 },
    xAxis: { type: 'category', data: tools.map(([k]) => k), axisLabel: { color: BODY } },
    yAxis: { type: 'value', minInterval: 1, axisLabel: { color: BODY } },
    series: [{
      type: 'bar', data: tools.map(([, v]) => v), barMaxWidth: 46,
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        // 顶部受光的光泽柱体
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#5b9bd5' }, { offset: 0.5, color: '#3a7fc1' }, { offset: 1, color: '#2860a0' },
        ]),
      },
    }],
  })

  // 意图路由占比（饼图：皮革 + 黄铜）
  const routeEl = document.getElementById('chart-route')
  const rc = data.route_counter || { chat: 0, agent: 0 }
  echarts.init(routeEl).setOption({
    title: { text: '意图路由占比', left: 'center', textStyle: titleStyle },
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: ['38%', '65%'],
      data: [{ name: '普通对话 chat', value: rc.chat || 0, itemStyle: { color: '#8b7355' } },
             { name: '智能体 agent', value: rc.agent || 0, itemStyle: { color: '#c9a227' } }],
      label: { formatter: '{b}: {c}', color: BODY },
    }],
  })

  // 近 7 日消息量（折线图，黄铜金）
  const dailyEl = document.getElementById('chart-daily')
  echarts.init(dailyEl).setOption({
    title: { text: '近 7 日用户消息量', left: 'center', textStyle: titleStyle },
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, bottom: 30, top: 40 },
    xAxis: { type: 'category', data: data.daily.days, axisLabel: { color: BODY } },
    yAxis: { type: 'value', minInterval: 1, axisLabel: { color: BODY } },
    series: [{ type: 'line', data: data.daily.counts, smooth: true,
               lineStyle: { color: '#a07818', width: 3 },
               areaStyle: { opacity: 0.25, color: '#c9a227' }, itemStyle: { color: '#a07818' } }],
  })
}

onMounted(async () => {
  try {
    const res = await getStatsOverview()
    s.value = res.data
    setTimeout(() => initCharts(res.data), 50)   // 等 DOM 渲染完成
  } catch (e) {
    console.error('加载统计失败', e)
  }
})
</script>

<template>
  <div class="page">
    <h2 class="page-title">📊 数据统计</h2>
    <p class="page-desc">每次对话自动记录路由链路、工具调用与耗时，本页数据全部来自真实埋点（chat_messages 表）。</p>

    <div v-if="s" class="kpi-row">
      <div class="kpi">会话总数<b>{{ s.total_sessions }}</b></div>
      <div class="kpi">用户消息<b>{{ s.total_messages }}</b></div>
      <div class="kpi">工具调用<b>{{ s.tool_calls_total }}</b></div>
      <div class="kpi">平均耗时<b>{{ (s.avg_duration_ms / 1000).toFixed(1) }}s</b></div>
    </div>

    <div class="chart-grid">
      <div id="chart-tools" class="chart"></div>
      <div id="chart-route" class="chart"></div>
    </div>
    <div id="chart-daily" class="chart chart-wide"></div>

    <el-empty v-if="s && s.total_messages === 0" description="还没有对话数据，去「智能对话」聊几句再回来看图表" />
  </div>
</template>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 28px 24px; }
.page-title {
  font-family: var(--sk-font-display);
  font-weight: 900; font-size: 24px;
  margin: 0 0 8px; color: var(--sk-ink);
  text-shadow: 0 2px 0 rgba(255, 255, 255, 0.45), 0 4px 12px rgba(0, 0, 0, 0.12);
}
.page-desc { color: var(--sk-body); font-size: 13px; margin: 0 0 16px; text-shadow: 0 1px 0 rgba(255, 255, 255, 0.4); }
.kpi-row { display: flex; gap: 20px; margin-bottom: 20px; }
.kpi {
  flex: 1; border-radius: 12px; padding: 14px; text-align: center;
  background-image: var(--sk-weave), linear-gradient(180deg, var(--sk-paper-hi), var(--sk-paper-lo));
  border: 1px solid var(--sk-paper-border);
  box-shadow: var(--sk-shadow-card);
  font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.12em;
  color: var(--sk-label);
}
.kpi b {
  display: block; font-family: var(--sk-font-display);
  font-size: 25px; font-weight: 900; color: var(--sk-ink); margin-top: 5px;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.55);
}
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.chart {
  border-radius: 12px; height: 300px; margin-bottom: 20px;
  background-image: var(--sk-weave), linear-gradient(180deg, var(--sk-paper-hi), var(--sk-paper-lo));
  border: 1px solid var(--sk-paper-border);
  box-shadow: var(--sk-shadow-card);
}
.chart-wide { width: 100%; }
</style>
