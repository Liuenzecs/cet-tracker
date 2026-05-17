<template>
  <span class="status-tag" :style="tagStyle">
    {{ displayValue }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { EXAM_TYPES, SESSION_TYPES, FAMILIARITY_MAP } from '@/types'

const props = defineProps<{
  type: 'exam_type' | 'session_type' | 'familiarity' | 'accuracy' | 'source_section'
  value: string
}>()

const tagStyle = computed(() => {
  switch (props.type) {
    case 'exam_type': {
      const isCET6 = props.value === 'CET6'
      return {
        background: isCET6 ? '#FEF2F2' : '#EFF6FF',
        color: isCET6 ? '#DC2626' : '#2563EB',
      }
    }
    case 'session_type': {
      const config: Record<string, { bg: string; color: string }> = {
        full_mock: { bg: '#F3E8FF', color: '#7C3AED' },
        listening: { bg: '#ECFDF5', color: '#059669' },
        reading: { bg: '#EFF6FF', color: '#2563EB' },
        writing: { bg: '#FFF7ED', color: '#EA580C' },
        translation: { bg: '#FDF2F8', color: '#DB2777' },
      }
      return config[props.value] || { background: '#F3F4F6', color: '#6B7280' }
    }
    case 'familiarity': {
      const fam = FAMILIARITY_MAP[props.value]
      if (fam) return { background: `${fam.color}18`, color: fam.color }
      return { background: '#F3F4F6', color: '#6B7280' }
    }
    case 'accuracy': {
      const num = parseFloat(props.value)
      if (isNaN(num)) return { background: '#F3F4F6', color: '#6B7280' }
      if (num >= 80) return { background: 'var(--color-success-light)', color: '#16A34A' }
      if (num >= 60) return { background: 'var(--color-warning-light)', color: '#D97706' }
      return { background: 'var(--color-danger-light)', color: '#DC2626' }
    }
    case 'source_section': {
      const cfg: Record<string, { bg: string; color: string }> = {
        listening: { bg: '#ECFDF5', color: '#059669' },
        reading: { bg: '#EFF6FF', color: '#2563EB' },
        writing: { bg: '#FFF7ED', color: '#EA580C' },
        translation: { bg: '#FDF2F8', color: '#DB2777' },
        other: { bg: '#F3F4F6', color: '#6B7280' },
      }
      return cfg[props.value] || { background: '#F3F4F6', color: '#6B7280' }
    }
    default:
      return { background: '#F3F4F6', color: '#6B7280' }
  }
})

const displayValue = computed(() => {
  switch (props.type) {
    case 'exam_type':
      return props.value
    case 'session_type': {
      const item = SESSION_TYPES.find((s) => s.value === props.value)
      return item?.label || props.value
    }
    case 'familiarity': {
      return FAMILIARITY_MAP[props.value]?.label || props.value
    }
    case 'accuracy':
      return `${props.value}%`
    case 'source_section':
      return props.value
    default:
      return props.value
  }
})
</script>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: var(--text-caption);
  font-weight: 600;
  line-height: 1.6;
  white-space: nowrap;
}
</style>
