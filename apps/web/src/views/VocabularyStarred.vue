<template>
  <div class="page-container">
    <PageHeader title="星标词汇" description="集中复习总是记不清的顽固词" />

    <div v-if="loading" v-loading="true" style="min-height: 300px" />

    <template v-else>
      <!-- Stats cards -->
      <div class="star-stats-row">
        <div class="star-stat-card all">
          <span class="ssc-value">{{ totalStarred }}</span>
          <span class="ssc-label">星标总数</span>
        </div>
        <div class="star-stat-card high">
          <span class="ssc-value">{{ highPriorityCount }}</span>
          <span class="ssc-label">高优先级</span>
        </div>
        <div class="star-stat-card due">
          <span class="ssc-value">{{ dashboardStats?.starred_due_today_count ?? 0 }}</span>
          <span class="ssc-label">今日待复习</span>
        </div>
        <div class="star-stat-card mastered">
          <span class="ssc-value">{{ masteredStarredCount }}</span>
          <span class="ssc-label">已掌握但仍标星</span>
        </div>
      </div>

      <!-- Toolbar -->
      <div class="star-toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索词汇..."
            clearable
            style="width: 220px"
            @input="onSearchInput"
            @clear="onSearchClear"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="familiarityFilter" placeholder="掌握状态" clearable style="width: 140px" @change="resetAndLoad">
            <el-option label="全部" value="" />
            <el-option v-for="(info, key) in FAMILIARITY_MAP" :key="key" :label="info.label" :value="key" />
          </el-select>
          <el-select v-model="priorityFilter" placeholder="优先级" clearable style="width: 120px" @change="resetAndLoad">
            <el-option label="全部" value="" />
            <el-option label="高" value="high" />
            <el-option label="普通" value="normal" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button type="warning" @click="router.push('/vocabulary/review?starred=true')">
            <el-icon><Reading /></el-icon>
            复习星标词汇
          </el-button>
        </div>
      </div>

      <!-- List -->
      <template v-if="entries.length > 0">
        <div class="starred-list">
          <div v-for="entry in entries" :key="entry.id" class="starred-card" :class="{ 'priority-high': entry.star_priority === 'high' }">
            <div class="sc-header">
              <div class="sc-term-row">
                <span class="sc-term" @click="router.push(`/vocabulary/${entry.note_id}`)">{{ entry.term }}</span>
                <span v-if="entry.uk_phonetic" class="sc-phonetic">UK {{ entry.uk_phonetic }}</span>
                <span v-if="entry.us_phonetic" class="sc-phonetic">US {{ entry.us_phonetic }}</span>
                <span v-else-if="!entry.uk_phonetic && entry.pronunciation_ipa" class="sc-phonetic">{{ entry.pronunciation_ipa }}</span>
              </div>
              <div class="sc-tags">
                <StatusTag type="familiarity" :value="entry.familiarity" />
                <el-tag v-if="entry.star_priority === 'high'" type="warning" size="small" effect="dark">高优先</el-tag>
              </div>
            </div>

            <div v-if="entry.star_note" class="sc-note">{{ entry.star_note }}</div>

            <div class="sc-meta">
              <span class="sc-meta-item">复习 {{ entry.review_count }} 次</span>
              <span v-if="entry.last_reviewed_at" class="sc-meta-item">上次 {{ formatDate(entry.last_reviewed_at) }}</span>
              <span v-if="entry.next_review_at" class="sc-meta-item">下次 {{ formatDate(entry.next_review_at) }}</span>
            </div>

            <div class="sc-actions">
              <el-button size="small" text @click="openEditDialog(entry)">
                <el-icon><Edit /></el-icon>
                备注
              </el-button>
              <el-button size="small" text type="danger" @click="handleUnstar(entry)">
                <el-icon><StarFilled /></el-icon>
                取消星标
              </el-button>
            </div>
          </div>
        </div>

        <div class="pagination-row">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="totalStarred"
            layout="prev, pager, next"
            background
            @current-change="loadEntries"
          />
        </div>
      </template>

      <EmptyState
        v-else
        title="暂无星标词汇"
        description="你可以在词汇详情页或复习页把总是记不清的词标星。"
      >
        <template #action>
          <el-button type="primary" @click="router.push('/vocabulary')">去词汇笔记</el-button>
          <el-button @click="router.push('/vocabulary/review')">去复习</el-button>
        </template>
      </EmptyState>

      <!-- Edit note dialog -->
      <el-dialog v-model="editDialogVisible" title="编辑星标备注" width="420px" destroy-on-close>
        <el-form v-if="editingEntry" label-position="top">
          <el-form-item label="备注">
            <el-input v-model="editNoteText" type="textarea" :rows="3" placeholder="为什么总是记不清这个词？" />
          </el-form-item>
          <el-form-item label="优先级">
            <el-radio-group v-model="editPriority">
              <el-radio-button value="normal">普通</el-radio-button>
              <el-radio-button value="high">高</el-radio-button>
            </el-radio-group>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingNote" @click="saveNote">保存</el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Edit, StarFilled, Reading } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getStarredEntries, starEntry } from '@/api/vocabulary'
