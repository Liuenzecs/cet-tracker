"""Vocabulary quality service — duplicate detection and quality validation."""

from typing import Any, Dict, List, Optional, Tuple

from sqlmodel import Session, select

from app.models.vocabulary import VocabularyEntry, VocabularyNote
from app.schemas.quality import ValidateItemResult
from app.utils.term_utils import normalize_term


def check_duplicates(
    db: Session,
    terms: List[str],
) -> List[Dict[str, Any]]:
    """Check which terms already exist in vocabulary_entries.

    Returns list of duplicate info dicts with existing entry metadata.
    """
    if not terms:
        return []

    normalized_input = [(term, normalize_term(term)) for term in terms]

    # Build a set of normalized terms for efficient lookup
    normalized_set = {nt for _, nt in normalized_input}
    if not normalized_set:
        return []

    # Query all existing entries whose normalized term matches
    all_entries = list(db.exec(select(VocabularyEntry)).all())
    duplicates: List[Dict[str, Any]] = []

    for entry in all_entries:
        entry_norm = normalize_term(entry.term)
        if entry_norm in normalized_set:
            # Find the original input term
            original_term = entry.term
            for orig, norm in normalized_input:
                if norm == entry_norm:
                    original_term = orig
                    break

            # Get note title
            note = db.get(VocabularyNote, entry.note_id)
            note_title = note.title if note else "未知笔记"

            duplicates.append({
                "term": original_term,
                "normalized_term": entry_norm,
                "existing_entry_id": entry.id,
                "existing_note_id": entry.note_id,
                "existing_note_title": note_title,
                "familiarity": entry.familiarity,
            })

    return duplicates


def validate_generated_entries(
    input_words: List[str],
    entries: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Validate AI-generated entries for quality issues.

    Returns a summary and per-item results. No AI call needed.
    """
    items: List[ValidateItemResult] = []
    total_errors = 0
    total_warnings = 0

    for entry in entries:
        term = str(entry.get("term", ""))
        messages: List[str] = []
        level = "ok"

        # Error: empty term
        if not term.strip():
            messages.append("term 不能为空")
            level = "error"

        # Error: [object Object] in any field
        entry_str = str(entry)
        if "[object Object]" in entry_str:
            messages.append("检测到 [object Object]")
            level = "error"

        # Warning: no meanings
        meanings = entry.get("meanings", []) or []
        if not meanings:
            messages.append("缺少释义")
            if level == "ok":
                level = "warning"

        # Warning: no examples
        examples = entry.get("examples", []) or []
        if not examples:
            messages.append("缺少例句")
            if level == "ok":
                level = "warning"

        # Warning: markdown table noise
        for key, val in entry.items():
            if isinstance(val, str) and ("|---" in val or "|---|---" in val):
                messages.append("发现 Markdown 表格残留符号")
                if level == "ok":
                    level = "warning"
                break

        # Warning: long English examples
        for ex in examples:
            if isinstance(ex, dict) and ex.get("en"):
                if len(ex["en"].split()) > 40:
                    messages.append("英文例句超过 40 词")
                    if level == "ok":
                        level = "warning"
                    break

        # Warning: empty Chinese translation
        for ex in examples:
            if isinstance(ex, dict) and ex.get("en") and not ex.get("zh"):
                messages.append("部分例句缺少中文翻译")
                if level == "ok":
                    level = "warning"
                break

        # Warning: invalid entry_type
        entry_type = entry.get("entry_type", "word")
        if entry_type not in ("word", "phrase", "proper_noun", "unknown"):
            messages.append(f"无效的 entry_type: {entry_type}（已修正为 unknown）")
            if level == "ok":
                level = "warning"

        # Warning: term looks like a document title
        doc_title_keywords = ["图片笔记", "笔记扩展", "词汇表", "目录", "复习表", "词汇总览"]
        for kw in doc_title_keywords:
            if kw in term:
                messages.append(f"term 看起来像是文档标题: {term}")
                if level != "error":
                    level = "warning"
                break

        # Warning: suspicious CET content patterns
        suspicious_patterns = ["题干", "选项A", "选项B", "选项C", "选项D", "听力原文", "阅读原文", "真题"]
        for sp in suspicious_patterns:
            if sp in entry_str:
                messages.append(f"发现疑似真题内容标记: {sp}")
                if level != "error":
                    level = "warning"
                break

        if level == "error":
            total_errors += 1
        elif level == "warning":
            total_warnings += 1

        items.append(ValidateItemResult(term=term, level=level, messages=messages))

    # Check entry count vs input word count
    if len(entries) == 0:
        total_errors += 1
    elif len(input_words) > 0 and len(entries) < len(input_words) * 0.5:
        # More than 50% missing — add a general warning to first item
        if items:
            items[0].messages.append(f"生成的词条数({len(entries)})明显少于输入词数({len(input_words)})")
            if items[0].level == "ok":
                items[0].level = "warning"
                total_warnings += 1

    return {
        "summary": {
            "total": len(entries),
            "valid": len(entries) - total_errors - total_warnings,
            "warnings": total_warnings,
            "errors": total_errors,
        },
        "items": [item.model_dump() for item in items],
    }
