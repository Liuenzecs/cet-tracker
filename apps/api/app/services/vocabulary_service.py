"""Service layer for vocabulary notes and entries."""

import datetime as dt
from typing import List, Optional, Tuple

from sqlmodel import Session, select, func

from app.models.vocabulary import VocabularyEntry, VocabularyNote
from app.schemas.vocabulary import (
    VocabularyEntryUpdate,
    VocabularyNoteCreate,
)
from app.schemas.vocabulary_normalize import (
    GeneratedVocabularyEntry,
    SaveGeneratedNoteRequest,
)
from app.utils.markdown_parser import parse_vocabulary_markdown


def get_notes(
    db: Session,
    exam_type: Optional[str] = None,
    source_section: Optional[str] = None,
    source_session_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[VocabularyNote], int]:
    """Get vocabulary notes with optional filtering and pagination."""
    base_query = select(VocabularyNote)
    if exam_type:
        base_query = base_query.where(VocabularyNote.exam_type == exam_type)
    if source_section:
        base_query = base_query.where(VocabularyNote.source_section == source_section)
    if source_session_id is not None:
        base_query = base_query.where(VocabularyNote.source_session_id == source_session_id)

    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total = db.exec(count_query).one()

    # Paginate
    query = base_query.order_by(VocabularyNote.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    items = list(db.exec(query).all())

    return items, total


def get_review_entries(
    db: Session,
    familiarity: Optional[str] = None,
) -> List[VocabularyEntry]:
    """Get vocabulary entries for review, filtered by familiarity."""
    valid_familiarities = ("new", "learning", "familiar", "mastered")
    if familiarity and familiarity in valid_familiarities:
        target = [familiarity]
    else:
        target = ["new", "learning"]

    query = (
        select(VocabularyEntry)
        .where(VocabularyEntry.familiarity.in_(target))
        .order_by(
            VocabularyEntry.familiarity.asc(),
            VocabularyEntry.updated_at.desc(),
        )
    )
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


def get_entries_paginated(
    db: Session,
    note_id: int,
    page: int = 1,
    page_size: int = 10,
    familiarity: Optional[str] = None,
    q: Optional[str] = None,
) -> Tuple[List[VocabularyEntry], int]:
    """Get entries for a note with pagination, filtering, and search."""
    base_query = select(VocabularyEntry).where(VocabularyEntry.note_id == note_id)

    if familiarity and familiarity in ("new", "learning", "familiar", "mastered"):
        base_query = base_query.where(VocabularyEntry.familiarity == familiarity)

    if q:
        base_query = base_query.where(VocabularyEntry.term.contains(q))

    # Count
    count_query = select(func.count()).select_from(base_query.subquery())
    total = db.exec(count_query).one()

    # Paginate
    query = base_query.order_by(VocabularyEntry.term.asc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    items = list(db.exec(query).all())

    return items, total


def get_review_entries_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 1,
    familiarity: Optional[str] = None,
    q: Optional[str] = None,
    note_id: Optional[int] = None,
) -> Tuple[List[VocabularyEntry], int]:
    """Get review entries with pagination, filtering, and search."""
    valid_familiarities = ("new", "learning", "familiar", "mastered")
    if familiarity and familiarity in valid_familiarities:
        target = [familiarity]
    else:
        target = ["new", "learning"]

    base_query = (
        select(VocabularyEntry)
        .where(VocabularyEntry.familiarity.in_(target))
    )

    if note_id is not None:
        base_query = base_query.where(VocabularyEntry.note_id == note_id)

    if q:
        base_query = base_query.where(VocabularyEntry.term.contains(q))

    # Count
    count_query = select(func.count()).select_from(base_query.subquery())
    total = db.exec(count_query).one()

    # Paginate
    query = base_query.order_by(
        VocabularyEntry.familiarity.asc(),
        VocabularyEntry.updated_at.desc(),
    )
    query = query.offset((page - 1) * page_size).limit(page_size)
    items = list(db.exec(query).all())

    return items, total


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


def create_note_from_generated(db: Session, data: SaveGeneratedNoteRequest) -> VocabularyNote:
    """Create a vocabulary note from AI-generated entries.

    Saves the note with standardized_markdown as raw_markdown,
    and creates vocabulary_entries from the structured entry data.
    """
    note = VocabularyNote(
        title=data.title,
        raw_markdown=data.standardized_markdown or data.raw_input,
        source_session_id=data.source_session_id,
        exam_type=data.exam_type,
        paper_name=data.paper_name,
        source_section=data.source_section,
    )
    db.add(note)
    db.flush()

    for gen_entry in data.entries:
        # Convert GeneratedVocabularyEntry to JSON-compatible storage format
        meanings_json = []
        for m in gen_entry.meanings or []:
            parts = []
            if m.pos:
                parts.append(m.pos)
            if m.zh:
                parts.append(m.zh)
            if m.en:
                parts.append(f"({m.en})")
            meanings_json.append(" ".join(parts))

        usages_json = []
        for u in gen_entry.usages or []:
            if u.meaning:
                usages_json.append(f"{u.pattern} — {u.meaning}")
            else:
                usages_json.append(u.pattern)

        examples_json = []
        for e in gen_entry.examples or []:
            examples_json.append({"en": e.en, "zh": e.zh})

        writing_sentences_json = []
        for ws in gen_entry.writing_sentences or []:
            if ws.zh:
                writing_sentences_json.append(f"{ws.en} — {ws.zh}")
            else:
                writing_sentences_json.append(ws.en)

        comparisons_json = []
        for c in gen_entry.comparisons or []:
            comparisons_json.append({
                "left": c.left,
                "right": c.right,
                "left_meaning": c.left_meaning,
                "right_meaning": c.right_meaning,
            })

        entry = VocabularyEntry(
            note_id=note.id,
            term=gen_entry.term,
            entry_type=gen_entry.entry_type,
            meanings_json=meanings_json,
            usages_json=usages_json,
            examples_json=examples_json,
            mistake_tips_json=gen_entry.mistake_tips or [],
            synonyms_json=gen_entry.synonyms or [],
            comparisons_json=comparisons_json,
            writing_sentences_json=writing_sentences_json,
            tags_json=gen_entry.tags or [],
        )
        db.add(entry)

    db.commit()
    db.refresh(note)
    return note


def append_entries_to_note(
    db: Session,
    note: VocabularyNote,
    entries: List[GeneratedVocabularyEntry],
) -> int:
    """Append generated entries to an existing vocabulary note."""
    count = 0
    for gen_entry in entries:
        meanings_json = []
        for m in gen_entry.meanings or []:
            parts = []
            if m.pos: parts.append(m.pos)
            if m.zh: parts.append(m.zh)
            if m.en: parts.append(f"({m.en})")
            meanings_json.append(" ".join(parts))

        usages_json = []
        for u in gen_entry.usages or []:
            if u.meaning:
                usages_json.append(f"{u.pattern} — {u.meaning}")
            else:
                usages_json.append(u.pattern)

        examples_json = [
            {"en": e.en, "zh": e.zh} for e in (gen_entry.examples or [])
        ]

        writing_sentences_json = []
        for ws in gen_entry.writing_sentences or []:
            if ws.zh:
                writing_sentences_json.append(f"{ws.en} — {ws.zh}")
            else:
                writing_sentences_json.append(ws.en)

        comparisons_json = [
            {"left": c.left, "right": c.right, "left_meaning": c.left_meaning, "right_meaning": c.right_meaning}
            for c in (gen_entry.comparisons or [])
        ]

        entry = VocabularyEntry(
            note_id=note.id,
            term=gen_entry.term,
            entry_type=gen_entry.entry_type,
            meanings_json=meanings_json,
            usages_json=usages_json,
            examples_json=examples_json,
            mistake_tips_json=gen_entry.mistake_tips or [],
            synonyms_json=gen_entry.synonyms or [],
            comparisons_json=comparisons_json,
            writing_sentences_json=writing_sentences_json,
            tags_json=gen_entry.tags or [],
        )
        db.add(entry)
        count += 1

    db.commit()
    return count
