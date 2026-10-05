<script setup>
// 智能知识库：FAQ 条目管理 + 知识库检索工具的数据源
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Search } from '@element-plus/icons-vue'
import { listKnowledge, addKnowledge, updateKnowledge, deleteKnowledge } from '../api/index.js'

const router = useRouter()
const items = ref([])
const dialog = ref(false)
const form = ref({})
const testQ = ref('')
const testA = ref('')
const testing = ref(false)

async function load() {
  const res = await listKnowledge()
  items.value = res.data
}

function openAdd() {
  form.value = { id: null, question: '', answer: '', keywords: '' }
  dialog.value = true
}

function openEdit(row) {
  form.value = { ...row }
  dialog.value = true
}

async function submit() {
  const f = form.value
  if (!f.question || !f.answer) {
    ElMessage.warning('问题和答案不能为空')
    return
  }
  if (f.id) {
    await updateKnowledge(f.id, { question: f.question, answer: f.answer, keywords: f.keywords })
  } else {
    await addKnowledge({ question: f.question, answer: f.answer, keywords: f.keywords })
  }
  dialog.value = false
  await load()
  ElMessage.success('已保存，智能体现在可以检索到这条知识')
}

async function remove(row) {
  try { await ElMessageBox.confirm(`确定删除「${row.question}」？`, '提示', { type: 'warning' }) } catch { return }
  await deleteKnowledge(row.id)
  await load()
  ElMessage.success('已删除')
}

async function testSearch() {
  if (!testQ.value.trim()) { ElMessage.warning('请输入要测试的问题'); return }
  testing.value = true
  testA.value = ''
  try {
    // 直接通过智能体验证检索效果
    const { sendAgentChat } = await import('../api/index.js')
    const res = await sendAgentChat(testQ.value, 'knowledge-test-' + Date.now())
    testA.value = (res.data.data.tools_used || []).includes('search_knowledge')
      ? res.data.data.reply
      : '（智能体未调用知识库工具，换个问法试试，例如"你们的退货政策是什么"）'
  } finally {
    testing.value = false
  }
}

function askAgent() {
  router.push({ name: 'chat', query: { ask: testQ.value, agent: '1' } })
}

onMounted(load)
</script>

<template>
  <div class="page">
    <h2 class="page-title">📚 智能知识库</h2>
    <p class="page-desc">
      这里维护的 FAQ 是智能体第 6 个工具 <code>search_knowledge</code> 的数据源：
      智能体回答售后政策类问题会自动检索本库并注明"来自知识库"。
    </p>

    <!-- 检索效果测试 -->
    <div class="test-box">
      <el-input v-model="testQ" placeholder="输入一个问题测试知识库检索效果，如：你们的退货政策是什么？"
                class="test-input" @keyup.enter="testSearch" />
      <el-button type="primary" :icon="Search" :loading="testing" @click="testSearch">测试检索</el-button>
      <el-button @click="askAgent">去对话页提问</el-button>
    </div>
    <el-alert v-if="testA" :title="testA" type="success" :closable="false" class="test-result" />

    <div class="toolbar">
      <el-button type="primary" :icon="Plus" @click="openAdd">新增知识条目</el-button>
    </div>
    <el-table :data="items" border>
      <el-table-column prop="question" label="问题" width="240" />
      <el-table-column prop="answer" label="标准答案" min-width="280" />
      <el-table-column prop="keywords" label="检索关键词" width="180" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" :icon="Delete" @click="remove(row)" />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" :title="form.id ? '编辑知识条目' : '新增知识条目'" width="560px">
      <el-form label-width="90px">
        <el-form-item label="问题"><el-input v-model="form.question" placeholder="如：退货政策是什么？" /></el-form-item>
        <el-form-item label="标准答案">
          <el-input v-model="form.answer" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="form.keywords" placeholder="逗号分隔，如：退货,退款,售后" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 28px 24px; }
.page-title { margin: 0 0 6px; }
.page-desc { color: #909399; font-size: 13px; margin: 0 0 16px; }
.page-desc code { background: #eef1f6; padding: 1px 6px; border-radius: 4px; }
.test-box { display: flex; gap: 10px; margin-bottom: 12px; }
.test-input { flex: 1; }
.test-result { margin-bottom: 16px; white-space: pre-wrap; }
.toolbar { margin: 4px 0 12px; }
</style>
