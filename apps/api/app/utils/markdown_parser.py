"""Markdown parser for CET vocabulary entries.

Parses structured markdown into vocabulary entry dicts for database storage.
Key principle: NEVER throw exceptions. Fall back to raw content in meanings.

Supported formats:

Format A (colon-style fields):
    # pending
    释义：等待处理的；悬而未决的
    常见用法：
    - pending decision
    - pending approval

Format B (heading + sub-sections):
    ## pending
    ### 释义
    - 等待处理的
    - 悬而未决的

Format C (plain term with colon fields):
    pending
    释义：等待处理的；悬而未决的
    例句：
    The case is still pending. — 案件仍在审理中。

Format D (markdown table):
    | 单词 | 释义 | 例句 |
    | pending | 待处理的 | The case is still pending. |

Format E (AI-generated / mixed):
    Hybrid with bold, numbering, tables, colons, separators.
"""

import re
from typing import Any, Dict, List, Optional, Union

from app.utils.text_cleaner import (
    clean_inline_markdown,
    clean_markdown_noise,
    normalize_text_list,
    normalize_examples,
    normalize_comparisons,
)

# Patterns for detecting document-level titles that should NOT be entries
_DOC_TITLE_PATTERNS = [
    re.compile(r"图片笔记", re.IGNORECASE),
    re.compile(r"笔记扩展", re.IGNORECASE),
    re.compile(r"词汇笔记", re.IGNORECASE),
    re.compile(r"词汇表", re.IGNORECASE),
    re.compile(r"目录$"),
    re.compile(r"大纲$"),
    re.compile(r"索引$"),
    re.compile(r"前言$"),
    re.compile(r"说明$"),
    re.compile(r"总结$"),
    re.compile(r"复习表$"),
    re.compile(r"词汇总览", re.IGNORECASE),
    re.compile(r"分类词汇", re.IGNORECASE),
]


def _is_document_title(text: str) -> bool:
    """Check if a line looks like a document-level title rather than a vocabulary entry."""
    text = text.strip()
    # Strip heading markers and leading numbers
    stripped = re.sub(r"^#{1,6}\s*", "", text)
    stripped = re.sub(r"^\d+[\.\、\s]+", "", stripped).strip()

    if not stripped or len(stripped) < 2:
        return True  # too short to be a useful entry

    for pat in _DOC_TITLE_PATTERNS:
        if pat.search(stripped):
            return True

    # If it starts with common Chinese title patterns without being a word
    if re.match(r"^(第[一二三四五六七八九十\d]+|[章节]|Part|Section|Unit)", stripped):
        return True

    return False


def _parse_example_line(line: str) -> Optional[Dict[str, str]]:
    """Parse a single example line like 'The case is still pending. --- 案件仍在审理中。'"""
    line = clean_inline_markdown(line)
    line = clean_markdown_noise(line)
    if not line:
        return None

    for sep in [" --- ", " -- ", " — ", " —— ", "：", ": "]:
        if sep in line:
            parts = line.split(sep, 1)
            en = parts[0].strip()
            zh = parts[1].strip() if len(parts) > 1 else ""
            if en:
                return {"en": en, "zh": zh}
    return None


def _parse_list_items(raw_section: str) -> List[str]:
    """Extract list items from a markdown section. Cleans markdown noise."""
    items: List[str] = []
    for line in raw_section.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Skip markdown table separator rows
        if re.match(r"^[\|\s\-:]+$", line) and re.search(r"---", line):
            continue
        # Match bullet points or numbered items
        match = re.match(r"^(?:[-*]\s+|\d+[\.\、\)]\s+)(.*)$", line)
        if match:
            text = match.group(1).strip()
            text = clean_inline_markdown(text)
            if text:
                items.append(text)
        else:
            text = clean_inline_markdown(line)
            if text:
                items.append(text)
    return items


def _parse_examples(raw_section: str) -> List[Dict[str, str]]:
    """Parse example items into {en, zh} dicts."""
    results: List[Dict[str, str]] = []
    for line in raw_section.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Skip table separators
        if re.match(r"^[\|\s\-:]+$", line) and re.search(r"---", line):
            continue
        clean = re.sub(r"^[-*\d]+[.\s\)]+\s*", "", line)
        parsed = _parse_example_line(clean)
        if parsed:
            results.append(parsed)
        else:
            clean_text = clean_inline_markdown(clean)
            clean_text = clean_markdown_noise(clean_text)
            if clean_text:
                results.append({"en": clean_text, "zh": ""})
    return results


