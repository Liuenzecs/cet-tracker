"""Router for weekly and monthly reports."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.schemas.common import APIResponse
from app.services.report_service import generate_weekly_report, generate_monthly_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/weekly")
def weekly_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_session),
):
    """Generate a weekly training report."""
    result = generate_weekly_report(db, start_date, end_date)
    return APIResponse(data=result)


@router.get("/monthly")
def monthly_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_session),
):
    """Generate a monthly training report."""
    result = generate_monthly_report(db, start_date, end_date)
    return APIResponse(data=result)
