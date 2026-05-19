"""ReviewTask model — review tasks generated from training sessions."""

from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ReviewTask(SQLModel, table=True):
    __tablename__ = "review_tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="exam_sessions.id", ondelete="CASCADE")
    task_type: str = Field(max_length=50)  # listening_review / reading_review / vocabulary_review / writing_review / translation_review / general
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None)
    status: str = Field(default="todo", max_length=20)  # todo / doing / done / skipped
    priority: str = Field(default="medium", max_length=10)  # low / medium / high
    due_date: Optional[date] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
