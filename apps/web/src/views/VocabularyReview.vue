<template>
  <div class="page-container">
    <PageHeader :title="pageTitle" description="按熟悉度筛选，逐词强化记忆" />

    <div v-if="loading" v-loading="true" style="min-height: 300px" />

    <template v-else>
      <!-- Header bar -->
      <div class="review-toolbar">
        <div class="toolbar-left">
          <el-radio-group v-model="familiarityFilter" size="default" @change="resetAndLoad">
            <el-radio-button value="">全部待复习</el-radio-button>
            <el-radio-button value="new">生词</el-radio-button>
            <el-radio-button value="learning">学习中</el-radio-button>
            <el-radio-button value="familiar">已熟悉</el-radio-button>
            <el-radio-button value="mastered">已掌握</el-radio-button>
          </el-radio-group>
        </div>
        <div class="toolbar-right">
          <span v-if="totalEntries > 0" class="review-progress">
            当前进度 {{ currentPage }} / {{ totalPages }}，共 {{ totalEntries }} 个待复习
          </span>
          <span v-else class="review-progress-empty">该筛选条件下没有词汇</span>
        </div>
      </div>

      <!-- Completed state -->
      <div v-if="totalEntries === 0 && !loading" class="review-complete">
        <el-result
          icon="success"
          :title="reviewSummary.total > 0 ? '本次复习完成！' : '复习完成！'"
          :sub-title="reviewSummary.total > 0
            ? `本次复习 ${reviewSummary.total} 词：掌握 ${reviewSummary.mastered}，熟悉 ${reviewSummary.familiar}，模糊 ${reviewSummary.learning}，不认识 ${reviewSummary.newCount}`
            : '当前筛选条件下没有需要复习的词汇'"
        >
          <template #extra>
            <el-button v-if="noteIdFilter" type="primary" @click="router.push(`/vocabulary/${noteIdFilter}`)">返回词汇笔记</el-button>
            <el-button v-if="starredFilter" type="warning" @click="router.push('/vocabulary/starred')">返回星标词汇</el-button>
            <el-button type="primary" @click="familiarityFilter = '', resetAndLoad()">查看全部</el-button>
            <el-button @click="router.push('/vocabulary/import')">导入笔记</el-button>
          </template>
        </el-result>
      </div>

      <!-- Flashcard -->
      <div v-else-if="currentEntry" class="flashcard-container">
        <div class="flashcard" :class="{ revealed: revealed }">
          <!-- Front: term only -->
          <div v-if="!revealed" class="flashcard-front" @click="reveal">
            <div class="fc-badge">
              <StatusTag type="familiarity" :value="currentEntry.familiarity" />
            </div>
            <div class="fc-term-row">
              <h2 class="fc-term">{{ currentEntry.term }}</h2>
              <button v-if="currentEntry.is_starred" class="star-indicator" title="已标星">
                <el-icon :size="18" color="#F59E0B"><StarFilled /></el-icon>
              </button>
            </div>
            <button class="speak-btn" title="发音" @click.stop="speak(currentEntry.term)">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
              </svg>
            </button>
            <p v-if="currentEntry.uk_phonetic" class="fc-ipa">UK {{ currentEntry.uk_phonetic }}</p>
            <p v-if="currentEntry.us_phonetic" class="fc-ipa">US {{ currentEntry.us_phonetic }}</p>
            <p v-else-if="!currentEntry.uk_phonetic && currentEntry.pronunciation_ipa" class="fc-ipa">{{ currentEntry.pronunciation_ipa }}</p>
            <p v-if="currentEntry.entry_type && currentEntry.entry_type !== 'word'" class="fc-type">{{ currentEntry.entry_type }}</p>
            <p class="fc-hint">点击查看释义</p>
          </div>

          <!-- Back: full details -->
          <div v-else class="flashcard-back">
            <div class="fc-back-header">
              <div style="display:flex;align-items:baseline;gap:var(--space-sm)">
                <h2 class="fc-term">{{ currentEntry.term }}</h2>
                <button class="speak-btn small" title="发音" @click.stop="speak(currentEntry.term)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                  <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
                </svg>
              </button>
            </div>
            </div>
            <p v-if="currentEntry.uk_phonetic || currentEntry.us_phonetic" class="fc-ipa-back">
              <template v-if="currentEntry.uk_phonetic">UK {{ currentEntry.uk_phonetic }}</template>
              <template v-if="currentEntry.uk_phonetic && currentEntry.us_phonetic"> &middot; </template>
              <template v-if="currentEntry.us_phonetic">US {{ currentEntry.us_phonetic }}</template>
            </p>
            <p v-else-if="currentEntry.pronunciation_ipa" class="fc-ipa-back">{{ currentEntry.pronunciation_ipa }}</p>

            <!-- Meanings -->
            <div v-if="currentEntry.meanings_json?.length" class="fc-section">
              <div class="fc-meanings">
                {{ formatTextList(currentEntry.meanings_json).join('；') }}
              </div>
            </div>

            <!-- Usages -->
            <div v-if="currentEntry.usages_json?.length" class="fc-section">
              <div class="fc-label">常见用法</div>
              <div class="tags-row">
                <el-tag v-for="(u, i) in formatTextList(currentEntry.usages_json)" :key="i" size="small" effect="plain">{{ u }}</el-tag>
              </div>
            </div>

            <!-- Examples -->
            <div v-if="currentEntry.examples_json?.length" class="fc-section">
              <div class="fc-label">例句</div>
              <div v-for="(ex, i) in currentEntry.examples_json" :key="i" class="fc-example">
                <p class="fc-example-en">{{ formatText(ex.en) }}</p>
                <p v-if="ex.zh" class="fc-example-zh">{{ formatText(ex.zh) }}</p>
              </div>
            </div>

            <!-- Mistake tips -->
            <div v-if="currentEntry.mistake_tips_json?.length" class="fc-section">
              <div class="fc-label warning">易错点</div>
              <div v-for="(tip, i) in formatTextList(currentEntry.mistake_tips_json)" :key="i" class="fc-mistake">
                {{ tip }}
              </div>
            </div>

            <!-- Comparisons -->
            <div v-if="currentEntry.comparisons_json?.length" class="fc-section">
              <div class="fc-label">易混词对比</div>
              <div v-for="(comp, i) in currentEntry.comparisons_json" :key="i" class="fc-comp">
                <span class="fc-comp-word">{{ formatComparison(comp).left }}</span>
                <span class="fc-comp-vs">vs</span>
                <span class="fc-comp-word">{{ formatComparison(comp).right }}</span>
                <span v-if="formatComparison(comp).leftMeaning" class="fc-comp-meaning">{{ formatComparison(comp).leftMeaning }}</span>
              </div>
            </div>

            <!-- Synonyms -->
            <div v-if="currentEntry.synonyms_json?.length" class="fc-section">
              <div class="fc-label">同义替换</div>
              <div class="tags-row">
                <el-tag v-for="(s, i) in formatTextList(currentEntry.synonyms_json)" :key="i" size="small" type="success">{{ s }}</el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flashcard-actions">
          <template v-if="!revealed">
            <el-button size="large" type="primary" @click="reveal">
              <el-icon><View /></el-icon>
              显示释义
            </el-button>
          </template>
          <template v-else>
            <el-button size="default" :loading="starToggling" @click.stop="toggleStar">
              <el-icon :color="currentEntry?.is_starred ? '#F59E0B' : undefined">
                <StarFilled v-if="currentEntry?.is_starred" /><Star v-else />
              </el-icon>
              {{ currentEntry?.is_starred ? '已标星' : '标星' }}
            </el-button>
            <el-button size="large" type="danger" :loading="marking" @click="markFamiliarity('new')">
              <el-icon><Close /></el-icon>
              不认识
            </el-button>
            <el-button size="large" type="warning" :loading="marking" @click="markFamiliarity('learning')">
              <el-icon><QuestionFilled /></el-icon>
              模糊
            </el-button>
            <el-button size="large" type="success" :loading="marking" @click="markFamiliarity('familiar')">
              <el-icon><CircleCheck /></el-icon>
              熟悉
            </el-button>
            <el-button size="large" type="primary" :loading="marking" @click="markFamiliarity('mastered')">
              <el-icon><Star /></el-icon>
              掌握
            </el-button>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View, Close, QuestionFilled, CircleCheck, Star, StarFilled } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import { useRoute } from 'vue-router'