def _parse_comparisons(raw_section: str) -> List[Dict[str, Any]]:
    """Parse structured comparisons like 'X vs Y - definition' or '| 词 | 使用对象 | 例句 |'."""
    results: List[Dict[str, Any]] = []

    # First check if this is a markdown table for comparisons
    if "|" in raw_section:
        table_results = _parse_comparison_table(raw_section)
        if table_results:
            return table_results

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

        # Skip table separators
        if re.match(r"^[\|\s\-:]+$", line) and re.search(r"---", line):
            continue

        vs_match = re.match(
            r"^(.+?)\s+vs[.]?\s+(.+?)(?:\s*[-=]\s*(.*))?$", line, re.IGNORECASE
        )
        if vs_match:
            if current and items:
                current["details"] = items
                results.append(current)
                items = []

            term_a = clean_inline_markdown(vs_match.group(1).strip())
            term_b = clean_inline_markdown(vs_match.group(2).strip())
            desc = vs_match.group(3).strip() if vs_match.group(3) else ""
            desc = clean_inline_markdown(desc)
            current = {
                "term_a": term_a,
                "term_b": term_b,
                "description": desc,
                "details": [],
            }
            if desc:
                items.append(desc)
        elif re.match(r"^[-*]\s+(.*)", line) or re.match(r"^\d+\.\s+(.*)", line):
            text = re.sub(r"^[-*\d]+[.\s]+\s*", "", line).strip()
            text = clean_inline_markdown(text)
            items.append(text)
        elif current:
            text = clean_inline_markdown(line)
            items.append(text)

    if current and items:
        current["details"] = items
        results.append(current)

    return results


def _parse_comparison_table(raw_section: str) -> List[Dict[str, Any]]:
    """Parse a markdown table for comparisons like:
    | 词 | 使用对象 | 例句 |
    | come true | dream, wish | My dream came true. |
    """
    lines = raw_section.strip().split("\n")
    # Need at least header + separator + one data row
    data_rows: List[List[str]] = []
    for line in lines:
        line = line.strip()
        if not line or not line.startswith("|"):
            continue
        if re.match(r"^[\|\s\-:]+$", line):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        data_rows.append(cells)

    if len(data_rows) < 2:
        return []

    header = data_rows[0]
    results: List[Dict[str, Any]] = []

    for row in data_rows[1:]:
        if len(row) < 2:
            continue
        # Treat row[0] as left term, row[1] as left_meaning
        left = clean_inline_markdown(row[0])
        right = ""
        left_meaning = clean_inline_markdown(row[1]) if len(row) > 1 else ""
        right_meaning = clean_inline_markdown(row[2]) if len(row) > 2 else ""

        if left:
            results.append({
                "term_a": left,
                "term_b": right,
                "description": left_meaning,
                "details": [c for c in [left_meaning, right_meaning] if c],
            })

    return results


