# CET Tracker — Roadmap

## Versioning Philosophy

CET Tracker follows semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** (2.x): Architectural shifts — new deployment model, multi-user, platform expansion.
- **MINOR** (1.x): Feature batches — new capabilities that extend the product but do not redefine it.
- **PATCH** (1.0.x): Bug fixes, performance improvements, small UX refinements.

Versions are cumulative. Each version includes all features from prior versions.

---

## v1.0 — MVP (Current)

**Goal**: A complete, usable local-first CET preparation tracker. All core CRUD operations, vocabulary import, and data visualization are functional.

- [x] **Exam session CRUD** — Create, read, update, delete practice sessions with exam type, session type, date, duration, and notes.
- [x] **Listening result recording** — Record total questions, correct count, wrong question numbers with per-question mistake tags, and a free-text reflection for listening sessions.
- [x] **Reading result recording** — Same as listening, plus a `question_type` field (选词填空 / 长篇阅读 / 仔细阅读). Multiple reading results per session.
- [x] **Markdown vocabulary import** — Paste structured Markdown, parse it into structured vocabulary entries. Preview before saving. Save the note even if parsing yields zero entries.
- [x] **Card-based vocabulary display** — Each vocabulary entry renders as a richly designed card with visually distinct sections (meanings, usages, examples, mistake tips, synonyms, comparisons, writing sentences).
- [x] **Dashboard with charts** — Stat cards, listening and reading trend line charts, vocabulary mastery donut chart, recent sessions list, pending review count.
- [x] **JSON import/export** — Export all data as a single JSON file. Import replaces all existing data with a single confirmation step.
- [x] **Mastery state tracking** — Four states (new / learning / familiar / mastered) per vocabulary entry, manually assigned by the user. Review count and last reviewed timestamp tracked.

**Tech stack**:
- Backend: Python FastAPI + SQLModel + SQLite
- Frontend: Vue 3 + Element Plus + ECharts
- No authentication, no cloud services, no external APIs

---

## v1.1 — Enhanced Review

**Goal**: Make vocabulary review more effective with simple spaced repetition scheduling, better filtering, and expanded statistics.

### Spaced Repetition (Simple)

- [ ] **Review intervals**: After each review action, set `next_review_at` based on the new familiarity state:
  - new -> learning: review in 1 day
  - learning -> learning (stays): review in 3 days
  - learning -> familiar: review in 7 days
  - familiar -> familiar (stays): review in 14 days
  - familiar -> mastered: review in 30 days
  - mastered -> mastered (stays): review in 30 days
- [ ] **Dashboard reminder**: Show a count of "due for review" entries (where `next_review_at <= now` and familiarity is not mastered) on the dashboard stat cards.
- [ ] **Review queue ordering**: On the Review page, prioritize entries where `next_review_at <= now` (overdue first), then by `next_review_at` ascending.
- [ ] **Configurable intervals**: Allow users to customize the interval values from the Settings page.

### Vocabulary Search and Filter

- [ ] **Full-text search**: Search across `term`, `meanings_json`, and `examples_json`. Simple SQLite LIKE-based search for v1.1 (FTS5 in v1.2 if needed).
- [ ] **Filter by familiarity**: Quick filter chips (New / Learning / Familiar / Mastered) on the vocabulary detail and list pages.
- [ ] **Filter by source**: Filter vocabulary entries by source session or source section.
- [ ] **Filter by tag**: Filter by `tags_json` values.
- [ ] **Sort options**: By term (A-Z), by date added, by last reviewed, by review count.

### Bulk Operations

- [ ] **Batch set familiarity**: Select multiple vocabulary entries and set all to a chosen familiarity state.
- [ ] **Batch delete entries**: Select and delete multiple entries from a vocabulary note.
- [ ] **Merge notes**: Combine two vocabulary notes into one (entries move to the target note).

### Writing and Translation Modules

