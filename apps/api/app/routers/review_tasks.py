"""Router for review task CRUD and generation."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.listening_result import ListeningResult
from app.models.reading_result import ReadingResult
from app.models.review_task import ReviewTask
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.review_task import (
    ReviewTaskCreate,
    ReviewTaskResponse,
    ReviewTaskUpdate,
)

router = APIRouter(prefix="/api", tags=["review-tasks"])


@router.get("/review-tasks")
def list_tasks(
    session_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_session),
):
    """List review tasks with filtering and pagination."""
    from sqlmodel import func

    query = select(ReviewTask)
    if session_id is not None:
        query = query.where(ReviewTask.session_id == session_id)
    if status:
        query = query.where(ReviewTask.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.exec(count_query).one()

    query = query.order_by(ReviewTask.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    items = list(db.exec(query).all())

    return APIResponse(
        data=PaginatedResponse(
            items=[ReviewTaskResponse.model_validate(t).model_dump() for t in items],
            total=total, page=page, page_size=page_size,
        ).model_dump()
    )


@router.post("/review-tasks")
def create_task(
    body: ReviewTaskCreate,
    db: Session = Depends(get_session),
):
    """Create a review task manually."""
    task = ReviewTask(
        session_id=body.session_id,
        task_type=body.task_type,
        title=body.title,
        description=body.description,
        priority=body.priority,
        due_date=body.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return APIResponse(data=ReviewTaskResponse.model_validate(task).model_dump(), success=True)


@router.get("/review-tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_session)):
    """Get a single review task."""
    task = db.get(ReviewTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Review task not found")
    return APIResponse(data=ReviewTaskResponse.model_validate(task).model_dump())


@router.put("/review-tasks/{task_id}")
def update_task(
    task_id: int,
    body: ReviewTaskUpdate,
    db: Session = Depends(get_session),
):
    """Update a review task."""
    task = db.get(ReviewTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Review task not found")

    import datetime as dt
    update_data = body.model_dump(exclude_unset=True)

    if body.status == "done" and not update_data.get("completed_at"):
        update_data["completed_at"] = dt.datetime.utcnow()

    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = dt.datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)
    return APIResponse(data=ReviewTaskResponse.model_validate(task).model_dump())


@router.delete("/review-tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_session)):
    """Delete a review task."""
    task = db.get(ReviewTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Review task not found")
    db.delete(task)
    db.commit()
    return APIResponse(data={"deleted": True})


@router.post("/sessions/{session_id}/generate-review-tasks")
def generate_tasks(
    session_id: int,
    db: Session = Depends(get_session),
):
    """Auto-generate review tasks for a session based on its listening/reading results."""
    from app.models.exam_session import ExamSession

    session = db.get(ExamSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check for existing tasks to avoid duplicates
    existing_tasks = db.exec(
        select(ReviewTask).where(ReviewTask.session_id == session_id)
    ).all()
    existing_titles = {t.title for t in existing_tasks}

    generated: List[str] = []

    # Listening-based tasks
    lr = db.exec(
        select(ListeningResult).where(ListeningResult.session_id == session_id)
    ).first()
    if lr:
        accuracy = (lr.correct_count / lr.total_questions * 100) if lr.total_questions > 0 else 100

        if accuracy < 70:
            title = f"听力复盘 — {session.paper_name}"
            if title not in existing_titles:
                task = ReviewTask(
                    session_id=session_id,
                    task_type="listening_review",
                    title=title,
                    description=f"听力正确率 {accuracy:.1f}%，低于 70%，建议精听复盘",
                    priority="high",
                )
                db.add(task)
                generated.append(title)

        # Check mistake tags for vocabulary issues
        if lr.mistake_tags_json:
            has_vocab = False
            for tags in lr.mistake_tags_json.values():
                if isinstance(tags, list) and "单词不认识" in tags:
                    has_vocab = True
                    break
            if has_vocab:
                title = f"听力词汇复习 — {session.paper_name}"
                if title not in existing_titles:
                    task = ReviewTask(
                        session_id=session_id,
                        task_type="vocabulary_review",
                        title=title,
                        description="听力中存在单词不认识问题，建议整理生词",
                        priority="medium",
                    )
                    db.add(task)
                    generated.append(title)

    # Reading-based tasks
    reading_results = db.exec(
        select(ReadingResult).where(ReadingResult.session_id == session_id)
    ).all()
    for rr in reading_results:
        accuracy = (rr.correct_count / rr.total_questions * 100) if rr.total_questions > 0 else 100

        if accuracy < 70:
            title = f"阅读 {rr.question_type} 复盘 — {session.paper_name}"
            if title not in existing_titles:
                task = ReviewTask(
                    session_id=session_id,
                    task_type="reading_review",
                    title=title,
                    description=f"阅读 {rr.question_type} 正确率 {accuracy:.1f}%，低于 70%，建议错题复盘",
                    priority="high",
                )
                db.add(task)
                generated.append(title)

        if rr.mistake_tags_json:
            has_vocab = False
            has_locate = False
            for tags in rr.mistake_tags_json.values():
                if isinstance(tags, list):
                    if "词汇不认识" in tags:
                        has_vocab = True
                    if "定位错误" in tags:
                        has_locate = True

            if has_vocab:
                title = f"阅读词汇复习 — {session.paper_name}"
                if title not in existing_titles:
                    task = ReviewTask(
                        session_id=session_id,
                        task_type="vocabulary_review",
                        title=title,
                        description="阅读中存在词汇不认识问题，建议整理生词",
                        priority="medium",
                    )
                    db.add(task)
                    generated.append(title)

            if has_locate:
                title = f"阅读定位训练 — {session.paper_name}"
                if title not in existing_titles:
                    task = ReviewTask(
                        session_id=session_id,
                        task_type="reading_review",
                        title=title,
                        description="阅读中存在定位错误问题，建议专项练习",
                        priority="medium",
                    )
                    db.add(task)
                    generated.append(title)

    db.commit()

    result_tasks = db.exec(
        select(ReviewTask).where(ReviewTask.session_id == session_id)
    ).all()

    return APIResponse(data={
        "generated": generated,
        "total_tasks": len(result_tasks),
        "tasks": [ReviewTaskResponse.model_validate(t).model_dump() for t in result_tasks],
    })
