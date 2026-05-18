// API Response envelope
export interface APIResponse<T> {
  success: boolean
  data: T | null
  error: string | null
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// Exam Session
export interface ExamSession {
  id: number
  exam_type: 'CET4' | 'CET6'
  paper_name: string
  session_type: 'full_mock' | 'listening' | 'reading' | 'writing' | 'translation'
  date: string
  duration_minutes: number
  note?: string
  created_at: string
  updated_at: string
}

export interface SessionCreate {
  exam_type: string
  paper_name: string
  session_type: string
  date: string
  duration_minutes: number
  note?: string
}

// Listening Result
export interface ListeningResult {
  id: number
  session_id: number
  total_questions: number
  correct_count: number
  wrong_questions_text?: string
  wrong_questions_json: number[]
  mistake_tags_json: Record<string, string[]>
  reflection?: string
  created_at: string
  updated_at: string
}

export interface ListeningCreate {
  total_questions: number
  correct_count: number
  wrong_questions_text?: string
  wrong_questions_json?: number[]
  mistake_tags_json?: Record<string, string[]>
  reflection?: string
}

// Reading Result
export interface ReadingResult {
  id: number
  session_id: number
  question_type: string
  total_questions: number
  correct_count: number
  wrong_questions_text?: string
  wrong_questions_json: number[]
  mistake_tags_json: Record<string, string[]>
  reflection?: string
  created_at: string
  updated_at: string
}

export interface ReadingCreate {
  question_type: string
  total_questions: number
  correct_count: number
  wrong_questions_text?: string
  wrong_questions_json?: number[]
  mistake_tags_json?: Record<string, string[]>
  reflection?: string
}

// Vocabulary
export interface VocabularyNote {
  id: number
  title: string
  raw_markdown: string
  source_session_id?: number
  exam_type?: string
  paper_name?: string
  source_section: string
  entry_count?: number
  created_at: string
  updated_at: string
}

export interface VocabularyNoteCreate {
  title: string
  raw_markdown: string
  source_session_id?: number
  exam_type?: string
  paper_name?: string
  source_section: string
}

export interface VocabularyEntry {
  id: number
  note_id: number
  term: string
  entry_type: string
  meanings_json: string[]
  usages_json: string[]
  examples_json: Array<{ en: string; zh: string }>
  mistake_tips_json: string[]
  synonyms_json: string[]
  comparisons_json: any[]
  writing_sentences_json: string[]
  familiarity: 'new' | 'learning' | 'familiar' | 'mastered'
  review_count: number
  last_reviewed_at?: string
  next_review_at?: string
  tags_json: string[]
  created_at: string
  updated_at: string
}

export interface VocabularyEntryUpdate {
  term?: string
  entry_type?: string
  familiarity?: string
  last_reviewed_at?: string
  next_review_at?: string
  review_count?: number
  meanings_json?: string[]
  usages_json?: string[]
  examples_json?: Array<{ en: string; zh: string }>
  mistake_tips_json?: string[]
  synonyms_json?: string[]
  comparisons_json?: any[]
  writing_sentences_json?: string[]
  tags_json?: string[]
}

// Stats
export interface DashboardStats {
  total_sessions: number
  total_listening_sessions: number
  total_reading_sessions: number
  avg_listening_accuracy: number | null
  avg_reading_accuracy: number | null
  listening_trend: Array<{ date: string; accuracy: number }>
  reading_trend: Array<{ date: string; accuracy: number; question_type: string }>
  total_vocabulary: number
  vocabulary_by_familiarity: Record<string, number>
  pending_review: number
  recent_sessions: ExamSession[]
}

// Import/Export
export interface ExportData {
  sessions: any[]
  listening_results: any[]
  reading_results: any[]
  vocabulary_notes: any[]
  vocabulary_entries: any[]
}

export interface ParseResult {
  entries: VocabularyEntry[]
}

// AI Normalization
export interface NormalizedMeaning {
  pos: string
  zh: string
  en: string
}

export interface NormalizedUsage {
  pattern: string
  meaning: string
}

export interface NormalizedExample {
  en: string
  zh: string
}

export interface NormalizedComparison {
  left: string
  right: string
  left_meaning: string
  right_meaning: string
}

export interface NormalizedEntry {
  term: string
  entry_type: string
  meanings: NormalizedMeaning[]
  usages: NormalizedUsage[]
  examples: NormalizedExample[]
  mistake_tips: string[]
  synonyms: string[]
  comparisons: NormalizedComparison[]
  writing_sentences: string[]
}

export interface NormalizeMarkdownResponse {
  title: string
  entries: NormalizedEntry[]
  warnings: string[]
  source: string
}

export interface AIProviderStatus {
  enabled: boolean
  provider: string
  configured: boolean
  message: string
}

// v0.2.1 Word-list generation
export interface GenerationOptions {
  detail_level: 'brief' | 'standard' | 'detailed'
  example_style: 'cet' | 'academic' | 'daily'
  include_writing_sentences: boolean
  include_comparisons: boolean
  language: string
}

export interface GenerateFromWordsRequest {
  title: string
  exam_type: string
  paper_name?: string
  source_section: string
  source_session_id?: number | null
  words: string[]
  options: GenerationOptions
}

export interface GeneratedWritingSentence {
  en: string
  zh: string
}

export interface GeneratedVocabularyEntry {
  term: string
  entry_type: string
  meanings: NormalizedMeaning[]
  usages: NormalizedUsage[]
  examples: NormalizedExample[]
  mistake_tips: string[]
  synonyms: string[]
  comparisons: NormalizedComparison[]
  writing_sentences: GeneratedWritingSentence[]
  tags: string[]
}

export interface GenerateFromWordsResponse {
  title: string
  standardized_markdown: string
  entries: GeneratedVocabularyEntry[]
  warnings: string[]
  source: string
}

export interface SaveGeneratedNoteRequest {
  title: string
  raw_input: string
  standardized_markdown: string
  source_session_id?: number | null
  exam_type?: string
  paper_name?: string
  source_section: string
  entries: GeneratedVocabularyEntry[]
}

// Constants
export const EXAM_TYPES = ['CET4', 'CET6'] as const

export const SESSION_TYPES = [
  { value: 'full_mock', label: '完整模考' },
  { value: 'listening', label: '听力训练' },
  { value: 'reading', label: '阅读训练' },
  { value: 'writing', label: '写作训练' },
  { value: 'translation', label: '翻译训练' },
] as const

export const READING_QUESTION_TYPES = ['选词填空', '长篇阅读', '仔细阅读'] as const

export const FAMILIARITY_MAP: Record<string, { label: string; color: string }> = {
  new: { label: '生词', color: '#3B82F6' },
  learning: { label: '学习中', color: '#F59E0B' },
  familiar: { label: '已熟悉', color: '#22C55E' },
  mastered: { label: '已掌握', color: '#8B5CF6' },
}

export const LISTENING_MISTAKE_TAGS = [
  '听前读题不足', '关键词没抓住', '同义替换没反应过来',
  '数字/时间/地点漏听', '转折词没抓住', '选项干扰',
  '文章结构没听懂', '语速跟不上', '单词不认识', '走神',
]

export const READING_MISTAKE_TAGS = [
  '定位错误', '同义替换没看出', '句子结构没读懂',
  '词汇不认识', '选项比较不细', '主旨判断错误', '时间分配失败',
]

export const SOURCE_SECTIONS = [
  { value: 'listening', label: '听力' },
  { value: 'reading', label: '阅读' },
  { value: 'writing', label: '写作' },
  { value: 'translation', label: '翻译' },
  { value: 'other', label: '其他' },
] as const
