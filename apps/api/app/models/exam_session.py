"""ExamSession model — represents a single training session."""

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.listening_result import ListeningResult
    from app.models.reading_result import ReadingResult


class ExamSession(SQLModel, table=True):
    __tablename__ = "exam_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    exam_type: str = Field(max_length=10)  # CET4, CET6
    paper_name: str = Field(max_length=200)
    session_type: str = Field(max_length=50)  # full_mock, listening, reading, writing, translation
    date: date
    duration_minutes: int
    note: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    listening_results: List["ListeningResult"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    reading_results: List["ReadingResult"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
