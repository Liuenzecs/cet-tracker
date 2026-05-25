# CET Tracker — Database Schema

## Overview

The CET Tracker uses a local **SQLite** database. All tables are auto-created on application startup via the ORM (SQLModel / SQLAlchemy). No manual migration scripts are required for first-time setup. The database file is stored locally; the application reads its path from configuration.

---

## Entity Relationship Diagram

```
exam_sessions (1) ──< (0..1) listening_results
     │
     └──< (0..n) reading_results
     │
     └──< (0..n) vocabulary_notes (via source_session_id, nullable)

vocabulary_notes (1) ──< (0..n) vocabulary_entries
```

---

## Table Definitions

### 1. exam_sessions

The top-level entity representing a single practice session.

```sql
CREATE TABLE exam_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_type       VARCHAR NOT NULL CHECK (exam_type IN ('CET4', 'CET6')),
    paper_name      VARCHAR NOT NULL,
    session_type    VARCHAR NOT NULL CHECK (session_type IN ('full_mock', 'listening', 'reading', 'writing', 'translation')),
    date            DATE NOT NULL,
    duration_minutes INTEGER,
    note            TEXT,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Column notes**:
- `exam_type`: Constrained to CET4 or CET6.
- `session_type`: Constrained to the five session types.
- `date`: The date the practice session was taken (not the date it was recorded).
- `duration_minutes`: Nullable — user may not track duration.
- `note`: Free-text notes about the session.

**Indexes**:
```sql
CREATE INDEX idx_sessions_exam_type ON exam_sessions(exam_type);
CREATE INDEX idx_sessions_session_type ON exam_sessions(session_type);
CREATE INDEX idx_sessions_date ON exam_sessions(date DESC);
```

---

### 2. listening_results

The recorded outcome of a listening section. At most one per session (enforced at the application layer).

```sql
CREATE TABLE listening_results (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id          INTEGER NOT NULL,
    total_questions     INTEGER NOT NULL,
    correct_count       INTEGER NOT NULL,
    wrong_questions_text VARCHAR,
    wrong_questions_json JSON NOT NULL DEFAULT '[]',
    mistake_tags_json    JSON NOT NULL DEFAULT '{}',
    reflection          TEXT,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES exam_sessions(id) ON DELETE CASCADE
);
```

**Column notes**:
- `wrong_questions_text`: Human-readable string, e.g., `"1,5,8,12,15"`. Stored for display convenience alongside the JSON version.
- `wrong_questions_json`: Machine-readable array, e.g., `[1, 5, 8, 12, 15]`.
- `mistake_tags_json`: Object mapping question number (as string key) to array of tag strings, e.g., `{"1": ["关键词没抓住"], "5": ["单词不认识", "走神"]}`.
- `reflection`: Free-text reflection on the listening performance.

**JSON field defaults**: `wrong_questions_json` defaults to `'[]'`, `mistake_tags_json` defaults to `'{}'`.

**Indexes**:
```sql
CREATE INDEX idx_listening_session ON listening_results(session_id);
```

---

### 3. reading_results

The recorded outcome of a reading section. A session can have multiple reading results (one per question type).

```sql
CREATE TABLE reading_results (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id          INTEGER NOT NULL,
    question_type       VARCHAR NOT NULL CHECK (question_type IN ('选词填空', '长篇阅读', '仔细阅读')),
    total_questions     INTEGER NOT NULL,
    correct_count       INTEGER NOT NULL,
    wrong_questions_text VARCHAR,
    wrong_questions_json JSON NOT NULL DEFAULT '[]',
    mistake_tags_json    JSON NOT NULL DEFAULT '{}',
    reflection          TEXT,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES exam_sessions(id) ON DELETE CASCADE
);
```

**Column notes**:
- `question_type`: The CET reading question type. This is what differentiates reading_results from listening_results — otherwise identical structure.
- Same JSON field defaults and semantics as listening_results.

**Indexes**:
```sql
CREATE INDEX idx_reading_session ON reading_results(session_id);
CREATE INDEX idx_reading_question_type ON reading_results(question_type);
```

---

### 4. vocabulary_notes

A container for vocabulary entries from a single import. Links back to a source exam session (optional).

```sql
CREATE TABLE vocabulary_notes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               VARCHAR NOT NULL,
    raw_markdown        TEXT,
    source_session_id   INTEGER,
    exam_type           VARCHAR CHECK (exam_type IN ('CET4', 'CET6')),
    paper_name          VARCHAR,
    source_section      VARCHAR CHECK (source_section IN ('listening', 'reading', 'writing', 'translation', 'other')),
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (source_session_id) REFERENCES exam_sessions(id) ON DELETE SET NULL
);
```

**Column notes**:
- `source_session_id`: Nullable. When the associated session is deleted, this is set to NULL (ON DELETE SET NULL) rather than cascading — the vocabulary note is valuable independently.
- `exam_type` and `paper_name`: Denormalized from the source session for convenience; also nullable because vocabulary can be imported standalone.
- `source_section`: Which exam section the vocabulary came from.
- `raw_markdown`: The original Markdown text that was parsed. Preserved so the user can re-parse with improved logic later.

**Indexes**:
```sql
CREATE INDEX idx_vocab_notes_source ON vocabulary_notes(source_session_id);
CREATE INDEX idx_vocab_notes_exam_type ON vocabulary_notes(exam_type);
```

---

### 5. vocabulary_entries

A single vocabulary item. Owned by a vocabulary note (CASCADE on delete).

```sql
CREATE TABLE vocabulary_entries (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id               INTEGER NOT NULL,
    term                  VARCHAR NOT NULL,
    entry_type            VARCHAR NOT NULL DEFAULT 'word' CHECK (entry_type IN ('word', 'phrase', 'proper_noun', 'unknown')),
    meanings_json         JSON NOT NULL DEFAULT '[]',
    usages_json           JSON NOT NULL DEFAULT '[]',
    examples_json         JSON NOT NULL DEFAULT '[]',
    mistake_tips_json     JSON NOT NULL DEFAULT '[]',
    synonyms_json         JSON NOT NULL DEFAULT '[]',
    comparisons_json      JSON NOT NULL DEFAULT '[]',
    writing_sentences_json JSON NOT NULL DEFAULT '[]',
    familiarity           VARCHAR NOT NULL DEFAULT 'new' CHECK (familiarity IN ('new', 'learning', 'familiar', 'mastered')),
    review_count          INTEGER NOT NULL DEFAULT 0,
    last_reviewed_at      DATETIME,
    next_review_at        DATETIME,
    tags_json             JSON NOT NULL DEFAULT '[]',
    pronunciation_ipa     VARCHAR(200),
    uk_phonetic           VARCHAR(200),
    us_phonetic           VARCHAR(200),
    created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (note_id) REFERENCES vocabulary_notes(id) ON DELETE CASCADE
);
```

**Column notes**:

| Column | Type | Description |
|--------|------|-------------|
| `entry_type` | VARCHAR | Classifies the entry: word (single word), phrase (multi-word expression), proper_noun (name/place), unknown (unparseable). Defaults to "word". |
| `meanings_json` | JSON array of strings | Chinese definitions, e.g., `["等待处理的", "悬而未决的", "即将发生的"]` |
| `usages_json` | JSON array of strings | Common collocations/patterns, e.g., `["pending decision — 待定的决定", "pending approval — 等待批准"]` |
| `examples_json` | JSON array of objects | Example sentences with translations: `[{"en": "The case is still pending.", "zh": "案件仍在审理中。"}]` |
| `mistake_tips_json` | JSON array of strings | Common mistakes or points of confusion |
| `synonyms_json` | JSON array of strings | Synonym words or expressions |
| `comparisons_json` | JSON array of objects | Comparison with similar words: `[{"word": "impending", "note": "即将发生的（通常指不好的事）"}]` |
| `writing_sentences_json` | JSON array of strings | Example sentences suitable for CET writing tasks |
| `familiarity` | VARCHAR | Mastery state. Constrained to four values. Defaults to "new". |
| `review_count` | INTEGER | How many times this entry has been reviewed. Incremented by the review feature. |
| `last_reviewed_at` | DATETIME | Timestamp of the most recent review action. |
| `next_review_at` | DATETIME | Reserved for v1.1 spaced repetition scheduling. Not used in v1.0. |
| `tags_json` | JSON array of strings | User-defined or auto-generated tags for filtering |
| `pronunciation_ipa` | VARCHAR | IPA phonetic notation. AI-generated or manually entered. Nullable. |
| `uk_phonetic` | VARCHAR | British English IPA (e.g., /ˈʃedjuːl/). Nullable. |
| `us_phonetic` | VARCHAR | American English IPA (e.g., /ˈskedʒuːl/). Nullable. |

**Indexes**:
```sql
CREATE INDEX idx_vocab_entries_note ON vocabulary_entries(note_id);
CREATE INDEX idx_vocab_entries_familiarity ON vocabulary_entries(familiarity);
CREATE INDEX idx_vocab_entries_term ON vocabulary_entries(term);
CREATE INDEX idx_vocab_entries_next_review ON vocabulary_entries(next_review_at);
```

---

## JSON Field Default Values

All JSON columns use SQLite's JSON text storage (stored as TEXT, queried with `json_extract` or parsed in application code). Default values are specified in the DDL using string literals:

| Table | Column | Default |
|-------|--------|---------|
| listening_results | wrong_questions_json | `'[]'` |
| listening_results | mistake_tags_json | `'{}'` |
| reading_results | wrong_questions_json | `'[]'` |
| reading_results | mistake_tags_json | `'{}'` |
| vocabulary_entries | meanings_json | `'[]'` |
| vocabulary_entries | usages_json | `'[]'` |
| vocabulary_entries | examples_json | `'[]'` |
| vocabulary_entries | mistake_tips_json | `'[]'` |
| vocabulary_entries | synonyms_json | `'[]'` |
| vocabulary_entries | comparisons_json | `'[]'` |
| vocabulary_entries | writing_sentences_json | `'[]'` |
| vocabulary_entries | tags_json | `'[]'` |

---

## Foreign Key Summary

```
listening_results.session_id  → exam_sessions.id    ON DELETE CASCADE
reading_results.session_id    → exam_sessions.id    ON DELETE CASCADE
vocabulary_notes.source_session_id → exam_sessions.id   ON DELETE SET NULL
vocabulary_entries.note_id    → vocabulary_notes.id  ON DELETE CASCADE
```

**Cascade behavior rationale**:
- When a session is deleted, its listening and reading results are also deleted (they have no meaning without the session).
- When a session is deleted, any vocabulary notes that referenced it have `source_session_id` set to NULL (the vocabulary remains useful independently).
- When a vocabulary note is deleted, all its entries are also deleted (entries are meaningless without their parent note).

---

## Migration Strategy

### Initial Creation (v1.0)

Tables are created automatically on first application startup using SQLModel's `SQLModel.metadata.create_all(engine)`. The order of `CREATE TABLE` statements respects foreign key dependencies:

1. `exam_sessions` (no dependencies)
2. `listening_results` (depends on exam_sessions)
3. `reading_results` (depends on exam_sessions)
4. `vocabulary_notes` (depends on exam_sessions for FK, but nullable)
5. `vocabulary_entries` (depends on vocabulary_notes)
6. `vocabulary_review_logs` (v0.3.0; depends on vocabulary_entries and vocabulary_notes)
7. `review_tasks` (v0.3.0; depends on exam_sessions)

### v0.3.0: vocabulary_review_logs

```sql
CREATE TABLE vocabulary_review_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id        INTEGER NOT NULL,
    note_id         INTEGER NOT NULL,
    old_familiarity VARCHAR(20) NOT NULL,
    new_familiarity VARCHAR(20) NOT NULL,
    action          VARCHAR(20) NOT NULL,  -- again / hard / good / easy / manual
    reviewed_at     DATETIME NOT NULL,
    note            TEXT,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entry_id) REFERENCES vocabulary_entries(id) ON DELETE CASCADE,
    FOREIGN KEY (note_id) REFERENCES vocabulary_notes(id) ON DELETE CASCADE
);
```

### v0.3.0: review_tasks

```sql
CREATE TABLE review_tasks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id    INTEGER NOT NULL,
    task_type     VARCHAR(50) NOT NULL,  -- listening_review / reading_review / vocabulary_review / ...
    title         VARCHAR(200) NOT NULL,
    description   TEXT,
    status        VARCHAR(20) NOT NULL DEFAULT 'todo',  -- todo / doing / done / skipped
    priority      VARCHAR(10) NOT NULL DEFAULT 'medium',  -- low / medium / high
    due_date      DATE,
    completed_at  DATETIME,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES exam_sessions(id) ON DELETE CASCADE
);
```

### v0.3.0: listening_results new columns

```sql
ALTER TABLE listening_results ADD COLUMN intensive_status VARCHAR(20) NOT NULL DEFAULT 'not_started';
ALTER TABLE listening_results ADD COLUMN intensive_note TEXT;
ALTER TABLE listening_results ADD COLUMN intensive_completed_at DATETIME;
```

### Future Migrations (v1.1+)

For schema changes after v1.0:
1. Use Alembic for migration management.
2. Each migration is a standalone script with `upgrade()` and `downgrade()` functions.
3. Migration files are stored in `migrations/versions/`.
4. The application checks the current schema version on startup and applies pending migrations automatically.

### SQLite PRAGMA Recommendations

```sql
PRAGMA journal_mode = WAL;       -- Better concurrent read performance
PRAGMA foreign_keys = ON;        -- Enforce FK constraints (SQLite disables by default)
PRAGMA busy_timeout = 5000;      -- Wait up to 5s if DB is locked
```
