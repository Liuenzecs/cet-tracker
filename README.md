# CET Tracker

A local-first CET-4 / CET-6 exam preparation tracking system that closes the loop from practice to mastery.

## Overview

CET Tracker helps you:

- **Log** practice exam sessions (full mock, listening, reading, writing, translation)
- **Record** mistakes with structured error tags and reflections
- **Build** a vocabulary notebook from AI-generated Markdown notes
- **Review** vocabulary with card-based visual layouts
- **Visualize** progress with charts and statistics
- **Export/Import** your data as JSON for backup

> Screenshots coming soon — check back after first release.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + Vite + TypeScript |
| UI Library | Element Plus |
| Charts | ECharts |
| Backend | FastAPI |
| ORM | SQLModel (SQLAlchemy fallback) |
| Database | SQLite |
| Package Manager (FE) | pnpm |
| Package Manager (BE) | uv |

## Quick Start

### Prerequisites

- Node.js >= 18
- Python >= 3.10
- pnpm (or npm)
- uv (or pip)

### 1. Install Backend Dependencies

```bash
cd apps/api

# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd apps/web

# Using pnpm (recommended)
pnpm install

# Or using npm
npm install
```

### 3. Start the Backend

```bash
cd apps/api
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Start the Frontend

```bash
cd apps/web
pnpm dev
```

The app will be available at `http://localhost:5173`.

### 5. Seed Demo Data (Optional)

```bash
cd apps/api
uv run python ../../scripts/seed_demo.py
```

## Import / Export

- **Export**: Go to Settings → Export JSON to download all data.
- **Import**: Go to Settings → Import JSON to restore from a backup file.

## Project Structure

```
cet-tracker/
├── apps/
│   ├── web/          # Vue 3 frontend
│   └── api/          # FastAPI backend
├── data/             # SQLite database (not committed)
├── docs/             # Design documents
│   ├── PRD.md
│   ├── DATABASE_SCHEMA.md
│   ├── API_CONTRACT.md
│   ├── UI_DESIGN.md
│   ├── VOCABULARY_MARKDOWN_FORMAT.md
│   └── ROADMAP.md
├── scripts/          # Dev scripts and seed data
├── .env.example
├── .gitignore
└── README.md
```

## Privacy & Data

- All data is stored locally in `data/cet_tracker.db`.
- No data is ever uploaded to any server.
- No user accounts or cloud sync.
- The database file is excluded from Git by `.gitignore`.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for planned features and version history.

## License

MIT
