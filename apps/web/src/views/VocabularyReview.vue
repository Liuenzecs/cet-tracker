<template>
  <div class="page-container">
    <PageHeader title="词汇复习" description="按熟悉度筛选，逐词强化记忆" />

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
          title="复习完成！"
          sub-title="当前筛选条件下没有需要复习的词汇"
        >
          <template #extra>
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
            <h2 class="fc-term">{{ currentEntry.term }}</h2>
            <p v-if="currentEntry.entry_type && currentEntry.entry_type !== 'word'" class="fc-type">{{ currentEntry.entry_type }}</p>
            <p class="fc-hint">点击查看释义</p>
          </div>

          <!-- Back: full details -->
          <div v-else class="flashcard-back">
            <h2 class="fc-term">{{ currentEntry.term }}</h2>

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
import { View, Close, QuestionFilled, CircleCheck, Star } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import { getReviewEntries, updateVocabularyEntry } from '@/api/vocabulary'
import type { VocabularyEntry } from '@/types'
import { formatText, formatTextList, formatComparison } from '@/utils/vocabularyFormat'

const router = useRouter()
const loading = ref(true)
const entries = ref<VocabularyEntry[]>([])
const totalEntries = ref(0)
const currentPage = ref(1)
const pageSize = ref(1)
const familiarityFilter = ref('')
const revealed = ref(false)
const marking = ref(false)
const searchQuery = ref('')

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

    const res = await getReviewEntries(params)
    entries.value = res.data?.items ?? []
    totalEntries.value = res.data?.total ?? 0
    revealed.value = false

    // If current page has no data, go to previous page or show done
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

async function markFamiliarity(newFamiliarity: string) {
  if (!currentEntry.value || marking.value) return
  marking.value = true
  try {
    await updateVocabularyEntry(currentEntry.value.id, {
      familiarity: newFamiliarity,
      last_reviewed_at: new Date().toISOString(),
    })
    ElMessage.success(`已标记为「${familiarityLabel(newFamiliarity)}」`)

    // Move to next item
    revealed.value = false
    currentPage.value = currentPage.value + 1

    // If past the end, go back to page 1
    if (currentPage.value > totalPages.value) {
      // When we've reviewed all on the current filter, reload
      currentPage.value = 1
    }

    await loadReview()
  } catch {
    ElMessage.error('更新失败')
  } finally {
    marking.value = false
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
