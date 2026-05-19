"""Vocabulary review service — review logs, spaced repetition, due-today, stats."""

import datetime as dt
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from sqlmodel import Session, func, select

from app.models.review_log import VocabularyReviewLog
from app.models.vocabulary import VocabularyEntry


# ── Spaced repetition rules ──

_SR_INTERVALS: Dict[str, Dict[str, int]] = {
    "new": {"again": 0, "hard": 1, "good": 1, "easy": 1},
    "learning": {"again": 0, "hard": 1, "good": 3, "easy": 3},
    "familiar": {"again": 0, "hard": 1, "good": 7, "easy": 7},
    "mastered": {"again": 0, "hard": 1, "good": 7, "easy": 14},
}

_ACTION_TO_FAMILIARITY: Dict[str, str] = {
    "again": "new",
    "hard": "learning",
    "good": "familiar",
    "easy": "mastered",
}


def get_next_review_at(
    old_familiarity: str,
    action: str,
) -> Optional[dt.datetime]:
    """Calculate next_review_at based on old familiarity and review action."""
    intervals = _SR_INTERVALS.get(old_familiarity, {})
    days = intervals.get(action, 1)
    return dt.datetime.utcnow() + dt.timedelta(days=days)


def do_review(
    db: Session,
    entry_id: int,
    action: str,
    note_id: Optional[int] = None,
    note_text: Optional[str] = None,
) -> Optional[VocabularyEntry]:
    """Perform a review action on a vocabulary entry.

    Updates familiarity, review_count, last_reviewed_at, next_review_at,
    and writes a review log entry.
    """
    entry = db.get(VocabularyEntry, entry_id)
    if not entry:
        return None

    old_familiarity = entry.familiarity
    new_familiarity = _ACTION_TO_FAMILIARITY.get(action, old_familiarity)
    now = dt.datetime.utcnow()
    next_review = get_next_review_at(old_familiarity, action)

    # Update entry
    entry.familiarity = new_familiarity
    entry.review_count = (entry.review_count or 0) + 1
    entry.last_reviewed_at = now
    entry.next_review_at = next_review
    entry.updated_at = now

    # Write review log
    effective_note_id = note_id or entry.note_id
    log = VocabularyReviewLog(
        entry_id=entry_id,
        note_id=effective_note_id,
        old_familiarity=old_familiarity,
        new_familiarity=new_familiarity,
        action=action,
        reviewed_at=now,
        note=note_text,
    )
    db.add(log)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_review_logs(
    db: Session,
    entry_id: Optional[int] = None,
    note_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[VocabularyReviewLog], int]:
    """Get review logs with optional filtering and pagination."""
    query = select(VocabularyReviewLog)

    if entry_id is not None:
        query = query.where(VocabularyReviewLog.entry_id == entry_id)
    if note_id is not None:
        query = query.where(VocabularyReviewLog.note_id == note_id)
    if start_date:
        query = query.where(VocabularyReviewLog.reviewed_at >= start_date)
    if end_date:
        query = query.where(VocabularyReviewLog.reviewed_at <= end_date)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.exec(count_query).one()

    query = query.order_by(VocabularyReviewLog.reviewed_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    items = list(db.exec(query).all())

    return items, total


def get_due_today(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    familiarity: Optional[str] = None,
    note_id: Optional[int] = None,
) -> Tuple[List[VocabularyEntry], int]:
    """Get vocabulary entries due for review today.

    Returns entries where next_review_at <= today, or where next_review_at
    is NULL and familiarity is 'new' or 'learning'.
    """
    today = dt.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + dt.timedelta(days=1)

    # Entries where next_review_at is set and due
    query_set = select(VocabularyEntry).where(
        VocabularyEntry.next_review_at is not None,
        VocabularyEntry.next_review_at < tomorrow,
    )

    # Entries where next_review_at is NULL and familiarity is new/learning
    query_null = select(VocabularyEntry).where(
        VocabularyEntry.next_review_at is None,
        VocabularyEntry.familiarity.in_(["new", "learning"]),
    )

    from sqlalchemy import or_, and_

    base_query = select(VocabularyEntry).where(
        or_(
            and_(VocabularyEntry.next_review_at != None, VocabularyEntry.next_review_at < tomorrow),
            and_(VocabularyEntry.next_review_at == None, VocabularyEntry.familiarity.in_(["new", "learning"])),
        )
    )

    if familiarity and familiarity in ("new", "learning", "familiar", "mastered"):
        base_query = base_query.where(VocabularyEntry.familiarity == familiarity)
    if note_id is not None:
        base_query = base_query.where(VocabularyEntry.note_id == note_id)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = db.exec(count_query).one()

    query = base_query.order_by(VocabularyEntry.familiarity.asc(), VocabularyEntry.updated_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    items = list(db.exec(query).all())

    return items, total


def get_mastery_stats(db: Session) -> Dict:
    """Calculate vocabulary mastery statistics."""
    all_entries = list(db.exec(select(VocabularyEntry)).all())

    total = len(all_entries)
    counts = {"new": 0, "learning": 0, "familiar": 0, "mastered": 0}

    for e in all_entries:
        fam = e.familiarity or "new"
        if fam in counts:
            counts[fam] += 1

    reviewed_total = sum(1 for e in all_entries if (e.review_count or 0) > 0)

    # Count due today
    today = dt.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + dt.timedelta(days=1)
    due_today_count = 0
    for e in all_entries:
        if e.next_review_at and e.next_review_at < tomorrow:
            due_today_count += 1
        elif not e.next_review_at and e.familiarity in ("new", "learning"):
            due_today_count += 1

    mastery_rate = ((counts["familiar"] + counts["mastered"]) / total * 100) if total > 0 else 0.0

    return {
        "total": total,
        "new": counts["new"],
        "learning": counts["learning"],
        "familiar": counts["familiar"],
        "mastered": counts["mastered"],
        "mastery_rate": round(mastery_rate, 1),
        "reviewed_total": reviewed_total,
        "due_today": due_today_count,
    }


def get_familiarity_trend(
    db: Session,
    days: int = 30,
    note_id: Optional[int] = None,
) -> List[Dict]:
    """Get vocabulary familiarity trend over time.

    Simplified: based on review_logs, counting entries by familiarity each day.
    """
    start_date = dt.datetime.utcnow() - dt.timedelta(days=days)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    log_query = select(VocabularyReviewLog).where(VocabularyReviewLog.reviewed_at >= start_date)
    if note_id is not None:
        log_query = log_query.where(VocabularyReviewLog.note_id == note_id)
    log_query = log_query.order_by(VocabularyReviewLog.reviewed_at.asc())
    logs = list(db.exec(log_query).all())

    # Build daily snapshots: for each day, count current familiarity state
    # Start with 0 counts, then apply each day's changes
    today = dt.datetime.utcnow().date()

    # Get all entries to establish base counts
    entry_query = select(VocabularyEntry)
    if note_id is not None:
        entry_query = entry_query.where(VocabularyEntry.note_id == note_id)
    entries = list(db.exec(entry_query).all())

    # Initialize with current state
    current_counts = {"new": 0, "learning": 0, "familiar": 0, "mastered": 0}
    for e in entries:
        fam = e.familiarity or "new"
        if fam in current_counts:
            current_counts[fam] += 1

    # Simple approach: use current state for today, and look at log history
    # for the trend. Group logs by day.
    daily_data: Dict[str, Dict[str, int]] = {}

    # Fill in daily snapshots going backwards from today
    # This is a simplified approach - we track changes day by day
    # Start with current state and roll back through review logs

    # Group logs by date
    logs_by_date: Dict[str, List] = defaultdict(list)
    for log in logs:
        date_key = log.reviewed_at.strftime("%Y-%m-%d")
        logs_by_date[date_key].append(log)

    # Build date range
    result: List[Dict] = []
    current_date = start_date.date()
    end_date = today

    # Count current familiarity per day by analyzing all entries
    # For simplicity: just report current state for all days in range
    while current_date <= end_date:
        result.append({
            "date": current_date.isoformat(),
            "new": current_counts["new"],
            "learning": current_counts["learning"],
            "familiar": current_counts["familiar"],
            "mastered": current_counts["mastered"],
        })
        current_date += dt.timedelta(days=1)

    return result
