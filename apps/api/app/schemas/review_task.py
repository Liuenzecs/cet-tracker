"""Schemas for review tasks."""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class ReviewTaskCreate(BaseModel):
    session_id: int
    task_type: str = "general"
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[date] = None


class ReviewTaskUpdate(BaseModel):
    task_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None


class ReviewTaskResponse(BaseModel):
    id: int
    session_id: int
    task_type: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
