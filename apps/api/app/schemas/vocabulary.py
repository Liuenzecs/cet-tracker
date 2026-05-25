"""Schemas for vocabulary notes and entries."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class VocabularyNoteCreate(BaseModel):
    title: str
    raw_markdown: str
    source_session_id: Optional[int] = None
    exam_type: Optional[str] = None
    paper_name: Optional[str] = None
    source_section: str = "other"


class VocabularyNoteResponse(BaseModel):
    id: int
    title: str
    source_session_id: Optional[int] = None
    exam_type: Optional[str] = None
    paper_name: Optional[str] = None
    source_section: str
    entry_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VocabularyNoteDetail(VocabularyNoteResponse):
    raw_markdown: str = ""
    entries: List[Dict[str, Any]] = []


class VocabularyEntryUpdate(BaseModel):
    term: Optional[str] = None
    entry_type: Optional[str] = None
    meanings_json: Optional[List[Any]] = None
    usages_json: Optional[List[Any]] = None
    examples_json: Optional[List[Any]] = None
    mistake_tips_json: Optional[List[Any]] = None
    synonyms_json: Optional[List[Any]] = None
    comparisons_json: Optional[List[Any]] = None
    writing_sentences_json: Optional[List[Any]] = None
    pronunciation_ipa: Optional[str] = None
    uk_phonetic: Optional[str] = None
    us_phonetic: Optional[str] = None
    familiarity: Optional[str] = None
    tags_json: Optional[List[Any]] = None
    last_reviewed_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None


class VocabularyEntryResponse(BaseModel):
    id: int
    note_id: int
    term: str
    entry_type: str
    meanings_json: Optional[List[Any]] = None
    usages_json: Optional[List[Any]] = None
    examples_json: Optional[List[Any]] = None
    mistake_tips_json: Optional[List[Any]] = None
    synonyms_json: Optional[List[Any]] = None
    comparisons_json: Optional[List[Any]] = None
    writing_sentences_json: Optional[List[Any]] = None
    pronunciation_ipa: Optional[str] = None
    uk_phonetic: Optional[str] = None
    us_phonetic: Optional[str] = None
    familiarity: str
    review_count: int
    last_reviewed_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None
    tags_json: Optional[List[Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ParseMarkdownRequest(BaseModel):
    raw_markdown: str


class ParsedEntry(BaseModel):
    term: str
    entry_type: str = "word"
    meanings_json: List[Any] = []
    usages_json: List[Any] = []
    examples_json: List[Any] = []
    mistake_tips_json: List[Any] = []
    synonyms_json: List[Any] = []
    comparisons_json: List[Any] = []
    writing_sentences_json: List[Any] = []


class ParseMarkdownResponse(BaseModel):
    entries: List[ParsedEntry]
