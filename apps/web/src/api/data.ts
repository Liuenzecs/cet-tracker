import apiClient from './client'
import type { ExportData } from '@/types'

export function exportDataJSON() {
  return apiClient.get<ExportData>('/api/export/json')
}

export function importDataJSON(data: ExportData) {
  return apiClient.post<{ message: string }>('/api/import/json', data)
}
