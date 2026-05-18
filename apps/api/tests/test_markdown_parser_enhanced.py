"""Tests for the enhanced v0.2.0 markdown parser."""

import pytest
from app.utils.markdown_parser import parse_vocabulary_markdown


class TestParseH1Heading:
    """Format A: # heading with colon fields."""

    def test_h1_with_colon_fields(self):
        md = """# pending

释义：等待处理的；悬而未决的
常见用法：
- pending decision
- pending approval
"""
        results = parse_vocabulary_markdown(md)
        assert len(results) >= 1
        entry = results[0]
        assert entry["term"] == "pending"
        assert len(entry["meanings_json"]) >= 1


class TestParseColonFields:
    """Format C: plain term with colon-delimited fields."""

    def test_plain_term_with_colon(self):
        md = """pending
释义：等待处理的；悬而未决的
例句：
The case is still pending. — 案件仍在审理中。"""
        results = parse_vocabulary_markdown(md)
        assert len(results) >= 1
        entry = results[0]
        assert entry["term"] == "pending"
        assert len(entry["meanings_json"]) >= 1
        assert len(entry["examples_json"]) >= 1

    def test_term_with_multiple_colon_fields(self):
        md = """sustainable
释义：可持续的
常见用法：
- sustainable development — 可持续发展
- sustainable growth — 可持续增长
易错点：
- 不是"可支撑的"（那是 supporting）
同义替换：
- viable, maintainable"""
        results = parse_vocabulary_markdown(md)
        assert len(results) >= 1
        entry = results[0]
        assert entry["term"] == "sustainable"
        assert len(entry["meanings_json"]) >= 1
        assert len(entry["usages_json"]) >= 1
        assert len(entry["mistake_tips_json"]) >= 1
        assert len(entry["synonyms_json"]) >= 1


class TestParseMarkdownTable:
    """Format D: markdown table."""

    def test_basic_table(self):
        md = """| 单词 | 释义 | 例句 |
| pending | 待处理的 | The case is still pending. |
| sustainable | 可持续的 | We need a sustainable solution. |"""
        results = parse_vocabulary_markdown(md)
        assert len(results) >= 1
        terms = [r["term"] for r in results]
        assert "pending" in terms

    def test_table_with_multiple_columns(self):
        md = """| 单词 | 释义 | 用法 | 例句 |
| pending | 待处理的 | pending decision | The case is still pending. |"""
        results = parse_vocabulary_markdown(md)
        assert len(results) >= 1
        entry = results[0]
        assert entry["term"] == "pending"
        assert len(entry["meanings_json"]) >= 1


class TestIgnoreDocumentTitle:
    """Document titles like '图片笔记扩展' should not become entries."""

    def test_ignore_chinese_title(self):
        md = """# 图片笔记扩展：词汇释义、用法、例句

## pending

### 释义
待处理的"""
        results = parse_vocabulary_markdown(md)
        terms = [r["term"] for r in results]
        assert "pending" in terms
        # The document title should NOT appear as an entry
        assert not any("图片笔记" in t for t in terms)

    def test_ignore_vocabulary_table_title(self):
        md = """# 词汇表

## apple
释义：苹果"""
        results = parse_vocabulary_markdown(md)
        terms = [r["term"] for r in results]
        assert "apple" in terms
        assert not any("词汇表" in t for t in terms)

    def test_ignore_review_table_title(self):
        md = """# 复习表

## book
释义：书"""
        results = parse_vocabulary_markdown(md)
        terms = [r["term"] for r in results]
        assert "book" in terms
        assert not any("复习表" in t for t in terms)

    def test_ignore_index_title(self):
        md = """# 目录

## word
释义：单词"""
        results = parse_vocabulary_markdown(md)
        terms = [r["term"] for r in results]
        assert "word" in terms
        assert not any("目录" in t for t in terms)


class TestParserRemovesMarkdownNoise:
    """Parser output must not contain raw markdown noise."""

    def test_no_bold_in_meanings(self):
        md = """## pending

### 释义
- **pending**：adj. 待定的；尚未决定的"""
        results = parse_vocabulary_markdown(md)
        assert len(results) >= 1
        for meaning in results[0]["meanings_json"]:
            assert "**" not in str(meaning)

    def test_no_table_separators(self):
        md = """## pending

### 常见用法
| 用法 | 含义 | 例子 |
|---|---|---|
| pending decision | 待定的决定 | a pending decision |"""
        results = parse_vocabulary_markdown(md)
        assert len(results) >= 1
        for usage in results[0].get("usages_json", []):
            assert "|--" not in str(usage)
            assert "---|---" not in str(usage)

    def test_no_heading_markers_in_output(self):
        md = """## pending

### 释义
### 这个不应该出现
- 待处理的"""
        results = parse_vocabulary_markdown(md)
        assert len(results) >= 1
        for meaning in results[0]["meanings_json"]:
            assert not str(meaning).startswith("###")

    def test_comparison_output_is_clean(self):
        md = """## materialise vs come true

### 易混词对比
| 词 | 使用对象 | 例句 |
|---|---|---|
| come true | dream, wish | My dream came true. |
| materialise | plan, hope | The expected benefits failed to materialise. |"""
        results = parse_vocabulary_markdown(md)
        assert len(results) >= 1
        comps = results[0].get("comparisons_json", [])
        for comp in comps:
            if isinstance(comp, dict):
                for v in comp.values():
                    if isinstance(v, str):
                        assert "|" not in v or "---" in v  # Allow pipe char, but not |---
                        assert "**" not in v


class TestParserAlwaysReturns:
    def test_malformed_input(self):
        results = parse_vocabulary_markdown("\x00\x01")
        assert isinstance(results, list)

    def test_empty_string(self):
        assert parse_vocabulary_markdown("") == []

    def test_only_noise(self):
        results = parse_vocabulary_markdown("---\n***\n___")
        # Should either be empty or have one fallback
        assert isinstance(results, list)


class TestComplexExample:
    """The exact example from the acceptance criteria."""

    def test_acceptance_example(self):
        md = """# 图片笔记扩展：词汇释义、用法、例句

## pending

### 释义
**pending**：adj. 待定的；尚未决定的；prep. 在……期间

### 常见用法
| 用法 | 含义 | 例子 |
|---|---|---|
| pending decision | 待定的决定 | a pending decision |
| remain pending | 仍然悬而未决 | The matter remains pending. |

### 例句
1. **The final decision is still pending.**
最终决定仍未作出。

---

## materialise vs come true

### 易混词对比
| 词 | 使用对象 | 例句 |
|---|---|---|
| come true | dream, wish | My dream came true. |
| materialise | plan, hope, opportunity | The expected benefits failed to materialise. |"""
        results = parse_vocabulary_markdown(md)

        terms = [r["term"] for r in results]
        assert "pending" in terms

        # Check no markdown noise
        for entry in results:
            for field in ["meanings_json", "usages_json", "examples_json",
                          "mistake_tips_json", "synonyms_json"]:
                for item in entry.get(field, []) or []:
                    if isinstance(item, str):
                        assert "**" not in item
                        assert "|--" not in item
                    elif isinstance(item, dict):
                        for v in item.values():
                            if isinstance(v, str):
                                assert "**" not in v
