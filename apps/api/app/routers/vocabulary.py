"""Router for vocabulary note and entry endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_session
from app.schemas.common import APIResponse, PaginatedResponse
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
from app.schemas.vocabulary_normalize import (
    AIProviderStatus,
    GenerateFromWordsRequest,
    GenerateFromWordsResponse,
    NormalizeMarkdownRequest,
    NormalizeMarkdownResponse,
    SaveGeneratedNoteRequest,
)
from app.services import vocabulary_service
from app.services.ai_normalizer_service import (
    is_ai_configured,
    normalize_markdown,
    generate_from_words,
    validate_word_input,
)
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
def list_notes(
    exam_type: Optional[str] = Query(None),
    source_section: Optional[str] = Query(None),
    source_session_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_session),
):
    """List vocabulary notes with optional filtering and pagination."""
    items, total = vocabulary_service.get_notes(
        db,
        exam_type=exam_type,
        source_section=source_section,
        source_session_id=source_session_id,
        page=page,
        page_size=page_size,
    )
    return APIResponse(
        data=PaginatedResponse(
            items=[_note_to_response(n).model_dump() for n in items],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
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
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    familiarity: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_session),
):
    """List entries for a vocabulary note with pagination, filtering, and search."""
    note = vocabulary_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Vocabulary note not found")

    entries, total = vocabulary_service.get_entries_paginated(
        db, note_id,
        page=page, page_size=page_size,
        familiarity=familiarity,
        q=q,
    )
    return APIResponse(
        data=PaginatedResponse(
            items=[VocabularyEntryResponse.model_validate(e).model_dump() for e in entries],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
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


@router.get("/review")
def get_review_entries(
    page: int = Query(1, ge=1),
    page_size: int = Query(1, ge=1, le=200),
    familiarity: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_session),
):
    """Get vocabulary entries for review with pagination and filtering.

    If familiarity is not provided, returns entries with 'new' or 'learning' status.
    Valid values: new, learning, familiar, mastered.
    """
    entries, total = vocabulary_service.get_review_entries_paginated(
        db,
        page=page, page_size=page_size,
        familiarity=familiarity,
        q=q,
    )
    return APIResponse(
        data=PaginatedResponse(
            items=[VocabularyEntryResponse.model_validate(e).model_dump() for e in entries],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
    )


@router.get("/ai-status")
def get_ai_status():
    """Check if AI normalization is available."""
    available, message = is_ai_configured()
    return APIResponse(
        data=AIProviderStatus(
            enabled=available,
            provider="deepseek",
            configured=available,
            message=message,
        ).model_dump()
    )


@router.post("/normalize-markdown")
async def normalize_markdown_endpoint(
    body: NormalizeMarkdownRequest,
):
    """Normalize raw markdown into structured vocabulary using AI.

    Returns structured entries if AI is configured, or warnings if not.
    This endpoint does NOT save anything to the database.
    """
    if not body.raw_markdown or not body.raw_markdown.strip():
        raise HTTPException(status_code=400, detail="raw_markdown is required")

    result = await normalize_markdown(body.raw_markdown, provider=body.provider)
    return APIResponse(
        data=NormalizeMarkdownResponse(
            title=result.get("title", ""),
            entries=result.get("entries", []),
            warnings=result.get("warnings", []),
            source=result.get("source", "ai"),
        ).model_dump()
    )


@router.post("/generate-from-words")
async def generate_from_words_endpoint(
    body: GenerateFromWordsRequest,
):
    """Generate structured vocabulary entries from a word list using AI.

    This endpoint does NOT save anything to the database.
    Returns structured entries + standardized_markdown for preview.
    """
    # Validate input
    cleaned_words = validate_word_input("\n".join(body.words))
    if not cleaned_words:
        raise HTTPException(status_code=400, detail="words 不能为空")

    if len(cleaned_words) > 50:
        raise HTTPException(status_code=400, detail="一次最多生成 50 个词")

    if body.exam_type not in ("CET4", "CET6"):
        raise HTTPException(status_code=422, detail="exam_type 必须是 CET4 或 CET6")

    if body.source_section not in ("listening", "reading", "writing", "translation", "other"):
        raise HTTPException(status_code=422, detail="source_section 无效")

    if body.options.detail_level not in ("brief", "standard", "detailed"):
        raise HTTPException(status_code=422, detail="detail_level 无效")

    if body.options.example_style not in ("cet", "academic", "daily"):
        raise HTTPException(status_code=422, detail="example_style 无效")

    # Generate
    result = await generate_from_words(
        words=cleaned_words,
        exam_type=body.exam_type,
        title=body.title,
        options=body.options.model_dump(),
    )

    # If AI not configured, return a proper error with code
    code = result.get("code")
    if code == "AI_NOT_CONFIGURED":
        return APIResponse(
            success=True,
            data=GenerateFromWordsResponse(
                title=result.get("title", ""),
                standardized_markdown="",
                entries=[],
                warnings=result.get("warnings", []),
                source="ai",
            ).model_dump(),
        )

    return APIResponse(
        data=GenerateFromWordsResponse(
            title=result.get("title", ""),
            standardized_markdown=result.get("standardized_markdown", ""),
            entries=result.get("entries", []),
            warnings=result.get("warnings", []),
            source=result.get("source", "ai"),
        ).model_dump()
    )


@router.post("/notes/from-generated")
def save_generated_note(
    body: SaveGeneratedNoteRequest,
    db: Session = Depends(get_session),
):
    """Save a vocabulary note from AI-generated entries.

    This endpoint does NOT call AI — it saves user-confirmed entries.
    """
    if not body.entries:
        raise HTTPException(status_code=400, detail="entries 不能为空")

    try:
        note = vocabulary_service.create_note_from_generated(db, body)
        entry_count = len(note.entries) if note.entries else 0
        return APIResponse(
            data={
                "id": note.id,
                "title": note.title,
                "entry_count": entry_count,
                "created_at": note.created_at.isoformat(),
            },
            success=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


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