import { getReviewEntries, reviewEntry, starEntry } from '@/api/vocabulary'
import { useSpeech } from '@/composables/useSpeech'
import type { VocabularyEntry } from '@/types'
import { formatText, formatTextList, formatComparison } from '@/utils/vocabularyFormat'

const router = useRouter()
const route = useRoute()
const { speak } = useSpeech()
const loading = ref(true)
const entries = ref<VocabularyEntry[]>([])
const totalEntries = ref(0)
const currentPage = ref(1)
const pageSize = ref(1)
const familiarityFilter = ref('')
const revealed = ref(false)
const marking = ref(false)
const starToggling = ref(false)
const searchQuery = ref('')

// Star tracking
const starReviewedCount = ref(0)

// v0.3.0: support note_id and due params from route query
const noteIdFilter = computed(() => {
  const q = route.query?.note_id
  return q ? parseInt(q as string) : undefined
})
const dueFilter = computed(() => {
  return (route.query?.due as string) || undefined
})
const starredFilter = computed(() => {
  return (route.query?.starred as string) === 'true'
})
const pageTitle = computed(() => {
  if (starredFilter.value) return '复习星标词汇'
  if (noteIdFilter.value) return '复习本次新增词汇'
  if (dueFilter.value === 'today') return '今日待复习'
  return '词汇复习'
})