- [ ] **Writing result recording**: New result type for writing practice. Fields: topic/prompt, word count, time spent, self-rating (1-5 on content/organization/language), reflection.
- [ ] **Translation result recording**: New result type for translation practice. Fields: source text, translated text, self-rating (1-5 on accuracy/fluency/completeness), key mistakes, reflection.
- [ ] **Dashboard integration**: Include writing and translation session counts, average self-ratings, and trend charts on the dashboard.

### Enhanced Statistics

- [ ] **Accuracy by question type**: On dashboard, break down reading accuracy by question type (选词填空 vs 长篇阅读 vs 仔细阅读) as a grouped bar chart.
- [ ] **Error tag analysis**: Pie or bar chart showing distribution of mistake tags (e.g., "单词不认识: 45次", "关键词没抓住: 23次") to help users identify weak areas.
- [ ] **Session heatmap**: Calendar heatmap showing practice frequency per day (GitHub-style contribution graph).
- [ ] **Weekly/Monthly summaries**: Aggregated stats for the current week and month vs previous periods.

### Export Enhancements

- [ ] **Anki-compatible CSV export**: Export vocabulary entries as a CSV file compatible with Anki import (fields: term, meanings, examples, tags).
- [ ] **Selective export**: Export only vocabulary, only sessions, or only a specific date range.

---

## v1.2 — Deepen Features

**Goal**: Add user customization, richer content, and quality-of-life improvements that make the tool feel more personal and comprehensive.

### Custom Error Tags

- [ ] **User-defined tags**: Allow users to create, edit, and delete custom mistake tags beyond the built-in defaults.
- [ ] **Tag management page**: Settings sub-page for managing custom tags (CRUD, color assignment).
- [ ] **Tag colors**: Assign colors to tags for visual distinction in charts and on result cards.

### Exam Paper Library

- [ ] **Pre-populated paper names**: Built-in list of known CET-4 and CET-6 exam papers organized by year and month (e.g., "2024年6月真题卷1", "2024年6月真题卷2", "2024年6月真题卷3").
- [ ] **Quick-select on session create**: Autocomplete or cascading dropdown (Year -> Month -> Paper) when creating a session.
- [ ] **Paper metadata**: Each paper can have a difficulty rating and a note about which sections are included.

### Goal Setting and Progress

- [ ] **Target score**: User sets a target CET score or accuracy goal.
- [ ] **Progress bar**: Visual progress toward the target on the dashboard.
- [ ] **Session milestones**: Celebrate milestones (10 sessions, 50 sessions, 100 vocabulary entries, etc.) with a subtle achievement notification.
- [ ] **Weekly goal**: Set a weekly practice target (e.g., "3 sessions per week") with a progress indicator.

### Study Streak Calendar

- [ ] **Calendar heatmap**: GitHub-style contribution graph showing days with practice activity.
- [ ] **Current streak**: Display consecutive days with at least one session.
- [ ] **Longest streak**: Track and display the record streak.

### Audio for Vocabulary

- [ ] **Local TTS playback**: Use the browser's built-in Web Speech API (`SpeechSynthesis`) to pronounce vocabulary terms on demand. No external API required.
- [ ] **Play button per entry**: Small speaker icon on each vocabulary entry card.
- [ ] **Auto-play option**: Optional setting to auto-pronounce the term when reviewing.
- [ ] **Pre-downloaded audio** (stretch): Bundle common CET vocabulary audio files (optional download within the app).

### Dark Mode

- [ ] **Dark theme**: Full dark mode support with a carefully designed dark color palette (not just inverted colors).
- [ ] **Theme toggle**: Switch in Settings or persistent toggle in the sidebar footer.
- [ ] **System preference detection**: Auto-detect `prefers-color-scheme: dark` on first load.
- [ ] **Dark chart styles**: Chart colors and grid lines adapted for dark backgrounds.

---

## v2.0 — Future

**Goal**: Transform CET Tracker from a single-user local tool into a more powerful, extensible platform. These features represent significant architectural changes and will require careful planning.

### AI-Powered Vocabulary (Optional)

