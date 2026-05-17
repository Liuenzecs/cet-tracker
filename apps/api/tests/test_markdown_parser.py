"""Tests for the vocabulary markdown parser."""

import pytest
from app.utils.markdown_parser import parse_vocabulary_markdown


def test_parse_empty_markdown():
    """Empty or whitespace-only markdown returns an empty list."""
    assert parse_vocabulary_markdown("") == []
    assert parse_vocabulary_markdown("   \n\n  ") == []


def test_parse_basic_entry():
    """A single entry with ## heading and ### sections."""
    md = """## pending

### 释义
- 待解决的；待处理的
- 悬而未决的

### 常见用法
- pending case 待审理案件
- pending decision 待定决定

### 例句
- The case is still pending. --- 案件仍在审理中。
- The meeting is pending approval. --- 会议待批准。
"""
    results = parse_vocabulary_markdown(md)
    assert len(results) == 1
    entry = results[0]
    assert entry["term"] == "pending"
    assert entry["entry_type"] == "word"
    assert len(entry["meanings_json"]) >= 1
    assert len(entry["usages_json"]) >= 1
    assert len(entry["examples_json"]) >= 1
    # Check example parsing
    assert any(e.get("en", "").startswith("The case") for e in entry["examples_json"])
    assert any(e.get("zh", "").startswith("案件") for e in entry["examples_json"])


def test_parse_numbered_heading():
    """Entry with a numbered heading like '## 1. pending'."""
    md = """## 1. pending

### 释义
- 待处理的
"""
    results = parse_vocabulary_markdown(md)
    assert len(results) == 1
    assert results[0]["term"] == "pending"


def test_parse_multiple_entries():
    """Multiple ## headings produce multiple entries."""
    md = """## pending

### 释义
- 待处理的

## imminent

### 释义
- 即将发生的
"""
    results = parse_vocabulary_markdown(md)
    assert len(results) == 2
    assert results[0]["term"] == "pending"
    assert results[1]["term"] == "imminent"


def test_parse_without_sections():
    """Entry with ## heading but no ### sections puts content in meanings."""
    md = """## pending

Some plain text about the word "pending". It has multiple meanings.
"""
    results = parse_vocabulary_markdown(md)
    assert len(results) == 1
    assert results[0]["term"] == "pending"
    assert len(results[0]["meanings_json"]) >= 1
    assert "pending" in str(results[0]["meanings_json"])
    # Other fields should be empty
    assert results[0]["usages_json"] == []
    assert results[0]["examples_json"] == []


def test_parse_edge_case_section_names():
    """Parser recognizes alternative section names."""
    md = """## pending

### 含义
- 待处理的

### 注意点
- 别和 imminent 弄混

### 写作句
- The issue is still pending. --- 问题仍在处理中。
"""
    results = parse_vocabulary_markdown(md)
    assert len(results) == 1
    entry = results[0]
    assert len(entry["meanings_json"]) >= 1
    assert len(entry["mistake_tips_json"]) >= 1
    assert len(entry["writing_sentences_json"]) >= 1


def test_parse_examples_detail():
    """Example lines are correctly split into en/zh pairs."""
    md = """## test word

### 例句
- Hello world --- 你好世界。
"""
    results = parse_vocabulary_markdown(md)
    assert len(results) == 1
    examples = results[0]["examples_json"]
    assert len(examples) == 1
    assert examples[0]["en"] == "Hello world"
    assert examples[0]["zh"] == "你好世界。"


def test_parse_example_with_chinese_colon():
    """Example using Chinese colon as separator."""
    md = """## example

### 例句
- The sky is blue：天空是蓝色的。
"""
    results = parse_vocabulary_markdown(md)
    assert len(results) == 1
    examples = results[0]["examples_json"]
    assert len(examples) == 1
    assert examples[0]["en"] == "The sky is blue"
    assert "天空是蓝色的" in examples[0]["zh"]


def test_parse_example_no_separator():
    """Example without a clear separator stores as en only."""
    md = """## word

### 例句
- Just a plain sentence here
"""
    results = parse_vocabulary_markdown(md)
    assert len(results) == 1
    examples = results[0]["examples_json"]
    assert len(examples) == 1
    assert "plain sentence" in examples[0]["en"]


def test_parse_comparisons():
    """Structured comparison sections are parsed correctly."""
    md = """## pending

### 易混词对比
pending vs imminent
- pending = 等待决定/处理（中性）
- imminent = 即将发生的（通常指不好的事）
"""
    results = parse_vocabulary_markdown(md)
    assert len(results) == 1
    comparisons = results[0]["comparisons_json"]
    assert len(comparisons) >= 1
    comp = comparisons[0]
    assert comp["term_a"].lower() == "pending"
    assert comp["term_b"].lower() == "imminent"


def test_parse_quick_review():
    """Quick review section is stored in meanings as a special entry."""
    md = """## pending

### 快速复习表
- 释义：待处理的
- 用法：pending case
"""
    results = parse_vocabulary_markdown(md)
    assert len(results) == 1
    meanings = results[0]["meanings_json"]
    # Should have a quick_review entry
    review_entry = None
    for m in meanings:
        if isinstance(m, dict) and m.get("type") == "quick_review":
            review_entry = m
            break
    assert review_entry is not None


def test_parser_never_throws():
    """Parser returns a fallback entry instead of raising exceptions."""
    # Malformed input that could potentially cause issues
    md = "\x00\x01\x02"  # Binary-ish content
    results = parse_vocabulary_markdown(md)
    assert isinstance(results, list)
    # Should have at least a fallback entry
    assert len(results) >= 1
    assert "term" in results[0]
