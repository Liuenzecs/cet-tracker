"""VocabularyNote and VocabularyEntry models for the vocabulary notebook."""

from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import Column, JSON, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    pass


class VocabularyNote(SQLModel, table=True):
    __tablename__ = "vocabulary_notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    raw_markdown: str = Field(sa_type=Text)
    source_session_id: Optional[int] = Field(
        default=None,
        foreign_key="exam_sessions.id",
        ondelete="SET NULL",
    )
    exam_type: Optional[str] = Field(default=None, max_length=10)
    paper_name: Optional[str] = Field(default=None, max_length=200)
    source_section: str = Field(default="other", max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    entries: List["VocabularyEntry"] = Relationship(
        back_populates="note",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class VocabularyEntry(SQLModel, table=True):
    __tablename__ = "vocabulary_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    note_id: int = Field(foreign_key="vocabulary_notes.id", ondelete="CASCADE")
    term: str = Field(max_length=200)
    entry_type: str = Field(default="word", max_length=20)  # word, phrase, collocation
    meanings_json: Optional[List] = Field(default=None, sa_column=Column(JSON))
    usages_json: Optional[List] = Field(default=None, sa_column=Column(JSON))
    examples_json: Optional[List] = Field(default=None, sa_column=Column(JSON))
    mistake_tips_json: Optional[List] = Field(default=None, sa_column=Column(JSON))
    synonyms_json: Optional[List] = Field(default=None, sa_column=Column(JSON))
    comparisons_json: Optional[List] = Field(default=None, sa_column=Column(JSON))
    writing_sentences_json: Optional[List] = Field(default=None, sa_column=Column(JSON))
    familiarity: str = Field(default="new", max_length=20)  # new, learning, reviewing, mastered
    review_count: int = Field(default=0)
    last_reviewed_at: Optional[datetime] = Field(default=None)
    next_review_at: Optional[datetime] = Field(default=None)
    pronunciation_ipa: Optional[str] = Field(default=None, max_length=200)
    uk_phonetic: Optional[str] = Field(default=None, max_length=200)
    us_phonetic: Optional[str] = Field(default=None, max_length=200)
    tags_json: Optional[List] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    note: "VocabularyNote" = Relationship(back_populates="entries")
