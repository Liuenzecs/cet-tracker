"""Router for data import / export endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas.common import APIResponse
from app.schemas.import_export import ExportData
from app.services import import_export_service

router = APIRouter(prefix="/api", tags=["import-export"])


@router.get("/export/json")
def export_json(db: Session = Depends(get_session)):
    """Export all data as JSON."""
    data = import_export_service.export_all(db)
    return APIResponse(data=data.model_dump())


@router.post("/import/json")
def import_json(
    body: ExportData,
    db: Session = Depends(get_session),
):
    """Import data from JSON, replacing all existing data."""
    try:
        result = import_export_service.import_all(db, body)
        return APIResponse(data=result.model_dump(), success=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")
