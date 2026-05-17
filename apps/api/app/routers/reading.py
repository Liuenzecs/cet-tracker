"""Router for reading result endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas.common import APIResponse
from app.schemas.reading import (
    ReadingCreate,
    ReadingResponse,
    ReadingUpdate,
)
from app.services import reading_service, session_service

router = APIRouter(prefix="/api", tags=["reading"])


@router.get("/sessions/{session_id}/reading")
def get_reading(
    session_id: int,
    db: Session = Depends(get_session),
):
    """Get all reading results for a session."""
    if not session_service.get_session(db, session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    results = reading_service.get_reading_results(db, session_id)
    return APIResponse(
        data=[ReadingResponse.model_validate(r).model_dump() for r in results]
    )


@router.post("/sessions/{session_id}/reading")
def create_reading(
    session_id: int,
    body: ReadingCreate,
    db: Session = Depends(get_session),
):
    """Create a reading result for a session."""
    if not session_service.get_session(db, session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    result = reading_service.create_reading_result(db, session_id, body)
    return APIResponse(
        data=ReadingResponse.model_validate(result).model_dump(),
        success=True,
    )


@router.put("/reading/{result_id}")
def update_reading(
    result_id: int,
    body: ReadingUpdate,
    db: Session = Depends(get_session),
):
    """Update an existing reading result."""
    result = reading_service.update_reading_result(db, result_id, body)
    if not result:
        raise HTTPException(status_code=404, detail="Reading result not found")
    return APIResponse(data=ReadingResponse.model_validate(result).model_dump())


@router.delete("/reading/{result_id}")
def delete_reading(
    result_id: int,
    db: Session = Depends(get_session),
):
    """Delete a reading result."""
    deleted = reading_service.delete_reading_result(db, result_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Reading result not found")
    return APIResponse(data={"deleted": True})
