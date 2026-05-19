"""Service layer for data import / export."""

import datetime as dt
from typing import Any, Dict, List

from sqlmodel import Session, select, text

from app.models.exam_session import ExamSession
from app.models.listening_result import ListeningResult
from app.models.reading_result import ReadingResult
from app.models.vocabulary import VocabularyEntry, VocabularyNote
from app.schemas.import_export import ExportData, ImportResult


def _model_to_dict(obj) -> Dict[str, Any]:
    """Convert a SQLModel object to a JSON-safe dict, handling date/datetime."""
    result = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, (dt.datetime, dt.date)):
            val = val.isoformat()
        elif val is None:
            val = None
        result[col.name] = val
    return result


def export_all(db: Session) -> ExportData:
    """Export all data as JSON-safe dicts."""

    sessions = [dict(_model_to_dict(s)) for s in db.exec(select(ExamSession)).all()]
    listening_results = [
        dict(_model_to_dict(r)) for r in db.exec(select(ListeningResult)).all()
    ]
    reading_results = [
        dict(_model_to_dict(r)) for r in db.exec(select(ReadingResult)).all()
    ]
    vocab_notes = [
        dict(_model_to_dict(n)) for n in db.exec(select(VocabularyNote)).all()
    ]
    vocab_entries = [
        dict(_model_to_dict(e)) for e in db.exec(select(VocabularyEntry)).all()
    ]

    return ExportData(
        sessions=sessions,
        listening_results=listening_results,
        reading_results=reading_results,
        vocabulary_notes=vocab_notes,
        vocabulary_entries=vocab_entries,
    )


def _parse_iso_dates(item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ISO date/datetime strings back to Python date/datetime objects."""
    date_fields = {"date"}
    datetime_fields = {"created_at", "updated_at", "last_reviewed_at", "next_review_at"}

    result = dict(item)
    for key, value in result.items():
        if value is None:
            continue
        if isinstance(value, str):
            if key in date_fields:
                try:
                    result[key] = dt.date.fromisoformat(value)
                except (ValueError, TypeError):
                    pass
            elif key in datetime_fields:
                try:
                    result[key] = dt.datetime.fromisoformat(value)
                except (ValueError, TypeError):
                    pass
    return result


def import_all(db: Session, data: ExportData) -> ImportResult:
    """Import data, replacing all existing data."""

    # Clear existing data in reverse dependency order
    db.exec(text("DELETE FROM vocabulary_entries"))
    db.exec(text("DELETE FROM vocabulary_notes"))
    db.exec(text("DELETE FROM reading_results"))
    db.exec(text("DELETE FROM listening_results"))
    db.exec(text("DELETE FROM exam_sessions"))

    # Reset autoincrement on SQLite (table only exists if AUTOINCREMENT columns defined)
    try:
        db.exec(text("DELETE FROM sqlite_sequence"))
    except Exception:
        pass  # sqlite_sequence table doesn't exist — safe to ignore

    # Import sessions
    count_sessions = 0
    for item in data.sessions:
        s = ExamSession(**_parse_iso_dates(item))
        db.add(s)
        count_sessions += 1

    # Import listening results
    count_listening = 0
    for item in data.listening_results:
        r = ListeningResult(**_parse_iso_dates(item))
        db.add(r)
        count_listening += 1

    # Import reading results
    count_reading = 0
    for item in data.reading_results:
        r = ReadingResult(**_parse_iso_dates(item))
        db.add(r)
        count_reading += 1

    # Import vocabulary notes
    count_notes = 0
    for item in data.vocabulary_notes:
        n = VocabularyNote(**_parse_iso_dates(item))
        db.add(n)
        count_notes += 1

    # Import vocabulary entries
    count_entries = 0
    for item in data.vocabulary_entries:
        e = VocabularyEntry(**_parse_iso_dates(item))
        db.add(e)
        count_entries += 1

    db.commit()

    return ImportResult(
        sessions_imported=count_sessions,
        listening_results_imported=count_listening,
        reading_results_imported=count_reading,
        vocabulary_notes_imported=count_notes,
        vocabulary_entries_imported=count_entries,
    )
