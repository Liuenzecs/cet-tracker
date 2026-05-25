"""Tests for the review system."""

from app.services.review_service import get_next_review_at, _ACTION_TO_FAMILIARITY


class TestSpacedRepetition:
    def test_again_returns_new(self):
        assert _ACTION_TO_FAMILIARITY["again"] == "new"

    def test_hard_returns_learning(self):
        assert _ACTION_TO_FAMILIARITY["hard"] == "learning"

    def test_good_returns_familiar(self):
        assert _ACTION_TO_FAMILIARITY["good"] == "familiar"

    def test_easy_returns_mastered(self):
        assert _ACTION_TO_FAMILIARITY["easy"] == "mastered"


class TestNextReviewAt:
    def test_learning_good_gives_3_days(self):
        import datetime as dt
        result = get_next_review_at("learning", "good")
        assert result is not None
        expected = dt.datetime.utcnow() + dt.timedelta(days=3)
        diff = abs((result - expected).total_seconds())
        assert diff < 60  # within 1 minute

    def test_familiar_good_gives_7_days(self):
        import datetime as dt
        result = get_next_review_at("familiar", "good")
        expected = dt.datetime.utcnow() + dt.timedelta(days=7)
        diff = abs((result - expected).total_seconds())
        assert diff < 60

    def test_new_again_gives_0_days(self):
        import datetime as dt
        result = get_next_review_at("new", "again")
        expected = dt.datetime.utcnow()
        diff = abs((result - expected).total_seconds())
        assert diff < 60

    def test_mastered_easy_gives_14_days(self):
        import datetime as dt
        result = get_next_review_at("mastered", "easy")
        expected = dt.datetime.utcnow() + dt.timedelta(days=14)
        diff = abs((result - expected).total_seconds())
        assert diff < 60
