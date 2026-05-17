"""Router for vocabulary note and entry endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas.common import APIResponse
from app.schemas.vocabulary import (
    ParseMarkdownRequest,
    ParseMarkdownResponse,
    ParsedEntry,
    VocabularyEntryResponse,
    VocabularyEntryUpdate,
    VocabularyNoteCreate,
    VocabularyNoteDetail,
    VocabularyNoteResponse,
)
from app.services import vocabulary_service
from app.utils.markdown_parser import parse_vocabulary_markdown

router = APIRouter(prefix="/api/vocabulary", tags=["vocabulary"])


def _note_to_response(note) -> VocabularyNoteResponse:
    """Convert VocabularyNote model to response, including entry_count."""
    entry_count = len(note.entries) if note.entries else 0
    return VocabularyNoteResponse(
        id=note.id,
        title=note.title,
        source_session_id=note.source_session_id,
        exam_type=note.exam_type,
        paper_name=note.paper_name,
        source_section=note.source_section,
        entry_count=entry_count,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.get("/notes")
def list_notes(db: Session = Depends(get_session)):
    """List all vocabulary notes."""
    notes = vocabulary_service.get_notes(db)
    return APIResponse(
        data=[_note_to_response(n).model_dump() for n in notes]
    )


@router.post("/notes")
def create_note(
    body: VocabularyNoteCreate,
    db: Session = Depends(get_session),
):
    """Create a vocabulary note with parsed entries from markdown."""
    note = vocabulary_service.create_note(db, body)
    return APIResponse(
        data=_note_to_response(note).model_dump(),
        success=True,
    )


@router.get("/notes/{note_id}")
def get_note_detail(
    note_id: int,
    db: Session = Depends(get_session),
):
    """Get a vocabulary note with its entries."""
    note = vocabulary_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Vocabulary note not found")

    entries = vocabulary_service.get_entries(db, note_id)
    entry_count = len(entries)

    detail = VocabularyNoteDetail(
        id=note.id,
        title=note.title,
        raw_markdown=note.raw_markdown,
        source_session_id=note.source_session_id,
        exam_type=note.exam_type,
        paper_name=note.paper_name,
        source_section=note.source_section,
        entry_count=entry_count,
        created_at=note.created_at,
        updated_at=note.updated_at,
        entries=[
            VocabularyEntryResponse.model_validate(e).model_dump() for e in entries
        ],
    )

    return APIResponse(data=detail.model_dump())


@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_session),
):
    """Delete a vocabulary note and its entries."""
    deleted = vocabulary_service.delete_note(db, note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vocabulary note not found")
    return APIResponse(data={"deleted": True})


@router.get("/notes/{note_id}/entries")
def list_entries(
    note_id: int,
    db: Session = Depends(get_session),
):
    """List all entries for a vocabulary note."""
    note = vocabulary_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Vocabulary note not found")

    entries = vocabulary_service.get_entries(db, note_id)
    return APIResponse(
        data=[VocabularyEntryResponse.model_validate(e).model_dump() for e in entries]
    )


@router.put("/entries/{entry_id}")
def update_entry(
    entry_id: int,
    body: VocabularyEntryUpdate,
    db: Session = Depends(get_session),
):
    """Update a vocabulary entry (partial update)."""
    entry = vocabulary_service.update_entry(db, entry_id, body)
    if not entry:
        raise HTTPException(status_code=404, detail="Vocabulary entry not found")
    return APIResponse(data=VocabularyEntryResponse.model_validate(entry).model_dump())


@router.post("/parse-markdown")
def parse_markdown(
    body: ParseMarkdownRequest,
):
    """Parse raw markdown and return structured entries without saving."""
    try:
        parsed = parse_vocabulary_markdown(body.raw_markdown)
        entries = [
            ParsedEntry(
                term=entry["term"],
                entry_type=entry.get("entry_type", "word"),
                meanings_json=entry.get("meanings_json", []),
                usages_json=entry.get("usages_json", []),
                examples_json=entry.get("examples_json", []),
                mistake_tips_json=entry.get("mistake_tips_json", []),
                synonyms_json=entry.get("synonyms_json", []),
                comparisons_json=entry.get("comparisons_json", []),
                writing_sentences_json=entry.get("writing_sentences_json", []),
            )
            for entry in parsed
        ]
        return APIResponse(
            data=ParseMarkdownResponse(entries=entries).model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
