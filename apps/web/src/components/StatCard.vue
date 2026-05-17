<template>
  <div class="stat-card">
    <div class="stat-icon" :style="{ background: iconBg }">
      <el-icon :size="20" :color="color || '#4F6EF7'">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="stat-body">
      <span class="stat-label">{{ label }}</span>
      <div class="stat-value-row">
        <span class="stat-value">{{ formattedValue }}</span>
        <span v-if="trend" class="stat-trend" :class="trendClass">
          <span class="trend-arrow">{{ trendArrow }}</span>
          {{ trend }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  icon: any
  label: string
  value: string | number
  trend?: string
  color?: string
}>()

const iconBg = computed(() => {
  const c = props.color || 'var(--color-primary)'
  return `${c}15`
})

const formattedValue = computed(() => {
  const v = props.value
  if (v === null || v === undefined) return '--'
  if (typeof v === 'number') {
    if (Number.isInteger(v)) return v.toLocaleString()
    return v.toFixed(1)
  }
  return v
})

const trendArrow = computed(() => {
  if (!props.trend) return ''
  return props.trend.startsWith('+') ? '↑' : '↓'
})

const trendClass = computed(() => {
  if (!props.trend) return ''
  return props.trend.startsWith('+') ? 'trend-up' : 'trend-down'
})
</script>

<style scoped>
.stat-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border);
  display: flex;
  align-items: flex-start;
  gap: var(--space-lg);
  transition: box-shadow 0.2s ease;
}

.stat-card:hover {
  box-shadow: var(--shadow-card-hover);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-body {
  flex: 1;
  min-width: 0;
}

.stat-label {
  display: block;
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

.stat-value-row {
  display: flex;
  align-items: baseline;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.stat-value {
  font-size: var(--text-data);
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.stat-trend {
  font-size: var(--text-caption);
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.trend-arrow {
  margin-right: 1px;
}

.trend-up {
  color: #16A34A;
  background: var(--color-success-light);
}

.trend-down {
  color: #DC2626;
  background: var(--color-danger-light);
}
</style>
