"""Schemas for vocabulary review logs."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ReviewLogResponse(BaseModel):
    id: int
    entry_id: int
    note_id: int
    old_familiarity: str
    new_familiarity: str
    action: str
    reviewed_at: datetime
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewLogListResponse(BaseModel):
    items: List[ReviewLogResponse]
    total: int
    page: int
    page_size: int
