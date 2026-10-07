<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { sendChat, sendAgentChat, getMessages } from '../api/index.js'

const props = defineProps({ sessionId: { type: String, required: true } })
const route = useRoute()

const messages = ref([])       // [{role:'user'|'assistant', content:'...'}]
const inputText = ref('')
const loading = ref(false)
const agentMode = ref(false)   // 智能体模式开关
const streamMode = ref(true)   // 流式输出开关，默认开启
const streaming = ref(false)   // 流式回复进行中（占位气泡已推入，不再显示独立思考气泡）
const msgListRef = ref(null)

onMounted(async () => {
  await loadHistory()
  // 支持从其他页面（业务数据/知识库）带问题跳转过来，自动开启智能体并提问
  if (route.query.ask) {
    inputText.value = String(route.query.ask)
    if (route.query.agent === '1') agentMode.value = true
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
    if (streamMode.value && !agentMode.value) {
      await handleSendStream(text)
      return
    }
    const res = agentMode.value
      ? await sendAgentChat(text, props.sessionId)
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

// 流式发送：fetch 逐块读取 SSE
// 注意：浏览器原生 EventSource 只支持 GET，POST 流式要用 fetch + ReadableStream 手动读
async function handleSendStream(text) {
  streaming.value = true
  messages.value.push({ role: 'assistant', content: '' })
  const idx = messages.value.length - 1

  try {
    const res = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('dxz_token') || ''}`,  // SSE 也要带 JWT
      },
      body: JSON.stringify({ message: text, session_id: props.sessionId }),
    })
    const reader = res.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      for (const line of decoder.decode(value).split('\n\n')) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6)
        if (payload === '[DONE]') continue
        try { messages.value[idx].content += JSON.parse(payload).delta } catch (e) { /* 忽略半截包 */ }
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
      <span class="title">{{ agentMode ? '智能体模式（可查订单/天气/计算/时间/优惠券）' : '普通对话模式' }}</span>
      <span class="header-right">
        <span class="agent-toggle">
          <el-switch v-model="streamMode" />
          <span class="agent-label">流式输出</span>
        </span>
        <span class="agent-toggle">
          <el-switch v-model="agentMode" />
          <span class="agent-label">智能体模式</span>
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
