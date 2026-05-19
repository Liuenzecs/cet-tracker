import apiClient from './client'
import type { WeeklyReport } from '@/types'

export function getWeeklyReport(params?: Record<string, any>) {
  return apiClient.get<WeeklyReport>('/reports/weekly', { params })
}

export function getMonthlyReport(params?: Record<string, any>) {
  return apiClient.get<WeeklyReport>('/reports/monthly', { params })
}
