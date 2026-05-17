<template>
  <div class="page-header">
    <div class="page-header-left">
      <h1 class="page-header-title">{{ title }}</h1>
      <p v-if="description" class="page-header-desc">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="page-header-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
  gap: var(--space-lg);
}

.page-header-left {
  flex: 1;
  min-width: 0;
}

.page-header-title {
  font-size: var(--text-hero);
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
  line-height: 1.3;
}

.page-header-desc {
  font-size: var(--text-body);
  color: var(--color-text-secondary);
  margin-top: var(--space-xs);
}

.page-header-actions {
  display: flex;
  gap: var(--space-sm);
  flex-shrink: 0;
  align-items: center;
}
</style>
