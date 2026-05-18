"""Tests for the text cleaner utilities."""

import pytest
from app.utils.text_cleaner import (
    clean_inline_markdown,
    clean_markdown_noise,
    normalize_text_list,
    normalize_examples,
    normalize_comparisons,
)


class TestCleanInlineMarkdown:
    def test_removes_bold(self):
        assert clean_inline_markdown("**bold text**") == "bold text"
        assert clean_inline_markdown("__also bold__") == "also bold"
        assert clean_inline_markdown("**pending**：adj.") == "pending：adj."

    def test_removes_italic(self):
        assert clean_inline_markdown("*italic text*") == "italic text"
        assert clean_inline_markdown("_also italic_") == "also italic"

    def test_removes_inline_code(self):
        assert clean_inline_markdown("`code text`") == "code text"
        assert clean_inline_markdown("use `pending` here") == "use pending here"

    def test_removes_strikethrough(self):
        assert clean_inline_markdown("~~deleted~~") == "deleted"

    def test_handles_empty_and_non_string(self):
        assert clean_inline_markdown("") == ""
        assert clean_inline_markdown("   ") == ""
        assert clean_inline_markdown(None) == ""
        assert clean_inline_markdown(123) == "123"

    def test_handles_mixed_formatting(self):
        text = "**bold** and *italic* and `code`"
        result = clean_inline_markdown(text)
        assert result == "bold and italic and code"

    def test_preserves_plain_text(self):
        assert clean_inline_markdown("plain text") == "plain text"
        assert clean_inline_markdown("待处理的；悬而未决的") == "待处理的；悬而未决的"


class TestCleanMarkdownNoise:
    def test_removes_horizontal_rules(self):
        assert clean_markdown_noise("---") == ""
        assert clean_markdown_noise("***") == ""
        assert clean_markdown_noise("___") == ""
        assert clean_markdown_noise("---------") == ""

    def test_removes_table_separators(self):
        assert clean_markdown_noise("|---|---|---|") == ""
        assert clean_markdown_noise("|:---|:---:|---:|") == ""
        assert clean_markdown_noise("| --- | --- | --- |") == ""

    def test_removes_heading_markers(self):
        assert clean_markdown_noise("# Title") == "Title"
        assert clean_markdown_noise("## Section") == "Section"
        assert clean_markdown_noise("### Sub Section") == "Sub Section"
        assert clean_markdown_noise("###### Deep") == "Deep"

    def test_preserves_meaningful_text(self):
        assert clean_markdown_noise("pending") == "pending"
        assert clean_markdown_noise("待处理的") == "待处理的"

    def test_handles_empty(self):
        assert clean_markdown_noise("") == ""
        assert clean_markdown_noise(None) == ""


class TestNormalizeTextList:
    def test_filters_empty_and_noise(self):
        items = ["valid", "", "**bold**", "---", None, "|"]
        result = normalize_text_list(items)
        assert "valid" in result
        assert "bold" in result
        assert "---" not in result
        assert "" not in result

    def test_deduplicates(self):
        items = ["word", "word", "phrase"]
        result = normalize_text_list(items)
        assert len(result) == 2
        assert result == ["word", "phrase"]

    def test_handles_dict_items(self):
        items = [{"en": "hello", "zh": "你好"}]
        result = normalize_text_list(items)
        assert len(result) == 1
        assert "hello" in result[0]

    def test_handles_none_input(self):
        assert normalize_text_list(None) == []


class TestNormalizeExamples:
    def test_normalizes_dict_examples(self):
        items = [
            {"en": "The case is still pending.", "zh": "案件仍在审理中。"},
            {"en": "**bold example**", "zh": "**加粗例句**"},
        ]
        result = normalize_examples(items)
        assert len(result) == 2
        assert result[0]["en"] == "The case is still pending."
        assert result[1]["en"] == "bold example"
        assert result[1]["zh"] == "加粗例句"

    def test_normalizes_string_examples(self):
        items = ["Hello — 你好", "World --- 世界"]
        result = normalize_examples(items)
        assert len(result) == 2
        assert result[0]["en"] == "Hello"
        assert result[0]["zh"] == "你好"
        assert result[1]["en"] == "World"
        assert result[1]["zh"] == "世界"

    def test_filters_empty(self):
        items = ["", None, "  "]
        result = normalize_examples(items)
        assert result == []


class TestNormalizeComparisons:
    def test_normalizes_left_right(self):
        items = [
            {"left": "pending", "right": "impending",
             "left_meaning": "待处理的", "right_meaning": "即将发生的"}
        ]
        result = normalize_comparisons(items)
        assert len(result) == 1
        assert result[0]["left"] == "pending"
        assert result[0]["right"] == "impending"

    def test_normalizes_word1_word2_format(self):
        items = [{"word1": "come true", "word2": "materialise", "description": "实现"}]
        result = normalize_comparisons(items)
        assert len(result) == 1
        assert result[0]["left"] == "come true"
        assert result[0]["right"] == "materialise"
        assert result[0]["left_meaning"] == "实现"

    def test_normalizes_string_comparisons(self):
        items = ["pending vs impending"]
        result = normalize_comparisons(items)
        assert len(result) == 1
        assert result[0]["left"] == "pending vs impending"

    def test_cleans_markdown(self):
        items = [{"left": "**pending**", "right": "*impending*"}]
        result = normalize_comparisons(items)
        assert result[0]["left"] == "pending"
        assert result[0]["right"] == "impending"
