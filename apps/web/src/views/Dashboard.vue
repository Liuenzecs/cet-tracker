<template>
  <div class="page-container">
    <PageHeader title="备考概览" description="追踪你的 CET 备考进度与数据" />

    <!-- Empty state -->
    <EmptyState
      v-if="!loading && stats && stats.total_sessions === 0"
      title="开始你的 CET 备考之旅"
      description="创建第一条训练记录，开始追踪听力、阅读和词汇学习进度"
      action-text="创建训练记录"
      @action="router.push('/sessions/new')"
    >
      <template #icon>
        <el-icon :size="48" color="#D1D5DB"><Notebook /></el-icon>
      </template>
    </EmptyState>

    <template v-else>
      <!-- Stat cards row -->
      <div class="stat-cards-grid">
        <StatCard :icon="DataAnalysis" label="累计训练" :value="stats?.total_sessions ?? 0" color="#4F6EF7" />
        <StatCard
          :icon="Headset"
          label="听力正确率"
          :value="stats?.avg_listening_accuracy ? `${stats.avg_listening_accuracy.toFixed(1)}%` : '--'"
          :trend="listeningTrend"
          color="#059669"
        />
        <StatCard
          :icon="Reading"
          label="阅读正确率"
          :value="stats?.avg_reading_accuracy ? `${stats.avg_reading_accuracy.toFixed(1)}%` : '--'"
          :trend="readingTrend"
          color="#2563EB"
        />
        <StatCard :icon="Collection" label="词汇总数" :value="stats?.total_vocabulary ?? 0" color="#7C3AED" />
      </div>

      <!-- v0.3.0 Quick cards -->
      <div class="quick-cards-row">
        <div class="quick-card due-vocab" @click="router.push('/vocabulary/review?due=today')">
          <div class="qc-icon"><el-icon :size="20"><Clock /></el-icon></div>
          <div class="qc-body">
            <span class="qc-value">{{ stats?.due_vocabulary_count ?? 0 }}</span>
            <span class="qc-label">今日待复习</span>
          </div>
        </div>
        <div class="quick-card mastery" @click="router.push('/stats')">
          <div class="qc-icon"><el-icon :size="20"><TrendCharts /></el-icon></div>
          <div class="qc-body">
            <span class="qc-value">{{ (stats?.mastery_rate ?? 0).toFixed(0) }}%</span>
            <span class="qc-label">词汇掌握率</span>
          </div>
        </div>
        <div class="quick-card tasks" @click="router.push('/sessions')">
          <div class="qc-icon"><el-icon :size="20"><List /></el-icon></div>
          <div class="qc-body">
            <span class="qc-value">{{ stats?.pending_review_tasks_count ?? 0 }}</span>
            <span class="qc-label">待复盘任务</span>
          </div>
        </div>
        <div class="quick-card intensive" @click="router.push('/sessions')">
          <div class="qc-icon"><el-icon :size="20"><Headset /></el-icon></div>
          <div class="qc-body">
            <span class="qc-value">{{ stats?.intensive_pending_count ?? 0 }}</span>
            <span class="qc-label">待精听训练</span>
          </div>
        </div>
      </div>

      <!-- Quick actions -->
      <div class="quick-actions">
        <el-button type="primary" @click="router.push('/sessions/new')"><el-icon><Plus /></el-icon>新增训练记录</el-button>
        <el-button type="primary" plain @click="router.push('/vocabulary/import')"><el-icon><MagicStick /></el-icon>输入单词生成笔记</el-button>
        <el-button type="success" plain @click="router.push('/vocabulary/review?due=today')"><el-icon><Clock /></el-icon>今日复习</el-button>
        <el-button plain @click="router.push('/reports')"><el-icon><Document /></el-icon>查看周报</el-button>
      </div>

      <!-- Charts row -->
      <div class="charts-grid">
        <SectionCard title="听力正确率趋势">
          <div class="chart-wrapper">
            <template v-if="hasListeningTrend">
              <v-chart :option="listeningChartOption" autoresize style="height: 300px" />
            </template>
            <EmptyState v-else title="暂无听力数据" description="创建包含听力结果的训练记录以查看趋势" />
          </div>
        </SectionCard>

        <SectionCard title="阅读正确率趋势">
          <div class="chart-wrapper">
            <template v-if="hasReadingTrend">
              <v-chart :option="readingChartOption" autoresize style="height: 300px" />
            </template>
            <EmptyState v-else title="暂无阅读数据" description="创建包含阅读结果的训练记录以查看趋势" />
          </div>
        </SectionCard>
      </div>

      <!-- Bottom row -->
      <div class="bottom-grid">
        <SectionCard title="最近训练">
          <template #actions>
            <el-button size="small" type="primary" @click="router.push('/sessions/new')">新增训练</el-button>
          </template>
          <div v-if="recentSessions.length > 0" class="recent-sessions-list">
            <div
              v-for="session in recentSessions"
              :key="session.id"
              class="recent-session-item"
              @click="router.push(`/sessions/${session.id}`)"
            >
              <div class="rs-left">
                <span class="rs-name">{{ session.paper_name }}</span>
                <div class="rs-meta">
                  <StatusTag type="exam_type" :value="session.exam_type" />
                  <StatusTag type="session_type" :value="session.session_type" />
                  <span class="rs-date">{{ formatDate(session.date) }}</span>
                </div>
              </div>
              <div class="rs-right">
                <span class="rs-duration">{{ session.duration_minutes }} 分钟</span>
                <el-icon color="#9CA3AF"><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
          <EmptyState v-else title="暂无训练记录" action-text="创建第一条" @action="router.push('/sessions/new')" />
        </SectionCard>

        <SectionCard title="词汇掌握">
          <div class="chart-wrapper">
            <template v-if="hasVocabData">
              <v-chart :option="vocabChartOption" autoresize style="height: 260px" />
              <div class="pending-review-badge">
                待复习: <strong>{{ stats?.pending_review ?? 0 }}</strong> 词
              </div>
            </template>
            <EmptyState v-else title="暂无词汇数据" description="导入你的第一份词汇笔记" action-text="导入笔记" @action="router.push('/vocabulary/import')" />
          </div>
        </SectionCard>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Headset, Reading, Collection, ArrowRight, Notebook, Clock, TrendCharts, List, Plus, MagicStick, Document } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import PageHeader from '@/components/PageHeader.vue'
