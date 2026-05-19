import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
    },
    {
      path: '/sessions',
      name: 'SessionList',
      component: () => import('@/views/SessionList.vue'),
    },
    {
      path: '/sessions/new',
      name: 'SessionCreate',
      component: () => import('@/views/SessionCreate.vue'),
    },
    {
      path: '/sessions/:id',
      name: 'SessionDetail',
      component: () => import('@/views/SessionDetail.vue'),
      props: true,
    },
    {
      path: '/vocabulary',
      name: 'VocabularyList',
      component: () => import('@/views/VocabularyList.vue'),
    },
    {
      path: '/vocabulary/import',
      name: 'VocabularyImport',
      component: () => import('@/views/VocabularyImport.vue'),
    },
    {
      path: '/vocabulary/review',
      name: 'VocabularyReview',
      component: () => import('@/views/VocabularyReview.vue'),
    },
    {
      path: '/vocabulary/:id',
      name: 'VocabularyDetail',
      component: () => import('@/views/VocabularyDetail.vue'),
      props: true,
    },
    {
      path: '/stats',
      name: 'Stats',
      component: () => import('@/views/Stats.vue'),
    },
    {
      path: '/reports',
      name: 'Reports',
      component: () => import('@/views/Reports.vue'),
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('@/views/Settings.vue'),
    },
  ],
})

export default router
