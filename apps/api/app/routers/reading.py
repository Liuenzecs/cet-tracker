"""Router for reading result endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.schemas.common import APIResponse
from app.schemas.reading import (
    ReadingCreate,
    ReadingResponse,
    ReadingUpdate,
)
from app.services import reading_service, session_service

router = APIRouter(prefix="/api", tags=["reading"])


@router.get("/sessions/{session_id}/reading")
def get_reading(
    session_id: int,
    db: Session = Depends(get_session),
):
    """Get all reading results for a session."""
    if not session_service.get_session(db, session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    results = reading_service.get_reading_results(db, session_id)
    return APIResponse(
        data=[ReadingResponse.model_validate(r).model_dump() for r in results]
    )


@router.post("/sessions/{session_id}/reading")
def create_reading(
    session_id: int,
    body: ReadingCreate,
    db: Session = Depends(get_session),
):
    """Create a reading result for a session."""
    if not session_service.get_session(db, session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    result = reading_service.create_reading_result(db, session_id, body)
    return APIResponse(
        data=ReadingResponse.model_validate(result).model_dump(),
        success=True,
    )


@router.put("/reading/{result_id}")
def update_reading(
    result_id: int,
    body: ReadingUpdate,
    db: Session = Depends(get_session),
):
    """Update an existing reading result."""
    result = reading_service.update_reading_result(db, result_id, body)
    if not result:
        raise HTTPException(status_code=404, detail="Reading result not found")
    return APIResponse(data=ReadingResponse.model_validate(result).model_dump())


@router.get("/reading/stats/mistakes")
def reading_mistake_stats(
    db: Session = Depends(get_session),
):
    """Get reading mistake statistics by question type and tag."""
    from collections import Counter
    from app.models.reading_result import ReadingResult

    all_readings = db.exec(select(ReadingResult)).all()

    by_type: dict = {}
    tag_counter: Counter = Counter()

    for rr in all_readings:
        qtype = rr.question_type
        if qtype not in by_type:
            by_type[qtype] = {"total_accuracy": 0.0, "count": 0}
        if rr.total_questions > 0:
            by_type[qtype]["total_accuracy"] += rr.correct_count / rr.total_questions * 100
            by_type[qtype]["count"] += 1

        if rr.mistake_tags_json:
            for tags in rr.mistake_tags_json.values():
                if isinstance(tags, list):
                    for t in tags:
                        tag_counter[t] += 1

    by_question_type = []
    for qtype, data in by_type.items():
        avg_acc = round(data["total_accuracy"] / data["count"], 1) if data["count"] > 0 else 0.0
        by_question_type.append({
            "question_type": qtype,
            "average_accuracy": avg_acc,
            "total_sessions": data["count"],
        })

    mistake_tags = [{"tag": tag, "count": cnt} for tag, cnt in tag_counter.most_common(10)]

    return APIResponse(data={"by_question_type": by_question_type, "mistake_tags": mistake_tags})


@router.delete("/reading/{result_id}")
def delete_reading(
    result_id: int,
    db: Session = Depends(get_session),
):
    """Delete a reading result."""
    deleted = reading_service.delete_reading_result(db, result_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Reading result not found")
    return APIResponse(data={"deleted": True})