import StatCard from '@/components/StatCard.vue'
import SectionCard from '@/components/SectionCard.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getDashboardStats } from '@/api/stats'
import type { DashboardStats } from '@/types'
import { FAMILIARITY_MAP } from '@/types'

use([LineChart, PieChart, GridComponent, TooltipComponent, TitleComponent, LegendComponent, CanvasRenderer])

const router = useRouter()
const loading = ref(true)
const stats = ref<DashboardStats | null>(null)

const recentSessions = computed(() => stats.value?.recent_sessions ?? [])

const hasListeningTrend = computed(() => {
  return (stats.value?.listening_trend?.length ?? 0) > 0
})

const hasReadingTrend = computed(() => {
  return (stats.value?.reading_trend?.length ?? 0) > 0
})

const hasVocabData = computed(() => {
  const v = stats.value?.vocabulary_by_familiarity
  return v && Object.values(v).some((c) => c > 0)
})

const listeningTrend = computed(() => {
  const data = stats.value?.listening_trend ?? []
  if (data.length < 2) return undefined
  const last = data[data.length - 1].accuracy
  const prev = data[data.length - 2].accuracy
  const diff = last - prev
  return diff >= 0 ? `+${diff.toFixed(1)}%` : `${diff.toFixed(1)}%`
})

const readingTrend = computed(() => {
  const data = stats.value?.reading_trend ?? []
  if (data.length < 2) return undefined
  const last = data[data.length - 1].accuracy
  const prev = data[data.length - 2].accuracy
  const diff = last - prev
  return diff >= 0 ? `+${diff.toFixed(1)}%` : `${diff.toFixed(1)}%`
})

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

const listeningChartOption = computed(() => ({
  grid: { top: 10, right: 20, bottom: 30, left: 45 },
  tooltip: {
    trigger: 'axis',
    formatter: (p: any) => `${p[0].axisValue}<br/>正确率: <b>${p[0].value}%</b>`,
  },
  xAxis: {
    type: 'category',
    data: (stats.value?.listening_trend ?? []).map((d) => d.date.slice(5)),
    axisLine: { lineStyle: { color: '#E5E7EB' } },
    axisTick: { show: false },
    axisLabel: { color: '#9CA3AF', fontSize: 12 },
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    axisLabel: { color: '#9CA3AF', fontSize: 12, formatter: '{value}%' },
    splitLine: { lineStyle: { color: '#F3F4F6' } },
  },
  series: [
    {
      data: (stats.value?.listening_trend ?? []).map((d) => d.accuracy),
      type: 'line',
      smooth: true,
      lineStyle: { color: '#059669', width: 2.5 },
      itemStyle: { color: '#059669' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(5, 150, 105, 0.15)' },
            { offset: 1, color: 'rgba(5, 150, 105, 0.02)' },
          ],
        },
      },
      symbol: 'circle',
      symbolSize: 6,
    },
  ],
}))

