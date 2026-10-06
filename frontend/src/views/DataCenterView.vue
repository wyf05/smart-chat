<script setup>
// 业务数据中心：订单 / 优惠券 两个 Tab，数据实时同步给智能体工具
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { listOrders, saveOrder, deleteOrder, listCoupons, saveCoupon, deleteCoupon } from '../api/index.js'

const router = useRouter()
const tab = ref('orders')

// ===== 订单 =====
const orders = ref([])
const orderDialog = ref(false)
const orderForm = ref({})

async function loadOrders() {
  const res = await listOrders()
  orders.value = res.data
}

function openOrder(row) {
  orderForm.value = row ? { ...row, __edit: true } : { order_id: '', status: '待付款', amount: '', receiver: '', logistics: '' }
  orderDialog.value = true
}

async function submitOrder() {
  const f = orderForm.value
  if (!f.order_id || !f.amount || !f.receiver) {
    ElMessage.warning('订单号、金额、收件人不能为空')
    return
  }
  await saveOrder(f)
  orderDialog.value = false
  await loadOrders()
  ElMessage.success('已保存，智能体现在可以查到最新数据')
}

async function removeOrder(row) {
  try { await ElMessageBox.confirm(`确定删除订单 ${row.order_id}？`, '提示', { type: 'warning' }) } catch { return }
  await deleteOrder(row.order_id)
  await loadOrders()
  ElMessage.success('已删除')
}

function askAgent(text) {
  // 跳到聊天页并通过 query 参数预填问题；agent=1 自动开启智能体模式（需要工具查真实数据）
  router.push({ name: 'chat', query: { ask: text, agent: '1' } })
}

// ===== 优惠券 =====
const coupons = ref([])
const couponDialog = ref(false)
const couponForm = ref({})

async function loadCoupons() {
  const res = await listCoupons()
  coupons.value = res.data
}

function openCoupon(row) {
  couponForm.value = row ? { ...row } : { code: '', title: '', discount: '', valid_until: '', status: '可用' }
  couponDialog.value = true
}

async function submitCoupon() {
  const f = couponForm.value
  if (!f.code || !f.title || !f.discount) {
    ElMessage.warning('券码、名称、优惠说明不能为空')
    return
  }
  await saveCoupon(f)
  couponDialog.value = false
  await loadCoupons()
  ElMessage.success('已保存，智能体现在可以查到最新数据')
}

async function removeCoupon(row) {
  try { await ElMessageBox.confirm(`确定删除优惠券 ${row.code}？`, '提示', { type: 'warning' }) } catch { return }
  await deleteCoupon(row.code)
  await loadCoupons()
  ElMessage.success('已删除')
}

onMounted(() => { loadOrders(); loadCoupons() })
</script>

<template>
  <div class="page">
    <h2 class="page-title">📦 业务数据中心</h2>
    <p class="page-desc">这里的订单和优惠券就是智能体工具查询的数据源：修改数据后去「智能对话」提问，回答会实时变化。</p>

    <el-tabs v-model="tab">
      <el-tab-pane label="订单管理" name="orders">
        <div class="toolbar">
          <el-button type="primary" :icon="Plus" @click="openOrder(null)">新增订单</el-button>
        </div>
        <el-table :data="orders">
          <el-table-column prop="order_id" label="订单号" width="130" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="{ 待付款: 'warning', 打包中: 'info', 已发货: 'primary', 已签收: 'success' }[row.status]">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="金额（元）" width="110" />
          <el-table-column prop="receiver" label="收件人" width="110" />
          <el-table-column prop="logistics" label="物流信息" min-width="220" />
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="openOrder(row)">编辑</el-button>
              <el-button size="small" type="success"
                         @click="askAgent(`订单 ${row.order_id} 现在到哪了？`)">去咨询</el-button>
              <el-button size="small" type="danger" :icon="Delete" @click="removeOrder(row)" />
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="优惠券中心" name="coupons">
        <div class="toolbar">
          <el-button type="primary" :icon="Plus" @click="openCoupon(null)">新增优惠券</el-button>
        </div>
        <el-table :data="coupons">
          <el-table-column prop="code" label="券码" width="120" />
          <el-table-column prop="title" label="名称" width="150" />
          <el-table-column prop="discount" label="优惠说明" min-width="180" />
          <el-table-column prop="valid_until" label="有效期至" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="{ 可用: 'success', 已使用: 'info', 已过期: 'danger' }[row.status]">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="openCoupon(row)">编辑</el-button>
              <el-button size="small" type="success"
                         @click="askAgent(`优惠券 ${row.code} 还能用吗？`)">去咨询</el-button>
              <el-button size="small" type="danger" :icon="Delete" @click="removeCoupon(row)" />
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 订单编辑弹窗 -->
    <el-dialog v-model="orderDialog" :title="orderForm.__edit ? '编辑订单' : '新增订单'" width="480px">
      <el-form label-width="80px">
        <el-form-item label="订单号">
          <el-input v-model="orderForm.order_id" :disabled="!!orderForm.__edit" placeholder="如 DD20260005" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="orderForm.status">
            <el-option v-for="s in ['待付款', '打包中', '已发货', '已签收']" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额（元）"><el-input v-model="orderForm.amount" /></el-form-item>
        <el-form-item label="收件人"><el-input v-model="orderForm.receiver" /></el-form-item>
        <el-form-item label="物流信息"><el-input v-model="orderForm.logistics" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="orderDialog = false">取消</el-button>
        <el-button type="primary" @click="submitOrder">保存</el-button>
      </template>
    </el-dialog>

    <!-- 优惠券编辑弹窗 -->
    <el-dialog v-model="couponDialog" title="优惠券" width="480px">
      <el-form label-width="80px">
        <el-form-item label="券码"><el-input v-model="couponForm.code" placeholder="如 QUAN200" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="couponForm.title" /></el-form-item>
        <el-form-item label="优惠说明"><el-input v-model="couponForm.discount" /></el-form-item>
        <el-form-item label="有效期至"><el-input v-model="couponForm.valid_until" placeholder="如 2026-12-31" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="couponForm.status">
            <el-option v-for="s in ['可用', '已使用', '已过期']" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="couponDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCoupon">保存</el-button>
      </template>
    </el-dialog>
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
.toolbar { margin-bottom: 12px; display: flex; gap: 10px; }
</style>
