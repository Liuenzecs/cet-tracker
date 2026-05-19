"""Schemas for listening result create / update / response."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ListeningCreate(BaseModel):
    total_questions: int
    correct_count: int
    wrong_questions_text: Optional[str] = None
    wrong_questions_json: Optional[List[Any]] = None
    mistake_tags_json: Optional[Dict[str, Any]] = None
    reflection: Optional[str] = None


class ListeningUpdate(BaseModel):
    total_questions: Optional[int] = None
    correct_count: Optional[int] = None
    wrong_questions_text: Optional[str] = None
    wrong_questions_json: Optional[List[Any]] = None
    mistake_tags_json: Optional[Dict[str, Any]] = None
    reflection: Optional[str] = None
    intensive_status: Optional[str] = None
    intensive_note: Optional[str] = None
    intensive_completed_at: Optional[datetime] = None


class ListeningResponse(BaseModel):
    id: int
    session_id: int
    total_questions: int
    correct_count: int
    wrong_questions_text: Optional[str] = None
    wrong_questions_json: Optional[List[Any]] = None
    mistake_tags_json: Optional[Dict[str, Any]] = None
    reflection: Optional[str] = None
    intensive_status: str = "not_started"
    intensive_note: Optional[str] = None
    intensive_completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
