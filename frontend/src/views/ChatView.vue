<script setup>
// 智能对话页：侧边栏会话列表 + 聊天面板（从原主界面迁移为子页面）
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import SessionSidebar from '../components/SessionSidebar.vue'
import ChatPanel from '../components/ChatPanel.vue'
import { listSessions, createSession, deleteSession } from '../api/index.js'

const route = useRoute()
const sessions = ref([])              // 会话列表
const activeId = ref('')              // 当前激活会话ID

onMounted(async () => {
  await refreshSessions()
  // 从其他页面带问题跳转过来且当前没有会话时，自动新建一个
  if (route.query.ask && sessions.value.length === 0) {
    await handleCreate()
    return
  }
  if (sessions.value.length > 0) {
    activeId.value = sessions.value[0].id   // 默认打开最近会话
  }
})

async function refreshSessions() {
  const res = await listSessions()
  sessions.value = res.data
}

async function handleCreate() {
  const res = await createSession()
  await refreshSessions()
  activeId.value = res.data.id      // 新建后直接切换过去
}

function handleSelect(id) {
  activeId.value = id
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('删除后聊天记录不可恢复，确定删除？', '提示', { type: 'warning' })
  } catch { return }   // 用户点了取消
  await deleteSession(id)
  await refreshSessions()
  if (activeId.value === id) {
    activeId.value = sessions.value.length > 0 ? sessions.value[0].id : ''
  }
  ElMessage.success('已删除')
}
</script>

<template>
  <div class="chat-layout">
    <SessionSidebar
      :sessions="sessions"
      :active-id="activeId"
      @select="handleSelect"
      @create="handleCreate"
      @delete="handleDelete"
    />
    <ChatPanel v-if="activeId" :key="activeId" :session-id="activeId" />
    <div v-else class="no-session">
      <div>点击左上角「新对话」开始使用</div>
    </div>
  </div>
</template>

<style scoped>
.chat-layout {
  display: flex; height: calc(100vh - 56px);
  background: linear-gradient(180deg, var(--sk-bg-from), var(--sk-bg-to));
}
.no-session {
  flex: 1; display: flex; align-items: center; justify-content: center;
  color: var(--sk-ink-2); font-size: 15px;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5);
}
</style>
