"""Schemas for exam session create / update / response."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SessionCreate(BaseModel):
    exam_type: str
    paper_name: str
    session_type: str
    date: date
    duration_minutes: int
    note: Optional[str] = None


class SessionUpdate(BaseModel):
    exam_type: Optional[str] = None
    paper_name: Optional[str] = None
    session_type: Optional[str] = None
    date: Optional[date] = None
    duration_minutes: Optional[int] = None
    note: Optional[str] = None


class SessionResponse(BaseModel):
    id: int
    exam_type: str
    paper_name: str
    session_type: str
    date: date
    duration_minutes: int
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionDetail(SessionResponse):
    listening_result: Optional[Dict[str, Any]] = None
    reading_results: List[Dict[str, Any]] = []
