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
        <span class="meta-text">共 {{ entries.length }} 词</span>
      </div>

      <!-- Raw markdown toggle -->
      <el-collapse style="margin-bottom: var(--space-xl)">
        <el-collapse-item title="查看原始 Markdown">
          <pre class="raw-md">{{ note.raw_markdown }}</pre>
        </el-collapse-item>
      </el-collapse>

      <!-- Entry cards -->
      <template v-if="entries.length > 0">
        <div class="entry-cards">
          <div
            v-for="entry in entries"
            :key="entry.id"
            class="entry-card"
          >
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
                <span v-for="(m, i) in entry.meanings_json" :key="i" class="meaning-item">
                  {{ m }}<template v-if="i < entry.meanings_json.length - 1">；</template>
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
                  v-for="(u, i) in entry.usages_json"
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
                <el-icon :size="14"><Edit /></el-icon>
                例句
              </div>
              <div class="examples-list">
                <div v-for="(ex, i) in entry.examples_json" :key="i" class="example-item">
                  <p class="example-en">{{ ex.en }}</p>
                  <p class="example-zh">{{ ex.zh }}</p>
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
                <div v-for="(tip, i) in entry.mistake_tips_json" :key="i" class="mistake-item">
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
                  v-for="(s, i) in entry.synonyms_json"
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
                六级写作可用句
              </div>
              <div class="writing-box">
                <p v-for="(ws, i) in entry.writing_sentences_json" :key="i" class="writing-sentence">
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
                    <span class="comp-word">{{ comp.word1 || comp.left }}</span>
                    <span class="comp-vs">vs</span>
                    <span class="comp-word">{{ comp.word2 || comp.right }}</span>
                  </div>
                  <div class="comp-defs" v-if="comp.meaning1 || comp.meaning2 || comp.diff">
                    <div class="comp-def-item">
                      <span class="comp-def-text">
                        {{ comp.meaning1 || comp.diff?.split('|')[0]?.trim() || '--' }}
                      </span>
                    </div>
                    <div class="comp-def-item">
                      <span class="comp-def-text">
                        {{ comp.meaning2 || comp.diff?.split('|')[1]?.trim() || '--' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <EmptyState
        v-else
        title="暂无词汇条目"
        description="该笔记未解析出任何词汇条目"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Delete, Reading, Edit, WarningFilled, Refresh, EditPen, List, Collection } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getVocabularyNote, deleteVocabularyNote, getVocabularyEntries, updateVocabularyEntry } from '@/api/vocabulary'
import { useConfirm } from '@/components/ConfirmDialog.vue'
import type { VocabularyNote, VocabularyEntry } from '@/types'
import { FAMILIARITY_MAP } from '@/types'

const props = defineProps<{ id: string }>()
const router = useRouter()
const { confirm } = useConfirm()

const noteId = computed(() => parseInt(props.id))
const loading = ref(true)
const note = ref<VocabularyNote | null>(null)
const entries = ref<VocabularyEntry[]>([])

const headerDescription = computed(() => {
  if (!note.value) return ''
  const parts = [note.value.source_section]
  if (note.value.paper_name) parts.unshift(note.value.paper_name)
  return parts.join(' · ')
})

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
}

async function loadNote() {
  loading.value = true
  try {
    const [noteRes, entryRes] = await Promise.all([
      getVocabularyNote(noteId.value),
      getVocabularyEntries(noteId.value),
    ])
    note.value = noteRes.data
    entries.value = entryRes.data ?? []
  } catch {
    ElMessage.error('加载笔记失败')
    router.push('/vocabulary')
  } finally {
    loading.value = false
  }
}

async function handleFamiliarityChange(entry: VocabularyEntry, value: string) {
  try {
    await updateVocabularyEntry(entry.id, { familiarity: value })
    entry.familiarity = value as VocabularyEntry['familiarity']
    ElMessage.success(`已更新为「${FAMILIARITY_MAP[value]?.label || value}」`)
  } catch { /* handled */ }
}

async function handleDelete() {
  const ok = await confirm('删除后笔记和所有词汇条目将被永久移除，不可恢复。', '确认删除', { type: 'error' })
  if (!ok) return
  try {
    await deleteVocabularyNote(noteId.value)
    ElMessage.success('已删除')
    router.push('/vocabulary')
  } catch { /* handled */ }
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

.warning-label {
  color: #D97706;
}

.writing-label {
  color: var(--color-primary);
}

/* Meanings */
.meanings-block {
  background: #F0F4FF;
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  font-size: var(--text-body);
  color: var(--color-text-primary);
  line-height: 1.8;
}

.meaning-item {
  font-weight: 500;
}

/* Tags */
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

/* Examples */
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

/* Mistake tips */
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

.mistake-icon {
  margin-right: var(--space-sm);
}

/* Writing */
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

.writing-sentence + .writing-sentence {
  margin-top: var(--space-sm);
}

/* Comparisons */
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
</style>
