import apiClient from './client'
import type { ExamSession, SessionCreate } from '@/types'

export function getSessions(params?: Record<string, any>) {
  return apiClient.get<{ items: ExamSession[]; total: number; page: number; page_size: number }>('/api/sessions', { params })
}

export function getSession(id: number) {
  return apiClient.get<ExamSession>(`/api/sessions/${id}`)
}

export function createSession(data: SessionCreate) {
  return apiClient.post<ExamSession>('/api/sessions', data)
}

export function updateSession(id: number, data: Partial<SessionCreate>) {
  return apiClient.put<ExamSession>(`/api/sessions/${id}`, data)
}

export function deleteSession(id: number) {
  return apiClient.delete(`/api/sessions/${id}`)
}
