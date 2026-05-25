"""v0.3.2 API smoke test — complete minimal closed loop.

Uses a test SQLite database via DATABASE_URL override before app import.
Does NOT call real DeepSeek.
"""

import os
import tempfile

# Set test DB before any app imports
_TEST_DB = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"

import pytest
from fastapi.testclient import TestClient

from app.database import engine, init_db, SQLModel


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield


@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


class TestSmokeFlow:
    _session_id = None
    _listening_id = None
    _reading_id = None
    _note_id = None
    _entry_id = None

    def test_01_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_02_create_session(self, client):
        r = client.post("/api/sessions", json={
            "exam_type": "CET6", "paper_name": "Smoke Test",
            "session_type": "full_mock", "date": "2024-06-15",
            "duration_minutes": 130, "note": "smoke"
        })
        assert r.status_code == 200
        TestSmokeFlow._session_id = r.json()["data"]["id"]

    def test_03_listening(self, client):
        r = client.post(f"/api/sessions/{self._session_id}/listening", json={
            "total_questions": 25, "correct_count": 16,
            "wrong_questions_text": "1,5,8,12,15,17,18,20,23",
            "mistake_tags_json": {"1": ["单词不认识"]},
            "reflection": "smoke"
        })
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["intensive_status"] == "not_started"
        TestSmokeFlow._listening_id = data["id"]

    def test_04_reading(self, client):
        r = client.post(f"/api/sessions/{self._session_id}/reading", json={
            "question_type": "仔细阅读", "total_questions": 10, "correct_count": 5,
            "mistake_tags_json": {"3": ["词汇不认识"], "7": ["定位错误"]}
        })
        assert r.status_code == 200
        TestSmokeFlow._reading_id = r.json()["data"]["id"]

    def test_05_create_note(self, client):
        r = client.post("/api/vocabulary/notes", json={
            "title": "Smoke Vocab",
            "raw_markdown": "## pending\n\n### 释义\n待处理的\n\n### 例句\n- The case is pending. --- 案件审理中。",
            "source_session_id": self._session_id,
            "exam_type": "CET6", "source_section": "reading"
        })
        assert r.status_code == 200
        TestSmokeFlow._note_id = r.json()["data"]["id"]

    def test_06_entries(self, client):
        r = client.get(f"/api/vocabulary/notes/{self._note_id}/entries")
        assert r.status_code == 200
        items = r.json()["data"]["items"]
        assert len(items) > 0
        TestSmokeFlow._entry_id = items[0]["id"]
        # v0.3.4: manually set phonetics on the entry
        client.put(f"/api/vocabulary/entries/{self._entry_id}", json={
            "uk_phonetic": "/ˈpendɪŋ/",
            "us_phonetic": "/ˈpendɪŋ/",
        })

    def test_07_duplicates(self, client):
        r = client.post("/api/vocabulary/check-duplicates", json={"terms": ["pending", "nonexistent"]})
        assert r.status_code == 200
        assert len(r.json()["data"]["duplicates"]) >= 1

    def test_08_validate(self, client):
        r = client.post("/api/vocabulary/validate-generated", json={
            "input_words": ["pending"],
            "entries": [{"term": "pending", "entry_type": "word",
                         "meanings": [{"zh": "x"}], "examples": [{"en": "x", "zh": "y"}]}]
        })
        assert r.status_code == 200

    def test_09_ai_status(self, client):
        r = client.get("/api/vocabulary/ai-status")
        assert r.status_code == 200

    def test_10_ai_graceful(self, client):
        r = client.post("/api/vocabulary/generate-from-words", json={
            "title": "t", "exam_type": "CET6", "source_section": "other",
            "words": ["pending"],
            "options": {"detail_level": "brief", "example_style": "cet",
                        "include_writing_sentences": False, "include_comparisons": False,
                        "language": "zh-CN"}
        })
        assert r.status_code in (200, 422)

    def test_11_review(self, client):
        r = client.get("/api/vocabulary/review")
        assert r.status_code == 200

    def test_12_review_action(self, client):
        r = client.put(f"/api/vocabulary/entries/{self._entry_id}/review?action=good")
        assert r.status_code == 200
        entry = r.json()["data"]
        assert entry["review_count"] >= 1
        assert entry["last_reviewed_at"] is not None

    def test_13_review_log(self, client):
        r = client.get(f"/api/vocabulary/review-logs?entry_id={self._entry_id}")
        assert r.status_code == 200
        assert len(r.json()["data"]["items"]) >= 1

    def test_14_due_today(self, client):
        r = client.get("/api/vocabulary/due-today")
        assert r.status_code == 200

    def test_15_mastery(self, client):
        r = client.get("/api/vocabulary/stats/mastery")
        assert r.status_code == 200
        assert "mastery_rate" in r.json()["data"]

    def test_16_trend(self, client):
        r = client.get("/api/vocabulary/stats/familiarity-trend?days=7")
        assert r.status_code == 200

    def test_17_generate_tasks(self, client):
        r = client.post(f"/api/sessions/{self._session_id}/generate-review-tasks")
        assert r.status_code == 200

    def test_18_list_tasks(self, client):
        r = client.get(f"/api/review-tasks?session_id={self._session_id}")
        assert r.status_code == 200

    def test_19_reports(self, client):
        r = client.get("/api/reports/weekly")
        assert r.status_code == 200
        r = client.get("/api/reports/monthly")
        assert r.status_code == 200

    def test_20_dashboard(self, client):
        r = client.get("/api/stats/dashboard")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["total_sessions"] >= 1
        assert "due_vocabulary_count" in data
        assert "mastery_rate" in data

    def test_21_reading_mistakes(self, client):
        r = client.get("/api/reading/stats/mistakes")
        assert r.status_code == 200

    def test_22_intensive(self, client):
        r = client.put(f"/api/listening/{self._listening_id}", json={
            "intensive_status": "completed", "intensive_note": "Done"
        })
        assert r.status_code == 200
        assert r.json()["data"]["intensive_status"] == "completed"

    def test_23_export_import(self, client):
        r = client.get("/api/export/json")
        assert r.status_code == 200
        envelope = r.json()
        assert envelope["success"] is True
        data = envelope["data"]
        r = client.post("/api/import/json", json=data)
        assert r.status_code == 200
        r = client.get("/api/stats/dashboard")
        assert r.status_code == 200

    def test_24_parse_md(self, client):
        r = client.post("/api/vocabulary/parse-markdown", json={"raw_markdown": "## test\n\n### 释义\n测试"})
        assert r.status_code == 200

    def test_25_star_entry(self, client):
        """v0.4.0: star the smoke entry."""
        eid = self._entry_id
        if eid is None:
            # entry may have been re-assigned by import
            r = client.get("/api/vocabulary/notes")
            notes = r.json()["data"]["items"]
            if notes:
                r = client.get(f"/api/vocabulary/notes/{notes[0]['id']}/entries")
                items = r.json()["data"]["items"]
                if items:
                    eid = items[0]["id"]
        if eid is None:
            pytest.skip("No entry available for star test")
        r = client.put(f"/api/vocabulary/entries/{eid}/star", json={
            "is_starred": True, "star_note": "smoke star", "star_priority": "high"
        })
        assert r.status_code == 200
        assert r.json()["data"]["is_starred"] is True
        TestSmokeFlow._entry_id = eid

    def test_26_starred_list(self, client):
        r = client.get("/api/vocabulary/starred")
        assert r.status_code == 200

    def test_27_starred_review(self, client):
        r = client.get("/api/vocabulary/review?starred=true")
        assert r.status_code == 200

    def test_27_starred_review(self, client):
        r = client.get("/api/vocabulary/review?starred=true")
        assert r.status_code == 200
