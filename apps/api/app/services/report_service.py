"""Report service — weekly and monthly report generation."""

import datetime as dt
from collections import Counter
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

from app.models.exam_session import ExamSession
from app.models.listening_result import ListeningResult
from app.models.reading_result import ReadingResult
from app.models.review_log import VocabularyReviewLog
from app.models.review_task import ReviewTask
from app.models.vocabulary import VocabularyEntry


def _get_period_range(
    period: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> tuple:
    """Calculate start and end datetimes for a period."""
    now = dt.datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == "weekly":
        # Monday of this week
        start = today - dt.timedelta(days=today.weekday())
        end = today + dt.timedelta(days=1)  # up to today
    elif period == "monthly":
        # First of this month
        start = today.replace(day=1)
        end = today + dt.timedelta(days=1)
    else:
        start = today
        end = today + dt.timedelta(days=1)

    if start_date:
        try:
            start = dt.datetime.fromisoformat(start_date)
        except (ValueError, TypeError):
            pass
    if end_date:
        try:
            end = dt.datetime.fromisoformat(end_date)
        except (ValueError, TypeError):
            pass

    return start, end


def generate_weekly_report(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a weekly training report."""
    start, end = _get_period_range("weekly", start_date, end_date)

    # Sessions in period
    session_query = select(ExamSession).where(
        ExamSession.date >= start.date(),
        ExamSession.date <= end.date(),
    )
    sessions = list(db.exec(session_query).all())

    session_ids = [s.id for s in sessions]

    # Listening stats
    listening_query = select(ListeningResult).where(ListeningResult.session_id.in_(session_ids))
    listening_results = list(db.exec(listening_query).all()) if session_ids else []
    listening_accuracies = []
    for lr in listening_results:
        if lr.total_questions > 0:
            listening_accuracies.append(lr.correct_count / lr.total_questions * 100)

    # Reading stats
    reading_query = select(ReadingResult).where(ReadingResult.session_id.in_(session_ids))
    reading_results = list(db.exec(reading_query).all()) if session_ids else []
    reading_accuracies = []
    for rr in reading_results:
        if rr.total_questions > 0:
            reading_accuracies.append(rr.correct_count / rr.total_questions * 100)

    # Vocabulary in period
    review_logs_query = select(VocabularyReviewLog).where(
        VocabularyReviewLog.reviewed_at >= start,
        VocabularyReviewLog.reviewed_at <= end,
    )
    review_logs = list(db.exec(review_logs_query).all())

    all_entries = list(db.exec(select(VocabularyEntry)).all())
    mastered_count = sum(1 for e in all_entries if e.familiarity == "mastered")
    due_count = 0
    tomorrow = dt.datetime.utcnow() + dt.timedelta(days=1)
    for e in all_entries:
        if e.next_review_at and e.next_review_at < tomorrow:
            due_count += 1

    # Review tasks
    tasks_query = select(ReviewTask).where(
        ReviewTask.created_at >= start,
        ReviewTask.created_at <= end,
    )
    period_tasks = list(db.exec(tasks_query).all())
    tasks_created = len(period_tasks)
    tasks_completed = sum(1 for t in period_tasks if t.status == "done")
    tasks_pending = tasks_created - tasks_completed

    # Error tag analysis for weaknesses
    tag_counter: Counter = Counter()
    for lr in listening_results:
        if lr.mistake_tags_json:
            for tags in lr.mistake_tags_json.values():
                if isinstance(tags, list):
                    for t in tags:
                        tag_counter[t] += 1
    for rr in reading_results:
        if rr.mistake_tags_json:
            for tags in rr.mistake_tags_json.values():
                if isinstance(tags, list):
                    for t in tags:
                        tag_counter[t] += 1

    weaknesses = [tag for tag, _ in tag_counter.most_common(3)]

    # Build suggestions
    suggestions: List[str] = []
    if listening_accuracies and (sum(listening_accuracies) / len(listening_accuracies)) < 70:
        suggestions.append("本周听力正确率偏低，下周优先完成 2 次听力精听训练")
    if reading_accuracies and (sum(reading_accuracies) / len(reading_accuracies)) < 70:
        suggestions.append("建议针对阅读薄弱题型进行专项练习")
    if due_count > 0:
        suggestions.append(f"当前有 {due_count} 个词汇待复习，建议保持每日复习习惯")
    if tasks_pending > 0:
        suggestions.append(f"有 {tasks_pending} 个复盘任务待完成")
    if not suggestions:
        suggestions.append("保持当前节奏，继续稳定训练")

    return {
        "period": {
            "start_date": start.date().isoformat(),
            "end_date": end.date().isoformat(),
        },
        "training": {
            "session_count": len(sessions),
            "listening_count": len(listening_results),
            "reading_count": len(reading_results),
            "average_listening_accuracy": round(sum(listening_accuracies) / len(listening_accuracies), 1) if listening_accuracies else None,
            "average_reading_accuracy": round(sum(reading_accuracies) / len(reading_accuracies), 1) if reading_accuracies else None,
        },
        "vocabulary": {
            "new_entries": len(all_entries),
            "review_count": len(review_logs),
            "mastered_count": mastered_count,
            "due_today": due_count,
        },
        "review_tasks": {
            "created": tasks_created,
            "completed": tasks_completed,
            "pending": tasks_pending,
        },
        "weaknesses": weaknesses,
        "suggestions": suggestions,
    }


def generate_monthly_report(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a monthly training report."""
    return generate_weekly_report(db, start_date, end_date)  # Same logic, different period names
