"""Schemas for vocabulary quality checks."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CheckDuplicatesRequest(BaseModel):
    terms: List[str]


class DuplicateItem(BaseModel):
    term: str
    normalized_term: str
    existing_entry_id: int
    existing_note_id: int
    existing_note_title: str
    familiarity: str


class CheckDuplicatesResponse(BaseModel):
    duplicates: List[DuplicateItem] = []


class ValidateGeneratedRequest(BaseModel):
    input_words: List[str] = []
    entries: List[Dict[str, Any]]


class ValidateItemResult(BaseModel):
    term: str
    level: str = "ok"  # ok / warning / error
    messages: List[str] = []


class ValidateGeneratedResponse(BaseModel):
    summary: Dict[str, int] = {}
    items: List[ValidateItemResult] = []


class GenerateSingleWordRequest(BaseModel):
    word: str
    options: Optional[Dict[str, Any]] = None
