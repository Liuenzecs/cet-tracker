"""Service layer for exam session CRUD operations."""

from typing import List, Optional, Tuple

from sqlmodel import Session, select

from app.models.exam_session import ExamSession
from app.schemas.sessions import SessionCreate, SessionUpdate


def get_sessions(
    db: Session,
    exam_type: Optional[str] = None,
    session_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[ExamSession], int]:
    """Get paginated sessions with optional filtering."""
    query = select(ExamSession)
    count_query = select(ExamSession)

    if exam_type:
        query = query.where(ExamSession.exam_type == exam_type)
        count_query = count_query.where(ExamSession.exam_type == exam_type)
    if session_type:
        query = query.where(ExamSession.session_type == session_type)
        count_query = count_query.where(ExamSession.session_type == session_type)

    total = len(db.exec(count_query).all())

    query = query.order_by(ExamSession.date.desc()).offset((page - 1) * page_size).limit(page_size)
    items = db.exec(query).all()

    return list(items), total


def get_session(db: Session, session_id: int) -> Optional[ExamSession]:
    """Get a single session by ID."""
    return db.get(ExamSession, session_id)


def create_session(db: Session, data: SessionCreate) -> ExamSession:
    """Create a new exam session."""
    session = ExamSession(**data.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_session(db: Session, session_id: int, data: SessionUpdate) -> Optional[ExamSession]:
    """Update an existing exam session."""
    session = db.get(ExamSession, session_id)
    if not session:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(session, key, value)

    import datetime as dt
    session.updated_at = dt.datetime.utcnow()

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session_id: int) -> bool:
    """Delete a session by ID."""
    session = db.get(ExamSession, session_id)
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True
