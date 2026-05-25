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
    StarEntryRequest,
    VocabularyEntryResponse,
    VocabularyEntryUpdate,
    VocabularyNoteCreate,
    VocabularyNoteDetail,
    VocabularyNoteResponse,
)
from app.schemas.quality import (
    CheckDuplicatesRequest,
    CheckDuplicatesResponse,
    GenerateSingleWordRequest,
    ValidateGeneratedRequest,
    ValidateGeneratedResponse,
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
    generate_single_word,
    validate_word_input,
)
from app.services.quality_service import check_duplicates, validate_generated_entries
from app.services.review_service import (
    do_review,
    get_review_logs,
    get_due_today,
    get_mastery_stats,
    get_familiarity_trend,
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
    page_size: int = Query(20, ge=1, le=200),
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


@router.put("/entries/{entry_id}/star")
def star_entry(
    entry_id: int,
    body: StarEntryRequest,
    db: Session = Depends(get_session),
):
    """Star or unstar a vocabulary entry."""
    if body.star_priority not in ("normal", "high"):
        raise HTTPException(status_code=422, detail="star_priority 必须是 normal 或 high")
    entry = vocabulary_service.star_entry(
        db, entry_id, body.is_starred,
        star_note=body.star_note, star_priority=body.star_priority,
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Vocabulary entry not found")
    return APIResponse(data=VocabularyEntryResponse.model_validate(entry).model_dump())


@router.get("/starred")
def list_starred(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    q: Optional[str] = Query(None),
    familiarity: Optional[str] = Query(None),
    star_priority: Optional[str] = Query(None),
    source_section: Optional[str] = Query(None),
    note_id: Optional[int] = Query(None),
    db: Session = Depends(get_session),
):
    """List starred vocabulary entries with pagination and filtering."""
    entries, total = vocabulary_service.get_starred_entries(
        db, page=page, page_size=page_size,
        q=q, familiarity=familiarity, star_priority=star_priority,
        source_section=source_section, note_id=note_id,
    )
    return APIResponse(
        data=PaginatedResponse(
            items=[VocabularyEntryResponse.model_validate(e).model_dump() for e in entries],
            total=total, page=page, page_size=page_size,
        ).model_dump()
    )


@router.get("/review")
def get_review_entries(
    page: int = Query(1, ge=1),
    page_size: int = Query(1, ge=1, le=200),
    familiarity: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    note_id: Optional[int] = Query(None),
    due: Optional[str] = Query(None),
    starred: Optional[bool] = Query(None),
    db: Session = Depends(get_session),
):
    """Get vocabulary entries for review with pagination and filtering.

    If note_id is provided, only returns entries from that note.
    If due=today, only returns entries due for review today.
    If starred=true, only returns starred entries.
    If familiarity is not provided, returns entries with 'new' or 'learning' status.
    """
    if due == "today":
        entries, total = get_due_today(
            db,
            page=page, page_size=page_size,
            familiarity=familiarity,
            note_id=note_id,
        )
    else:
        entries, total = vocabulary_service.get_review_entries_paginated(
            db,
            page=page, page_size=page_size,
            familiarity=familiarity,
            q=q,
            note_id=note_id,
        )

    # Filter by starred if requested
    if starred:
        entries = [e for e in entries if e.is_starred]
        total = len(entries)

    return APIResponse(
        data=PaginatedResponse(
            items=[VocabularyEntryResponse.model_validate(e).model_dump() for e in entries],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
    )


@router.get("/review-logs")
def list_review_logs(
    entry_id: Optional[int] = Query(None),
    note_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_session),
):
    """Get vocabulary review logs with filtering and pagination."""
    items, total = get_review_logs(
        db,
        entry_id=entry_id, note_id=note_id,
        start_date=start_date, end_date=end_date,
        page=page, page_size=page_size,
    )
    return APIResponse(
        data=PaginatedResponse(
            items=[{"id": log.id, "entry_id": log.entry_id, "note_id": log.note_id,
                   "old_familiarity": log.old_familiarity, "new_familiarity": log.new_familiarity,
                   "action": log.action, "reviewed_at": log.reviewed_at.isoformat(),
                   "note": log.note, "created_at": log.created_at.isoformat()} for log in items],
            total=total, page=page, page_size=page_size,
        ).model_dump()
    )


@router.get("/due-today")
def list_due_today(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    familiarity: Optional[str] = Query(None),
    note_id: Optional[int] = Query(None),
    db: Session = Depends(get_session),
):
    """Get vocabulary entries due for review today."""
    entries, total = get_due_today(
        db,
        page=page, page_size=page_size,
        familiarity=familiarity, note_id=note_id,
    )
    return APIResponse(
        data=PaginatedResponse(
            items=[VocabularyEntryResponse.model_validate(e).model_dump() for e in entries],
            total=total, page=page, page_size=page_size,
        ).model_dump()
    )


@router.get("/stats/mastery")
def get_mastery(
    db: Session = Depends(get_session),
):
    """Get vocabulary mastery statistics."""
    stats = get_mastery_stats(db)
    return APIResponse(data=stats)


@router.get("/stats/familiarity-trend")
def get_fam_trend(
    days: int = Query(30),
    note_id: Optional[int] = Query(None),
    db: Session = Depends(get_session),
):
    """Get vocabulary familiarity trend over time."""
    trend = get_familiarity_trend(db, days=days, note_id=note_id)
    return APIResponse(data={"items": trend})


@router.put("/entries/{entry_id}/review")
def review_entry(
    entry_id: int,
    action: str = Query(..., description="again / hard / good / easy"),
    db: Session = Depends(get_session),
):
    """Perform a review action on an entry. Updates familiarity, counters, and logs."""
    if action not in ("again", "hard", "good", "easy"):
        raise HTTPException(status_code=422, detail="action 必须是 again / hard / good / easy 之一")

    entry = do_review(db, entry_id, action)
    if not entry:
        raise HTTPException(status_code=404, detail="Vocabulary entry not found")

    return APIResponse(data=VocabularyEntryResponse.model_validate(entry).model_dump())


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


@router.post("/notes/{note_id}/append-entries")
def append_entries_to_note(
    note_id: int,
    body: SaveGeneratedNoteRequest,
    db: Session = Depends(get_session),
):
    """Append AI-generated entries to an existing vocabulary note."""
    note = vocabulary_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Vocabulary note not found")

    if not body.entries:
        raise HTTPException(status_code=400, detail="entries 不能为空")

    try:
        count = vocabulary_service.append_entries_to_note(db, note, body.entries)
        return APIResponse(
            data={
                "note_id": note.id,
                "title": note.title,
                "appended_count": count,
            },
            success=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"追加失败: {str(e)}")


@router.post("/check-duplicates")
def check_duplicate_terms(
    body: CheckDuplicatesRequest,
    db: Session = Depends(get_session),
):
    """Check which terms already exist in vocabulary_entries."""
    duplicates = check_duplicates(db, body.terms)
    return APIResponse(data=CheckDuplicatesResponse(duplicates=duplicates).model_dump())


@router.post("/validate-generated")
def validate_generated(
    body: ValidateGeneratedRequest,
):
    """Validate AI-generated entries for quality issues."""
    result = validate_generated_entries(body.input_words, body.entries)
    return APIResponse(data=ValidateGeneratedResponse(
        summary=result["summary"],
        items=result["items"],
    ).model_dump())


@router.post("/generate-single-word")
async def generate_single_word_endpoint(
    body: GenerateSingleWordRequest,
):
    """Generate vocabulary entry for a single word using AI."""
    if not body.word or not body.word.strip():
        raise HTTPException(status_code=400, detail="word is required")

    result = await generate_single_word(body.word, body.options)
    return APIResponse(data=GenerateFromWordsResponse(
        title="",
        standardized_markdown=result.get("standardized_markdown", ""),
        entries=[result["entry"]] if result.get("entry") else [],
        warnings=result.get("warnings", []),
        source=result.get("source", "ai"),
    ).model_dump())


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