const readingChartOption = computed(() => {
  const groups: Record<string, Array<{ date: string; accuracy: number }>> = {}
  for (const item of stats.value?.reading_trend ?? []) {
    if (!groups[item.question_type]) groups[item.question_type] = []
    groups[item.question_type].push(item)
  }
  const dates = Array.from(new Set<string>((stats.value?.reading_trend ?? []).map((d) => d.date.slice(5))))
  const colors: Record<string, string> = { '选词填空': '#2563EB', '长篇阅读': '#7C3AED', '仔细阅读': '#059669' }
  const series = Object.entries(groups).map(([name, data]) => ({
    name,
    type: 'line' as const,
    smooth: true,
    lineStyle: { color: colors[name] || '#4F6EF7', width: 2 },
    itemStyle: { color: colors[name] || '#4F6EF7' },
    data: data.map((d) => d.accuracy),
    symbol: 'circle',
    symbolSize: 5,
  }))

  return {
    grid: { top: 10, right: 20, bottom: 30, left: 45 },
    tooltip: { trigger: 'axis' as const },
    legend: {
      data: Object.keys(groups),
      bottom: 0,
      textStyle: { color: '#6B7280', fontSize: 12 },
    },
    xAxis: {
      type: 'category' as const,
      data: dates,
      axisLine: { lineStyle: { color: '#E5E7EB' } },
      axisTick: { show: false },
      axisLabel: { color: '#9CA3AF', fontSize: 12 },
    },
    yAxis: {
      type: 'value' as const,
      min: 0,
      max: 100,
      axisLabel: { color: '#9CA3AF', fontSize: 12, formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#F3F4F6' } },
    },
    series,
  }
})

const vocabChartOption = computed(() => {
  const data = Object.entries(stats.value?.vocabulary_by_familiarity ?? {}).map(([key, count]) => ({
    name: FAMILIARITY_MAP[key]?.label || key,
    value: count,
    itemStyle: { color: FAMILIARITY_MAP[key]?.color || '#9CA3AF' },
  }))

  return {
    tooltip: {
      trigger: 'item' as const,
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical' as const,
      right: 10,
      top: 'center',
      textStyle: { color: '#6B7280', fontSize: 12 },
    },
    series: [
      {
        type: 'pie' as const,
        radius: ['50%', '75%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        label: { show: false },
        emphasis: {
          label: { show: true, fontWeight: 'bold' },
        },
        data,
      },
    ],
  }
})

onMounted(async () => {
  try {
    const res = await getDashboardStats()
    stats.value = res.data
  } catch (err) {
    ElMessage.error('加载概览数据失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.chart-wrapper {
  min-height: 280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.pending-review-badge {
  margin-top: var(--space-sm);
  font-size: var(--text-body);
  color: var(--color-text-secondary);
}

.pending-review-badge strong {
  color: var(--color-primary);
  font-size: var(--text-card-title);
}

.recent-sessions-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.recent-session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background 0.15s ease;
  border: 1px solid transparent;
}

.recent-session-item:hover {
  background: var(--color-bg);
  border-color: var(--color-border);
}

.rs-left {
  flex: 1;
  min-width: 0;
}

.rs-name {
  font-size: var(--text-body);
  font-weight: 600;
  color: var(--color-text-primary);
  display: block;
  margin-bottom: var(--space-xs);
}

.rs-meta {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.rs-date {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
}

.rs-right {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-shrink: 0;
}

.rs-duration {
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
}

.quick-cards-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}
@media (max-width: 768px) { .quick-cards-row { grid-template-columns: repeat(2, 1fr); } }

.quick-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-lg);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid var(--color-border);
}
.quick-card:hover { transform: translateY(-1px); box-shadow: var(--shadow-card); }
.quick-card.due-vocab { background: #FFF7ED; border-color: #FDBA74; }
.quick-card.mastery { background: #F0FDF4; border-color: #86EFAC; }
.quick-card.tasks { background: #EFF6FF; border-color: #93C5FD; }
.quick-card.intensive { background: #FEF3C7; border-color: #FCD34D; }

.qc-icon { color: var(--color-text-tertiary); flex-shrink: 0; }
.qc-body { display: flex; flex-direction: column; }
.qc-value { font-size: 24px; font-weight: 800; color: var(--color-text-primary); }
.qc-label { font-size: var(--text-caption); color: var(--color-text-tertiary); }

.quick-actions {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-xl);
  flex-wrap: wrap;
}
</style>
