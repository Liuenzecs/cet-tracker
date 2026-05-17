"""Markdown parser for CET vocabulary entries.

Parses structured markdown into vocabulary entry dicts for database storage.
Key principle: NEVER throw exceptions. Fall back to raw content in meanings.
"""

import re
from typing import Any, Dict, List, Optional


def _parse_example_line(line: str) -> Optional[Dict[str, str]]:
    """Parse a single example line like 'The case is still pending. --- 案件仍在审理中。'

    Returns {'en': 'The case is still pending.', 'zh': '案件仍在审理中。'}
    or None if the line cannot be parsed.
    """
    # Try splitting on em-dash (with optional spaces)
    for sep in [" --- ", " -- ", " — ", " —— ", "：", ": "]:
        if sep in line:
            parts = line.split(sep, 1)
            en = parts[0].strip()
            zh = parts[1].strip() if len(parts) > 1 else ""
            if en:
                return {"en": en, "zh": zh}
    return None


def _parse_list_items(raw_section: str) -> List[str]:
    """Extract list items from a markdown section.

    Items are lines starting with '- ', '* ', or numbered '1. '.
    """
    items: List[str] = []
    for line in raw_section.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Match bullet points or numbered items
        match = re.match(r"^(?:[-*]\s+|\d+\.\s+)(.*)$", line)
        if match:
            items.append(match.group(1).strip())
        else:
            # Also include continuation lines that aren't list markers
            items.append(line)
    return items


def _parse_examples(raw_section: str) -> List[Dict[str, str]]:
    """Parse example items into {en, zh} dicts."""
    results: List[Dict[str, str]] = []
    for line in raw_section.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Remove list markers for parsing
        clean = re.sub(r"^[-*]\s+", "", line)
        parsed = _parse_example_line(clean)
        if parsed:
            results.append(parsed)
        else:
            # If can't parse, store as en with empty zh
            results.append({"en": clean, "zh": ""})
    return results


def _parse_comparisons(raw_section: str) -> List[Dict[str, Any]]:
    """Parse structured comparisons like 'X vs Y - definition'."""
    results: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None
    items: List[str] = []

    for line in raw_section.strip().split("\n"):
        line = line.strip()
        if not line:
            if current and items:
                current["details"] = items
                results.append(current)
                current = None
                items = []
            continue

        # Check if this is a comparison header (X vs Y)
        vs_match = re.match(r"^(.+?)\s+vs[.]?\s+(.+?)(?:\s*[-=]\s*(.*))?$", line, re.IGNORECASE)
        if vs_match:
            # Save previous
            if current and items:
                current["details"] = items
                results.append(current)
                items = []

            term_a = vs_match.group(1).strip()
            term_b = vs_match.group(2).strip()
            desc = vs_match.group(3).strip() if vs_match.group(3) else ""
            current = {
                "term_a": term_a,
                "term_b": term_b,
                "description": desc,
                "details": [],
            }
            if desc:
                items.append(desc)
        elif re.match(r"^[-*]\s+(.*)", line) or re.match(r"^\d+\.\s+(.*)", line):
            # List item within comparison
            text = re.sub(r"^[-*\d]+[.\s]+\s*", "", line).strip()
            items.append(text)
        elif current:
            items.append(line)

    # Save the last one
    if current and items:
        current["details"] = items
        results.append(current)

    return results


def _standardize_section_name(name: str) -> str:
    """Map various Chinese section names to standardized field keys."""
    name = name.strip().lower()

    meaning_keywords = ["释义", "含义", "意思", "定义"]
    usage_keywords = ["常见用法", "用法", "搭配", "常见搭配", "使用"]
    example_keywords = ["例句", "示例", "例子"]
    mistake_keywords = ["易错点", "注意点", "注意事项", "易错", "注意"]
    synonym_keywords = ["同义替换", "近义词", "同义词", "替换"]
    comparison_keywords = ["易混词对比", "近义词对比", "对比", "比较", "易混"]
    writing_keywords = ["六级写作可用句", "写作可用句", "写作句", "写作"]
    review_keywords = ["快速复习表", "复习", "复习表"]

    for kw in meaning_keywords:
        if kw in name:
            return "meanings"
    for kw in usage_keywords:
        if kw in name:
            return "usages"
    for kw in example_keywords:
        if kw in name:
            return "examples"
    for kw in mistake_keywords:
        if kw in name:
            return "mistake_tips"
    for kw in synonym_keywords:
        if kw in name:
            return "synonyms"
    for kw in comparison_keywords:
        if kw in name:
            return "comparisons"
    for kw in writing_keywords:
        if kw in name:
            return "writing_sentences"
    for kw in review_keywords:
        if kw in name:
            return "quick_review"

    return "meanings"  # Default fallback


