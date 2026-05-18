"""Text cleaning utilities for markdown-to-structured-field conversion.

Removes markdown noise from parsed vocabulary content so the UI never
shows raw **bold**, |---|---|, ### headings, etc.
"""

import re
from typing import Any, Dict, List, Union


def clean_inline_markdown(text: str) -> str:
    """Remove inline markdown formatting symbols, preserving content.

    Handles: **bold**, *italic*, `code`, ~~strikethrough~~, ==highlight==.
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""

    text = text.strip()
    # bold: **text** or __text__
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    # italic: *text* or _text_ (but not **)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)
    text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"\1", text)
    # inline code: `text`
    text = re.sub(r"`(.+?)`", r"\1", text)
    # strikethrough: ~~text~~
    text = re.sub(r"~~(.+?)~~", r"\1", text)
    # highlight: ==text==
    text = re.sub(r"==(.+?)==", r"\1", text)

    return text.strip()


def clean_markdown_noise(text: str) -> str:
    """Strip structural markdown noise from a text line.

    Removes:
    - Leading #, ##, ###, #### headings
    - Horizontal rules: ---, ***, ___, * * *
    - Markdown table separator rows like |---|---|
    - Leading/trailing whitespace and empty strings
    """
    if not isinstance(text, str):
        return ""

    text = text.strip()

    # Detect horizontal rules (---, ***, ___, * * *, - - -)
    if re.match(r"^[-*_]{3,}\s*$", text):
        return ""
    if re.match(r"^(\*\s+){2,}\*?\s*$", text):
        return ""
    if re.match(r"^(-\s+){2,}-?\s*$", text):
        return ""

    # Detect markdown table separator: |---|:---:|---|
    if re.match(r"^[\|\s\-:]+$", text) and re.search(r"---", text):
        return ""

    # Remove leading heading markers
    text = re.sub(r"^#{1,6}\s+", "", text)

    # Remove leading/trailing pipes from table cells that got through
    text = text.strip().strip("|").strip()

    return text


def normalize_text_list(items: List[Any]) -> List[str]:
    """Normalize a list of items into clean, displayable strings.

    - Strips inline markdown from each item
    - Filters out empty strings and noise-only strings
    - Deduplicates while preserving order
    - Converts non-string items via str()
    """
    seen: set = set()
    result: List[str] = []

    for item in (items or []):
        if isinstance(item, dict):
            # For quick_review dicts with content list, expand content
            if isinstance(item.get("content"), list):
                for c in item["content"]:
                    s = clean_inline_markdown(str(c))
                    s = clean_markdown_noise(s)
                    if s and s not in seen:
                        seen.add(s)
                        result.append(s)
                continue
            # For other dict items, try to produce a readable string
            parts = []
            for v in item.values():
                if v and isinstance(v, str):
                    parts.append(str(v))
                elif isinstance(v, (list, tuple)):
                    for vi in v:
                        if vi and isinstance(vi, str):
                            parts.append(str(vi))
            s = "; ".join(parts)
        elif isinstance(item, (list, tuple)):
            s = "; ".join(str(v) for v in item if v)
        else:
            s = str(item) if item is not None else ""

        s = clean_inline_markdown(s)
        s = clean_markdown_noise(s)

        if s and s.strip() and s not in seen:
            seen.add(s)
            result.append(s)

    return result


def normalize_examples(items: List[Any]) -> List[Dict[str, str]]:
    """Normalize examples into clean {en, zh} dicts.

    Handles:
    - Dicts with en/zh keys (standard format)
    - Strings that contain a separator (—, ---, --, :, ：)
    - Dicts with other keys (tries to extract meaningful content)
    """
    result: List[Dict[str, str]] = []

    for item in (items or []):
        if isinstance(item, dict):
            en = item.get("en", "")
            zh = item.get("zh", "")
            # Try alternate keys
            if not en or not isinstance(en, str):
                for k in ("english", "sentence", "text", "example", "original"):
                    if k in item and isinstance(item[k], str):
                        en = item[k]
                        break
            if not zh or not isinstance(zh, str):
                for k in ("chinese", "translation", "meaning", "translate", "释义"):
                    if k in item and isinstance(item[k], str):
                        zh = item[k]
                        break
            en = clean_inline_markdown(str(en)) if en else ""
            zh = clean_inline_markdown(str(zh)) if zh else ""
            if en:
                result.append({"en": en, "zh": zh})
        elif isinstance(item, str):
            # Try to split on common separators
            parsed = _parse_example_line(item)
            if parsed:
                result.append(parsed)
            else:
                cleaned = clean_inline_markdown(item)
                cleaned = clean_markdown_noise(cleaned)
                if cleaned:
                    result.append({"en": cleaned, "zh": ""})

    return result


def normalize_comparisons(items: List[Any]) -> List[Dict[str, str]]:
    """Normalize comparisons into clean {left, right, left_meaning, right_meaning} dicts.

    Handles diverse formats produced by the parser and AI:
    - {word1, word2, meaning1, meaning2}
    - {left, right, left_meaning, right_meaning}
    - {term_a, term_b, description, details}
    - {word, note}
    - Raw strings with "vs" pattern
    """
    result: List[Dict[str, str]] = []

    for item in (items or []):
        if isinstance(item, dict):
            left = (
                item.get("left")
                or item.get("word1")
                or item.get("term_a")
                or item.get("word")
                or ""
            )
            right = (
                item.get("right")
                or item.get("word2")
                or item.get("term_b")
                or ""
            )
            left_meaning = (
                item.get("left_meaning")
                or item.get("meaning1")
                or item.get("description")
                or item.get("note")
                or ""
            )
            right_meaning = (
                item.get("right_meaning")
                or item.get("meaning2")
                or ""
            )

            left = clean_inline_markdown(str(left))
            right = clean_inline_markdown(str(right))
            left_meaning = clean_inline_markdown(str(left_meaning))
            right_meaning = clean_inline_markdown(str(right_meaning))

            # If we have details list, try to extract meanings
            details = item.get("details", [])
            if isinstance(details, list):
                for d in details:
                    d_clean = clean_inline_markdown(str(d))
                    if not left_meaning:
                        left_meaning = d_clean
                    elif not right_meaning:
                        right_meaning = d_clean

            if left:
                result.append({
                    "left": left,
                    "right": right,
                    "left_meaning": left_meaning,
                    "right_meaning": right_meaning,
                })
        elif isinstance(item, str):
            cleaned = clean_inline_markdown(item)
            cleaned = clean_markdown_noise(cleaned)
            if cleaned:
                result.append({
                    "left": cleaned,
                    "right": "",
                    "left_meaning": "",
                    "right_meaning": "",
                })

    return result


def _parse_example_line(line: str) -> Union[Dict[str, str], None]:
    """Parse a single example line like 'The case is still pending. — 案件仍在审理中。'"""
    if not line or not line.strip():
        return None

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
