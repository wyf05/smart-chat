<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { sendChat, sendAgentChat, sendSmartChat, getMessages } from '../api/index.js'

const props = defineProps({ sessionId: { type: String, required: true } })
const route = useRoute()

const messages = ref([])       // [{role:'user'|'assistant', content:'...'}]
const inputText = ref('')
const loading = ref(false)
const mode = ref('chat')       // 对话模式：chat=普通对话 / auto=自动路由（意图识别） / agent=智能体
const streamMode = ref(true)   // 流式输出开关，默认开启（三挡均支持流式）
const streaming = ref(false)   // 流式回复进行中（占位气泡已推入，不再显示独立思考气泡）
const msgListRef = ref(null)

// 挡位与流式开关持久化：刷新 / 重新登录后不再跳回默认值
const MODE_KEY = 'dxz_mode'
const STREAM_KEY = 'dxz_stream'
mode.value = localStorage.getItem(MODE_KEY) || 'chat'
streamMode.value = localStorage.getItem(STREAM_KEY) !== '0'
watch(mode, v => localStorage.setItem(MODE_KEY, v))
watch(streamMode, v => localStorage.setItem(STREAM_KEY, v ? '1' : '0'))

// 头部标题随模式切换
const modeTitle = computed(() => ({
  chat: '普通对话模式',
  auto: '自动路由模式（意图识别，自动分流普通对话/智能体）',
  agent: '智能体模式（可查订单/天气/计算/时间/优惠券）',
}[mode.value]))

onMounted(async () => {
  await loadHistory()
  // 支持从其他页面（业务数据/知识库）带问题跳转过来，自动开启智能体并提问
  if (route.query.ask) {
    inputText.value = String(route.query.ask)
    if (route.query.agent === '1') mode.value = 'agent'
    const text = inputText.value
    inputText.value = ''
    await handleSendText(text)
  }
})

async function loadHistory() {
  try {
    const res = await getMessages(props.sessionId)
    messages.value = res.data.map(m => ({ role: m.role, content: m.content }))
  } catch (e) {
    console.error('加载历史失败', e)
  }
  scrollToBottom()
}

async function handleSendText(text) {
  if (loading.value) return
  messages.value.push({ role: 'user', content: text })
  scrollToBottom()
  loading.value = true
  try {
    // 三挡均支持流式；流式关闭时走请求-响应
    if (streamMode.value) {
      const url = mode.value === 'agent' ? '/api/agent/chat/stream'
                : mode.value === 'auto' ? '/api/smart/chat/stream'
                : '/api/chat/stream'
      await handleSSE(url, text)
      return
    }
    const res = mode.value === 'agent'
      ? await sendAgentChat(text, props.sessionId)
      : mode.value === 'auto'
        ? await sendSmartChat(text, props.sessionId)
        : await sendChat(text, props.sessionId)
    if (res.data.code === 0) {
      let replyText = res.data.data.reply
      const tools = res.data.data.tools_used || []
      if (tools.length > 0) {
        replyText = `🔧 本轮调用了工具：${tools.join('、')}\n\n` + replyText
      }
      messages.value.push({ role: 'assistant', content: replyText })
    } else {
      ElMessage.error(res.data.message || '服务异常，请稍后再试')
    }
  } catch (err) {
    ElMessage.error('无法连接后端服务，请检查 8000 端口是否启动')
    console.error(err)
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text) { ElMessage.warning('请输入内容再发送'); return }
  inputText.value = ''
  await handleSendText(text)
}

