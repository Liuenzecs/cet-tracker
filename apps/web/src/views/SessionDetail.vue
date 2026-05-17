<template>
  <div class="page-container">
    <div v-if="loading" v-loading="true" style="min-height: 400px" />

    <template v-else-if="session">
      <!-- Header -->
      <PageHeader :title="session.paper_name" :description="`${formatDate(session.date)} · ${session.duration_minutes} 分钟`">
        <template #actions>
          <el-button @click="showEditDialog = true">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button type="danger" plain @click="handleDelete">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </PageHeader>

      <!-- Session Info -->
      <SectionCard title="训练信息" style="margin-bottom: var(--space-xl)">
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">考试类型</span>
            <StatusTag type="exam_type" :value="session.exam_type" />
          </div>
          <div class="info-item">
            <span class="info-label">训练类型</span>
            <StatusTag type="session_type" :value="session.session_type" />
          </div>
          <div class="info-item">
            <span class="info-label">训练日期</span>
            <span class="info-value">{{ session.date }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">时长</span>
            <span class="info-value">{{ session.duration_minutes }} 分钟</span>
          </div>
          <div v-if="session.note" class="info-item info-full">
            <span class="info-label">备注</span>
            <span class="info-value">{{ session.note }}</span>
          </div>
        </div>
      </SectionCard>

      <!-- Listening Section -->
      <SectionCard title="听力结果" style="margin-bottom: var(--space-xl)">
        <template #actions>
          <el-button
            v-if="!listeningResult"
            type="primary"
            size="small"
            @click="showListeningForm = !showListeningForm"
          >
            {{ showListeningForm ? '取消' : '录入听力结果' }}
          </el-button>
        </template>

        <!-- Listening form -->
        <div v-if="showListeningForm && !listeningResult" class="result-form">
          <el-form ref="listeningFormRef" :model="listeningForm" label-position="top">
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="总题数" required>
                  <el-input-number v-model="listeningForm.total_questions" :min="1" :max="100" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="正确题数" required>
                  <el-input-number v-model="listeningForm.correct_count" :min="0" :max="listeningForm.total_questions" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="正确率" required>
                  <el-input :model-value="listeningAccuracy" disabled />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="错题列表">
              <el-input
                v-model="listeningForm.wrong_questions_text"
                placeholder="如 1,5,8,12,15（逗号分隔）"
              />
              <div class="form-hint">输入错题的题号，用英文逗号分隔</div>
            </el-form-item>

            <el-form-item label="错误标签">
              <el-checkbox-group v-model="listeningForm.selectedTags">
                <el-checkbox
                  v-for="tag in LISTENING_MISTAKE_TAGS"
                  :key="tag"
                  :label="tag"
                  :value="tag"
                />
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="反思总结">
              <el-input v-model="listeningForm.reflection" type="textarea" :rows="3" placeholder="记录错误原因和改善措施" />
            </el-form-item>

            <div class="form-actions">
              <el-button @click="showListeningForm = false">取消</el-button>
              <el-button type="primary" :loading="listeningSubmitting" @click="submitListening">保存听力结果</el-button>
            </div>
          </el-form>
        </div>

        <!-- Listening result display -->
        <div v-if="listeningResult && !showListeningForm" class="result-display">
          <div class="result-header">
            <div class="accuracy-circle">
              <el-progress
                type="circle"
                :percentage="listeningPercent"
                :width="100"
                :stroke-width="8"
                :color="accuracyColor(listeningPercent)"
              />
              <span class="accuracy-label">正确率</span>
            </div>
            <div class="result-summary">
              <div class="summary-text">
                共 <strong>{{ listeningResult.total_questions }}</strong> 题，正确 <strong style="color: #16A34A">{{ listeningResult.correct_count }}</strong> 题
              </div>
              <div v-if="listeningResult.wrong_questions_json?.length" class="wrong-chips">
                <span class="wrong-label">错题:</span>
                <el-tag
                  v-for="q in listeningResult.wrong_questions_json"
                  :key="q"
                  size="small"
                  type="danger"
                  effect="plain"
                  style="margin-right: 4px; margin-bottom: 4px"
                >
                  #{{ q }}
                </el-tag>
              </div>
            </div>
            <div class="result-actions">
              <el-button size="small" @click="editListening">修改</el-button>
              <el-button size="small" type="danger" plain @click="handleDeleteListening">删除</el-button>
            </div>
          </div>

          <div v-if="listeningResult.reflection" class="result-reflection">
            <h4 class="result-section-title">反思</h4>
            <p>{{ listeningResult.reflection }}</p>
          </div>

          <div v-if="listeningTags.length > 0" class="result-tags">
            <h4 class="result-section-title">错误标签</h4>
            <div class="tags-list">
              <el-tag
                v-for="tag in listeningTags"
                :key="tag"
                size="small"
                type="warning"
                effect="plain"
              >
                {{ tag }}
              </el-tag>
            </div>
          </div>
        </div>
      </SectionCard>

      <!-- Reading Section -->
      <SectionCard title="阅读结果" style="margin-bottom: var(--space-xl)">
        <template #actions>
          <el-button v-if="!showReadingForm" type="primary" size="small" @click="showReadingForm = true">
            添加阅读结果
          </el-button>
        </template>

        <!-- Existing reading results -->
        <div v-if="readingResults.length > 0" class="reading-list">
          <div v-for="rr in readingResults" :key="rr.id" class="reading-result-item">
            <div class="rri-header">
              <StatusTag type="session_type" :value="rr.question_type" />
              <el-progress
                :percentage="Math.round((rr.correct_count / rr.total_questions) * 100)"
                :stroke-width="8"
                :color="accuracyColor(Math.round((rr.correct_count / rr.total_questions) * 100))"
                :text-inside="true"
                style="flex: 1; margin: 0 var(--space-lg)"
              />
              <el-button size="small" type="danger" plain @click="handleDeleteReading(rr.id)">删除</el-button>
            </div>
            <div class="rri-meta">
              <span>{{ rr.correct_count }} / {{ rr.total_questions }}</span>
              <span v-if="rr.reflection" class="rri-reflection">{{ rr.reflection }}</span>
            </div>
          </div>
        </div>

        <div v-if="!showReadingForm && readingResults.length === 0" class="no-result-hint">
          暂无阅读结果
        </div>

        <!-- Reading form -->
        <div v-if="showReadingForm" class="result-form">
          <el-form ref="readingFormRef" :model="readingForm" label-position="top">
            <el-form-item label="题型" required>
              <el-select v-model="readingForm.question_type" style="width: 100%">
                <el-option v-for="t in READING_QUESTION_TYPES" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="总题数" required>
                  <el-input-number v-model="readingForm.total_questions" :min="1" :max="100" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="正确题数" required>
                  <el-input-number v-model="readingForm.correct_count" :min="0" :max="readingForm.total_questions" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="错题列表">
              <el-input v-model="readingForm.wrong_questions_text" placeholder="如 1,5,8,12,15" />
            </el-form-item>

            <el-form-item label="错误标签">
              <el-checkbox-group v-model="readingForm.selectedTags">
                <el-checkbox v-for="tag in READING_MISTAKE_TAGS" :key="tag" :label="tag" :value="tag" />
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="反思">
              <el-input v-model="readingForm.reflection" type="textarea" :rows="3" placeholder="记录错误原因和改善措施" />
            </el-form-item>

            <div class="form-actions">
              <el-button @click="showReadingForm = false">取消</el-button>
              <el-button type="primary" :loading="readingSubmitting" @click="submitReading">保存</el-button>
            </div>
          </el-form>
        </div>
      </SectionCard>

      <!-- Associated Vocabulary -->
      <SectionCard title="关联词汇笔记">
        <template v-if="vocabNotes.length > 0">
          <div class="vocab-links">
            <router-link
              v-for="note in vocabNotes"
              :key="note.id"
              :to="`/vocabulary/${note.id}`"
              class="vocab-link-item"
            >
              <el-icon color="#4F6EF7"><Collection /></el-icon>
              <span>{{ note.title }}</span>
              <StatusTag v-if="note.exam_type" type="exam_type" :value="note.exam_type" />
              <el-icon color="#9CA3AF"><ArrowRight /></el-icon>
            </router-link>
          </div>
        </template>
        <div v-else class="no-result-hint">
          暂无关联词汇笔记
        </div>
      </SectionCard>
    </template>

    <!-- Edit dialog -->
    <el-dialog v-model="showEditDialog" title="编辑训练信息" width="500px">
      <el-form v-if="session" :model="editForm" label-position="top">
        <el-form-item label="考试类型">
          <el-radio-group v-model="editForm.exam_type">
            <el-radio-button value="CET4">CET-4</el-radio-button>
            <el-radio-button value="CET6">CET-6</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="试卷名称">
          <el-input v-model="editForm.paper_name" />
        </el-form-item>
        <el-form-item label="训练类型">
          <el-select v-model="editForm.session_type" style="width: 100%">
            <el-option v-for="st in SESSION_TYPES" :key="st.value" :label="st.label" :value="st.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="editForm.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="时长">
          <el-input-number v-model="editForm.duration_minutes" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.note" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="editSubmitting" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Edit, Delete, Collection, ArrowRight } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import SectionCard from '@/components/SectionCard.vue'
import StatusTag from '@/components/StatusTag.vue'
import { getSession, updateSession, deleteSession } from '@/api/sessions'
import { getListeningResult, createListeningResult, deleteListeningResult } from '@/api/listening'
import { getReadingResults, createReadingResult, deleteReadingResult } from '@/api/reading'
import { getVocabularyNotes } from '@/api/vocabulary'
import { useConfirm } from '@/components/ConfirmDialog.vue'
import type { ExamSession, ListeningResult, ReadingResult, VocabularyNote } from '@/types'
import { SESSION_TYPES, LISTENING_MISTAKE_TAGS, READING_MISTAKE_TAGS, READING_QUESTION_TYPES } from '@/types'

const props = defineProps<{ id: string }>()
const router = useRouter()
const { confirm } = useConfirm()

const sessionId = computed(() => parseInt(props.id))
const loading = ref(true)

// Session
const session = ref<ExamSession | null>(null)
const showEditDialog = ref(false)
const editSubmitting = ref(false)
const editForm = reactive({
  exam_type: 'CET4' as string,
  paper_name: '',
  session_type: '',
  date: '',
  duration_minutes: 30,
  note: '',
})

// Listening
const listeningResult = ref<ListeningResult | null>(null)
const showListeningForm = ref(false)
const listeningSubmitting = ref(false)
const listeningForm = reactive({
  total_questions: 25,
  correct_count: 0,
  wrong_questions_text: '',
  selectedTags: [] as string[],
  reflection: '',
})

// Reading
const readingResults = ref<ReadingResult[]>([])
const showReadingForm = ref(false)
const readingSubmitting = ref(false)
const readingForm = reactive({
  question_type: '仔细阅读',
  total_questions: 10,
  correct_count: 0,
  wrong_questions_text: '',
  selectedTags: [] as string[],
  reflection: '',
})

// Vocab links
const vocabNotes = ref<VocabularyNote[]>([])

const listeningPercent = computed(() => {
  if (!listeningResult.value) return 0
  return Math.round((listeningResult.value.correct_count / listeningResult.value.total_questions) * 100)
})

const listeningAccuracy = computed(() => {
  if (listeningForm.total_questions === 0) return '0%'
  return `${((listeningForm.correct_count / listeningForm.total_questions) * 100).toFixed(1)}%`
})

const listeningTags = computed(() => {
  const tags = listeningResult.value?.mistake_tags_json
  if (!tags) return []
  return Object.keys(tags).filter((k) => (tags[k]?.length ?? 0) > 0)
})

function accuracyColor(pct: number): string {
  if (pct >= 80) return '#22C55E'
  if (pct >= 60) return '#F59E0B'
  return '#EF4444'
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

function parseQuestionNumbers(text: string): number[] {
  if (!text.trim()) return []
  return text.split(/[,，\s]+/).map(Number).filter((n) => !isNaN(n) && n > 0)
}

// Load data
async function loadSession() {
  loading.value = true
  try {
    const res = await getSession(sessionId.value)
    session.value = res.data

    // Prep edit form
    editForm.exam_type = session.value.exam_type
    editForm.paper_name = session.value.paper_name
    editForm.session_type = session.value.session_type
    editForm.date = session.value.date
    editForm.duration_minutes = session.value.duration_minutes
    editForm.note = session.value.note || ''

    // Load sub-data in parallel
    await Promise.allSettled([loadListening(), loadReading(), loadVocab()])
  } catch {
    ElMessage.error('加载训练记录失败')
    router.push('/sessions')
  } finally {
    loading.value = false
  }
}

async function loadListening() {
  try {
    const res = await getListeningResult(sessionId.value)
    listeningResult.value = res.data
  } catch {
    listeningResult.value = null
  }
}

async function loadReading() {
  try {
    const res = await getReadingResults(sessionId.value)
    readingResults.value = res.data ?? []
  } catch {
    readingResults.value = []
  }
}

async function loadVocab() {
  try {
    const res = await getVocabularyNotes({ source_session_id: sessionId.value })
    vocabNotes.value = res.data?.items ?? []
  } catch {
    vocabNotes.value = []
  }
}

// Edit session
async function submitEdit() {
  editSubmitting.value = true
  try {
    await updateSession(sessionId.value, editForm)
    ElMessage.success('已更新')
    showEditDialog.value = false
    await loadSession()
  } catch { /* handled */ }
  finally { editSubmitting.value = false }
}

// Delete session
async function handleDelete() {
  const ok = await confirm('确定要删除这条训练记录吗？此操作不可恢复。', '确认删除', { type: 'error' })
  if (!ok) return
  try {
    await deleteSession(sessionId.value)
    ElMessage.success('已删除')
    router.push('/sessions')
  } catch { /* handled */ }
}

// Listening CRUD
async function submitListening() {
  listeningSubmitting.value = true
  try {
    const wrongQuestions = parseQuestionNumbers(listeningForm.wrong_questions_text)
    const tagsJson: Record<string, string[]> = {}
    for (const tag of listeningForm.selectedTags) {
      const qs = wrongQuestions.length > 0 ? wrongQuestions.map(String) : []
      tagsJson[tag] = qs
    }

    await createListeningResult(sessionId.value, {
      total_questions: listeningForm.total_questions,
      correct_count: listeningForm.correct_count,
      wrong_questions_text: listeningForm.wrong_questions_text || undefined,
      wrong_questions_json: wrongQuestions,
      mistake_tags_json: tagsJson,
      reflection: listeningForm.reflection || undefined,
    })
    ElMessage.success('听力结果已保存')
    showListeningForm.value = false
    await loadListening()
  } catch { /* handled */ }
  finally { listeningSubmitting.value = false }
}

function editListening() {
  if (!listeningResult.value) return
  listeningForm.total_questions = listeningResult.value.total_questions
  listeningForm.correct_count = listeningResult.value.correct_count
  listeningForm.wrong_questions_text = listeningResult.value.wrong_questions_text || ''
  listeningForm.reflection = listeningResult.value.reflection || ''
  showListeningForm.value = true
}

async function handleDeleteListening() {
  if (!listeningResult.value) return
  const ok = await confirm('删除听力结果？', '确认', { type: 'warning' })
  if (!ok) return
  try {
    await deleteListeningResult(listeningResult.value.id)
    listeningResult.value = null
    ElMessage.success('已删除')
  } catch { /* handled */ }
}

// Reading CRUD
async function submitReading() {
  readingSubmitting.value = true
  try {
    const wrongQuestions = parseQuestionNumbers(readingForm.wrong_questions_text)
    const tagsJson: Record<string, string[]> = {}
    for (const tag of readingForm.selectedTags) {
      tagsJson[tag] = wrongQuestions.length > 0 ? wrongQuestions.map(String) : []
    }

    await createReadingResult(sessionId.value, {
      question_type: readingForm.question_type,
      total_questions: readingForm.total_questions,
      correct_count: readingForm.correct_count,
      wrong_questions_text: readingForm.wrong_questions_text || undefined,
      wrong_questions_json: wrongQuestions,
      mistake_tags_json: tagsJson,
      reflection: readingForm.reflection || undefined,
    })
    ElMessage.success('阅读结果已保存')
    showReadingForm.value = false
    await loadReading()
  } catch { /* handled */ }
  finally { readingSubmitting.value = false }
}

async function handleDeleteReading(id: number) {
  const ok = await confirm('删除阅读结果？', '确认', { type: 'warning' })
  if (!ok) return
  try {
    await deleteReadingResult(id)
    await loadReading()
    ElMessage.success('已删除')
  } catch { /* handled */ }
}

onMounted(loadSession)
</script>

<style scoped>
.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-xl);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.info-full {
  grid-column: 1 / -1;
}

.info-label {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.info-value {
  font-size: var(--text-body);
  color: var(--color-text-primary);
  font-weight: 500;
}

/* Result display */
.result-display {
  position: relative;
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--space-xl);
}

.accuracy-circle {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
  flex-shrink: 0;
}

.accuracy-label {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
}

.result-summary {
  flex: 1;
}

.summary-text {
  font-size: var(--text-body);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-sm);
}

.wrong-chips {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.wrong-label {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
  margin-right: var(--space-xs);
}

.result-section-title {
  font-size: var(--text-caption);
  font-weight: 600;
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-sm);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.result-reflection {
  margin-top: var(--space-lg);
  padding: var(--space-lg);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  font-size: var(--text-body);
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.result-tags {
  margin-top: var(--space-lg);
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

/* Result form */
.result-form {
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border-light);
}

.form-hint {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
  margin-top: var(--space-xs);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
  margin-top: var(--space-lg);
}

/* Reading list */
.reading-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.reading-result-item {
  padding: var(--space-lg);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}

.rri-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.rri-meta {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  margin-top: var(--space-sm);
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
}

.rri-reflection {
  color: var(--color-text-tertiary);
}

.no-result-hint {
  text-align: center;
  padding: var(--space-2xl);
  color: var(--color-text-tertiary);
  font-size: var(--text-body);
}

/* Vocab links */
.vocab-links {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.vocab-link-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--color-text-primary);
  font-weight: 500;
  transition: background 0.15s;
}

.vocab-link-item:hover {
  background: var(--color-primary-light);
}

.result-actions {
  display: flex;
  gap: var(--space-sm);
  flex-shrink: 0;
}
</style>
