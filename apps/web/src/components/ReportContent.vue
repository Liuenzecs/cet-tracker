<template>
  <div>
    <!-- Period -->
    <div class="report-period">
      {{ report.period?.start_date }} ~ {{ report.period?.end_date }}
    </div>

    <!-- Training -->
    <SectionCard title="训练概览">
      <div class="stat-row">
        <div class="stat-item"><span class="stat-val">{{ report.training?.session_count ?? 0 }}</span><span class="stat-lbl">训练次数</span></div>
        <div class="stat-item"><span class="stat-val">{{ report.training?.listening_count ?? 0 }}</span><span class="stat-lbl">听力训练</span></div>
        <div class="stat-item"><span class="stat-val">{{ report.training?.reading_count ?? 0 }}</span><span class="stat-lbl">阅读训练</span></div>
        <div class="stat-item"><span class="stat-val">{{ report.training?.average_listening_accuracy ? `${report.training.average_listening_accuracy}%` : '--' }}</span><span class="stat-lbl">听力均准</span></div>
        <div class="stat-item"><span class="stat-val">{{ report.training?.average_reading_accuracy ? `${report.training.average_reading_accuracy}%` : '--' }}</span><span class="stat-lbl">阅读均准</span></div>
      </div>
    </SectionCard>

    <!-- Vocabulary -->
    <SectionCard title="词汇">
      <div class="stat-row">
        <div class="stat-item"><span class="stat-val">{{ report.vocabulary?.new_entries ?? 0 }}</span><span class="stat-lbl">总词汇</span></div>
        <div class="stat-item"><span class="stat-val">{{ report.vocabulary?.review_count ?? 0 }}</span><span class="stat-lbl">复习次数</span></div>
        <div class="stat-item"><span class="stat-val">{{ report.vocabulary?.mastered_count ?? 0 }}</span><span class="stat-lbl">已掌握</span></div>
        <div class="stat-item"><span class="stat-val">{{ report.vocabulary?.due_today ?? 0 }}</span><span class="stat-lbl">待复习</span></div>
      </div>
    </SectionCard>

    <!-- Review Tasks -->
    <SectionCard title="复盘任务">
      <div class="stat-row">
        <div class="stat-item"><span class="stat-val">{{ report.review_tasks?.created ?? 0 }}</span><span class="stat-lbl">新建</span></div>
        <div class="stat-item"><span class="stat-val">{{ report.review_tasks?.completed ?? 0 }}</span><span class="stat-lbl">已完成</span></div>
        <div class="stat-item"><span class="stat-val">{{ report.review_tasks?.pending ?? 0 }}</span><span class="stat-lbl">待完成</span></div>
      </div>
    </SectionCard>

    <!-- Weaknesses -->
    <SectionCard v-if="report.weaknesses?.length" title="薄弱环节">
      <div class="tag-list">
        <el-tag v-for="(w, i) in report.weaknesses" :key="i" type="warning" size="default" style="margin-right:8px;margin-bottom:4px">{{ w }}</el-tag>
      </div>
    </SectionCard>

    <!-- Suggestions -->
    <SectionCard v-if="report.suggestions?.length" title="建议">
      <ul class="suggestions-list">
        <li v-for="(s, i) in report.suggestions" :key="i">{{ s }}</li>
      </ul>
    </SectionCard>

    <!-- Copy button -->
    <div class="copy-row">
      <el-button @click="copyReport" type="primary" plain>复制报告</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import SectionCard from '@/components/SectionCard.vue'
import type { WeeklyReport } from '@/types'

const props = defineProps<{ report: WeeklyReport }>()

function copyReport() {
  const r = props.report
  const text = [
    `CET Tracker 训练报告 (${r.period?.start_date} ~ ${r.period?.end_date})`,
    '',
    `训练: ${r.training?.session_count ?? 0} 次 (听力 ${r.training?.listening_count ?? 0}, 阅读 ${r.training?.reading_count ?? 0})`,
    `听力均准: ${r.training?.average_listening_accuracy ?? '--'}% | 阅读均准: ${r.training?.average_reading_accuracy ?? '--'}%`,
    `词汇: 复习 ${r.vocabulary?.review_count ?? 0} 次 | 掌握 ${r.vocabulary?.mastered_count ?? 0} 词 | 待复习 ${r.vocabulary?.due_today ?? 0}`,
    `复盘任务: ${r.review_tasks?.completed ?? 0}/${r.review_tasks?.created ?? 0} 完成`,
    r.weaknesses?.length ? `薄弱: ${r.weaknesses.join(', ')}` : '',
    r.suggestions?.length ? `建议: ${r.suggestions.join('; ')}` : '',
  ].filter(Boolean).join('\n')

  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('报告已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}
</script>

<style scoped>
.report-period {
  font-size: var(--text-body);
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-xl);
}
.stat-row {
  display: flex;
  gap: var(--space-xl);
  flex-wrap: wrap;
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-md);
}
.stat-val {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-primary);
}
.stat-lbl {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
  margin-top: 4px;
}
.tag-list { margin: var(--space-sm) 0; }
.suggestions-list { margin: 0; padding-left: var(--space-xl); }
.suggestions-list li { margin-bottom: var(--space-sm); color: var(--color-text-primary); }
.copy-row { margin-top: var(--space-xl); text-align: center; }
</style>
