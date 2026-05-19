<template>
  <div class="page-container">
    <PageHeader title="周报 / 月报" description="规则化训练总结，基于本地数据生成" />

    <div v-if="loading" v-loading="true" style="min-height: 300px" />

    <template v-else>
      <el-tabs v-model="activePeriod">
        <el-tab-pane label="本周" name="weekly">
          <template v-if="weeklyReport">
            <ReportContent :report="weeklyReport" />
          </template>
          <EmptyState v-else title="暂无本周数据" description="创建训练记录和词汇笔记后即可生成周报" />
        </el-tab-pane>
        <el-tab-pane label="本月" name="monthly">
          <template v-if="monthlyReport">
            <ReportContent :report="monthlyReport" />
          </template>
          <EmptyState v-else title="暂无本月数据" description="创建训练记录和词汇笔记后即可生成月报" />
        </el-tab-pane>
      </el-tabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import ReportContent from '@/components/ReportContent.vue'
import { getWeeklyReport, getMonthlyReport } from '@/api/reports'
import type { WeeklyReport } from '@/types'

const activePeriod = ref('weekly')
const loading = ref(true)
const weeklyReport = ref<WeeklyReport | null>(null)
const monthlyReport = ref<WeeklyReport | null>(null)

onMounted(async () => {
  try {
    const [w, m] = await Promise.all([getWeeklyReport(), getMonthlyReport()])
    weeklyReport.value = w.data
    monthlyReport.value = m.data
  } catch { /* empty */ }
  finally { loading.value = false }
})
</script>
