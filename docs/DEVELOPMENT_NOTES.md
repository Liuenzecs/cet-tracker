# CET Tracker — Development Notes

## Database Migration

This project uses `SQLModel.metadata.create_all()` for table creation on startup.

**Known limitation:** `create_all()` creates new tables but does NOT add columns to
existing tables. If you upgrade from an older version and get errors about missing
columns (e.g., `intensive_status` on `listening_results`), you need to:

1. Backup your database: `cp data/cet_tracker.db data/cet_tracker.db.bak`
2. Delete the old database: `rm data/cet_tracker.db`
3. Re-seed demo data: `python scripts/reset_demo_data.py`

Or, alternatively, manually add the columns using SQLite:
```sql
ALTER TABLE listening_results ADD COLUMN intensive_status VARCHAR(20) NOT NULL DEFAULT 'not_started';
ALTER TABLE listening_results ADD COLUMN intensive_note TEXT;
ALTER TABLE listening_results ADD COLUMN intensive_completed_at DATETIME;
```

A proper migration system (Alembic) is planned for v1.0.

## v0.3.0 New Tables

- `vocabulary_review_logs` — review action audit trail
- `review_tasks` — training review task management

## v0.3.0 New Columns

- `listening_results.intensive_status` — not_started / in_progress / completed
- `listening_results.intensive_note` — free-text notes
- `listening_results.intensive_completed_at` — completion timestamp

## Running Tests

```bash
cd apps/api
uv run pytest tests/ -v
```

## Building Frontend

```bash
cd apps/web
pnpm install
pnpm build
```

## Resetting Demo Data

```bash
python scripts/reset_demo_data.py
```
