<template>
  <div class="section-card">
    <div class="section-card-header">
      <h3 class="section-card-title">{{ title }}</h3>
      <div v-if="$slots.actions" class="section-card-actions">
        <slot name="actions" />
      </div>
    </div>
    <div class="section-card-body">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<style scoped>
.section-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border);
  border-top: 3px solid var(--color-primary);
  overflow: hidden;
}

.section-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg) var(--space-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.section-card-title {
  font-size: var(--text-card-title);
  font-weight: 600;
  color: var(--color-text-primary);
}

.section-card-actions {
  display: flex;
  gap: var(--space-sm);
}

.section-card-body {
  padding: var(--space-xl);
}
</style>
