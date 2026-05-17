import apiClient from './client'
import type { VocabularyNote, VocabularyNoteCreate, VocabularyEntry, VocabularyEntryUpdate, ParseResult } from '@/types'

export function getVocabularyNotes(params?: Record<string, any>) {
  return apiClient.get<{ items: VocabularyNote[]; total: number; page: number; page_size: number }>('/api/vocabulary/notes', { params })
}

export function getVocabularyNote(id: number) {
  return apiClient.get<VocabularyNote>(`/api/vocabulary/notes/${id}`)
}

export function createVocabularyNote(data: VocabularyNoteCreate) {
  return apiClient.post<VocabularyNote>('/api/vocabulary/notes', data)
}

export function updateVocabularyNote(id: number, data: Partial<VocabularyNoteCreate>) {
  return apiClient.put<VocabularyNote>(`/api/vocabulary/notes/${id}`, data)
}

export function deleteVocabularyNote(id: number) {
  return apiClient.delete(`/api/vocabulary/notes/${id}`)
}

export function getVocabularyEntries(noteId: number) {
  return apiClient.get<VocabularyEntry[]>(`/api/vocabulary/notes/${noteId}/entries`)
}

export function updateVocabularyEntry(id: number, data: VocabularyEntryUpdate) {
  return apiClient.put<VocabularyEntry>(`/api/vocabulary/entries/${id}`, data)
}

export function parseMarkdown(markdown: string) {
  return apiClient.post<ParseResult>('/api/vocabulary/parse-markdown', { raw_markdown: markdown })
}

export function getReviewEntries(params?: Record<string, any>) {
  return apiClient.get<VocabularyEntry[]>('/api/vocabulary/review', { params })
}
