"""Service layer for reading result CRUD operations."""

import datetime as dt
from typing import List, Optional

from sqlmodel import Session, select

from app.models.reading_result import ReadingResult
from app.schemas.reading import ReadingCreate, ReadingUpdate


def get_reading_results(db: Session, session_id: int) -> List[ReadingResult]:
    """Get all reading results for a session."""
    query = select(ReadingResult).where(ReadingResult.session_id == session_id)
    return list(db.exec(query).all())


def create_reading_result(
    db: Session, session_id: int, data: ReadingCreate
) -> ReadingResult:
    """Create a reading result for a session."""
    result_data = data.model_dump()
    result_data["session_id"] = session_id
    result = ReadingResult(**result_data)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def update_reading_result(
    db: Session, result_id: int, data: ReadingUpdate
) -> Optional[ReadingResult]:
    """Update an existing reading result."""
    result = db.get(ReadingResult, result_id)
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


def delete_reading_result(db: Session, result_id: int) -> bool:
    """Delete a reading result by ID."""
    result = db.get(ReadingResult, result_id)
    if not result:
        return False
    db.delete(result)
    db.commit()
    return True