- [ ] **LLM integration behind user-provided API key**: User brings their own API key (OpenAI, Anthropic, or local LLM endpoint). No API costs are incurred by the application itself.
- [ ] **Auto-generate vocabulary from text**: Paste a reading passage, the LLM extracts unfamiliar/academic vocabulary and generates structured entries in the Markdown format.
- [ ] **Auto-generate example sentences**: Given a word, generate CET-appropriate example sentences.
- [ ] **Smart mistake tag suggestion**: Based on reflection text, suggest relevant mistake tags.
- [ ] **Writing feedback**: Optional AI review of writing practice submissions (grammar, vocabulary usage, structure).
- [ ] **Privacy-first design**: All AI features are opt-in. API calls are made directly from the user's browser or local server using their own key. No data is sent to third-party servers owned by the application.

### Multi-User Support

- [ ] **Local profiles**: Multiple user profiles within the same application instance, each with their own SQLite database file.
- [ ] **Profile switcher**: Switch between profiles from the sidebar or Settings.
- [ ] **Profile import/export**: Export/import individual profiles separately.
- [ ] **Shared data** (stretch): Option to share the exam paper library across profiles.

### Data Visualization v2

- [ ] **Radar chart**: Multi-dimensional view of skills (listening, reading, vocabulary, writing, translation) for a holistic assessment.
- [ ] **Error distribution heatmap**: Which question numbers are most frequently wrong across sessions.
- [ ] **Vocabulary acquisition timeline**: Cumulative chart of vocabulary entries by familiarity state over time.
- [ ] **Comparative analysis**: Compare two time periods or two exam types side by side.
- [ ] **Export charts as images**: Download chart screenshots for sharing or inclusion in study notes.

### PWA Support

- [ ] **Progressive Web App**: Installable on mobile devices with a home screen icon.
- [ ] **Offline-first with service worker**: Full functionality offline with cached assets.
- [ ] **Responsive mobile layout**: Properly designed mobile views (not just collapsed desktop views).
- [ ] **Touch-optimized interactions**: Swipe gestures for flashcard review, larger touch targets.

### Internationalization (i18n)

- [ ] **English UI option**: Full English-language interface as an alternative to Chinese.
- [ ] **Language switcher**: Toggle in Settings.
- [ ] **i18n framework**: vue-i18n integration with JSON locale files.
- [ ] **Default language detection**: Auto-detect from browser language settings.

### Plugin System

- [ ] **Custom analysis plugins**: Allow users to write simple scripts (Python or JavaScript) that run custom analysis on their data.
- [ ] **Plugin marketplace** (stretch): Community-shared plugins for specialized analysis.
- [ ] **Export plugins**: Custom export formats (e.g., direct Anki APKG generation, printable study sheets).

---

## Beyond v2.0 (Ideas)

These are speculative ideas that may or may not be pursued. They are listed to show the long-term vision and to ensure near-term design decisions do not close doors unnecessarily.

- **Collaborative study groups**: Share vocabulary notes and practice stats within a small study group (peer-to-peer sync, not cloud-based).
- **Gamification**: Points, levels, badges for consistent practice. Leaderboards within study groups.
- **CET-specific AI tutor**: A dedicated chat interface that explains CET grammar points, analyzes mistakes, and suggests study strategies.
- **OCR import**: Take a photo of a paper test result sheet and auto-extract wrong question numbers and scores.
- **Desktop app via Tauri**: Native desktop application with system tray, notifications, and better OS integration.
- **Mobile app via Capacitor**: Wrap the PWA into a native iOS/Android app for app store distribution.

---

## Contribution and Feedback

This roadmap is a living document. Priorities may shift based on user feedback and real-world usage patterns.

**How versions are planned**:
1. Each version has a clear, single-sentence goal.
2. Features within a version are sequenced to deliver value incrementally — the first item completed should already be useful on its own.
3. Versions are scoped to be completable within a reasonable timeframe (v1.1: ~4-6 weeks, v1.2: ~6-8 weeks, v2.0: multi-phase).
4. Bug fixes and minor UX improvements are released as patch versions (1.0.1, 1.0.2, etc.) and are not tracked on this roadmap.
