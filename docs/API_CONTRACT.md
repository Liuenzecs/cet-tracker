# CET Tracker — API Contract

## Base URL

All API endpoints are served from the local FastAPI server:

```
http://localhost:8000
```

---

## Envelope Format

Every API response (except the health check) uses a consistent envelope:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

On error:

```json
{
  "success": false,
  "data": null,
  "error": "Human-readable error message"
}
```

HTTP status codes:
- `200` — Success
- `201` — Created
- `400` — Bad request (validation error)
- `404` — Resource not found
- `422` — Unprocessable entity (FastAPI validation)
- `500` — Internal server error

---

## Health

### GET /health

No authentication required. Returns server status.

**Response 200**:
```json
{
  "status": "ok"
}
```

---

## Exam Sessions

### GET /api/sessions

List sessions with optional filtering and pagination.

**Query Parameters**:

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| exam_type | string | No | — | Filter: CET4 or CET6 |
| session_type | string | No | — | Filter: full_mock, listening, reading, writing, translation |
| page | integer | No | 1 | Page number (1-based) |
| page_size | integer | No | 20 | Items per page (max 200) |

**Response 200**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "exam_type": "CET4",
        "paper_name": "CET4 示例训练套卷",
        "session_type": "full_mock",
        "date": "2025-03-15",
        "duration_minutes": 130,
        "note": "First full mock attempt",
        "created_at": "2025-03-15T14:30:00",
        "updated_at": "2025-03-15T14:30:00"
      }
    ],
    "total": 12,
    "page": 1,
    "page_size": 20
  },
  "error": null
}
```

---

### POST /api/sessions

Create a new exam session.

**Request Body**:
```json
{
  "exam_type": "CET4",
  "paper_name": "CET4 示例训练套卷",
  "session_type": "full_mock",
  "date": "2025-03-15",
  "duration_minutes": 130,
  "note": "First full mock attempt"
}
```

**Validation**:
- `exam_type`: Required. Must be "CET4" or "CET6".
- `paper_name`: Required. Non-empty string.
- `session_type`: Required. Must be one of: "full_mock", "listening", "reading", "writing", "translation".
- `date`: Required. ISO 8601 date string (YYYY-MM-DD).
- `duration_minutes`: Optional. Positive integer.
- `note`: Optional. Free text.

**Response 201**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "exam_type": "CET4",
    "paper_name": "CET4 示例训练套卷",
    "session_type": "full_mock",
    "date": "2025-03-15",
    "duration_minutes": 130,
    "note": "First full mock attempt",
    "created_at": "2025-03-15T14:30:00",
    "updated_at": "2025-03-15T14:30:00"
  },
  "error": null
}
```

---

### GET /api/sessions/{id}

Get a single session with its associated listening and reading results.

