#!/usr/bin/env python3
"""Reset the local database and re-seed with demo data.

Usage: python scripts/reset_demo_data.py

WARNING: This DELETES your existing data/cet_tracker.db.
Back it up first if needed.
"""

import os
import sys
from pathlib import Path

# Ensure we run from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

DB_PATH = PROJECT_ROOT / "data" / "cet_tracker.db"

# 1. Remove old database
if DB_PATH.exists():
    print(f"Removing old database: {DB_PATH}")
    DB_PATH.unlink()
else:
    print(f"No existing database found at {DB_PATH}")

# 2. Import seed script and run it
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.seed_demo import main as seed_main

print("Seeding demo data...")
seed_main()

print("Done. Database reset with fresh demo data.")
