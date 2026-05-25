"""Backfill pronunciation_ipa for existing vocabulary entries using the
Free Dictionary API (https://dictionaryapi.dev/). No API key required."""

import json
import sqlite3
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cet_tracker.db"
API_BASE = "https://api.dictionaryapi.dev/api/v2/entries/en"


def fetch_ipa(word: str, tries: int = 3) -> str | None:
    """Fetch IPA pronunciation for a word. Returns None if not found."""
    url = f"{API_BASE}/{word}"
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "cet-tracker/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            if isinstance(data, list) and data:
                entry = data[0]
                phonetic = entry.get("phonetic")
                if phonetic and isinstance(phonetic, str) and phonetic.startswith("/"):
                    return phonetic
                for p in entry.get("phonetics", []) or []:
                    text = (p.get("text") or "").strip()
                    if text.startswith("/"):
                        return text
                for p in entry.get("phonetics", []) or []:
                    text = (p.get("text") or "").strip()
                    if text:
                        return f"/{text}/" if not text.startswith("/") else text
            return None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429 and attempt < tries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            return None
        except Exception:
            if attempt < tries - 1:
                time.sleep(1)
            else:
                return None
    return None


def main():
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Find entries without IPA
    cur.execute(
        "SELECT id, term FROM vocabulary_entries "
        "WHERE pronunciation_ipa IS NULL OR pronunciation_ipa = '' "
        "ORDER BY term"
    )
    rows = cur.fetchall()
    total = len(rows)
    print(f"Found {total} entries without IPA")

    if total == 0:
        conn.close()
        return

    updated = 0
    skipped = 0
    start = time.time()

    for i, row in enumerate(rows):
        entry_id, term = row["id"], row["term"]
        # Skip multi-word phrases (dictionary API only handles single words)
        if len(term.split()) > 2:
            skipped += 1
            continue

        ipa = fetch_ipa(term)
        if ipa:
            cur.execute(
                "UPDATE vocabulary_entries SET pronunciation_ipa = ? WHERE id = ?",
                (ipa, entry_id),
            )
            updated += 1
        else:
            skipped += 1

        # Progress every 10 words
        if (i + 1) % 10 == 0 or i == total - 1:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            print(
                f"  [{i + 1}/{total}] {updated} filled / {skipped} skipped "
                f"({rate:.1f} words/sec)"
            )

        # Be polite to the free API
        time.sleep(0.15)

    conn.commit()
    conn.close()
    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s — {updated} updated, {skipped} skipped")


if __name__ == "__main__":
    main()
