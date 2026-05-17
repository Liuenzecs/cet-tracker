<template>
  <div class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <el-icon :size="24" color="#4F6EF7"><Reading /></el-icon>
        <span class="sidebar-title">CET Tracker</span>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <el-icon :size="18"><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <router-link to="/settings" class="nav-item" :class="{ active: isActive('/settings') }">
          <el-icon :size="18"><Setting /></el-icon>
          <span>设置</span>
        </router-link>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import {
  HomeFilled,
  DataAnalysis,
  Collection,
  Reading,
  Setting,
} from '@element-plus/icons-vue'

const route = useRoute()

interface NavItem {
  path: string
  label: string
  icon: any
}

const navItems: NavItem[] = [
  { path: '/', label: '概览', icon: HomeFilled },
  { path: '/sessions', label: '训练记录', icon: DataAnalysis },
  { path: '/vocabulary', label: '词汇笔记', icon: Collection },
  { path: '/vocabulary/review', label: '复习', icon: Reading },
  { path: '/stats', label: '统计', icon: DataAnalysis },
]

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar */
.sidebar {
  width: var(--sidebar-width);
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-xl) var(--space-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.sidebar-title {
  font-size: var(--text-card-title);
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-md) var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar-footer {
  padding: var(--space-md) var(--space-sm);
  border-top: 1px solid var(--color-border-light);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--text-body);
  font-weight: 500;
  transition: all 0.15s ease;
  cursor: pointer;
  text-decoration: none;
}

.nav-item:hover {
  background: var(--color-bg);
  color: var(--color-text-primary);
}

.nav-item.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 600;
}

.nav-item.active .el-icon {
  color: var(--color-primary);
}

/* Main Content */
.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  min-height: 100vh;
}

/* Page transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .sidebar {
    width: 64px;
  }

  .sidebar-title {
    display: none;
  }

  .sidebar-brand {
    justify-content: center;
    padding: var(--space-lg) var(--space-sm);
  }

  .nav-item span {
    display: none;
  }

  .nav-item {
    justify-content: center;
    padding: var(--space-md);
  }

  .main-content {
    margin-left: 64px;
  }
}
</style>
