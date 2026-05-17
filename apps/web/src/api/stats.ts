import apiClient from './client'
import type { DashboardStats } from '@/types'

export function getDashboardStats() {
  return apiClient.get<DashboardStats>('/api/stats/dashboard')
}
