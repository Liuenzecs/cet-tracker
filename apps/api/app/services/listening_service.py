"""Service layer for listening result CRUD operations."""

import datetime as dt
from typing import Optional

from sqlmodel import Session, select

from app.models.listening_result import ListeningResult
from app.schemas.listening import ListeningCreate, ListeningUpdate


def get_listening_result(db: Session, session_id: int) -> Optional[ListeningResult]:
    """Get the listening result for a session (one per session)."""
    query = select(ListeningResult).where(ListeningResult.session_id == session_id)
    return db.exec(query).first()


def create_listening_result(
    db: Session, session_id: int, data: ListeningCreate
) -> ListeningResult:
    """Create a listening result for a session."""
    result_data = data.model_dump()
    result_data["session_id"] = session_id
    result = ListeningResult(**result_data)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def update_listening_result(
    db: Session, result_id: int, data: ListeningUpdate
) -> Optional[ListeningResult]:
    """Update an existing listening result."""
    result = db.get(ListeningResult, result_id)
    if not result:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(result, key, value)

    result.updated_at = dt.datetime.utcnow()
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def delete_listening_result(db: Session, result_id: int) -> bool:
    """Delete a listening result by ID."""
    result = db.get(ListeningResult, result_id)
    if not result:
        return False
    db.delete(result)
    db.commit()
    return True
