# CET Tracker — Product Requirements Document

## Product Positioning

CET Tracker is a **local-first**, single-user desktop application for Chinese university students preparing for the College English Test (CET) Band 4 and Band 6 exams. It is not a general-purpose study tool — every feature is designed around the specific structure of CET examinations and the vocabulary acquisition patterns common among Chinese learners.

**Target users**: Chinese university students who need to track their mock exam results, record and reflect on mistakes, and systematically build vocabulary from reading and listening materials.

**Core loop**:

```
Practice → Mistake Recording → Reflection → Vocabulary Notes → Visualization → Next Review
```

Students take mock or sectional practice tests, record their results (including exactly which questions they got wrong and why), write short reflections, extract unfamiliar vocabulary into structured notebook entries, and revisit the dashboard to see progress over time. The loop closes when review sessions confirm mastery of previously unfamiliar vocabulary, which feeds back into higher accuracy on subsequent practice tests.

### Design Principles

1. **Local-first, always offline**. All data lives in a single SQLite file on the user's machine. No network is required for any feature.
2. **Data portability**. Users own their data. JSON import/export is a first-class feature, not an afterthought.
3. **Structured, not free-form**. Mistake tags, vocabulary fields, and session types are typed and constrained. The tool imposes a disciplined workflow rather than a blank page.
4. **Focused on CET**. This is not a general vocabulary app. The UI, terminology, and data model all assume CET-specific context (CET4 vs CET6, the four exam sections, Chinese-English vocabulary pairs).

---

## MVP Scope

### IN Scope

| Feature | Description |
|---------|-------------|
| Exam session tracking | Create, read, update, delete practice sessions. Each session has an exam type (CET4/CET6), a session type (full mock / listening / reading / writing / translation), a date, duration, and optional notes. |
| Listening result recording | For a listening session, record: total questions, correct count, wrong question numbers, mistake tags per wrong question, and a free-text reflection. |
| Reading result recording | For a reading session, record the same fields as listening, plus a `question_type` field (选词填空 / 长篇阅读 / 仔细阅读) since a single session can cover multiple reading question types. |
| Vocabulary notebook from Markdown import | Paste structured Markdown into an import form. The server parses it and creates structured `VocabularyEntry` rows. The note is saved even if parsing yields zero entries. |
| Card-based vocabulary display | Each vocabulary entry renders as a richly designed card — not raw Markdown. Sections (meanings, usages, examples, mistake tips, synonyms, comparisons, writing sentences) are visually distinct. |
| Dashboard with statistics and charts | Summary stat cards, accuracy trend line charts, vocabulary mastery donut chart, recent sessions list, pending review count. |
| JSON import/export | Export all data as a single JSON file. Import replaces all existing data with the imported file. Full backup and restore. |
| Local SQLite database only | No external database. Tables auto-create on first startup via the ORM. |

### Explicitly OUT of Scope

| Feature | Reason |
|---------|--------|
| User login / accounts | Single-user local app. No auth needed. |
| Cloud sync | Local-only storage. Users manage backups via JSON export. |
| AI API integration | No LLM integration in MVP. May be added as optional v2.0 feature behind user-provided API key. |
| Electron/Tauri desktop app | MVP ships as a browser-based web app served by a local Python/FastAPI backend. Desktop wrapper is deferred. |
| Spaced repetition algorithm | Vocabulary uses simple four-state mastery (new/learning/familiar/mastered). No SM-2 or similar scheduling in v1.0. |
| Official CET score calculation | Accuracy percentages and counts only. No scaled-score formula. |
| Online dictionary lookup | All vocabulary is user-created from their own study materials. |
| Mobile app | Desktop web only for MVP. |

---

## Core User Flows

### Flow 1: Create a Practice Session

1. User navigates to the Sessions page.
2. Clicks "New Session" button.
3. Fills in form fields:
   - **Exam type**: CET4 or CET6 (required, dropdown)
   - **Paper name**: free text, e.g., "2024年6月真题卷1" (required)
   - **Session type**: full_mock / listening / reading / writing / translation (required, dropdown)
   - **Date**: date picker, defaults to today (required)
   - **Duration (minutes)**: number input (optional)
   - **Notes**: textarea (optional)
4. Clicks "Save".
5. Redirected to the new session's detail page, where they can record results.

### Flow 2: Record Listening Results

1. User opens a session detail page (session_type = listening or full_mock).
2. In the Listening section, clicks "Record Result" (if no result exists) or "Edit" (if one exists).
3. Fills in:
   - **Total questions**: number (e.g., 25)
   - **Correct count**: number (e.g., 18)
   - **Wrong question numbers**: comma-separated text, e.g., "1,5,8,12,15" — parsed into JSON array `[1,5,8,12,15]`
   - **Mistake tags**: for each wrong question, select one or more tags from a preset list (e.g., "关键词没抓住", "单词不认识", "拼写错误", "逻辑理解错误", "走神"). Stored as JSON: `{"1": ["关键词没抓住"], "5": ["单词不认识"]}`
   - **Reflection**: free-text textarea for overall reflection on this listening session
