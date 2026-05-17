"""Service layer for vocabulary notes and entries."""

import datetime as dt
from typing import List, Optional

from sqlmodel import Session, select

from app.models.vocabulary import VocabularyEntry, VocabularyNote
from app.schemas.vocabulary import (
    VocabularyEntryUpdate,
    VocabularyNoteCreate,
)
from app.utils.markdown_parser import parse_vocabulary_markdown


def get_notes(db: Session) -> List[VocabularyNote]:
    """Get all vocabulary notes."""
    query = select(VocabularyNote).order_by(VocabularyNote.created_at.desc())
    return list(db.exec(query).all())


def create_note(db: Session, data: VocabularyNoteCreate) -> VocabularyNote:
    """Create a vocabulary note with parsed entries from markdown."""
    note = VocabularyNote(
        title=data.title,
        raw_markdown=data.raw_markdown,
        source_session_id=data.source_session_id,
        exam_type=data.exam_type,
        paper_name=data.paper_name,
        source_section=data.source_section,
    )
    db.add(note)
    db.flush()  # Get note.id without committing

    # Parse markdown and create entries
    parsed_entries = parse_vocabulary_markdown(data.raw_markdown)
    for entry_data in parsed_entries:
        entry = VocabularyEntry(
            note_id=note.id,
            term=entry_data.get("term", ""),
            entry_type=entry_data.get("entry_type", "word"),
            meanings_json=entry_data.get("meanings_json", []),
            usages_json=entry_data.get("usages_json", []),
            examples_json=entry_data.get("examples_json", []),
            mistake_tips_json=entry_data.get("mistake_tips_json", []),
            synonyms_json=entry_data.get("synonyms_json", []),
            comparisons_json=entry_data.get("comparisons_json", []),
            writing_sentences_json=entry_data.get("writing_sentences_json", []),
        )
        db.add(entry)

    db.commit()
    db.refresh(note)
    return note


def get_note(db: Session, note_id: int) -> Optional[VocabularyNote]:
    """Get a single vocabulary note."""
    return db.get(VocabularyNote, note_id)


def delete_note(db: Session, note_id: int) -> bool:
    """Delete a vocabulary note (cascades to entries)."""
    note = db.get(VocabularyNote, note_id)
    if not note:
        return False
    db.delete(note)
    db.commit()
    return True


def get_entries(db: Session, note_id: int) -> List[VocabularyEntry]:
    """Get all entries for a vocabulary note."""
    query = select(VocabularyEntry).where(VocabularyEntry.note_id == note_id)
    return list(db.exec(query).all())


def update_entry(
    db: Session, entry_id: int, data: VocabularyEntryUpdate
) -> Optional[VocabularyEntry]:
    """Update a vocabulary entry (partial update)."""
    entry = db.get(VocabularyEntry, entry_id)
    if not entry:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # Handle review_count increment
    if update_data.get("last_reviewed_at") is not None:
        entry.review_count += 1

    for key, value in update_data.items():
        setattr(entry, key, value)

    entry.updated_at = dt.datetime.utcnow()
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
