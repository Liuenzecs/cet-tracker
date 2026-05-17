<template>
  <div class="page-container">
    <PageHeader title="词汇复习" description="按熟悉度筛选，强化记忆薄弱词汇" />

    <div v-if="loading" v-loading="true" style="min-height: 300px" />

    <template v-else>
      <!-- Filter -->
      <div class="review-filter">
        <el-radio-group v-model="familiarityFilter" size="default" @change="loadReview">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="new">生词</el-radio-button>
          <el-radio-button value="learning">学习中</el-radio-button>
        </el-radio-group>
        <span v-if="entries.length > 0" class="review-progress">
          {{ currentIndex + 1 }} / {{ entries.length }}
        </span>
      </div>

      <!-- Empty state -->
      <EmptyState
        v-if="entries.length === 0 && !loading"
        :title="familiarityFilter === 'new' ? '没有生词需要复习' : '没有需要复习的词汇'"
        :description="familiarityFilter === 'new' ? '所有生词都已进入学习状态，切换到「学习中」筛选继续复习' : '导入更多词汇笔记来扩充你的词汇库'"
        :action-text="familiarityFilter === 'new' ? '查看全部' : '导入笔记'"
        @action="familiarityFilter === 'new' ? (familiarityFilter = '', loadReview()) : router.push('/vocabulary/import')"
      >
        <template #icon>
          <el-icon :size="48" color="#D1D5DB"><CircleCheck /></el-icon>
        </template>
      </EmptyState>

      <!-- Flashcard -->
      <div v-else class="flashcard-container">
        <div class="flashcard" :class="{ revealed: revealed }">
          <!-- Front: term only -->
          <div v-if="!revealed" class="flashcard-front" @click="reveal">
            <div class="fc-badge">
              <StatusTag type="familiarity" :value="currentEntry.familiarity" />
            </div>
            <h2 class="fc-term">{{ currentEntry.term }}</h2>
            <p class="fc-hint">点击查看释义</p>
          </div>

          <!-- Back: full details -->
          <div v-else class="flashcard-back">
            <h2 class="fc-term">{{ currentEntry.term }}</h2>

            <!-- Meanings -->
            <div v-if="currentEntry.meanings_json?.length" class="fc-section">
              <div class="fc-meanings">
                {{ (currentEntry.meanings_json || []).join('；') }}
              </div>
            </div>

            <!-- Usages -->
            <div v-if="currentEntry.usages_json?.length" class="fc-section">
              <div class="fc-label">常见用法</div>
              <div class="tags-row">
                <el-tag v-for="(u, i) in currentEntry.usages_json" :key="i" size="small" effect="plain">{{ u }}</el-tag>
              </div>
            </div>

            <!-- Examples -->
            <div v-if="currentEntry.examples_json?.length" class="fc-section">
              <div class="fc-label">例句</div>
              <div v-for="(ex, i) in currentEntry.examples_json" :key="i" class="fc-example">
                <p class="fc-example-en">{{ ex.en }}</p>
                <p class="fc-example-zh">{{ ex.zh }}</p>
              </div>
            </div>

            <!-- Mistake tips -->
            <div v-if="currentEntry.mistake_tips_json?.length" class="fc-section">
              <div class="fc-label warning">易错点</div>
              <div v-for="(tip, i) in currentEntry.mistake_tips_json" :key="i" class="fc-mistake">
                {{ tip }}
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flashcard-actions">
          <template v-if="!revealed">
            <el-button size="large" @click="reveal">显示释义</el-button>
          </template>
          <template v-else>
            <el-button size="large" @click="prevEntry" :disabled="currentIndex === 0">
              <el-icon><ArrowLeft /></el-icon>
              上一个
            </el-button>
            <el-button size="large" type="success" @click="markFamiliar">
              <el-icon><CircleCheck /></el-icon>
              已熟悉
            </el-button>
            <el-button size="large" type="primary" @click="markMastered">
              <el-icon><Star /></el-icon>
              已掌握
            </el-button>
            <el-button size="large" @click="nextEntry" :disabled="currentIndex >= entries.length - 1">
              下一个
              <el-icon><ArrowRight /></el-icon>
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
import { CircleCheck, Star, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getReviewEntries, updateVocabularyEntry } from '@/api/vocabulary'
import type { VocabularyEntry } from '@/types'

const router = useRouter()
const loading = ref(true)
const entries = ref<VocabularyEntry[]>([])
const familiarityFilter = ref('')
const currentIndex = ref(0)
const revealed = ref(false)

const currentEntry = computed(() => {
  return entries.value[currentIndex.value] || ({} as VocabularyEntry)
})

async function loadReview() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (familiarityFilter.value) params.familiarity = familiarityFilter.value
    const res = await getReviewEntries(params)
    entries.value = res.data ?? []
    currentIndex.value = 0
    revealed.value = false
  } catch {
    ElMessage.error('加载复习列表失败')
  } finally {
    loading.value = false
  }
}

function reveal() {
  revealed.value = true
}

function nextEntry() {
  if (currentIndex.value < entries.value.length - 1) {
    currentIndex.value++
    revealed.value = false
  }
}

function prevEntry() {
  if (currentIndex.value > 0) {
    currentIndex.value--
    revealed.value = false
  }
}

async function markFamiliar() {
  try {
    await updateVocabularyEntry(currentEntry.value.id, { familiarity: 'familiar' })
    ElMessage.success('已标记为「已熟悉」')
    entries.value.splice(currentIndex.value, 1)
    revealed.value = false
    if (currentIndex.value >= entries.value.length) {
      currentIndex.value = Math.max(0, entries.value.length - 1)
    }
  } catch { /* handled */ }
}

async function markMastered() {
  try {
    await updateVocabularyEntry(currentEntry.value.id, { familiarity: 'mastered' })
    ElMessage.success('已标记为「已掌握」')
    entries.value.splice(currentIndex.value, 1)
    revealed.value = false
    if (currentIndex.value >= entries.value.length) {
      currentIndex.value = Math.max(0, entries.value.length - 1)
    }
  } catch { /* handled */ }
}

onMounted(loadReview)
</script>

<style scoped>
.review-filter {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
  flex-wrap: wrap;
  gap: var(--space-md);
}

.review-progress {
  font-size: var(--text-body);
  font-weight: 600;
  color: var(--color-primary);
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

.fc-label.warning {
  color: #D97706;
}

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

.flashcard-actions {
  display: flex;
  gap: var(--space-md);
  flex-wrap: wrap;
  justify-content: center;
}
</style>
