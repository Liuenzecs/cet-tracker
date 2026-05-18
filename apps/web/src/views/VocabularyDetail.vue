<template>
  <div class="page-container">
    <div v-if="loading" v-loading="true" style="min-height: 400px" />

    <template v-else-if="note">
      <!-- Header -->
      <PageHeader :title="note.title" :description="headerDescription">
        <template #actions>
          <el-button @click="router.push('/')">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <el-button type="danger" plain @click="handleDelete">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </PageHeader>

      <div class="note-meta-row">
        <StatusTag v-if="note.exam_type" type="exam_type" :value="note.exam_type" />
        <StatusTag type="source_section" :value="note.source_section" />
        <span class="meta-text">{{ formatDate(note.created_at) }}</span>
        <span class="meta-text">共 {{ totalEntries }} 词</span>
      </div>

      <!-- Raw markdown toggle -->
      <el-collapse style="margin-bottom: var(--space-xl)">
        <el-collapse-item title="查看原始 Markdown">
          <pre class="raw-md">{{ note.raw_markdown }}</pre>
        </el-collapse-item>
      </el-collapse>

      <!-- Filter bar -->
      <div class="filter-bar">
        <div class="filter-left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索词汇..."
            clearable
            style="width: 240px"
            @input="onSearchInput"
            @clear="onSearchClear"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="familiarityFilter"
            placeholder="掌握状态"
            clearable
            style="width: 140px"
            @change="onFilterChange"
          >
            <el-option label="全部" value="" />
            <el-option
              v-for="(info, key) in FAMILIARITY_MAP"
              :key="key"
              :label="info.label"
              :value="key"
            />
          </el-select>
        </div>
        <div class="filter-right">
          <span class="filter-info">共 {{ totalEntries }} 个词条，当前显示 {{ entries.length }} 个</span>
        </div>
      </div>

      <!-- Entry cards -->
      <template v-if="entries.length > 0">
        <div class="entry-cards">
          <div v-for="entry in entries" :key="entry.id" class="entry-card">
            <!-- Header -->
            <div class="entry-header">
              <div class="entry-term-row">
                <span class="entry-type-badge">{{ entry.entry_type }}</span>
                <h2 class="entry-term">{{ entry.term }}</h2>
                <el-select
                  :model-value="entry.familiarity"
                  size="small"
                  style="width: 120px"
                  @change="(v: string) => handleFamiliarityChange(entry, v)"
                >
                  <el-option
                    v-for="(info, key) in FAMILIARITY_MAP"
                    :key="key"
                    :label="info.label"
                    :value="key"
                  />
                </el-select>
              </div>
              <div class="entry-meta-right">
                <el-button size="small" text @click="openEditDialog(entry)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <span class="review-count">复习 {{ entry.review_count }} 次</span>
              </div>
            </div>

            <!-- Meanings -->
            <div v-if="entry.meanings_json?.length" class="entry-section">
              <div class="section-label">
                <el-icon :size="14"><Reading /></el-icon>
                释义
              </div>
              <div class="meanings-block">
                <span v-for="(m, i) in formatTextList(entry.meanings_json)" :key="i" class="meaning-item">
                  {{ m }}<template v-if="i < formatTextList(entry.meanings_json).length - 1">；</template>
                </span>
              </div>
            </div>

            <!-- Usages -->
            <div v-if="entry.usages_json?.length" class="entry-section">
              <div class="section-label">
                <el-icon :size="14"><Collection /></el-icon>
                常见用法
              </div>
              <div class="tags-row">
                <el-tag
                  v-for="(u, i) in formatTextList(entry.usages_json)"
                  :key="i"
                  size="default"
                  effect="plain"
                  class="usage-tag"
                >
                  {{ u }}
                </el-tag>
              </div>
            </div>

            <!-- Examples -->
            <div v-if="entry.examples_json?.length" class="entry-section">
              <div class="section-label">
                <el-icon :size="14"><Notebook /></el-icon>
                例句
              </div>
              <div class="examples-list">
                <div v-for="(ex, i) in entry.examples_json" :key="i" class="example-item">
                  <p class="example-en">{{ formatText(ex.en) }}</p>
                  <p v-if="ex.zh" class="example-zh">{{ formatText(ex.zh) }}</p>
                </div>
              </div>
            </div>

            <!-- Mistake tips -->
            <div v-if="entry.mistake_tips_json?.length" class="entry-section">
              <div class="section-label warning-label">
                <el-icon :size="14"><WarningFilled /></el-icon>
                易错点
              </div>
              <div class="mistake-box">
                <div v-for="(tip, i) in formatTextList(entry.mistake_tips_json)" :key="i" class="mistake-item">
                  <span class="mistake-icon">&#9888;</span>
                  {{ tip }}
                </div>
              </div>
            </div>

            <!-- Synonyms -->
            <div v-if="entry.synonyms_json?.length" class="entry-section">
              <div class="section-label">
                <el-icon :size="14"><Refresh /></el-icon>
                同义替换
              </div>
              <div class="tags-row">
                <el-tag
                  v-for="(s, i) in formatTextList(entry.synonyms_json)"
                  :key="i"
                  size="default"
                  effect="plain"
                  type="success"
                >
                  {{ s }}
                </el-tag>
              </div>
            </div>

            <!-- Writing sentences -->
            <div v-if="entry.writing_sentences_json?.length" class="entry-section">
              <div class="section-label writing-label">
                <el-icon :size="14"><EditPen /></el-icon>
                写作可用句
              </div>
              <div class="writing-box">
                <p v-for="(ws, i) in formatTextList(entry.writing_sentences_json)" :key="i" class="writing-sentence">
                  {{ ws }}
                </p>
              </div>
            </div>

            <!-- Comparisons -->
            <div v-if="entry.comparisons_json?.length" class="entry-section">
              <div class="section-label">
                <el-icon :size="14"><List /></el-icon>
                易混词对比
              </div>
              <div class="comparisons-grid">
                <div v-for="(comp, i) in entry.comparisons_json" :key="i" class="comparison-card">
                  <div class="comp-words">
                    <span class="comp-word">{{ formatComparison(comp).left }}</span>
                    <span class="comp-vs">vs</span>
                    <span class="comp-word">{{ formatComparison(comp).right }}</span>
                  </div>
                  <div v-if="formatComparison(comp).leftMeaning || formatComparison(comp).rightMeaning" class="comp-defs">
                    <div class="comp-def-item">
                      <span class="comp-def-text">{{ formatComparison(comp).leftMeaning || '--' }}</span>
                    </div>
                    <div class="comp-def-item">
                      <span class="comp-def-text">{{ formatComparison(comp).rightMeaning || '--' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="pagination-row">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="totalEntries"
            layout="prev, pager, next"
            background
            @current-change="onPageChange"
          />
        </div>
      </template>

      <EmptyState
        v-else
        title="暂无词汇条目"
        description="该笔记未解析出任何词汇条目，或当前筛选条件下无匹配结果"
      >
        <template v-if="familiarityFilter || searchQuery" #action>
          <el-button @click="clearFilters">清除筛选</el-button>
        </template>
      </EmptyState>
    </template>

    <!-- Edit dialog -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑词条"
      width="680px"
      destroy-on-close
    >
      <el-form v-if="editingEntry" label-position="top" size="default">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="词汇 (term)">
              <el-input v-model="editingEntry.term" />
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="类型">
              <el-select v-model="editingEntry.entry_type">
                <el-option label="word" value="word" />
                <el-option label="phrase" value="phrase" />
                <el-option label="proper_noun" value="proper_noun" />
                <el-option label="unknown" value="unknown" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="掌握状态">
              <el-select v-model="editingEntry.familiarity">
                <el-option
                  v-for="(info, key) in FAMILIARITY_MAP"
                  :key="key"
                  :label="info.label"
                  :value="key"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="释义 (meanings_json)">
          <el-input v-model="editMeaningsText" type="textarea" :rows="3" placeholder="每行一个释义" />
        </el-form-item>

        <el-form-item label="常见用法 (usages_json)">
          <el-input v-model="editUsagesText" type="textarea" :rows="3" placeholder="每行一个用法" />
        </el-form-item>

        <el-form-item label="例句 (examples_json)">
          <el-input v-model="editExamplesText" type="textarea" :rows="4" placeholder="每行一条: 英文 — 中文" />
        </el-form-item>

        <el-form-item label="易错点 (mistake_tips_json)">
          <el-input v-model="editMistakeTipsText" type="textarea" :rows="3" placeholder="每行一个易错点" />
        </el-form-item>

        <el-form-item label="同义词 (synonyms_json)">
          <el-input v-model="editSynonymsText" type="textarea" :rows="2" placeholder="每行一个同义词" />
        </el-form-item>

        <el-form-item label="易混词对比 (comparisons_json)">
          <el-input v-model="editComparisonsText" type="textarea" :rows="4" placeholder="每行一个对比: left vs right | left_meaning | right_meaning" />
        </el-form-item>

        <el-form-item label="写作可用句 (writing_sentences_json)">
          <el-input v-model="editWritingSentencesText" type="textarea" :rows="3" placeholder="每行一个句子" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingEdit" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Delete, Reading, Edit, WarningFilled, Refresh, EditPen, List, Collection, Notebook, Search } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getVocabularyNote, deleteVocabularyNote, getVocabularyEntries, updateVocabularyEntry } from '@/api/vocabulary'
import { useConfirm } from '@/composables/useConfirm'
import type { VocabularyNote, VocabularyEntry } from '@/types'
import { FAMILIARITY_MAP } from '@/types'
import { formatText, formatTextList, formatComparison } from '@/utils/vocabularyFormat'

const props = defineProps<{ id: string }>()
const router = useRouter()
const { confirm } = useConfirm()

const noteId = computed(() => parseInt(props.id))
const loading = ref(true)
const note = ref<VocabularyNote | null>(null)
const entries = ref<VocabularyEntry[]>([])
const totalEntries = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const familiarityFilter = ref('')
const searchQuery = ref('')

// Edit dialog
const editDialogVisible = ref(false)
const editingEntry = ref<VocabularyEntry | null>(null)
const savingEdit = ref(false)
const editMeaningsText = ref('')
const editUsagesText = ref('')
const editExamplesText = ref('')
const editMistakeTipsText = ref('')
const editSynonymsText = ref('')
const editComparisonsText = ref('')
const editWritingSentencesText = ref('')

const headerDescription = computed(() => {
  if (!note.value) return ''
  const parts = [note.value.source_section]
  if (note.value.paper_name) parts.unshift(note.value.paper_name)
  return parts.join(' · ')
})

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
}

async function loadEntries() {
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (familiarityFilter.value) params.familiarity = familiarityFilter.value
    if (searchQuery.value) params.q = searchQuery.value

    const res = await getVocabularyEntries(noteId.value, params)
    entries.value = res.data?.items ?? []
    totalEntries.value = res.data?.total ?? 0
  } catch {
    ElMessage.error('加载词条失败')
  }
}

