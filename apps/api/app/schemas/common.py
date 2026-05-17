"""Common response schemas for the CET Tracker API."""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""
    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: list[T]
    total: int
    page: int
    page_size: int