// 通用 SSE 读取：POST + ReadableStream（浏览器原生 EventSource 只支持 GET）
// 事件协议：{type:'route',route} 自动挡路由结果 | {type:'tool',name} 工具调用 |
//          {type:'delta',text} 正文增量 | {type:'error',message}；兼容旧协议 {delta}
async function handleSSE(url, text) {
  streaming.value = true
  messages.value.push({ role: 'assistant', content: '' })
  const idx = messages.value.length - 1

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('dxz_token') || ''}`,  // SSE 也要带 JWT
      },
      body: JSON.stringify({ message: text, session_id: props.sessionId }),
    })
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    const tools = []

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      for (const line of decoder.decode(value).split('\n\n')) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6)
        if (payload === '[DONE]') continue
        let obj
        try { obj = JSON.parse(payload) } catch (e) { continue }   // 忽略半截包
        if (obj.type === 'route') {
          messages.value[idx].content = `🧭 意图路由 → ${obj.route === 'agent' ? '智能体' : '普通对话'}\n\n`
        } else if (obj.type === 'tool') {
          if (!tools.includes(obj.name)) tools.push(obj.name)
          messages.value[idx].content = `🔧 本轮调用了工具：${tools.join('、')}\n\n`
        } else if (obj.type === 'delta') {
          let t = obj.text
          if (messages.value[idx].content.endsWith('\n\n')) t = t.replace(/^\n+/, '')   // 去掉工具前缀后模型开头的空行
          messages.value[idx].content += t
        } else if (obj.type === 'error') {
          ElMessage.error(obj.message || '服务异常，请稍后再试')
        } else if (obj.delta) {
          messages.value[idx].content += obj.delta
        }
        scrollToBottom()
      }
    }
  } finally {
    streaming.value = false
  }
}

async function scrollToBottom() {
  await nextTick()   // 等 Vue 把新消息渲染到页面后再滚动
  if (msgListRef.value) msgListRef.value.scrollTop = msgListRef.value.scrollHeight
}
</script>

<template>
  <div class="chat-panel">
    <div class="chat-header">
      <span class="title">{{ modeTitle }}</span>
      <span class="header-right">
        <span class="agent-toggle">
          <el-switch v-model="streamMode" />
          <span class="agent-label">流式输出</span>
        </span>
        <span class="agent-toggle">
          <el-radio-group v-model="mode" size="small">
            <el-radio-button value="chat">普通</el-radio-button>
            <el-radio-button value="auto">自动</el-radio-button>
            <el-radio-button value="agent">智能体</el-radio-button>
          </el-radio-group>
        </span>
      </span>
    </div>

    <div class="chat-body" ref="msgListRef">
      <div v-for="(msg, index) in messages" :key="index" class="msg-row" :class="msg.role">
        <div class="avatar">{{ msg.role === 'user' ? '🧑' : '🛍️' }}</div>
        <div class="bubble">
          <!-- 流式占位气泡在首字到达前原地显示思考态，避免与独立思考气泡重复 -->
          <template v-if="streaming && !msg.content && index === messages.length - 1">
            <el-icon class="is-loading"><Loading /></el-icon> 正在思考...
          </template>
          <template v-else>{{ msg.content }}</template>
        </div>
      </div>

      <div v-if="loading && !streaming" class="msg-row assistant">
        <div class="avatar">🛍️</div>
        <div class="bubble loading-bubble">
          <el-icon class="is-loading"><Loading /></el-icon> 正在思考...
        </div>
      </div>
    </div>

    <div class="chat-footer">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入消息，Enter 发送，Shift+Enter 换行"
        @keydown.enter.exact.prevent="handleSend"
      />
      <el-button type="primary" :loading="loading" :disabled="loading"
                 @click="handleSend" class="send-btn">发送</el-button>
    </div>
  </div>
</template>

<style scoped>
/* 拟物 v2：纸面聊天区；助手气泡=纸片，用户气泡=蓝色光泽块 */
.chat-panel {
  flex: 1; display: flex; flex-direction: column; min-width: 0;
  background: linear-gradient(180deg, #d4c4a8 0%, #c8b898 55%, #b8a888 100%);
}
.chat-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 20px;
  background-image: linear-gradient(180deg, var(--sk-nav-hi), var(--sk-nav-lo));
  border-bottom: 2px solid var(--sk-nav-border);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.7);
}
.chat-header .title {
  font-size: 14px; color: var(--sk-leather-deep); font-weight: 700;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.55);
}
.header-right { display: flex; align-items: center; gap: 16px; }
.agent-toggle { display: flex; align-items: center; gap: 6px; }
.agent-label { font-size: 13px; color: var(--sk-leather-deep); font-weight: 600; text-shadow: 0 1px 0 rgba(255, 255, 255, 0.45); }
.chat-body { flex: 1; overflow-y: auto; padding: 20px; }
.msg-row { display: flex; margin-bottom: 16px; align-items: flex-start; }
.msg-row.user { flex-direction: row-reverse; }
.avatar { font-size: 28px; margin: 0 10px; flex-shrink: 0; filter: drop-shadow(0 2px 2px rgba(0, 0, 0, 0.2)); }
.bubble {
  max-width: 70%; padding: 10px 14px; border-radius: 10px;
  line-height: 1.6; white-space: pre-wrap; word-break: break-word;
  color: var(--sk-ink);
}
/* 助手：纸片 */
.msg-row.assistant .bubble {
  background-image: linear-gradient(180deg, var(--sk-paper-hi), var(--sk-paper-lo));
  border: 1px solid var(--sk-paper-border);
  border-top-left-radius: 2px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.8);
}
/* 用户：蓝色光泽块（与主按钮同款材质） */
.msg-row.user .bubble {
  color: #fff;
  background-image: linear-gradient(180deg, var(--sk-blue-hi) 0%, var(--sk-blue-mid) 50%, var(--sk-blue-lo) 100%);
  border: 1px solid var(--sk-blue-border);
  border-top-right-radius: 2px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3), inset 0 -1px 0 rgba(0, 0, 0, 0.2);
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.3);
}
.loading-bubble { color: var(--sk-label); }
.chat-footer {
  display: flex; gap: 10px; padding: 12px 20px;
  background-image: linear-gradient(180deg, var(--sk-nav-hi), var(--sk-nav-lo));
  border-top: 2px solid var(--sk-nav-border);
  box-shadow: 0 -3px 8px rgba(0, 0, 0, 0.12);
}
.chat-footer .el-textarea { flex: 1; }
.send-btn { height: auto; }
</style>