// Review summary
const reviewSummary = ref({ total: 0, mastered: 0, familiar: 0, learning: 0, newCount: 0 })
const reviewComplete = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(totalEntries.value / pageSize.value)))

const currentEntry = computed(() => {
  return entries.value[0] || null
})

async function loadReview() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (familiarityFilter.value) params.familiarity = familiarityFilter.value
    if (searchQuery.value) params.q = searchQuery.value
    if (noteIdFilter.value) params.note_id = noteIdFilter.value
    if (dueFilter.value === 'today') params.due = 'today'
    if (starredFilter.value) params.starred = true

    const res = await getReviewEntries(params)
    entries.value = res.data?.items ?? []
    totalEntries.value = res.data?.total ?? 0
    revealed.value = false

    if (entries.value.length === 0 && currentPage.value > 1) {
      currentPage.value = Math.max(1, currentPage.value - 1)
      await loadReview()
      return
    }
  } catch {
    ElMessage.error('加载复习列表失败')
  } finally {
    loading.value = false
  }
}

function resetAndLoad() {
  currentPage.value = 1
  revealed.value = false
  loadReview()
}

function reveal() {
  revealed.value = true
}

const ACTION_MAP: Record<string, string> = {
  new: 'again', learning: 'hard', familiar: 'good', mastered: 'easy',
}

async function markFamiliarity(newFamiliarity: string) {
  if (!currentEntry.value || marking.value) return
  const action = ACTION_MAP[newFamiliarity] || 'again'
  marking.value = true
  try {
    await reviewEntry(currentEntry.value.id, action)
    if (currentEntry.value.is_starred) starReviewedCount.value += 1
    ElMessage.success(`已标记为「${familiarityLabel(newFamiliarity)}」`)

    // Update summary
    reviewSummary.value.total += 1
    if (newFamiliarity === 'mastered') reviewSummary.value.mastered += 1
    else if (newFamiliarity === 'familiar') reviewSummary.value.familiar += 1
    else if (newFamiliarity === 'learning') reviewSummary.value.learning += 1
    else reviewSummary.value.newCount += 1

    revealed.value = false
    currentPage.value = currentPage.value + 1

    if (currentPage.value > totalPages.value) {
      reviewComplete.value = true
      currentPage.value = 1
    }

    await loadReview()
  } catch {
    ElMessage.error('更新失败')
  } finally {
    marking.value = false
  }
}

