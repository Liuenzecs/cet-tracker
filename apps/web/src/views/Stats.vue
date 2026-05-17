<template>
  <div class="page-container">
    <PageHeader title="学习统计" description="可视化你的备考数据，发现进步与薄弱环节" />

    <div v-if="loading" v-loading="true" style="min-height: 400px" />

    <template v-else-if="stats">
      <!-- Overview stats -->
      <div class="stat-cards-grid">
        <StatCard :icon="DataAnalysis" label="累计训练" :value="stats.total_sessions" color="#4F6EF7" />
        <StatCard :icon="Headset" label="听力训练" :value="stats.total_listening_sessions" color="#059669" />
        <StatCard :icon="Reading" label="阅读训练" :value="stats.total_reading_sessions" color="#2563EB" />
        <StatCard :icon="Collection" label="词汇总数" :value="stats.total_vocabulary" color="#7C3AED" />
      </div>

      <!-- Charts row 1 -->
      <div class="charts-grid">
        <SectionCard title="听力正确率趋势">
          <div class="chart-wrapper">
            <template v-if="hasListeningTrend">
              <v-chart :option="listeningChartOption" autoresize style="height: 320px" />
            </template>
            <EmptyState v-else title="暂无数据" description="创建听力训练记录以查看趋势" />
          </div>
        </SectionCard>

        <SectionCard title="阅读正确率趋势">
          <div class="chart-wrapper">
            <template v-if="hasReadingTrend">
              <v-chart :option="readingChartOption" autoresize style="height: 320px" />
            </template>
            <EmptyState v-else title="暂无数据" description="创建阅读训练记录以查看趋势" />
          </div>
        </SectionCard>
      </div>

      <!-- Charts row 2 -->
      <div class="charts-grid">
        <SectionCard title="词汇掌握分布">
          <div class="chart-wrapper">
            <template v-if="hasVocabData">
              <v-chart :option="vocabBarOption" autoresize style="height: 320px" />
            </template>
            <EmptyState v-else title="暂无词汇数据" />
          </div>
        </SectionCard>

        <SectionCard title="待复习">
          <div class="review-center">
            <div class="review-big-number">{{ stats.pending_review }}</div>
            <div class="review-label">词待复习</div>
            <el-button
              v-if="stats.pending_review > 0"
              type="primary"
              style="margin-top: var(--space-xl)"
              @click="router.push('/vocabulary/review')"
            >
              开始复习
            </el-button>
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
import { DataAnalysis, Headset, Reading, Collection } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import PageHeader from '@/components/PageHeader.vue'
import StatCard from '@/components/StatCard.vue'
import SectionCard from '@/components/SectionCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getDashboardStats } from '@/api/stats'
import type { DashboardStats } from '@/types'
import { FAMILIARITY_MAP } from '@/types'

use([LineChart, BarChart, GridComponent, TooltipComponent, TitleComponent, LegendComponent, CanvasRenderer])

const router = useRouter()
const loading = ref(true)
const stats = ref<DashboardStats | null>(null)

const hasListeningTrend = computed(() => (stats.value?.listening_trend?.length ?? 0) > 0)
const hasReadingTrend = computed(() => (stats.value?.reading_trend?.length ?? 0) > 0)
const hasVocabData = computed(() => {
  const v = stats.value?.vocabulary_by_familiarity
  return v && Object.values(v).some((c) => c > 0)
})

const listeningChartOption = computed(() => ({
  grid: { top: 10, right: 20, bottom: 30, left: 45 },
  tooltip: { trigger: 'axis' as const, formatter: (p: any) => `${p[0].axisValue}<br/>正确率: <b>${p[0].value}%</b>` },
  xAxis: {
    type: 'category' as const,
    data: (stats.value?.listening_trend ?? []).map((d) => d.date.slice(5)),
    axisLine: { lineStyle: { color: '#E5E7EB' } },
    axisTick: { show: false },
    axisLabel: { color: '#9CA3AF', fontSize: 12 },
  },
  yAxis: {
    type: 'value' as const, min: 0, max: 100,
    axisLabel: { color: '#9CA3AF', fontSize: 12, formatter: '{value}%' },
    splitLine: { lineStyle: { color: '#F3F4F6' } },
  },
  series: [{
    type: 'line' as const, smooth: true,
    data: (stats.value?.listening_trend ?? []).map((d) => d.accuracy),
    lineStyle: { color: '#059669', width: 2.5 },
    itemStyle: { color: '#059669' },
    areaStyle: {
      color: {
        type: 'linear' as const,
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(5, 150, 105, 0.15)' },
          { offset: 1, color: 'rgba(5, 150, 105, 0.02)' },
        ],
      },
    },
    symbol: 'circle', symbolSize: 6,
  }],
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
    name, type: 'line' as const, smooth: true,
    lineStyle: { color: colors[name] || '#4F6EF7', width: 2 },
    itemStyle: { color: colors[name] || '#4F6EF7' },
    data: data.map((d) => d.accuracy), symbol: 'circle', symbolSize: 5,
  }))

  return {
    grid: { top: 10, right: 20, bottom: 30, left: 45 },
    tooltip: { trigger: 'axis' as const },
    legend: { data: Object.keys(groups), bottom: 0, textStyle: { color: '#6B7280', fontSize: 12 } },
    xAxis: {
      type: 'category' as const, data: dates,
      axisLine: { lineStyle: { color: '#E5E7EB' } },
      axisTick: { show: false },
      axisLabel: { color: '#9CA3AF', fontSize: 12 },
    },
    yAxis: {
      type: 'value' as const, min: 0, max: 100,
      axisLabel: { color: '#9CA3AF', fontSize: 12, formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#F3F4F6' } },
    },
    series,
  }
})

const vocabBarOption = computed(() => {
  const entries = Object.entries(stats.value?.vocabulary_by_familiarity ?? {})
  return {
    grid: { top: 10, right: 20, bottom: 40, left: 45 },
    tooltip: { trigger: 'axis' as const },
    xAxis: {
      type: 'category' as const,
      data: entries.map(([k]) => FAMILIARITY_MAP[k]?.label || k),
      axisLine: { lineStyle: { color: '#E5E7EB' } },
      axisTick: { show: false },
      axisLabel: { color: '#6B7280', fontSize: 13, fontWeight: 500 },
    },
    yAxis: {
      type: 'value' as const,
      axisLabel: { color: '#9CA3AF', fontSize: 12 },
      splitLine: { lineStyle: { color: '#F3F4F6' } },
      minInterval: 1,
    },
    series: [{
      type: 'bar' as const,
      data: entries.map(([k, v]) => ({
        value: v,
        itemStyle: { color: FAMILIARITY_MAP[k]?.color || '#9CA3AF', borderRadius: [6, 6, 0, 0] },
      })),
      barWidth: '40%',
      emphasis: { itemStyle: { opacity: 0.8 } },
    }],
  }
})

const reviewCenter = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 'var(--space-2xl)',
}

onMounted(async () => {
  try {
    const res = await getDashboardStats()
    stats.value = res.data
  } catch {
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.chart-wrapper {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.review-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-2xl);
}

.review-big-number {
  font-size: 64px;
  font-weight: 800;
  color: var(--color-primary);
  letter-spacing: -0.04em;
  line-height: 1;
}

.review-label {
  font-size: var(--text-card-title);
  color: var(--color-text-secondary);
  margin-top: var(--space-sm);
  font-weight: 500;
}
</style>