def _parse_markdown_table_section(raw_section: str) -> List[Dict[str, Any]]:
    """Parse a full markdown table section (header + rows) into entries.

    Returns list where each row may represent a complete entry if the table
    has columns for term/meanings/examples.
    """
    lines = raw_section.strip().split("\n")
    rows: List[List[str]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r"^[\|\s\-:]+$", line):
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if cells:
                rows.append(cells)

    if len(rows) < 2:
        return []

    header = rows[0]
    entries: List[Dict[str, Any]] = []

    # Map column indices to semantic fields
    col_map: Dict[str, int] = {}
    for i, h in enumerate(header):
        h_lower = h.lower().strip()
        if any(kw in h_lower for kw in ["单词", "词汇", "term", "word", "词"]):
            col_map["term"] = i
        elif any(kw in h_lower for kw in ["释义", "意思", "含义", "定义", "meaning"]):
            col_map["meaning"] = i
        elif any(kw in h_lower for kw in ["例句", "例子", "示例", "example"]):
            col_map["example"] = i
        elif any(kw in h_lower for kw in ["用法", "搭配", "usage"]):
            col_map["usage"] = i
        elif any(kw in h_lower for kw in ["易错", "注意", "tip", "mistake"]):
            col_map["mistake_tip"] = i
        elif any(kw in h_lower for kw in ["同义", "近义", "synonym"]):
            col_map["synonym"] = i
        elif any(kw in h_lower for kw in ["写作", "writing"]):
            col_map["writing"] = i

    # If we can't identify any columns, fall through
    if "term" not in col_map:
        return []

    for row in rows[1:]:
        term = clean_inline_markdown(row[col_map["term"]]) if col_map.get("term", -1) < len(row) else ""
        if not term:
            continue

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

        if "meaning" in col_map and col_map["meaning"] < len(row):
            meaning_text = clean_inline_markdown(row[col_map["meaning"]])
            if meaning_text:
                entry["meanings"].append(meaning_text)

        if "example" in col_map and col_map["example"] < len(row):
            example_text = clean_inline_markdown(row[col_map["example"]])
            if example_text:
                entry["examples"].append({"en": example_text, "zh": ""})

        if "usage" in col_map and col_map["usage"] < len(row):
            entry["usages"].append(clean_inline_markdown(row[col_map["usage"]]))

        if "mistake_tip" in col_map and col_map["mistake_tip"] < len(row):
            entry["mistake_tips"].append(clean_inline_markdown(row[col_map["mistake_tip"]]))

        if "synonym" in col_map and col_map["synonym"] < len(row):
            entry["synonyms"].append(clean_inline_markdown(row[col_map["synonym"]]))

        if "writing" in col_map and col_map["writing"] < len(row):
            entry["writing_sentences"].append(clean_inline_markdown(row[col_map["writing"]]))

        entries.append(entry)

    return entries


def _standardize_section_name(name: str) -> str:
    """Map various Chinese/English section names to standardized field keys."""
    name = name.strip().lower()

    meaning_keywords = ["释义", "含义", "意思", "定义", "meaning"]
    usage_keywords = ["常见用法", "用法", "搭配", "常见搭配", "使用", "usage"]
    example_keywords = ["例句", "示例", "例子", "example"]
    mistake_keywords = ["易错点", "注意点", "注意事项", "易错", "注意", "mistake"]
    synonym_keywords = ["同义替换", "近义词", "同义词", "替换", "synonym"]
    comparison_keywords = ["易混词对比", "近义词对比", "对比", "比较", "易混", "comparison"]
    writing_keywords = ["六级写作可用句", "写作可用句", "写作句", "写作", "writing"]
    review_keywords = ["快速复习表", "复习", "复习表", "review"]

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

    return "meanings"


def _parse_colon_fields(block: str) -> Dict[str, List[Any]]:
    """Parse a block with colon-delimited fields like:
    释义：xxx
    常见用法：
    - item1
    - item2

    Returns dict with list values keyed by standard field name.
    """
    result: Dict[str, List[Any]] = {
        "meanings": [],
        "usages": [],
        "examples": [],
        "mistake_tips": [],
        "synonyms": [],
        "comparisons": [],
        "writing_sentences": [],
    }

    field_patterns = [
        (re.compile(r"^(?:释义|含义|意思|定义|meaning)[：:]", re.IGNORECASE), "meanings"),
        (re.compile(r"^(?:常见用法|用法|搭配|常见搭配|使用|usage)[：:]", re.IGNORECASE), "usages"),
        (re.compile(r"^(?:例句|示例|例子|example)[：:]", re.IGNORECASE), "examples"),
        (re.compile(r"^(?:易错点|注意点|注意事项|易错|注意|mistake)[：:]", re.IGNORECASE), "mistake_tips"),
        (re.compile(r"^(?:同义替换|近义词|同义词|替换|synonym)[：:]", re.IGNORECASE), "synonyms"),
        (re.compile(r"^(?:易混词对比|近义词对比|对比|比较|易混|comparison)[：:]", re.IGNORECASE), "comparisons"),
        (re.compile(r"^(?:写作可用句|写作句|写作|六级写作|writing)[：:]", re.IGNORECASE), "writing_sentences"),
    ]

    lines = block.strip().split("\n")
    current_field: Optional[str] = None
    current_lines: List[str] = []
    collected_examples: List[str] = []

    def _flush():
        nonlocal current_field, current_lines
        if current_field and current_lines:
            content = "\n".join(current_lines)
            if current_field == "examples":
                collected_examples.append(content)
            elif current_field == "comparisons":
                result[current_field].extend(_parse_comparisons(content))
            else:
                result[current_field].extend(_parse_list_items(content))
        current_field = None
        current_lines = []

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            _flush()
            continue

        # Check if this line starts a new field
        matched = False
        for pat, field_key in field_patterns:
            m = pat.match(line_stripped)
            if m:
                _flush()
                current_field = field_key
                # Everything after the colon is the value on this line
                remaining = line_stripped[m.end():].strip()
                if remaining:
                    current_lines = [remaining]
                else:
                    current_lines = []
                matched = True
                break

        if not matched:
            if current_field:
                current_lines.append(line_stripped)
            else:
                # No field detected yet — accumulate as potential meaning
                if current_lines or line_stripped:
                    if not current_field:
                        current_field = "meanings"
                    current_lines.append(line_stripped)

    _flush()

    # Parse collected example blocks
    for ex_block in collected_examples:
        result["examples"].extend(_parse_examples(ex_block))

    return result


