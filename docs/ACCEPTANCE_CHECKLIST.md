# CET Tracker — Acceptance Checklist

## Backend

- [ ] Start backend: `cd apps/api && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- [ ] `GET /health` returns `{"status":"ok"}`
- [ ] `pytest` passes all tests (97+)
- [ ] `GET /api/stats/dashboard` returns valid stats
- [ ] `POST /api/vocabulary/generate-from-words` works or shows AI-not-configured message
- [ ] `POST /api/vocabulary/check-duplicates` works
- [ ] `POST /api/vocabulary/validate-generated` works
- [ ] `GET /api/vocabulary/due-today` returns paginated entries
- [ ] `PUT /api/vocabulary/entries/{id}/review?action=good` updates familiarity + writes log
- [ ] `GET /api/vocabulary/review-logs` returns review history
- [ ] `GET /api/vocabulary/stats/mastery` returns mastery stats
- [ ] `GET /api/vocabulary/stats/familiarity-trend` returns trend data
- [ ] `GET /api/review-tasks` returns task list
- [ ] `POST /api/sessions/{id}/generate-review-tasks` creates tasks
- [ ] `GET /api/reading/stats/mistakes` returns mistake statistics
- [ ] `GET /api/reports/weekly` returns weekly report
- [ ] `GET /api/reports/monthly` returns monthly report
- [ ] `GET /api/export/json` exports data
- [ ] `POST /api/import/json` imports data

## Frontend

- [ ] `cd apps/web && pnpm build` passes with 0 TypeScript errors
- [ ] Dashboard (`/`) loads and shows stat cards, due vocab, quick actions
- [ ] Session list (`/sessions`) loads with pagination
- [ ] Create session (`/sessions/new`) works
- [ ] Session detail (`/sessions/:id`) shows listening/reading/vocab/tasks
- [ ] Vocabulary import (`/vocabulary/import`) shows two tabs
- [ ] AI generate tab: word list input, generate button, preview, save
- [ ] AI not configured shows clear message without crash
- [ ] Markdown import tab works as before
- [ ] Vocabulary detail (`/vocabulary/:id`) shows entries with pagination
- [ ] Vocabulary review (`/vocabulary/review`) works in flashcard mode
- [ ] Review with `?note_id=X` works
- [ ] Review with `?due=today` works
- [ ] Reports (`/reports`) loads weekly/monthly and shows data
- [ ] Stats (`/stats`) loads with charts
- [ ] Settings (`/settings`) export/import works

## Copyright Compliance

- [ ] No real CET exam questions in any file
- [ ] No real CET listening audio files
- [ ] No real CET reading passages
- [ ] No official answer keys or scoring rubrics
- [ ] `scripts/seed_demo.py` uses fictional demo data only
- [ ] README has copyright notice

## Package

- [ ] `.env` is NOT in the repository
- [ ] `cet-tracker-clean.zip` does not contain `.env`, `node_modules/`, `.venv/`, `data/*.db`
- [ ] `scripts/package_clean.ps1` runs successfully