**Response 200**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "exam_type": "CET4",
    "paper_name": "CET4 示例训练套卷",
    "session_type": "full_mock",
    "date": "2025-03-15",
    "duration_minutes": 130,
    "note": "First full mock attempt",
    "created_at": "2025-03-15T14:30:00",
    "updated_at": "2025-03-15T14:30:00",
    "listening_result": {
      "id": 1,
      "total_questions": 25,
      "correct_count": 18,
      "wrong_questions_text": "1,5,8,12,15",
      "wrong_questions_json": [1, 5, 8, 12, 15],
      "mistake_tags_json": {
        "1": ["关键词没抓住"],
        "5": ["单词不认识"],
        "8": ["逻辑理解错误"],
        "12": ["走神"],
        "15": ["单词不认识", "拼写错误"]
      },
      "reflection": "Need to improve concentration during long passages.",
      "created_at": "2025-03-15T15:00:00",
      "updated_at": "2025-03-15T15:00:00"
    },
    "reading_results": [
      {
        "id": 1,
        "question_type": "仔细阅读",
        "total_questions": 10,
        "correct_count": 7,
        "wrong_questions_text": "3,7,9",
        "wrong_questions_json": [3, 7, 9],
        "mistake_tags_json": {
          "3": ["单词不认识"],
          "7": ["长难句理解错误"],
          "9": ["推断过度"]
        },
        "reflection": "Careless with inference questions.",
        "created_at": "2025-03-15T15:10:00",
        "updated_at": "2025-03-15T15:10:00"
      },
      {
        "id": 2,
        "question_type": "选词填空",
        "total_questions": 10,
        "correct_count": 6,
        "wrong_questions_text": "2,4,6,10",
        "wrong_questions_json": [2, 4, 6, 10],
        "mistake_tags_json": {
          "2": ["词性判断错误"],
          "4": ["单词不认识"],
          "6": ["单词不认识"],
          "10": ["上下文理解错误"]
        },
        "reflection": "Vocabulary gap is the main issue.",
        "created_at": "2025-03-15T15:10:00",
        "updated_at": "2025-03-15T15:10:00"
      }
    ]
  },
  "error": null
}
```

**Response 404**:
```json
{
  "success": false,
  "data": null,
  "error": "Session not found"
}
```

---

### PUT /api/sessions/{id}

Update an existing exam session. All fields optional (partial update).

**Request Body**:
```json
{
  "paper_name": "CET4 示例训练套卷（修订版）",
  "note": "Updated notes after review"
}
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "exam_type": "CET4",
    "paper_name": "CET4 示例训练套卷（修订版）",
    "session_type": "full_mock",
    "date": "2025-03-15",
    "duration_minutes": 130,
    "note": "Updated notes after review",
    "created_at": "2025-03-15T14:30:00",
    "updated_at": "2025-03-15T16:00:00"
  },
  "error": null
}
```

---

### DELETE /api/sessions/{id}

Delete a session and all associated results (CASCADE). Vocabulary notes linked to this session have their `source_session_id` set to NULL.

**Response 200**:
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

---

## Listening Results

### GET /api/sessions/{session_id}/listening

Get the listening result for a specific session.

**Response 200**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "session_id": 1,
    "total_questions": 25,
    "correct_count": 18,
    "wrong_questions_text": "1,5,8,12,15",
    "wrong_questions_json": [1, 5, 8, 12, 15],
    "mistake_tags_json": {
      "1": ["关键词没抓住"],
      "5": ["单词不认识"]
    },
    "reflection": "Need to improve concentration.",
    "created_at": "2025-03-15T15:00:00",
    "updated_at": "2025-03-15T15:00:00"
  },
  "error": null
}
```

**Response 404**: Returned when the session exists but has no listening result recorded yet.
```json
{
  "success": false,
  "data": null,
  "error": "No listening result found for this session"
}
```

---

### POST /api/sessions/{session_id}/listening

Create a listening result for a session. Only one listening result per session (returns 400 if one already exists).

**Request Body**:
```json
{
  "total_questions": 25,
  "correct_count": 18,
  "wrong_questions_text": "1,5,8,12,15",
  "wrong_questions_json": [1, 5, 8, 12, 15],
  "mistake_tags_json": {
    "1": ["关键词没抓住"],
    "5": ["单词不认识"],
    "8": ["逻辑理解错误"],
    "12": ["走神"],
    "15": ["单词不认识", "拼写错误"]
  },
  "reflection": "Need to improve concentration during long passages."
}
```

**Response 201**: Returns the created listening result object (same shape as GET response).

**Response 400** (duplicate):
```json
{
  "success": false,
  "data": null,
  "error": "A listening result already exists for this session. Use PUT to update."
}
```

---

### PUT /api/listening/{id}

Update a listening result.

**Request Body**: Same fields as POST. All fields optional (partial update).

**Response 200**: Returns the updated listening result object.

---

### DELETE /api/listening/{id}

Delete a listening result.

**Response 200**:
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

---

## Reading Results

