"""v0.3.2 Import/export roundtrip — create → export → clear → import → verify."""
import os, tempfile, json
_TEST_DB = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"
import pytest
from fastapi.testclient import TestClient
from app.database import engine, SQLModel

@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield

@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c

class TestRoundtrip:
    @classmethod
    def setup_class(cls):
        pass  # done in test methods

    def test_01_create_and_export(self, client):
        # Session
        r = client.post("/api/sessions", json={"exam_type":"CET6","paper_name":"RT Paper","session_type":"full_mock","date":"2024-06-20","duration_minutes":130,"note":"rt"})
        assert r.status_code == 200
        sid = r.json()["data"]["id"]

        # Listening + intensive
        r = client.post(f"/api/sessions/{sid}/listening", json={"total_questions":25,"correct_count":18,"mistake_tags_json":{"1":["单词不认识"]},"reflection":"rt"})
        assert r.status_code == 200
        lid = r.json()["data"]["id"]
        client.put(f"/api/listening/{lid}", json={"intensive_status":"completed","intensive_note":"Done"})

        # Reading
        r = client.post(f"/api/sessions/{sid}/reading", json={"question_type":"仔细阅读","total_questions":10,"correct_count":7,"mistake_tags_json":{"3":["词汇不认识"]}})
        assert r.status_code == 200

        # Vocab note
        r = client.post("/api/vocabulary/notes", json={"title":"RT Vocab","raw_markdown":"## pending\n\n### 释义\n待处理的","source_session_id":sid,"exam_type":"CET6","source_section":"reading"})
        assert r.status_code == 200
        nid = r.json()["data"]["id"]

        # Get entry + set phonetics + review
        r = client.get(f"/api/vocabulary/notes/{nid}/entries")
        entries = r.json()["data"]["items"]
        if entries:
            eid = entries[0]["id"]
            client.put(f"/api/vocabulary/entries/{eid}", json={
                "uk_phonetic": "/ˈpendɪŋ/",
                "us_phonetic": "/ˈpendɪŋ/",
            })
            client.put(f"/api/vocabulary/entries/{eid}/review?action=good")

        # Tasks
        client.post(f"/api/sessions/{sid}/generate-review-tasks")

        # EXPORT
        r = client.get("/api/export/json")
        assert r.status_code == 200
        envelope = r.json()
        assert envelope["success"] is True
        export_data = envelope["data"]
        TestRoundtrip.export_data = export_data

        assert "sessions" in export_data
        assert "listening_results" in export_data
        assert "reading_results" in export_data
        assert "vocabulary_notes" in export_data
        assert "vocabulary_entries" in export_data

        lr_list = export_data.get("listening_results", [])
        assert len(lr_list) == 1
        assert lr_list[0].get("intensive_status") == "completed"

        notes = export_data.get("vocabulary_notes", [])
        assert len(notes) == 1

        v_entries = export_data.get("vocabulary_entries", [])
        assert len(v_entries) >= 1
        entry = v_entries[0]
        assert "familiarity" in entry
        assert "review_count" in entry
        # v0.3.4: phonetics fields survive export
        assert entry.get("uk_phonetic") == "/ˈpendɪŋ/"
        assert entry.get("us_phonetic") == "/ˈpendɪŋ/"

    def test_02_import_and_verify(self, client):
        # Re-export to get current data (test isolation requires self-contained steps)
        r = client.get("/api/export/json")
        assert r.status_code == 200
        envelope = r.json()
        assert envelope["success"] is True
        export_data = envelope["data"]
        assert "sessions" in export_data

        r = client.post("/api/import/json", json=export_data)
        assert r.status_code == 200

        r = client.get("/api/stats/dashboard")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["total_sessions"] >= 1
        assert data["total_vocabulary"] >= 1

        r = client.get("/api/vocabulary/review")
        assert r.status_code == 200

        r = client.get("/api/reports/weekly")
        assert r.status_code == 200

        r = client.get("/api/review-tasks")
        assert r.status_code == 200