def _parse_entry_block(block: str) -> Optional[Dict[str, Any]]:
    """Parse a single entry block into a structured dict.

    Handles multiple sub-formats within the block:
    1. ## heading → ### sections
    2. # heading → colon fields
    3. Plain text → colon fields
    4. Table → table parsing
    """
    block = block.strip()
    if not block:
        return None

    lines = block.split("\n")
    first_line = lines[0].strip()

    # Skip document-level titles
    if _is_document_title(first_line):
        return None

    term = ""
    remaining = ""

    # Extract term from heading
    if first_line.startswith("## ") or first_line.startswith("### "):
        term = re.sub(r"^#{2,3}\s*", "", first_line).strip()
        term = re.sub(r"^\d+[\.\、\)]\s*", "", term).strip()
        remaining = "\n".join(lines[1:])
    elif first_line.startswith("# "):
        term = re.sub(r"^#\s*", "", first_line).strip()
        term = re.sub(r"^\d+[\.\、\)]\s*", "", term).strip()
        remaining = "\n".join(lines[1:])
    elif "|" in block[:200]:
        # Table format - first non-table text is the term
        remaining = block
        for line in lines:
            clean = clean_markdown_noise(line)
            if clean and "|" not in line and not term:
                candidate = clean_inline_markdown(clean)
                if not _is_document_title(candidate):
                    term = candidate
                    break
    else:
        # Plain text — first meaningful line is the term
        for i, line in enumerate(lines):
            clean = clean_markdown_noise(line)
            if clean and not _is_document_title(clean):
                term = clean_inline_markdown(clean)
                remaining = "\n".join(lines[i + 1:])
                break

    if not term or _is_document_title(term):
        return None

    remaining = remaining.strip()

    # Parse the remaining content
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

    if not remaining:
        return entry

    # Strategy 1: Try ### sub-sections (Format B)
    has_h3 = bool(re.search(r"\n###\s+", "\n" + remaining))
    if has_h3:
        sections = re.split(r"\n(?=### )", remaining)
        for section in sections:
            section = section.strip()
            if not section:
                continue
            section_lines = section.split("\n")
            section_name = re.sub(r"^###\s*", "", section_lines[0].strip()).strip()
            section_body = "\n".join(section_lines[1:]).strip()
            if not section_body:
                continue
            field_key = _standardize_section_name(section_name)

            if field_key == "examples":
                entry["examples"].extend(_parse_examples(section_body))
            elif field_key == "comparisons":
                entry["comparisons"].extend(_parse_comparisons(section_body))
            elif field_key == "quick_review":
                entry["meanings"].append(
                    {"type": "quick_review", "content": _parse_list_items(section_body)}
                )
            else:
                items = _parse_list_items(section_body)
                entry[field_key].extend(items)

    # Strategy 2: Try markdown table (Formats D, E)
    if "|" in remaining and not any(entry[k] for k in entry if k not in ("term", "entry_type")):
        table_entries = _parse_markdown_table_section(remaining)
        if table_entries and len(table_entries) == 1:
            # Single table row → merge into this entry
            t = table_entries[0]
            for k in ("meanings", "usages", "examples", "mistake_tips", "synonyms", "comparisons", "writing_sentences"):
                if t.get(k):
                    entry[k].extend(t[k])
        # If multiple rows, they'll be handled at the top-level split

    # Strategy 3: Try colon-delimited fields (Formats A, C)
    if not any(entry[k] for k in entry if k not in ("term", "entry_type")):
        colon_fields = _parse_colon_fields(remaining)
        for k, v in colon_fields.items():
            if v:
                entry[k].extend(v)

    # Strategy 4: Fallback — put everything in meanings
    has_content = any(entry[k] for k in entry if k not in ("term", "entry_type"))
    if not has_content and remaining.strip():
        cleaned_lines = []
        for line in remaining.strip().split("\n"):
            c = clean_markdown_noise(line)
            c = clean_inline_markdown(c)
            if c:
                cleaned_lines.append(c)
        if cleaned_lines:
            entry["meanings"] = cleaned_lines

    return entry