### GET /api/sessions/{session_id}/reading

Get all reading results for a session. Returns an array (empty array if none).

**Response 200**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "session_id": 1,
      "question_type": "仔细阅读",
      "total_questions": 10,
      "correct_count": 7,
      "wrong_questions_text": "3,7,9",
      "wrong_questions_json": [3, 7, 9],
      "mistake_tags_json": {
        "3": ["单词不认识"],
        "7": ["长难句理解错误"]
      },
      "reflection": "Careless with inference questions.",
      "created_at": "2025-03-15T15:10:00",
      "updated_at": "2025-03-15T15:10:00"
    }
  ],
  "error": null
}
```

---

### POST /api/sessions/{session_id}/reading

Create a reading result. Multiple reading results per session are allowed (one per question type recommended, but not enforced at the API level).

**Request Body**:
```json
{
  "question_type": "仔细阅读",
  "total_questions": 10,
  "correct_count": 7,
  "wrong_questions_text": "3,7,9",
  "wrong_questions_json": [3, 7, 9],
  "mistake_tags_json": {
    "3": ["单词不认识"],
    "7": ["长难句理解错误"],
    "9": ["推断过度"]
  },
  "reflection": "Careless with inference questions."
}
```

**Response 201**: Returns the created reading result object.

---

### PUT /api/reading/{id}

Update a reading result.

**Request Body**: Same fields as POST. All fields optional (partial update).

**Response 200**: Returns the updated reading result object.

---

### DELETE /api/reading/{id}

Delete a reading result.

**Response 200**:
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

---

## Vocabulary

### GET /api/vocabulary/notes

List all vocabulary notes.

**Query Parameters**:

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| exam_type | string | No | — | Filter: CET4 or CET6 |
| source_section | string | No | — | Filter: listening, reading, writing, translation, other |
| source_session_id | integer | No | — | Filter by linked training session |
| page | integer | No | 1 | Page number |
| page_size | integer | No | 20 | Items per page (max 200) |

**Response 200**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "CET4 示例训练阅读词汇",
        "source_session_id": 1,
        "exam_type": "CET4",
        "paper_name": "CET4 示例训练套卷",
        "source_section": "reading",
        "entry_count": 25,
        "created_at": "2025-03-16T10:00:00",
        "updated_at": "2025-03-16T10:00:00"
      }
    ],
    "total": 5,
    "page": 1,
    "page_size": 20
  },
  "error": null
}
```

Note: `entry_count` is a computed field (COUNT of vocabulary_entries for this note). `raw_markdown` is NOT included in the list response to keep payloads small.

---

### POST /api/vocabulary/notes

Create a vocabulary note with parsed entries from raw Markdown.

**Request Body**:
```json
{
  "title": "CET4 示例训练阅读词汇",
  "raw_markdown": "## 1. pending\n\n### 释义\n等待处理的；悬而未决的\n\n### 例句\n- The case is still pending. — 案件仍在审理中。",
  "source_session_id": 1,
  "exam_type": "CET4",
  "paper_name": "CET4 示例训练套卷",
  "source_section": "reading"
}
```

**Behavior**:
1. The note is created in `vocabulary_notes`.
2. `raw_markdown` is parsed according to the rules in `VOCABULARY_MARKDOWN_FORMAT.md`.
3. Each parsed entry becomes a `vocabulary_entries` row linked to the note.
4. If parsing yields zero entries, the note is still saved (the user can re-import later).
5. If a `source_session_id` is provided and the session has `exam_type` and `paper_name`, those values are auto-populated on the note if not explicitly provided.

