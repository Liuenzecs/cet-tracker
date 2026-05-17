import apiClient from './client'
import type { ListeningResult, ListeningCreate } from '@/types'

export function getListeningResult(sessionId: number) {
  return apiClient.get<ListeningResult>(`/api/sessions/${sessionId}/listening`)
}

export function createListeningResult(sessionId: number, data: ListeningCreate) {
  return apiClient.post<ListeningResult>(`/api/sessions/${sessionId}/listening`, data)
}

export function updateListeningResult(id: number, data: Partial<ListeningCreate>) {
  return apiClient.put<ListeningResult>(`/api/listening/${id}`, data)
}

export function deleteListeningResult(id: number) {
  return apiClient.delete(`/api/listening/${id}`)
}