async function loadNote() {
  loading.value = true
  try {
    const noteRes = await getVocabularyNote(noteId.value)
    note.value = noteRes.data
    await loadEntries()
  } catch {
    ElMessage.error('加载笔记失败')
    router.push('/vocabulary')
  } finally {
    loading.value = false
  }
}

function onPageChange() {
  loadEntries()
}

function onFilterChange() {
  currentPage.value = 1
  loadEntries()
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

function clearFilters() {
  familiarityFilter.value = ''
  searchQuery.value = ''
  currentPage.value = 1
  loadEntries()
}

async function handleFamiliarityChange(entry: VocabularyEntry, value: string) {
  try {
    await updateVocabularyEntry(entry.id, { familiarity: value })
    entry.familiarity = value as VocabularyEntry['familiarity']
    ElMessage.success(`已更新为「${FAMILIARITY_MAP[value]?.label || value}」`)
  } catch {
    ElMessage.error('更新失败')
  }
}

async function handleDelete() {
  const ok = await confirm('删除后笔记和所有词汇条目将被永久移除，不可恢复。', '确认删除', { type: 'error' })
  if (!ok) return
  try {
    await deleteVocabularyNote(noteId.value)
    ElMessage.success('已删除')
    router.push('/vocabulary')
  } catch {
    ElMessage.error('删除失败')
  }
}

// Edit entry
function openEditDialog(entry: VocabularyEntry) {
  editingEntry.value = JSON.parse(JSON.stringify(entry))
  editMeaningsText.value = (entry.meanings_json || []).join('\n')
  editUsagesText.value = (entry.usages_json || []).join('\n')
  editExamplesText.value = (entry.examples_json || []).map((e: any) => {
    if (typeof e === 'string') return e
    return `${e.en || ''} — ${e.zh || ''}`
  }).join('\n')
  editMistakeTipsText.value = (entry.mistake_tips_json || []).join('\n')
  editSynonymsText.value = (entry.synonyms_json || []).join('\n')
  editComparisonsText.value = (entry.comparisons_json || []).map((c: any) => {
    const left = c.left || c.word1 || c.term_a || ''
    const right = c.right || c.word2 || c.term_b || ''
    const lm = c.left_meaning || c.meaning1 || c.description || ''
    const rm = c.right_meaning || c.meaning2 || ''
    return `${left} vs ${right} | ${lm} | ${rm}`
  }).join('\n')
  editWritingSentencesText.value = (entry.writing_sentences_json || []).join('\n')
  editDialogVisible.value = true
}

async function saveEdit() {
  if (!editingEntry.value) return
  savingEdit.value = true
  try {
    const e = editingEntry.value
    const payload: Record<string, any> = {
      term: e.term,
      entry_type: e.entry_type,
      familiarity: e.familiarity,
      meanings_json: editMeaningsText.value.split('\n').filter(s => s.trim()),
      usages_json: editUsagesText.value.split('\n').filter(s => s.trim()),
      examples_json: editExamplesText.value.split('\n').filter(s => s.trim()).map(line => {
        const m = line.match(/^(.+?)\s*[—\-]\s*(.+)$/)
        if (m) return { en: m[1].trim(), zh: m[2].trim() }
        return { en: line.trim(), zh: '' }
      }),
      mistake_tips_json: editMistakeTipsText.value.split('\n').filter(s => s.trim()),
      synonyms_json: editSynonymsText.value.split('\n').filter(s => s.trim()),
      comparisons_json: editComparisonsText.value.split('\n').filter(s => s.trim()).map(line => {
        const parts = line.split('|').map(s => s.trim())
        const vsParts = parts[0]?.split(/\s+vs\s+/i) || ['', '']
        return {
          left: vsParts[0]?.trim() || '',
          right: vsParts[1]?.trim() || '',
          left_meaning: parts[1] || '',
          right_meaning: parts[2] || '',
        }
      }),
      writing_sentences_json: editWritingSentencesText.value.split('\n').filter(s => s.trim()),
    }
    await updateVocabularyEntry(e.id, payload)
    ElMessage.success('词条已更新')
    editDialogVisible.value = false
    await loadEntries()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingEdit.value = false
  }
}

onMounted(loadNote)
</script>

<style scoped>
.note-meta-row {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-xl);
  flex-wrap: wrap;
}

