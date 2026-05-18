"""Router for exam session CRUD endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_session
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.sessions import (
    SessionCreate,
    SessionDetail,
    SessionResponse,
    SessionUpdate,
)
from app.services import session_service
from app.services import listening_service
from app.services import reading_service

router = APIRouter(prefix="/api", tags=["sessions"])


def _session_to_response(session) -> SessionResponse:
    return SessionResponse.model_validate(session)


@router.get("/sessions")
def list_sessions(
    exam_type: Optional[str] = Query(None),
    session_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_session),
):
    """List sessions with optional filtering and pagination."""
    items, total = session_service.get_sessions(
        db, exam_type=exam_type, session_type=session_type, page=page, page_size=page_size
    )
    return APIResponse(
        data=PaginatedResponse(
            items=[_session_to_response(s) for s in items],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
    )


@router.post("/sessions")
def create_session(
    body: SessionCreate,
    db: Session = Depends(get_session),
):
    """Create a new exam session."""
    session = session_service.create_session(db, body)
    return APIResponse(data=_session_to_response(session).model_dump(), success=True)


@router.get("/sessions/{session_id}")
def get_session_detail(
    session_id: int,
    db: Session = Depends(get_session),
):
    """Get a session with its listening and reading results."""
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get associated results
    lr = listening_service.get_listening_result(db, session_id)
    rrs = reading_service.get_reading_results(db, session_id)

    # Build base session dict from the ORM object (exclude relationship fields)
    session_dict = session.model_dump(
        exclude={"listening_results", "reading_results"}
    )
    detail = SessionDetail(**session_dict)

    if lr:
        detail.listening_result = {
            "id": lr.id,
            "total_questions": lr.total_questions,
            "correct_count": lr.correct_count,
            "accuracy": round(lr.correct_count / lr.total_questions * 100, 1)
            if lr.total_questions > 0
            else 0,
            "wrong_questions_text": lr.wrong_questions_text,
            "wrong_questions_json": lr.wrong_questions_json,
            "mistake_tags_json": lr.mistake_tags_json,
            "reflection": lr.reflection,
        }
    detail.reading_results = [
        {
            "id": rr.id,
            "question_type": rr.question_type,
            "total_questions": rr.total_questions,
            "correct_count": rr.correct_count,
            "accuracy": round(rr.correct_count / rr.total_questions * 100, 1)
            if rr.total_questions > 0
            else 0,
            "wrong_questions_text": rr.wrong_questions_text,
            "wrong_questions_json": rr.wrong_questions_json,
            "mistake_tags_json": rr.mistake_tags_json,
            "reflection": rr.reflection,
        }
        for rr in rrs
    ]

    return APIResponse(data=detail.model_dump())


@router.put("/sessions/{session_id}")
def update_session(
    session_id: int,
    body: SessionUpdate,
    db: Session = Depends(get_session),
):
    """Update an existing exam session."""
    session = session_service.update_session(db, session_id, body)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return APIResponse(data=_session_to_response(session).model_dump())


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_session),
):
    """Delete a session and all associated results."""
    deleted = session_service.delete_session(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return APIResponse(data={"deleted": True})
