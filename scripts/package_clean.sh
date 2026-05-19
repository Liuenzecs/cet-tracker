#!/usr/bin/env bash
# CET Tracker — clean packaging script (macOS/Linux)
# Run from project root: bash scripts/package_clean.sh

set -euo pipefail

OUTPUT="cet-tracker-clean.zip"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "CET Tracker — Clean Packaging"
echo "Project root: $PROJECT_ROOT"

cd "$PROJECT_ROOT"

# Remove old zip
rm -f "$OUTPUT"

# Create clean zip with exclusions
zip -r "$OUTPUT" . \
    -x '.git/*' \
    -x '.claude/*' \
    -x '.env' \
    -x '.env.*' \
    -x '!.env.example' \
    -x 'node_modules/*' \
    -x '.venv/*' \
    -x 'venv/*' \
    -x '__pycache__/*' \
    -x '*.pyc' \
    -x '.pytest_cache/*' \
    -x 'dist/*' \
    -x 'apps/web/dist/*' \
    -x 'data/*.db' \
    -x 'data/*.sqlite' \
    -x 'data/*.sqlite3' \
    -x '.DS_Store' \
    -x 'Thumbs.db' \
    -x 'cet-tracker-clean.zip'

FILE_SIZE=$(du -h "$OUTPUT" | cut -f1)
echo "Packaged: $OUTPUT ($FILE_SIZE)"
