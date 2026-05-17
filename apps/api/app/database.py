"""Database configuration for CET Tracker API."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

# Load .env from project root
load_dotenv()

# Database URL defaults to SQLite in the project data directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "cet_tracker.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# Ensure data directory exists
DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create engine with SQLite-friendly settings
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def get_session():
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session


def init_db():
    """Create all database tables."""
    # Import all models so SQLModel.metadata knows about them
    import app.models  # noqa: F401
    SQLModel.metadata.create_all(engine)