4. Clicks "Save". Accuracy is calculated and displayed immediately (e.g., 72%).

### Flow 3: Record Reading Results

1. User opens a session detail page (session_type = reading or full_mock).
2. In the Reading section, clicks "Add Reading Result" — a session can have multiple reading entries (one per question type).
3. Selects **Question type**: 选词填空 / 长篇阅读 / 仔细阅读.
4. Fills in the same fields as listening (total, correct, wrong questions, tags, reflection).
5. Clicks "Save". Multiple reading results can exist per session, grouped by question_type.

### Flow 4: Import Markdown Vocabulary Notes

1. User navigates to Vocabulary page.
2. Clicks "Import Vocabulary".
3. Fills in:
   - **Title**: e.g., "2024年6月真题卷1 阅读词汇"
   - **Source session**: optional dropdown to link this note to an existing session
   - **Source section**: listening / reading / writing / translation / other
   - **Raw Markdown**: large textarea where user pastes structured Markdown (see `VOCABULARY_MARKDOWN_FORMAT.md`)
4. OPTIONAL: clicks "Preview" to see parsed entries without saving.
5. Clicks "Save". The note and all parsed entries are created.
6. User sees the vocabulary note detail page with rendered entry cards.

### Flow 5: Review Vocabulary

1. User navigates to Vocabulary page and clicks on a note.
2. Sees all entries rendered as cards.
3. Clicks on an entry to expand/reveal meanings.
4. Can change the familiarity state (new → learning → familiar → mastered) via a dropdown on each card.
5. Alternatively, opens the Review mode: filtered to "new" or "learning" entries, shows term first, user clicks to reveal meanings, then marks as familiar or mastered.
6. Progress counter shows how many have been reviewed.

### Flow 6: View Dashboard

1. User opens the app — Dashboard is the landing page.
2. Sees 4 stat cards: total sessions, avg listening accuracy, avg reading accuracy, total vocabulary count.
3. Below: listening trend chart (line chart, last 10 sessions) and reading trend chart (line chart by question type).
4. Below: recent 5 sessions list on left, vocabulary mastery donut chart on right with pending review count.
5. If no data exists, the entire dashboard shows contextual empty states with CTAs.

### Flow 7: Export/Import Data

**Export**:
1. User navigates to Settings page.
2. Under "Export", clicks "Export JSON" button.
3. Browser downloads a `.json` file containing all data (sessions, results, vocabulary).
4. Success message shown.

**Import**:
1. User navigates to Settings page.
2. Under "Import", selects a previously exported JSON file.
3. A preview shows the counts (e.g., "5 sessions, 8 listening results, 10 reading results, 3 vocabulary notes, 45 entries").
4. User clicks "Import" — a confirmation dialog warns: "This will replace ALL existing data. Continue?"
5. On confirm, all existing data is cleared and the imported data is inserted.
6. Success message with summary.

---

## Glossary

### ExamSession

A single practice attempt — either a full mock exam or a sectional practice. It is the top-level entity. It can have zero or more listening results and zero or more reading results associated with it.

### ListeningResult

The recorded outcome of a listening section within an exam session. Contains the score breakdown (total vs correct), which specific questions were wrong, categorized mistake tags, and an optional reflection. At most one listening result per session.

### ReadingResult

The recorded outcome of a reading section within an exam session. Identical fields to ListeningResult but with an additional `question_type` discriminator (选词填空 / 长篇阅读 / 仔细阅读). A session can have multiple reading results (one per question type).

### VocabularyNote

A container for a set of vocabulary entries extracted from a single source (e.g., one exam paper's reading section). Has a title, the raw Markdown that was used to generate entries, an optional link back to the source exam session, and metadata about which exam and section the vocabulary came from.

### VocabularyEntry

A single vocabulary item within a note. Contains the term, its meanings, usages, example sentences, mistake tips, synonyms, comparisons with similar words, and example writing sentences. Has a familiarity (mastery) state and review tracking fields.

### Mastery States

| State | Meaning | Typical next action |
|-------|---------|---------------------|
| **new** | Just imported, never reviewed | Review meanings, move to learning |
| **learning** | Currently being studied, not yet reliable | Practice recall, move to familiar |
| **familiar** | Generally known, occasional mistakes | Reinforce, move to mastered |
| **mastered** | Fully acquired, no further review needed | Occasional maintenance only |

These are simple user-assigned states in v1.0. No algorithmic scheduling is applied. The `review_count`, `last_reviewed_at`, and `next_review_at` fields are present in the schema but `next_review_at` is not used by any automated logic in MVP — it is reserved for the v1.1 spaced repetition feature.