def parse_vocabulary_markdown(raw_markdown: str) -> List[Dict[str, Any]]:
    """Parse raw vocabulary markdown into structured entry dicts.

    Returns a list of dicts, each with keys matching VocabularyEntry fields.
    Never raises exceptions --- falls back to raw content in meanings.
    """
    if not raw_markdown or not raw_markdown.strip():
        return []

    entries: List[Dict[str, Any]] = []

    try:
        # Split by ## headings to get entry blocks
        # We need to find all ## headings, not ###
        blocks = re.split(r"\n(?=## [^#])", raw_markdown)

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            lines = block.split("\n")
            first_line = lines[0].strip()

            # Extract term: remove ## prefix and number prefix like "1. "
            term = re.sub(r"^##\s*", "", first_line).strip()
            term = re.sub(r"^\d+\.\s*", "", term).strip()

            if not term:
                continue

            # Get remaining content (after first line)
            remaining = "\n".join(lines[1:])

            # Initialize entry
            entry: Dict[str, List[Any]] = {
                "term": term,
                "entry_type": "word",
                "meanings": [],
                "usages": [],
                "examples": [],
                "mistake_tips": [],
                "synonyms": [],
                "comparisons": [],
                "writing_sentences": [],
            }

            # Split by ### sections
            sections = re.split(r"\n(?=### )", remaining)

            for section in sections:
                section = section.strip()
                if not section:
                    continue

                section_lines = section.split("\n")
                section_name = section_lines[0].strip()
                section_name = re.sub(r"^###\s*", "", section_name).strip()
                section_body = "\n".join(section_lines[1:]).strip()

                if not section_body:
                    continue

                field_key = _standardize_section_name(section_name)

                if field_key == "examples":
                    entry["examples"].extend(_parse_examples(section_body))
                elif field_key == "comparisons":
                    entry["comparisons"].extend(_parse_comparisons(section_body))
                elif field_key == "quick_review":
                    # Store quick review as a special meaning entry
                    entry["meanings"].append(
                        {"type": "quick_review", "content": _parse_list_items(section_body)}
                    )
                else:
                    # For meanings, usages, mistake_tips, synonyms, writing_sentences
                    items = _parse_list_items(section_body)
                    entry[field_key].extend(items)

            # If no sections were found, put entire remaining content in meanings
            has_content = any(
                entry[k] for k in entry if k not in ("term", "entry_type")
            )
            if not has_content and remaining.strip():
                entry["meanings"] = [remaining.strip()]

            # Convert to output format with _json suffix keys
            entries.append({
                "term": entry["term"],
                "entry_type": entry["entry_type"],
                "meanings_json": entry["meanings"],
                "usages_json": entry["usages"],
                "examples_json": entry["examples"],
                "mistake_tips_json": entry["mistake_tips"],
                "synonyms_json": entry["synonyms"],
                "comparisons_json": entry["comparisons"],
                "writing_sentences_json": entry["writing_sentences"],
            })

    except Exception:
        # Never fail --- return raw markdown as a single entry
        return [{
            "term": "未分类条目",
            "entry_type": "word",
            "meanings_json": [raw_markdown],
            "usages_json": [],
            "examples_json": [],
            "mistake_tips_json": [],
            "synonyms_json": [],
            "comparisons_json": [],
            "writing_sentences_json": [],
        }]

    return entries