**Response 201**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "CET4 示例训练阅读词汇",
    "source_session_id": 1,
    "exam_type": "CET4",
    "paper_name": "CET4 示例训练套卷",
    "source_section": "reading",
    "entry_count": 2,
    "created_at": "2025-03-16T10:00:00",
    "updated_at": "2025-03-16T10:00:00"
  },
  "error": null
}
```

---

### GET /api/vocabulary/notes/{id}

Get a single vocabulary note with its entries.

**Response 200**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "CET4 示例训练阅读词汇",
    "raw_markdown": "## 1. pending\n\n### 释义\n等待处理的...",
    "source_session_id": 1,
    "exam_type": "CET4",
    "paper_name": "CET4 示例训练套卷",
    "source_section": "reading",
    "created_at": "2025-03-16T10:00:00",
    "updated_at": "2025-03-16T10:00:00",
    "entries": [
      {
        "id": 1,
        "note_id": 1,
        "term": "pending",
        "entry_type": "word",
        "meanings_json": ["等待处理的", "悬而未决的", "即将发生的"],
        "usages_json": ["pending decision — 待定的决定", "pending approval — 等待批准"],
        "examples_json": [
          {"en": "The case is still pending.", "zh": "案件仍在审理中。"}
        ],
        "mistake_tips_json": ["不是\"悬挂\"的意思（那是 suspend）"],
        "synonyms_json": ["awaiting", "undecided", "unresolved"],
        "comparisons_json": [
          {"word": "impending", "note": "即将发生的（通常指不好的事）"}
        ],
        "writing_sentences_json": [
          "With the final exam pending, students are under increasing pressure."
        ],
        "familiarity": "new",
        "review_count": 0,
        "last_reviewed_at": null,
        "next_review_at": null,
        "tags_json": [],
        "created_at": "2025-03-16T10:00:00",
        "updated_at": "2025-03-16T10:00:00"
      }
    ]
  },
  "error": null
}
```

---

### DELETE /api/vocabulary/notes/{id}

Delete a vocabulary note and all its entries (CASCADE).

**Response 200**:
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

---

### GET /api/vocabulary/notes/{id}/entries

Get entries for a note with pagination, filtering, and search.

**Query Parameters**:

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| page_size | integer | No | 10 | Items per page (max 200) |
| familiarity | string | No | — | Filter: new, learning, familiar, mastered |
| q | string | No | — | Search by term (substring match) |

**Response 200**:
```json
{
  "success": true,
  "data": {
    "items": [
      { "id": 1, "term": "pending", "familiarity": "new", ... },
      { "id": 2, "term": "sustainable", "familiarity": "learning", ... }
    ],
    "total": 25,
    "page": 1,
    "page_size": 10
  },
  "error": null
}
```

---

### PUT /api/vocabulary/entries/{id}

Update a vocabulary entry. Partial update — only send fields that changed.

**Request Body**:
```json
{
  "familiarity": "learning",
  "review_count": 1,
  "last_reviewed_at": "2025-03-17T09:00:00"
}
```

**Response 200**: Returns the updated entry object.

---

### GET /api/vocabulary/review

Get vocabulary entries for review with pagination and filtering.

**Query Parameters**:

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| page_size | integer | No | 1 | Items per page (max 200). Default 1 for flashcard mode. |
| familiarity | string | No | — | Filter: new, learning, familiar, mastered. If not provided, returns entries with "new" or "learning". |
| q | string | No | — | Search by term (substring match) |

