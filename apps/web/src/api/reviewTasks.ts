import apiClient from './client'
import type { ReviewTask, ReviewTaskCreate } from '@/types'
import type { PaginatedResult } from './vocabulary'

export function getReviewTasks(params?: Record<string, any>) {
  return apiClient.get<PaginatedResult<ReviewTask>>('/review-tasks', { params })
}

export function createReviewTask(data: ReviewTaskCreate) {
  return apiClient.post<ReviewTask>('/review-tasks', data)
}

export function getReviewTask(id: number) {
  return apiClient.get<ReviewTask>(`/review-tasks/${id}`)
}

export function updateReviewTask(id: number, data: Partial<ReviewTaskCreate & { status: string; completed_at: string }>) {
  return apiClient.put<ReviewTask>(`/review-tasks/${id}`, data)
}

export function deleteReviewTask(id: number) {
  return apiClient.delete(`/review-tasks/${id}`)
}

export function generateReviewTasks(sessionId: number) {
  return apiClient.post<{ generated: string[]; total_tasks: number; tasks: ReviewTask[] }>(`/sessions/${sessionId}/generate-review-tasks`)
}
