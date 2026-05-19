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

// v0.2.1: Word-list generation (longer timeout for AI)
export function generateFromWords(data: GenerateFromWordsRequest) {
  return apiClient.post<GenerateFromWordsResponse>('/api/vocabulary/generate-from-words', data, { timeout: 180000 })
}

export function saveGeneratedNote(data: SaveGeneratedNoteRequest) {
  return apiClient.post<{ id: number; title: string; entry_count: number; created_at: string }>('/api/vocabulary/notes/from-generated', data)
}

export function appendEntriesToNote(noteId: number, data: SaveGeneratedNoteRequest) {
  return apiClient.post<{ note_id: number; title: string; appended_count: number }>(`/api/vocabulary/notes/${noteId}/append-entries`, data)
}

export function getVocabularyNotesList(params?: Record<string, any>) {
  return getVocabularyNotes(params)
}

// v0.3.0: Quality & Review
import type { DuplicateItem, ValidateSummary, ValidateItem, MasteryStats, FamiliarityTrendItem, GeneratedVocabularyEntry } from '@/types'

export function checkDuplicates(terms: string[]) {
  return apiClient.post<{ duplicates: DuplicateItem[] }>('/api/vocabulary/check-duplicates', { terms })
}

export function validateGenerated(inputWords: string[], entries: any[]) {
  return apiClient.post<{ summary: ValidateSummary; items: ValidateItem[] }>('/api/vocabulary/validate-generated', { input_words: inputWords, entries })
}

export function generateSingleWord(word: string, options?: Record<string, any>) {
  return apiClient.post<{ title: string; standardized_markdown: string; entries: GeneratedVocabularyEntry[]; warnings: string[]; source: string }>(
    '/api/vocabulary/generate-single-word', { word, options }, { timeout: 180000 }
  )
}

export function getDueToday(params?: Record<string, any>) {
  return apiClient.get<PaginatedResult<VocabularyEntry>>('/api/vocabulary/due-today', { params })
}

export function getReviewLogs(params?: Record<string, any>) {
  return apiClient.get<PaginatedResult<any>>('/api/vocabulary/review-logs', { params })
}

export function getMasteryStats() {
  return apiClient.get<MasteryStats>('/api/vocabulary/stats/mastery')
}

export function getFamiliarityTrend(params?: Record<string, any>) {
  return apiClient.get<{ items: FamiliarityTrendItem[] }>('/api/vocabulary/stats/familiarity-trend', { params })
}

export function reviewEntry(entryId: number, action: string) {
  return apiClient.put<VocabularyEntry>(`/api/vocabulary/entries/${entryId}/review?action=${action}`)
}
