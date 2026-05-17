"""ReadingResult model — stores reading practice results for a session."""

from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.exam_session import ExamSession


class ReadingResult(SQLModel, table=True):
    __tablename__ = "reading_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="exam_sessions.id", ondelete="CASCADE")
    question_type: str = Field(max_length=50)  # section_a, section_b, section_c
    total_questions: int
    correct_count: int
    wrong_questions_text: Optional[str] = Field(default=None)
    wrong_questions_json: Optional[List] = Field(default=None, sa_column=Column(JSON))
    mistake_tags_json: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    reflection: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    session: "ExamSession" = Relationship(back_populates="reading_results")