def parse_vocabulary_markdown(raw_markdown: str) -> List[Dict[str, Any]]:
    """Parse raw vocabulary markdown into structured entry dicts.

    Returns a list of dicts, each with keys matching VocabularyEntry fields.
    Never raises exceptions — falls back to raw content in meanings.
    """
    if not raw_markdown or not raw_markdown.strip():
        return []

    entries: List[Dict[str, Any]] = []

    try:
        # First, try to detect if the entire document is a markdown table
        if _looks_like_full_table(raw_markdown):
            entries = _parse_markdown_table_section(raw_markdown)
            return _finalize_entries(entries)

        # Split by ## or # headings for entry blocks
        # Use both # and ## as potential entry delimiters
        blocks = re.split(r"\n(?=##? [^#])", raw_markdown)

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            # Try to parse as an entry block
            entry = _parse_entry_block(block)
            if entry:
                entries.append(entry)
            else:
                # If block doesn't parse as entry, try further splitting by --- separator
                sub_blocks = re.split(r"\n---+\s*\n", block)
                for sub_block in sub_blocks:
                    sub_block = sub_block.strip()
                    if not sub_block:
                        continue
                    sub_entry = _parse_entry_block(sub_block)
                    if sub_entry:
                        entries.append(sub_entry)

        # If nothing found, try parsing the whole text as a single entry
        if not entries:
            fallback_entry = _parse_entry_block(raw_markdown)
            if fallback_entry:
                entries.append(fallback_entry)

        # If still nothing, create a fallback entry with cleaned content
        if not entries and raw_markdown.strip():
            cleaned = clean_markdown_noise(
                clean_inline_markdown(raw_markdown.strip())
            )
            if cleaned:
                entries.append({
                    "term": cleaned[:50],
                    "entry_type": "word",
                    "meanings": [cleaned],
                    "usages": [],
                    "examples": [],
                    "mistake_tips": [],
                    "synonyms": [],
                    "comparisons": [],
                    "writing_sentences": [],
                })

        return _finalize_entries(entries)

    except Exception:
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


def _looks_like_full_table(raw_markdown: str) -> bool:
    """Check if the entire markdown looks like a single table."""
    lines = [l for l in raw_markdown.strip().split("\n") if l.strip()]
    pipe_lines = [l for l in lines if "|" in l]
    return len(pipe_lines) >= 2 and len(pipe_lines) >= len(lines) * 0.7


def _finalize_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply final cleaning and conversion to output format."""
    result: List[Dict[str, Any]] = []
    for entry in entries:
        result.append({
            "term": entry["term"],
            "entry_type": entry.get("entry_type", "word"),
            "meanings_json": normalize_text_list(entry.get("meanings", [])),
            "usages_json": normalize_text_list(entry.get("usages", [])),
            "examples_json": normalize_examples(entry.get("examples", [])),
            "mistake_tips_json": normalize_text_list(entry.get("mistake_tips", [])),
            "synonyms_json": normalize_text_list(entry.get("synonyms", [])),
            "comparisons_json": normalize_comparisons(entry.get("comparisons", [])),
            "writing_sentences_json": normalize_text_list(entry.get("writing_sentences", [])),
        })
    return result
