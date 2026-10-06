<script setup>
import { Plus, Delete } from '@element-plus/icons-vue'

// props：父组件传进来的数据；emit：向父组件发事件
defineProps({
  sessions: { type: Array, default: () => [] },
  activeId: { type: String, default: '' },
})
const emit = defineEmits(['select', 'create', 'delete'])
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <span class="logo">🛍️ 店小智</span>
      <el-button type="primary" size="small" :icon="Plus" @click="emit('create')">
        新对话
      </el-button>
    </div>

    <div class="session-list">
      <div
        v-for="s in sessions"
        :key="s.id"
        class="session-item"
        :class="{ active: s.id === activeId }"
        @click="emit('select', s.id)"
      >
        <span class="session-title">{{ s.title }}</span>
        <el-icon class="delete-icon" @click.stop="emit('delete', s.id)">
          <Delete />
        </el-icon>
      </div>
      <div v-if="sessions.length === 0" class="empty-tip">暂无会话</div>
    </div>

    <div class="sidebar-footer">店小智 SmartService v2.0</div>
  </aside>
</template>

<style scoped>
/* 拟物 v2：纸面侧栏（织纹），会话项是纸片，激活项是皮革铭牌 */
.sidebar {
  width: 240px; flex-shrink: 0;
  display: flex; flex-direction: column;
  background-image: var(--sk-weave), linear-gradient(180deg, #f2ecd8 0%, #e4dabc 100%);
  border-right: 1px solid var(--sk-nav-border);
  box-shadow: inset -2px 0 4px rgba(0, 0, 0, 0.06);
  color: var(--sk-ink);
}
.sidebar-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 12px;
  border-bottom: 1px solid var(--sk-nav-border);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.6);
}
.logo { font-weight: bold; font-size: 15px; color: var(--sk-leather-deep); text-shadow: 0 1px 0 rgba(255, 255, 255, 0.55); }
.session-list { flex: 1; overflow-y: auto; padding: 8px; }
.session-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 12px; margin-bottom: 6px; border-radius: 8px;
  cursor: pointer; font-size: 13px; color: var(--sk-body);
  background-image: linear-gradient(180deg, var(--sk-paper-hi), #eee6ce);
  border: 1px solid rgba(0, 0, 0, 0.15);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.7);
  transition: all 0.15s ease-out;
}
.session-item:hover { transform: translateY(-1px); box-shadow: 0 4px 8px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.7); }
/* 激活会话：皮革铭牌 */
.session-item.active {
  color: #f5f0e8; font-weight: 600;
  background-image: linear-gradient(180deg, var(--sk-leather-hi), var(--sk-leather-lo));
  border-color: var(--sk-leather-border);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2), inset 0 -1px 0 rgba(255, 255, 255, 0.15);
  transform: translateY(1px);
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.3);
}
.session-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.delete-icon { display: none; flex-shrink: 0; margin-left: 6px; }
.session-item:hover .delete-icon { display: block; }
.sidebar-footer {
  padding: 10px; text-align: center; font-size: 12px;
  color: var(--sk-label);
  border-top: 1px solid var(--sk-nav-border);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
}
</style>