.meta-text {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
}

.raw-md {
  background: #1E1E2E;
  color: #CDD6F4;
  padding: var(--space-xl);
  border-radius: var(--radius-md);
  font-size: var(--text-caption);
  line-height: 1.7;
  overflow-x: auto;
  white-space: pre-wrap;
  max-height: 500px;
  overflow-y: auto;
}

/* Filter bar */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
  flex-wrap: wrap;
  gap: var(--space-md);
}

.filter-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.filter-info {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
}

/* Entry cards */
.entry-cards {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.entry-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.entry-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg) var(--space-xl);
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border-light);
}

.entry-term-row {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.entry-type-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--color-primary-light);
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.entry-term {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}

.entry-meta-right {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.review-count {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
}

/* Sections */
.entry-section {
  padding: var(--space-lg) var(--space-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.entry-section:last-child {
  border-bottom: none;
}

.section-label {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--text-caption);
  font-weight: 700;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: var(--space-md);
}

.warning-label { color: #D97706; }
.writing-label { color: var(--color-primary); }

.meanings-block {
  background: #F0F4FF;
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  font-size: var(--text-body);
  color: var(--color-text-primary);
  line-height: 1.8;
}

.meaning-item { font-weight: 500; }

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.usage-tag {
  border-radius: var(--radius-md) !important;
  font-size: var(--text-body);
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.example-item {
  padding: var(--space-md) var(--space-lg);
  background: var(--color-bg);
  border-radius: var(--radius-md);
}

.example-en {
  font-size: var(--text-body);
  color: var(--color-text-primary);
  font-weight: 500;
  margin-bottom: var(--space-xs);
}

.example-zh {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
}

.mistake-box {
  background: #FFFBEB;
  border: 1px solid #FDE68A;
  border-radius: var(--radius-md);
  padding: var(--space-md) var(--space-lg);
}

.mistake-item {
  font-size: var(--text-body);
  color: #92400E;
  line-height: 1.8;
  padding: var(--space-xs) 0;
}

.mistake-item + .mistake-item {
  border-top: 1px solid #FDE68A;
}

.mistake-icon { margin-right: var(--space-sm); }

.writing-box {
  background: linear-gradient(135deg, #EEF0FF 0%, #F8F9FF 100%);
  border-left: 3px solid var(--color-primary);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  padding: var(--space-md) var(--space-lg);
}

.writing-sentence {
  font-size: var(--text-body);
  color: var(--color-text-primary);
  line-height: 1.7;
  font-style: italic;
}

.writing-sentence + .writing-sentence { margin-top: var(--space-sm); }

.comparisons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-md);
}

.comparison-card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
}

.comp-words {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.comp-word {
  font-size: var(--text-card-title);
  font-weight: 700;
  color: var(--color-primary);
}

.comp-vs {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
  font-weight: 600;
}

.comp-defs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-sm);
}

.comp-def-item {
  padding: var(--space-sm) var(--space-md);
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  text-align: center;
}

.comp-def-text {
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.pagination-row {
  display: flex;
  justify-content: center;
  margin-top: var(--space-2xl);
}
</style>
