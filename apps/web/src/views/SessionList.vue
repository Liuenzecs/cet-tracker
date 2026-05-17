<template>
  <div class="page-container">
    <PageHeader title="训练记录" description="查看和管理所有备考训练记录">
      <template #actions>
        <el-button type="primary" @click="router.push('/sessions/new')">
          <el-icon><Plus /></el-icon>
          新增训练
        </el-button>
      </template>
    </PageHeader>

    <!-- Filters -->
    <div class="filter-bar">
      <el-select v-model="filterExamType" placeholder="考试类型" clearable style="width: 140px">
        <el-option label="CET4" value="CET4" />
        <el-option label="CET6" value="CET6" />
      </el-select>
      <el-select v-model="filterSessionType" placeholder="训练类型" clearable style="width: 140px">
        <el-option
          v-for="st in SESSION_TYPES"
          :key="st.value"
          :label="st.label"
          :value="st.value"
        />
      </el-select>
      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        small
        class="filter-pagination"
        @current-change="fetchSessions"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" v-loading="true" style="min-height: 300px" />

    <!-- Session cards -->
    <template v-else-if="sessions.length > 0">
      <div class="session-cards">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-card"
          @click="router.push(`/sessions/${session.id}`)"
        >
          <div class="sc-left">
            <div class="sc-paper-name">{{ session.paper_name }}</div>
            <div class="sc-meta">
              <StatusTag type="exam_type" :value="session.exam_type" />
              <StatusTag type="session_type" :value="session.session_type" />
              <span class="sc-date">{{ formatDate(session.date) }}</span>
            </div>
            <div v-if="session.note" class="sc-note">{{ session.note }}</div>
          </div>
          <div class="sc-right">
            <div class="sc-duration">{{ session.duration_minutes }} 分钟</div>
            <el-icon color="#9CA3AF"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <div class="pagination-row">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="fetchSessions"
        />
      </div>
    </template>

    <!-- Empty -->
    <EmptyState
      v-else
      title="暂无训练记录"
      description="开始记录你的每一次备考训练，追踪进步轨迹"
      action-text="新增训练"
      @action="router.push('/sessions/new')"
    >
      <template #icon>
        <el-icon :size="48" color="#D1D5DB"><Notebook /></el-icon>
      </template>
    </EmptyState>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, ArrowRight, Notebook } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getSessions } from '@/api/sessions'
import type { ExamSession } from '@/types'
import { SESSION_TYPES } from '@/types'

const router = useRouter()
const loading = ref(true)
const sessions = ref<ExamSession[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(15)
const filterExamType = ref('')
const filterSessionType = ref('')

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}/${m}/${day}`
}

async function fetchSessions() {
  loading.value = true
  try {
    const params: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (filterExamType.value) params.exam_type = filterExamType.value
    if (filterSessionType.value) params.session_type = filterSessionType.value
    const res = await getSessions(params)
    sessions.value = res.data.items ?? []
    total.value = res.data.total ?? 0
  } catch {
    ElMessage.error('加载训练记录失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchSessions()
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
  flex-wrap: wrap;
}

.filter-pagination {
  margin-left: auto;
}

.session-cards {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.session-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg) var(--space-xl);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all 0.15s ease;
}

.session-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-card-hover);
}

.sc-left {
  flex: 1;
  min-width: 0;
}

.sc-paper-name {
  font-size: var(--text-card-title);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
}

.sc-meta {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
  margin-bottom: var(--space-xs);
}

.sc-date {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
}

.sc-note {
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
  margin-top: var(--space-xs);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sc-right {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-shrink: 0;
  margin-left: var(--space-xl);
}

.sc-duration {
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.pagination-row {
  display: flex;
  justify-content: center;
  margin-top: var(--space-xl);
}
</style>
