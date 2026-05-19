#!/usr/bin/env python3
"""CET Tracker — Clean Package Checker (v0.3.3).

Checks that cet-tracker-clean.zip does not contain forbidden files.
"""

import zipfile
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN_PATTERNS = [
    ".env", "apps/api/.env", ".env.local", ".env.production",
    ".git/", ".claude/",
    "node_modules/", ".venv/", "venv/",
    "__pycache__/", "*.pyc",
    ".pytest_cache/",
    "dist/", "apps/web/dist/",
    "data/*.db", "data/*.sqlite", "data/*.sqlite3",
    ".DS_Store", "Thumbs.db",
]


def _matches(pattern: str, path: str) -> bool:
    """Simple glob-style matching for path checking."""
    path = path.replace("\\", "/").lstrip("./")
    pattern = pattern.replace("\\", "/")
    # Exact match
    if path == pattern:
        return True
    # Prefix match (directory wildcard)
    if pattern.endswith("/") and path.startswith(pattern):
        return True
    if pattern.endswith("/*") and path.startswith(pattern[:-1]):
        return True
    # Suffix match
    if pattern.startswith("*.") and path.endswith(pattern[1:]):
        return True
    # Contains match
    if pattern in path:
        return True
    return False


def check_clean_package(zip_path: str = None):
    """Check a clean package zip for forbidden files."""
    if zip_path is None:
        zip_path = PROJECT_ROOT / "cet-tracker-clean.zip"

    zip_path = Path(zip_path)
    result = {"passed": True, "issues": [], "total_files": 0}

    if not zip_path.exists():
        result["passed"] = False
        result["issues"].append(f"Zip not found: {zip_path}")
        return result

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            result["total_files"] = len(names)

            for name in names:
                for pattern in FORBIDDEN_PATTERNS:
                    if _matches(pattern, name):
                        result["passed"] = False
                        result["issues"].append(f"Forbidden: {name} (matches {pattern})")
                        break

        if not result["issues"]:
            result["issues"].append(f"All {len(names)} files clean")

    except Exception as e:
        result["passed"] = False
        result["issues"].append(f"Error reading zip: {e}")

    return result


if __name__ == "__main__":
    result = check_clean_package()
    print(f"Passed: {result['passed']}")
    for issue in result["issues"]:
        print(f"  - {issue}")
    sys.exit(0 if result["passed"] else 1)
