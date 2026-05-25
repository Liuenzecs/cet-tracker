"""Tests for report generation."""

from app.services.report_service import _get_period_range


class TestPeriodRange:
    def test_weekly_returns_tuple(self):
        start, end = _get_period_range("weekly")
        assert start is not None
        assert end is not None
        assert end > start

    def test_weekly_custom_dates(self):
        start, end = _get_period_range("weekly", "2026-05-01", "2026-05-10")
        assert start.date().isoformat() == "2026-05-01"
        assert end.date().isoformat() == "2026-05-10"
