"""Schemas for dashboard statistics and reports."""

from datetime import date as date_type
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TrendPoint(BaseModel):
    date: str
    accuracy: Optional[float] = None
    question_type: Optional[str] = None


class RecentSessionSummary(BaseModel):
    id: int
    exam_type: str
    paper_name: str
    session_type: str
    date: str
    duration_minutes: int = 0


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
    due_vocabulary_count: int = 0
    mastery_rate: float = 0.0
    pending_review_tasks_count: int = 0
    intensive_pending_count: int = 0
    starred_vocabulary_count: int = 0
    high_priority_starred_count: int = 0
    starred_due_today_count: int = 0
    top_mistake_tags: List[Dict[str, Any]] = []
    recent_sessions: List[RecentSessionSummary] = []
    recent_review_tasks: List[Dict[str, Any]] = []


class MasteryStats(BaseModel):
    total: int = 0
    new: int = 0
    learning: int = 0
    familiar: int = 0
    mastered: int = 0
    mastery_rate: float = 0.0
    reviewed_total: int = 0
    due_today: int = 0


class FamiliarityTrendItem(BaseModel):
    date: str
    new: int = 0
    learning: int = 0
    familiar: int = 0
    mastered: int = 0


class ReadingMistakeStats(BaseModel):
    by_question_type: List[Dict[str, Any]] = []
    mistake_tags: List[Dict[str, Any]] = []


class WeeklyReport(BaseModel):
    period: Dict[str, str] = {}
    training: Dict[str, Any] = {}
    vocabulary: Dict[str, Any] = {}
    review_tasks: Dict[str, Any] = {}
    weaknesses: List[str] = []
    suggestions: List[str] = []
