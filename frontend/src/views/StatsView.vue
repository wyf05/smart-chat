<script setup>
// 数据统计页：工具调用分布 / 意图路由占比 / 近7日消息量 / 延迟概览（ECharts）
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getStatsOverview } from '../api/index.js'

const s = ref(null)

function initCharts(data) {
  // 工具调用分布（柱状图）
  const toolEl = document.getElementById('chart-tools')
  const tools = Object.entries(data.tool_counter || {})
  echarts.init(toolEl).setOption({
    title: { text: '工具调用分布', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {},
    grid: { left: 40, right: 20, bottom: 30, top: 40 },
    xAxis: { type: 'category', data: tools.map(([k]) => k) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: 'bar', data: tools.map(([, v]) => v), itemStyle: { color: '#409eff' } }],
  })

  // 意图路由占比（饼图）
  const routeEl = document.getElementById('chart-route')
  const rc = data.route_counter || { chat: 0, agent: 0 }
  echarts.init(routeEl).setOption({
    title: { text: '意图路由占比', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: ['38%', '65%'],
      data: [{ name: '普通对话 chat', value: rc.chat || 0 },
             { name: '智能体 agent', value: rc.agent || 0 }],
      label: { formatter: '{b}: {c}' },
    }],
  })

  // 近 7 日消息量（折线图）
  const dailyEl = document.getElementById('chart-daily')
  echarts.init(dailyEl).setOption({
    title: { text: '近 7 日用户消息量', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, bottom: 30, top: 40 },
    xAxis: { type: 'category', data: data.daily.days },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: 'line', data: data.daily.counts, smooth: true,
               areaStyle: { opacity: 0.15 }, itemStyle: { color: '#67c23a' } }],
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
.page-title { margin: 0 0 6px; }
.page-desc { color: #909399; font-size: 13px; margin: 0 0 16px; }
.kpi-row { display: flex; gap: 16px; margin-bottom: 20px; }
.kpi {
  flex: 1; background: #fff; border-radius: 10px; padding: 14px; text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); font-size: 13px; color: #909399;
}
.kpi b { display: block; font-size: 24px; color: #409eff; margin-top: 4px; }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.chart {
  background: #fff; border-radius: 10px; height: 300px; margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.chart-wide { width: 100%; }
</style>
