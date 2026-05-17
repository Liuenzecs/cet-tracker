# CLAUDE.md — CET Tracker Project Rules

## Project Identity

This is **CET Tracker**, a local-first CET-4 / CET-6 exam preparation tracking system. It helps students track practice exams, record mistakes, review vocabulary, and visualize progress.

## Core Constraints (DO NOT VIOLATE)

1. **Local-first only** — No cloud login, no user accounts, no remote sync.
2. **No AI API integration** — MVP does not call OpenAI / Claude / DeepSeek / any external AI API. The Markdown parser is a local regex/keyword-based parser.
3. **Do not commit local database** — `data/*.db` files must NOT be committed to Git.
4. **Do not commit user personal data** — No hardcoded personal info in source code. Demo data goes in `scripts/seed_demo.py`.
5. **Do not create AGENTS.md** — This project uses `CLAUDE.md` as the single project rules file.
6. **No Electron / Tauri** — Browser-based local web app only.
7. **No official score calculation** — Simple correct/total ratios only.

## Development Rules

### When Modifying API or Database
- Update the corresponding doc in `docs/` (API_CONTRACT.md, DATABASE_SCHEMA.md).
- All API responses must use the envelope format: `{ success: boolean, data: any, error: string | null }`.

### When Modifying Frontend
- Maintain consistent visual style as defined in `docs/UI_DESIGN.md`.
- Pages must be polished, not raw demo quality. Use proper spacing, typography, color, and card-based layouts.
- Do NOT stack default Element Plus components without customization.
- All pages must handle: loading, empty, and error states.

### Code Quality
- Backend: router → service → model/schema layered architecture.
- Frontend: views use components, components use API layer. No monolithic views.
- All JSON fields must have sensible defaults.
- User input must be validated.
- Delete operations require confirmation dialog in frontend.
- Small, focused edits. No unrelated refactoring.

### After Each Change
- State which files were changed.
- State how to verify the change.
- State what's next.

## Tech Stack

- **Frontend**: Vue 3 + Vite + TypeScript + Element Plus + ECharts
- **Backend**: FastAPI + SQLModel (or SQLAlchemy fallback) + SQLite
- **Package managers**: pnpm (frontend), uv (backend); fallback to npm / pip

## Project Structure

```
cet-tracker/
├── apps/
│   ├── web/          # Vue 3 frontend
│   └── api/          # FastAPI backend
│       └── app/
│           ├── main.py
│           ├── database.py
│           ├── models/
│           ├── schemas/
│           ├── routers/
│           ├── services/
│           └── utils/
├── data/             # SQLite database (not committed)
├── docs/             # Design documents
├── scripts/          # Dev scripts and seed data
├── .env.example
├── .gitignore
├── README.md
└── CLAUDE.md
```

## Key Pages

- `/` — Dashboard
- `/sessions` — Training session list
- `/sessions/new` — Create session
- `/sessions/:id` — Session detail (listening, reading, vocabulary)
- `/vocabulary` — Vocabulary notebook list
- `/vocabulary/import` — Import Markdown vocabulary
- `/vocabulary/:id` — Vocabulary note detail (card-based entries)
- `/vocabulary/review` — Vocabulary review
- `/stats` — Statistics
- `/settings` — Import/Export