async function toggleStar() {
  if (!currentEntry.value || starToggling.value) return
  starToggling.value = true
  try {
    const newState = !currentEntry.value.is_starred
    await starEntry(currentEntry.value.id, {
      is_starred: newState,
      star_note: currentEntry.value.star_note,
      star_priority: currentEntry.value.star_priority || 'normal',
    })
    currentEntry.value.is_starred = newState
    ElMessage.success(newState ? '已标星' : '已取消星标')
  } catch {
    ElMessage.error('操作失败')
  } finally {
    starToggling.value = false
  }
}

function familiarityLabel(f: string): string {
  const map: Record<string, string> = {
    new: '不认识',
    learning: '模糊',
    familiar: '熟悉',
    mastered: '掌握',
  }
  return map[f] || f
}

onMounted(loadReview)
</script>

<style scoped>
.review-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
  flex-wrap: wrap;
  gap: var(--space-md);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.review-progress {
  font-size: var(--text-body);
  font-weight: 600;
  color: var(--color-primary);
}

.review-progress-empty {
  font-size: var(--text-body);
  color: var(--color-text-tertiary);
}

.review-complete {
  margin-top: var(--space-2xl);
}

.flashcard-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xl);
}

.flashcard {
  width: 100%;
  max-width: 640px;
  min-height: 280px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  border: 2px solid var(--color-border);
  padding: var(--space-2xl);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.flashcard:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-card-hover);
}

.flashcard.revealed {
  cursor: default;
  border-color: var(--color-primary);
}

.flashcard-front {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
}

.fc-badge {
  margin-bottom: var(--space-sm);
}

.fc-term-row {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}
.fc-term-row .fc-term { margin-bottom: 0; }
.star-indicator {
  display: inline-flex;
  border: none;
  background: none;
  cursor: pointer;
  padding: 0;
}
.fc-term {
  font-size: 36px;
  font-weight: 800;
  color: var(--color-text-primary);
  letter-spacing: -0.03em;
}

.fc-type {
  font-size: var(--text-body);
  color: var(--color-text-tertiary);
}

.fc-hint {
  font-size: var(--text-body);
  color: var(--color-text-tertiary);
  margin-top: var(--space-md);
}

.speak-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: var(--color-bg);
  border-radius: 50%;
  cursor: pointer;
  color: var(--color-text-tertiary);
  transition: all 0.15s ease;
  flex-shrink: 0;
  margin-top: var(--space-sm);
}

.speak-btn.small {
  width: 28px;
  height: 28px;
  margin-top: 0;
}

.speak-btn:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.fc-ipa {
  font-size: 14px;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  color: var(--color-text-tertiary);
  letter-spacing: 0.02em;
}

.fc-ipa-back {
  font-size: 14px;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  color: var(--color-text-tertiary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.fc-back-header {
  display: flex;
  align-items: baseline;
  gap: var(--space-sm);
}

.flashcard-back {
  flex: 1;
}

.flashcard-back .fc-term {
  margin-bottom: var(--space-xl);
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.fc-section {
  margin-bottom: var(--space-lg);
}

.fc-label {
  font-size: var(--text-caption);
  font-weight: 700;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: var(--space-sm);
}

.fc-label.warning { color: #D97706; }

.fc-meanings {
  background: #F0F4FF;
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  font-size: var(--text-body);
  color: var(--color-text-primary);
  line-height: 1.8;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.fc-example {
  padding: var(--space-sm) var(--space-md);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-xs);
}

.fc-example-en {
  font-size: var(--text-body);
  color: var(--color-text-primary);
  font-weight: 500;
}

.fc-example-zh {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
}

.fc-mistake {
  font-size: var(--text-body);
  color: #92400E;
  background: #FFFBEB;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-xs);
  border-left: 3px solid #F59E0B;
}

.fc-comp {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-xs);
  flex-wrap: wrap;
}

.fc-comp-word {
  font-weight: 600;
  color: var(--color-primary);
}

.fc-comp-vs {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
}

.fc-comp-meaning {
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
  margin-left: auto;
}

.flashcard-actions {
  display: flex;
  gap: var(--space-md);
  flex-wrap: wrap;
  justify-content: center;
}
</style>
