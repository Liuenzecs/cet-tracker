"""VocabularyReviewLog model — records each review action for audit trail."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class VocabularyReviewLog(SQLModel, table=True):
    __tablename__ = "vocabulary_review_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    entry_id: int = Field(foreign_key="vocabulary_entries.id", ondelete="CASCADE")
    note_id: int = Field(foreign_key="vocabulary_notes.id", ondelete="CASCADE")
    old_familiarity: str = Field(max_length=20)
    new_familiarity: str = Field(max_length=20)
    action: str = Field(max_length=20)  # again / hard / good / easy / manual
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)
    note: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
