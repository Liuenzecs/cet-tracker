<template>
  <div class="empty-state">
    <div class="empty-icon">
      <slot name="icon">
        <el-icon :size="48" color="#D1D5DB"><FolderOpened /></el-icon>
      </slot>
    </div>
    <h3 class="empty-title">{{ title }}</h3>
    <p v-if="description" class="empty-description">{{ description }}</p>
    <el-button v-if="actionText" type="primary" size="large" @click="$emit('action')">
      {{ actionText }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { FolderOpened } from '@element-plus/icons-vue'

defineProps<{
  title: string
  description?: string
  actionText?: string
}>()

defineEmits<{
  action: []
}>()
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-3xl) var(--space-xl);
  text-align: center;
}

.empty-icon {
  margin-bottom: var(--space-xl);
  opacity: 0.5;
}

.empty-title {
  font-size: var(--text-section);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
}

.empty-description {
  font-size: var(--text-body);
  color: var(--color-text-secondary);
  max-width: 360px;
  margin-bottom: var(--space-xl);
  line-height: 1.6;
}
</style>