**Response 200**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "note_id": 1,
        "term": "pending",
        "entry_type": "word",
        "meanings_json": ["等待处理的", "悬而未决的", "即将发生的"],
        "usages_json": ["pending decision — 待定的决定"],
        "examples_json": [
          {"en": "The case is still pending.", "zh": "案件仍在审理中。"}
        ],
        "familiarity": "new",
        "review_count": 0,
        "last_reviewed_at": null
      }
    ],
    "total": 105,
    "page": 1,
    "page_size": 1
  },
  "error": null
}
```

**Sorting**: Results are ordered by familiarity (new first) and then by `updated_at` descending.

---

### POST /api/vocabulary/parse-markdown

Preview parsed entries from raw Markdown without saving. Useful for the import form's "Preview" button.

**Request Body**:
```json
{
  "raw_markdown": "## 1. pending\n\n### 释义\n等待处理的\n\n### 例句\n- The case is still pending. — 案件仍在审理中。"
}
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "entries": [
      {
        "term": "pending",
        "entry_type": "word",
        "meanings_json": ["等待处理的"],
        "usages_json": [],
        "examples_json": [
          {"en": "The case is still pending.", "zh": "案件仍在审理中。"}
        ],
        "mistake_tips_json": [],
        "synonyms_json": [],
        "comparisons_json": [],
        "writing_sentences_json": [],
        "tags_json": []
      }
    ],
    "entry_count": 1
  },
  "error": null
}
```

This endpoint does NOT persist anything to the database.

---

### GET /api/vocabulary/ai-status

Check if AI normalization is configured and available.

**Response 200**:
```json
{
  "success": true,
  "data": {
    "enabled": false,
    "provider": "deepseek",
    "configured": false,
    "message": "AI 规范化未启用。请在后端 .env 中设置 AI_NORMALIZER_ENABLED=true 并重启服务。"
  },
  "error": null
}
```

This endpoint does NOT expose the API key.

---

### POST /api/vocabulary/normalize-markdown

Normalize raw markdown into structured vocabulary using AI (DeepSeek or compatible). This endpoint does NOT save anything to the database.

**Prerequisites**: AI_NORMALIZER_ENABLED=true and AI_API_KEY set in backend .env.

**Request Body**:
```json
{
  "raw_markdown": "## pending\n\n### 释义\n...",
  "provider": "deepseek"
}
```

**Response 200** (success):
```json
{
  "success": true,
  "data": {
    "title": "词汇笔记",
    "entries": [
      {
        "term": "pending",
        "entry_type": "word",
        "meanings": [
          {"pos": "adj.", "zh": "待处理的", "en": "not yet decided"}
        ],
        "usages": [
          {"pattern": "pending approval", "meaning": "等待批准"}
        ],
        "examples": [
          {"en": "The case is still pending.", "zh": "案件仍在审理中。"}
        ],
        "mistake_tips": [],
        "synonyms": ["undecided"],
        "comparisons": [],
        "writing_sentences": []
      }
    ],
    "warnings": [],
    "source": "ai"
  },
  "error": null
}
```

**Response 200** (AI not configured):
```json
{
  "success": true,
  "data": {
    "title": "",
    "entries": [],
    "warnings": ["AI 规范化未启用"],
    "source": "ai"
  },
  "error": null
}
```

---

### POST /api/vocabulary/generate-from-words

Generate structured vocabulary entries from a word list using AI. This endpoint does NOT save anything to the database.

**Prerequisites**: AI_NORMALIZER_ENABLED=true and AI_API_KEY set in backend .env.

**Request Body**:
```json
{
  "title": "CET6 阅读生词笔记",
  "exam_type": "CET6",
  "paper_name": "2024年6月第一套",
  "source_section": "reading",
  "source_session_id": null,
  "words": ["pending", "materialise", "real estate"],
  "options": {
    "detail_level": "standard",
    "example_style": "cet",
    "include_writing_sentences": true,
    "include_comparisons": true,
    "language": "zh-CN"
  }
}
```

**Validation**:
- `words`: Required. 1-50 entries, each max 100 chars.
- `exam_type`: Must be "CET4" or "CET6".
- `source_section`: Must be one of listening/reading/writing/translation/other.
- `options.detail_level`: brief / standard / detailed.
- `options.example_style`: cet / academic / daily.

**Response 200**:
```json
{
  "success": true,
  "data": {
    "title": "CET6 阅读生词笔记",
    "standardized_markdown": "# CET6 阅读生词笔记\n\n...",
    "entries": [
      {
        "term": "pending",
        "entry_type": "word",
        "meanings": [{"pos": "adj.", "zh": "待处理的", "en": "not yet decided"}],
        "usages": [{"pattern": "pending approval", "meaning": "等待批准"}],
        "examples": [{"en": "The decision is still pending.", "zh": "决定仍未作出。"}],
        "mistake_tips": ["不要和 impending 混淆"],
        "synonyms": ["undecided"],
        "comparisons": [],
        "writing_sentences": [],
        "tags": ["CET6"]
      }
    ],
    "warnings": [],
    "source": "ai"
  },
  "error": null
}
```

---

### POST /api/vocabulary/notes/from-generated

Save user-confirmed AI-generated vocabulary entries. This endpoint does NOT call AI — it persists entries that were already generated and reviewed.

**Request Body**:
```json
{
  "title": "CET6 阅读生词笔记",
  "raw_input": "pending\nmaterialise\nreal estate",
  "standardized_markdown": "# CET6...\n...",
  "source_session_id": null,
  "exam_type": "CET6",
  "paper_name": "2024年6月第一套",
  "source_section": "reading",
  "entries": [...]
}
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "CET6 阅读生词笔记",
    "entry_count": 3,
    "created_at": "2026-05-18T12:00:00"
  },
  "error": null
}
```

---

## Statistics

### GET /api/stats/dashboard

Aggregated dashboard statistics. All computed from current database state.

**Response 200**:
```json
{
  "success": true,
  "data": {
    "total_sessions": 12,
    "total_listening_sessions": 5,
    "total_reading_sessions": 8,
    "avg_listening_accuracy": 72.5,
    "avg_reading_accuracy": 68.3,
    "listening_trend": [
      {"date": "2025-03-01", "accuracy": 65.0},
      {"date": "2025-03-08", "accuracy": 68.0},
      {"date": "2025-03-15", "accuracy": 72.0},
      {"date": "2025-03-22", "accuracy": 70.0},
      {"date": "2025-03-29", "accuracy": 75.0}
    ],
    "reading_trend": [
      {"question_type": "仔细阅读", "date": "2025-03-15", "accuracy": 70.0},
      {"question_type": "选词填空", "date": "2025-03-15", "accuracy": 60.0},
      {"question_type": "仔细阅读", "date": "2025-03-22", "accuracy": 73.0}
    ],
    "total_vocabulary": 150,
    "vocabulary_by_familiarity": {
      "new": 60,
      "learning": 45,
      "familiar": 30,
      "mastered": 15
    },
    "pending_review": 105,
    "recent_sessions": [
      {
        "id": 12,
        "exam_type": "CET4",
        "paper_name": "CET4 示例训练套卷",
        "session_type": "full_mock",
        "date": "2025-03-29",
        "duration_minutes": 130
      }
    ]
  },
  "error": null
}
```

**Computation notes**:
- `total_listening_sessions`: Count of sessions where session_type is "listening" or "full_mock" AND a listening_result exists.
- `total_reading_sessions`: Count of sessions where session_type is "reading" or "full_mock" AND at least one reading_result exists.
- Accuracy for a session = (sum of correct_count / sum of total_questions) * 100 across relevant results.
- `avg_listening_accuracy`: Average accuracy across all sessions with listening results.
- `listening_trend`: Last 5 listening sessions ordered by date, each with accuracy. No `question_type`.
- `reading_trend`: Last 5 reading sessions, one point per reading result with `question_type` and accuracy.
- `pending_review`: Count of vocabulary entries where familiarity is "new" or "learning".
- `recent_sessions`: Last 5 sessions ordered by date descending. Each entry includes `duration_minutes`.

---

## Import/Export

### GET /api/export/json

Export ALL data as a single JSON file. The response triggers a file download.

**Response 200** (Content-Type: application/json, Content-Disposition: attachment):
```json
{
  "version": "1.0",
  "exported_at": "2025-03-30T12:00:00",
  "sessions": [
    {
      "id": 1,
      "exam_type": "CET4",
      "paper_name": "CET4 示例训练套卷",
      "session_type": "full_mock",
      "date": "2025-03-15",
      "duration_minutes": 130,
      "note": "First full mock attempt",
      "created_at": "2025-03-15T14:30:00",
      "updated_at": "2025-03-15T14:30:00"
    }
  ],
  "listening_results": [
    {
      "id": 1,
      "session_id": 1,
      "total_questions": 25,
      "correct_count": 18,
      "wrong_questions_text": "1,5,8,12,15",
      "wrong_questions_json": [1, 5, 8, 12, 15],
      "mistake_tags_json": {},
      "reflection": "Need to improve concentration.",
      "created_at": "2025-03-15T15:00:00",
      "updated_at": "2025-03-15T15:00:00"
    }
  ],
  "reading_results": [],
  "vocabulary_notes": [
    {
      "id": 1,
      "title": "CET4 示例训练阅读词汇",
      "raw_markdown": "...",
      "source_session_id": 1,
      "exam_type": "CET4",
      "paper_name": "CET4 示例训练套卷",
      "source_section": "reading",
      "created_at": "2025-03-16T10:00:00",
      "updated_at": "2025-03-16T10:00:00"
    }
  ],
  "vocabulary_entries": [
    {
      "id": 1,
      "note_id": 1,
      "term": "pending",
      "entry_type": "word",
      "meanings_json": [],
      "usages_json": [],
      "examples_json": [],
      "mistake_tips_json": [],
      "synonyms_json": [],
      "comparisons_json": [],
      "writing_sentences_json": [],
      "familiarity": "new",
      "review_count": 0,
      "last_reviewed_at": null,
      "next_review_at": null,
      "tags_json": [],
      "created_at": "2025-03-16T10:00:00",
      "updated_at": "2025-03-16T10:00:00"
    }
  ]
}
```

---

### POST /api/import/json

Import data from a JSON export file. **This replaces ALL existing data.**

**Request Body**: The full JSON object as produced by the export endpoint (same structure).

**Behavior**:
1. Validate the JSON structure (must have the top-level keys: sessions, listening_results, reading_results, vocabulary_notes, vocabulary_entries).
2. Within a transaction:
   a. Clear all existing data (DELETE FROM in reverse FK order: vocabulary_entries, vocabulary_notes, reading_results, listening_results, exam_sessions).
   b. Insert imported data in FK order.
3. If any step fails, the transaction is rolled back and no data is changed.

**Response 200**:
```json
{
  "success": true,
  "data": {
    "imported": {
      "sessions": 12,
      "listening_results": 8,
      "reading_results": 15,
      "vocabulary_notes": 5,
      "vocabulary_entries": 150
    }
  },
  "error": null
}
```

**Response 400** (invalid format):
```json
{
  "success": false,
  "data": null,
  "error": "Invalid import format: missing required key 'sessions'"
}
```

---

## Error Response Reference

All error responses follow this structure:

```json
{
  "success": false,
  "data": null,
  "error": "<message>"
}
```

### Common Error Messages

| HTTP Status | Error Message | When |
|-------------|---------------|------|
| 404 | "Session not found" | GET/PUT/DELETE /api/sessions/{id} with invalid id |
| 404 | "No listening result found for this session" | GET /api/sessions/{id}/listening when no result exists |
| 404 | "Vocabulary note not found" | GET/DELETE /api/vocabulary/notes/{id} with invalid id |
| 404 | "Vocabulary entry not found" | PUT /api/vocabulary/entries/{id} with invalid id |
| 400 | "A listening result already exists for this session. Use PUT to update." | POST /api/sessions/{id}/listening when one already exists |
| 400 | "Invalid import format: ..." | POST /api/import/json with malformed body |
| 422 | FastAPI validation error detail | Any endpoint with invalid request body |
| 500 | "Internal server error" | Unexpected server errors |
