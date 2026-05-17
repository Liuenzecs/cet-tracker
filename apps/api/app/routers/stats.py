"""Router for dashboard statistics."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.schemas.common import APIResponse
from app.services import stats_service

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_session)):
    """Get dashboard statistics."""
    stats = stats_service.get_dashboard_stats(db)
    return APIResponse(data=stats.model_dump())
