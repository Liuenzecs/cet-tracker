import apiClient from './client'
import type { ReadingResult, ReadingCreate } from '@/types'

export function getReadingResults(sessionId: number) {
  return apiClient.get<ReadingResult[]>(`/api/sessions/${sessionId}/reading`)
}

export function createReadingResult(sessionId: number, data: ReadingCreate) {
  return apiClient.post<ReadingResult>(`/api/sessions/${sessionId}/reading`, data)
}

export function updateReadingResult(id: number, data: Partial<ReadingCreate>) {
  return apiClient.put<ReadingResult>(`/api/reading/${id}`, data)
}

export function deleteReadingResult(id: number) {
  return apiClient.delete(`/api/reading/${id}`)
}
