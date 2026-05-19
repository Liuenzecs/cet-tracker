"""Generate a clean cet-tracker-clean.zip for distribution."""
import zipfile
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

EXCLUDE_PATTERNS = [
    r"\.git/.*", r"\.claude/.*", r"\.env$", r"\.env\..*",
    r"node_modules/.*", r"\.venv/.*", r"venv/.*",
    r"__pycache__/.*", r"\.pytest_cache/.*",
    r"dist/.*", r"apps/web/dist/.*",
    r"data/.*\.db$", r"data/.*\.sqlite$", r"data/.*\.sqlite3$",
    r".*\.pyc$", r"\.DS_Store$", r"Thumbs\.db$",
    r"cet-tracker-clean\.zip$",
]


def should_exclude(path: str) -> bool:
    for pat in EXCLUDE_PATTERNS:
        if re.search(pat, path):
            return True
    return False


def main():
    files = []
    for f in ROOT.rglob("*"):
        if not f.is_file():
            continue
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        if rel == ".env.example":
            files.append((f, rel))
            continue
        if should_exclude(rel):
            continue
        files.append((f, rel))

    print(f"Including {len(files)} files")

    output = ROOT / "cet-tracker-clean.zip"
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath, relpath in files:
            zf.write(fpath, relpath)

    size_kb = output.stat().st_size / 1024
    print(f"Created {output.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
