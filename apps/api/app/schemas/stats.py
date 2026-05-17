"""Schemas for dashboard statistics."""

from datetime import date as date_type
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TrendPoint(BaseModel):
    date: str  # ISO date string
    accuracy: Optional[float] = None


class RecentSessionSummary(BaseModel):
    id: int
    exam_type: str
    paper_name: str
    session_type: str
    date: str


class DashboardStats(BaseModel):
    total_sessions: int = 0
    total_listening_sessions: int = 0
    total_reading_sessions: int = 0
    avg_listening_accuracy: Optional[float] = None
    avg_reading_accuracy: Optional[float] = None
    listening_trend: List[TrendPoint] = []
    reading_trend: List[TrendPoint] = []
    total_vocabulary: int = 0
    vocabulary_by_familiarity: Dict[str, int] = {}
    pending_review: int = 0
    recent_sessions: List[RecentSessionSummary] = []
