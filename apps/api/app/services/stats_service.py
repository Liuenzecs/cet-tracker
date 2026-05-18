"""Service layer for dashboard statistics."""

from typing import Dict, List

from sqlmodel import Session, select, func

from app.models.exam_session import ExamSession
from app.models.listening_result import ListeningResult
from app.models.reading_result import ReadingResult
from app.models.vocabulary import VocabularyEntry
from app.schemas.stats import DashboardStats, RecentSessionSummary, TrendPoint


def get_dashboard_stats(db: Session) -> DashboardStats:
    """Compute dashboard statistics from all tables."""

    # Session counts
    all_sessions = db.exec(select(ExamSession).order_by(ExamSession.date.desc())).all()
    total_sessions = len(all_sessions)
    total_listening = sum(
        1 for s in all_sessions if s.session_type in ("full_mock", "listening")
    )
    total_reading = sum(
        1 for s in all_sessions if s.session_type in ("full_mock", "reading")
    )

    # Average accuracies
    all_listening = db.exec(select(ListeningResult)).all()
    avg_listening = None
    if all_listening:
        accuracies = []
        for r in all_listening:
            if r.total_questions > 0:
                accuracies.append(r.correct_count / r.total_questions)
        if accuracies:
            avg_listening = round(sum(accuracies) / len(accuracies) * 100, 1)

    all_reading = db.exec(select(ReadingResult)).all()
    avg_reading = None
    if all_reading:
        accuracies = []
        for r in all_reading:
            if r.total_questions > 0:
                accuracies.append(r.correct_count / r.total_questions)
        if accuracies:
            avg_reading = round(sum(accuracies) / len(accuracies) * 100, 1)

    # Listening trend: last 5 sessions that have listening results
    listening_trend: List[TrendPoint] = []
    listening_sessions = [s for s in all_sessions if s.session_type in ("full_mock", "listening")]
    for s in listening_sessions[:5]:
        lr = db.exec(
            select(ListeningResult).where(ListeningResult.session_id == s.id)
        ).first()
        if lr and lr.total_questions > 0:
            accuracy = round(lr.correct_count / lr.total_questions * 100, 1)
        else:
            accuracy = None
        listening_trend.append(
            TrendPoint(date=s.date.isoformat(), accuracy=accuracy)
        )

    # Reading trend: last 10 reading results (across sessions), each point includes question_type
    reading_trend: List[TrendPoint] = []
    reading_sessions = [s for s in all_sessions if s.session_type in ("full_mock", "reading")]
    for s in reading_sessions[:5]:
        rr_list = db.exec(
            select(ReadingResult).where(ReadingResult.session_id == s.id)
        ).all()
        for rr in rr_list:
            if rr.total_questions > 0:
                accuracy = round(rr.correct_count / rr.total_questions * 100, 1)
                reading_trend.append(
                    TrendPoint(
                        date=s.date.isoformat(),
                        accuracy=accuracy,
                        question_type=rr.question_type,
                    )
                )

    # Vocabulary stats
    all_entries = db.exec(select(VocabularyEntry)).all()
    total_vocab = len(all_entries)
    vocab_by_familiarity: Dict[str, int] = {}
    for e in all_entries:
        fam = e.familiarity or "new"
        vocab_by_familiarity[fam] = vocab_by_familiarity.get(fam, 0) + 1

    pending_review = sum(
        1 for e in all_entries if e.familiarity in ("new", "learning")
    )

    # Recent sessions
    recent_sessions: List[RecentSessionSummary] = []
    for s in all_sessions[:5]:
        recent_sessions.append(
            RecentSessionSummary(
                id=s.id,
                exam_type=s.exam_type,
                paper_name=s.paper_name,
                session_type=s.session_type,
                date=s.date.isoformat(),
                duration_minutes=s.duration_minutes,
            )
        )

    return DashboardStats(
        total_sessions=total_sessions,
        total_listening_sessions=total_listening,
        total_reading_sessions=total_reading,
        avg_listening_accuracy=avg_listening,
        avg_reading_accuracy=avg_reading,
        listening_trend=listening_trend,
        reading_trend=reading_trend,
        total_vocabulary=total_vocab,
        vocabulary_by_familiarity=vocab_by_familiarity,
        pending_review=pending_review,
        recent_sessions=recent_sessions,
    )