import { getDashboardStats } from '@/api/stats'
import type { VocabularyEntry, DashboardStats } from '@/types'
import { FAMILIARITY_MAP } from '@/types'

const router = useRouter()
const loading = ref(true)
const entries = ref<VocabularyEntry[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const totalStarred = ref(0)
const highPriorityCount = ref(0)
const masteredStarredCount = ref(0)
const searchQuery = ref('')
const familiarityFilter = ref('')
const priorityFilter = ref('')
const dashboardStats = ref<DashboardStats | null>(null)

// Edit dialog
const editDialogVisible = ref(false)
const editingEntry = ref<VocabularyEntry | null>(null)
const savingNote = ref(false)
const editNoteText = ref('')
const editPriority = ref<string>('normal')

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

async function loadEntries() {
  try {
    const params: Record<string, any> = { page: currentPage.value, page_size: pageSize.value }
    if (searchQuery.value) params.q = searchQuery.value
    if (familiarityFilter.value) params.familiarity = familiarityFilter.value
    if (priorityFilter.value) params.star_priority = priorityFilter.value

    const res = await getStarredEntries(params)
    entries.value = res.data?.items ?? []
    totalStarred.value = res.data?.total ?? 0
    highPriorityCount.value = entries.value.filter(e => e.star_priority === 'high').length
    // Count mastered but starred
    masteredStarredCount.value = entries.value.filter(e => e.familiarity === 'mastered').length
  } catch {
    ElMessage.error('加载星标词汇失败')
  }
}

let searchTimer: ReturnType<typeof setTimeout> | null = null
function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadEntries()
  }, 300)
}
function onSearchClear() {
  currentPage.value = 1
  loadEntries()
}
function resetAndLoad() {
  currentPage.value = 1
  loadEntries()
}

async function handleUnstar(entry: VocabularyEntry) {
  try {
    await starEntry(entry.id, { is_starred: false })
    ElMessage.success(`已取消「${entry.term}」的星标`)
    await loadEntries()
    // Refresh dashboard stats
    loadStats()
  } catch {
    ElMessage.error('操作失败')
  }
}

function openEditDialog(entry: VocabularyEntry) {
  editingEntry.value = entry
  editNoteText.value = entry.star_note || ''
  editPriority.value = entry.star_priority || 'normal'
  editDialogVisible.value = true
}

async function saveNote() {
  if (!editingEntry.value) return
  savingNote.value = true
  try {
    await starEntry(editingEntry.value.id, {
      is_starred: true,
      star_note: editNoteText.value,
      star_priority: editPriority.value,
    })
    ElMessage.success('备注已更新')
    editDialogVisible.value = false
    await loadEntries()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingNote.value = false
  }
}

async function loadStats() {
  try {
    const res = await getDashboardStats()
    dashboardStats.value = res.data
  } catch { /* non-critical */ }
}

onMounted(async () => {
  await Promise.all([loadEntries(), loadStats()])
  loading.value = false
})
</script>

<style scoped>
.star-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-xl);
}
@media (max-width: 768px) { .star-stats-row { grid-template-columns: repeat(2, 1fr); } }

.star-stat-card {
  padding: var(--space-lg);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-border);
}
.star-stat-card.all { background: #FEF3C7; border-color: #FCD34D; }
.star-stat-card.high { background: #FEE2E2; border-color: #FCA5A5; }
.star-stat-card.due { background: #EFF6FF; border-color: #93C5FD; }
.star-stat-card.mastered { background: #F0FDF4; border-color: #86EFAC; }

.ssc-value { font-size: 28px; font-weight: 800; color: var(--color-text-primary); }
.ssc-label { font-size: var(--text-caption); color: var(--color-text-tertiary); margin-top: var(--space-xs); }

.star-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
  gap: var(--space-md);
  flex-wrap: wrap;
}
.toolbar-left { display: flex; align-items: center; gap: var(--space-md); flex-wrap: wrap; }

.starred-list { display: flex; flex-direction: column; gap: var(--space-md); }

.starred-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  transition: border-color 0.15s;
}
.starred-card.priority-high {
  border-color: #FCD34D;
  border-width: 1.5px;
}

.sc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-sm);
  flex-wrap: wrap;
  gap: var(--space-sm);
}
.sc-term-row { display: flex; align-items: baseline; gap: var(--space-sm); flex-wrap: wrap; }
.sc-term {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
  cursor: pointer;
}
.sc-term:hover { text-decoration: underline; }
.sc-phonetic {
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  color: var(--color-text-tertiary);
}
.sc-tags { display: flex; gap: var(--space-xs); align-items: center; }
.sc-note {
  font-size: var(--text-body);
  color: var(--color-text-secondary);
  background: #FFFBEB;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-sm);
  border-left: 3px solid #F59E0B;
}
.sc-meta { display: flex; gap: var(--space-xl); flex-wrap: wrap; }
.sc-meta-item { font-size: var(--text-caption); color: var(--color-text-tertiary); }
.sc-actions { display: flex; gap: var(--space-sm); margin-top: var(--space-md); padding-top: var(--space-sm); border-top: 1px solid var(--color-border-light); }

.pagination-row { display: flex; justify-content: center; margin-top: var(--space-2xl); }
</style>
