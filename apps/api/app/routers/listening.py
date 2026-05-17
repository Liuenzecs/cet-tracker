"""Router for listening result endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas.common import APIResponse
from app.schemas.listening import (
    ListeningCreate,
    ListeningResponse,
    ListeningUpdate,
)
from app.services import listening_service, session_service

router = APIRouter(prefix="/api", tags=["listening"])


@router.get("/sessions/{session_id}/listening")
def get_listening(
    session_id: int,
    db: Session = Depends(get_session),
):
    """Get the listening result for a session."""
    # Verify session exists
    if not session_service.get_session(db, session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    result = listening_service.get_listening_result(db, session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Listening result not found for this session")

    return APIResponse(data=ListeningResponse.model_validate(result).model_dump())


@router.post("/sessions/{session_id}/listening")
def create_listening(
    session_id: int,
    body: ListeningCreate,
    db: Session = Depends(get_session),
):
    """Create a listening result for a session."""
    if not session_service.get_session(db, session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    result = listening_service.create_listening_result(db, session_id, body)
    return APIResponse(
        data=ListeningResponse.model_validate(result).model_dump(),
        success=True,
    )


@router.put("/listening/{result_id}")
def update_listening(
    result_id: int,
    body: ListeningUpdate,
    db: Session = Depends(get_session),
):
    """Update an existing listening result."""
    result = listening_service.update_listening_result(db, result_id, body)
    if not result:
        raise HTTPException(status_code=404, detail="Listening result not found")
    return APIResponse(data=ListeningResponse.model_validate(result).model_dump())


@router.delete("/listening/{result_id}")
def delete_listening(
    result_id: int,
    db: Session = Depends(get_session),
):
    """Delete a listening result."""
    deleted = listening_service.delete_listening_result(db, result_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Listening result not found")
    return APIResponse(data={"deleted": True})
