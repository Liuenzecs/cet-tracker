"""Schemas for reading result create / update / response."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ReadingCreate(BaseModel):
    question_type: str
    total_questions: int
    correct_count: int
    wrong_questions_text: Optional[str] = None
    wrong_questions_json: Optional[List[Any]] = None
    mistake_tags_json: Optional[Dict[str, Any]] = None
    reflection: Optional[str] = None


class ReadingUpdate(BaseModel):
    question_type: Optional[str] = None
    total_questions: Optional[int] = None
    correct_count: Optional[int] = None
    wrong_questions_text: Optional[str] = None
    wrong_questions_json: Optional[List[Any]] = None
    mistake_tags_json: Optional[Dict[str, Any]] = None
    reflection: Optional[str] = None


class ReadingResponse(BaseModel):
    id: int
    session_id: int
    question_type: str
    total_questions: int
    correct_count: int
    wrong_questions_text: Optional[str] = None
    wrong_questions_json: Optional[List[Any]] = None
    mistake_tags_json: Optional[Dict[str, Any]] = None
    reflection: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
