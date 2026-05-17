#!/usr/bin/env bash
# CET Tracker Development Launcher (macOS/Linux)
# Starts backend (FastAPI + uvicorn) in background, then frontend (Vite) in foreground.
# Press Ctrl+C to stop both.

set -euo pipefail

# ---- Helpers ----
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# ---- Cleanup on Ctrl+C ----
cleanup() {
    echo ""
    echo "Shutting down..."
    if [ -n "${BACKEND_PID:-}" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
        wait "$BACKEND_PID" 2>/dev/null || true
    fi
    echo "All processes stopped."
    exit 0
}
trap cleanup SIGINT SIGTERM

# ---- Check prerequisites ----
echo "Starting CET Tracker..."

if ! command -v python &>/dev/null && ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERROR: Python not found on PATH${NC}"
    exit 1
fi
PYTHON="python3"
command -v python3 &>/dev/null || PYTHON="python"
echo "  Python: $($PYTHON --version)"

if ! command -v node &>/dev/null; then
    echo -e "${RED}ERROR: Node.js not found on PATH${NC}"
    exit 1
fi
echo "  Node.js: $(node --version)"

# ---- Start backend in background ----
echo "Starting backend (FastAPI on http://127.0.0.1:8000)..."
cd "$PROJECT_ROOT/apps/api"
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

# Brief pause to let backend start
sleep 2

# ---- Start frontend in foreground ----
echo "Starting frontend (Vite)..."

cd "$PROJECT_ROOT/apps/web"

if command -v pnpm &>/dev/null; then
    echo "  Using pnpm"
    pnpm dev
else
    echo -e "${YELLOW}  pnpm not found, falling back to npm${NC}"
    npm run dev
fi
