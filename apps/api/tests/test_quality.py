"""Tests for vocabulary quality checks."""

from app.utils.term_utils import normalize_term
from app.services.quality_service import validate_generated_entries


class TestNormalizeTerm:
    def test_lowercase(self):
        assert normalize_term("Pending") == "pending"

    def test_trim_whitespace(self):
        assert normalize_term("  pending  ") == "pending"

    def test_collapse_spaces(self):
        assert normalize_term("real  estate") == "real estate"

    def test_strip_punctuation(self):
        assert normalize_term("pending.") == "pending"
        assert normalize_term('"pending"') == "pending"

    def test_does_not_merge_spellings(self):
        assert normalize_term("materialise") != normalize_term("materialize")

    def test_empty_string(self):
        assert normalize_term("") == ""


class TestValidateGeneratedEntries:
    def test_all_valid(self):
        entries = [{
            "term": "pending",
            "entry_type": "word",
            "meanings": [{"pos": "adj.", "zh": "待处理的"}],
            "examples": [{"en": "The case is pending.", "zh": "案件仍在审理中。"}],
        }]
        result = validate_generated_entries([], entries)
        assert result["summary"]["errors"] == 0
        assert result["items"][0]["level"] == "ok"

    def test_empty_term_error(self):
        entries = [{"term": "", "entry_type": "word"}]
        result = validate_generated_entries([], entries)
        assert result["items"][0]["level"] == "error"

    def test_no_meanings_warning(self):
        entries = [{"term": "test", "entry_type": "word", "meanings": []}]
        result = validate_generated_entries([], entries)
        assert result["items"][0]["level"] == "warning"

    def test_no_examples_warning(self):
        entries = [{"term": "test", "entry_type": "word", "meanings": [{"zh": "测试"}], "examples": []}]
        result = validate_generated_entries([], entries)
        assert result["items"][0]["level"] == "warning"

    def test_markdown_table_noise_warning(self):
        entries = [{"term": "test", "entry_type": "word", "meanings": [{"zh": "测试"}], "examples": [{"en": "x", "zh": "y"}], "usages_json": "|用法|含义|\n|---|---|"}]
        result = validate_generated_entries([], entries)
        levels = [it["level"] for it in result["items"]]
        assert "warning" in levels

    def test_document_title_warning(self):
        entries = [{"term": "图片笔记扩展", "entry_type": "word", "meanings": [{"zh": "x"}], "examples": [{"en": "x", "zh": "y"}]}]
        result = validate_generated_entries([], entries)
        assert result["items"][0]["level"] == "warning"

    def test_fewer_entries_than_input_warning(self):
        entries = [{"term": "pending", "entry_type": "word", "meanings": [{"zh": "x"}], "examples": [{"en": "x", "zh": "y"}]}]
        result = validate_generated_entries(["pending", "utmost", "real estate"], entries)
        assert len(result["items"]) == 1
