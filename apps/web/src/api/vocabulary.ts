import apiClient from './client'
import type { VocabularyNote, VocabularyNoteCreate, VocabularyEntry, VocabularyEntryUpdate, ParseResult, NormalizeMarkdownResponse, AIProviderStatus, GenerateFromWordsRequest, GenerateFromWordsResponse, SaveGeneratedNoteRequest } from '@/types'

export interface PaginatedResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

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

export function getVocabularyEntries(noteId: number, params?: Record<string, any>) {
  return apiClient.get<PaginatedResult<VocabularyEntry>>(`/api/vocabulary/notes/${noteId}/entries`, { params })
}

export function updateVocabularyEntry(id: number, data: VocabularyEntryUpdate) {
  return apiClient.put<VocabularyEntry>(`/api/vocabulary/entries/${id}`, data)
}

export function parseMarkdown(markdown: string) {
  return apiClient.post<ParseResult>('/api/vocabulary/parse-markdown', { raw_markdown: markdown })
}

export function normalizeMarkdown(markdown: string) {
  return apiClient.post<NormalizeMarkdownResponse>('/api/vocabulary/normalize-markdown', { raw_markdown: markdown, provider: 'deepseek' })
}

export function getAIStatus() {
  return apiClient.get<AIProviderStatus>('/api/vocabulary/ai-status')
}

export function getReviewEntries(params?: Record<string, any>) {
  return apiClient.get<PaginatedResult<VocabularyEntry>>('/api/vocabulary/review', { params })
}

// v0.2.1: Word-list generation
export function generateFromWords(data: GenerateFromWordsRequest) {
  return apiClient.post<GenerateFromWordsResponse>('/api/vocabulary/generate-from-words', data)
}

export function saveGeneratedNote(data: SaveGeneratedNoteRequest) {
  return apiClient.post<{ id: number; title: string; entry_count: number; created_at: string }>('/api/vocabulary/notes/from-generated', data)
}
