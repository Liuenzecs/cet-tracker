<template>
  <div class="page-container">
    <PageHeader title="词汇笔记" description="管理和复习你的词汇笔记">
      <template #actions>
        <el-button type="primary" @click="router.push('/vocabulary/import')">
          <el-icon><Plus /></el-icon>
          导入笔记
        </el-button>
      </template>
    </PageHeader>

    <div v-if="loading" v-loading="true" style="min-height: 300px" />

    <template v-else-if="notes.length > 0">
      <div class="notes-grid">
        <div
          v-for="note in notes"
          :key="note.id"
          class="note-card"
          @click="router.push(`/vocabulary/${note.id}`)"
        >
          <div class="note-card-header">
            <h3 class="note-title">{{ note.title }}</h3>
            <span class="note-count">{{ note.entry_count ?? 0 }} 词</span>
          </div>
          <div class="note-tags">
            <StatusTag v-if="note.exam_type" type="exam_type" :value="note.exam_type" />
            <StatusTag type="source_section" :value="note.source_section" />
          </div>
          <div class="note-footer">
            <span class="note-date">{{ formatDate(note.created_at) }}</span>
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
          @current-change="fetchNotes"
        />
      </div>
    </template>

    <EmptyState
      v-else
      title="暂无词汇笔记"
      description="导入你的第一份词汇笔记，开始系统化地积累 CET 词汇"
      action-text="导入笔记"
      @action="router.push('/vocabulary/import')"
    >
      <template #icon>
        <el-icon :size="48" color="#D1D5DB"><Collection /></el-icon>
      </template>
    </EmptyState>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Collection, ArrowRight } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getVocabularyNotes } from '@/api/vocabulary'
import type { VocabularyNote } from '@/types'

const router = useRouter()
const loading = ref(true)
const notes = ref<VocabularyNote[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
}

async function fetchNotes() {
  loading.value = true
  try {
    const res = await getVocabularyNotes({ page: page.value, page_size: pageSize.value })
    notes.value = res.data?.items ?? []
    total.value = res.data?.total ?? 0
  } catch {
    ElMessage.error('加载词汇笔记失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchNotes)
</script>

<style scoped>
.notes-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-lg);
}

@media (max-width: 768px) {
  .notes-grid {
    grid-template-columns: 1fr;
  }
}

.note-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border);
  padding: var(--space-xl);
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.note-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-1px);
}

.note-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-md);
}

.note-title {
  font-size: var(--text-card-title);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.4;
  flex: 1;
}

.note-count {
  font-size: var(--text-caption);
  color: var(--color-primary);
  background: var(--color-primary-light);
  padding: 2px 10px;
  border-radius: 999px;
  font-weight: 600;
  white-space: nowrap;
}

.note-tags {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.note-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border-light);
}

.note-date {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
}

.pagination-row {
  display: flex;
  justify-content: center;
  margin-top: var(--space-xl);
}
</style>
