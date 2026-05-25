"""AI-powered normalization service for vocabulary markdown.

Converts messy markdown into structured JSON via DeepSeek or compatible API.
Key principles:
- Optional: disabled by default, never blocks local parsing.
- API key lives in backend .env only, never exposed to frontend.
- Timeout, error handling, schema validation on AI output.
- Falls back to local parser on any failure.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.schemas.vocabulary_normalize import (
    GenerateFromWordsResponse,
    GeneratedVocabularyEntry,
    GeneratedWritingSentence,
    NormalizedComparison,
    NormalizedEntry,
    NormalizedExample,
    NormalizedMeaning,
    NormalizedUsage,
    NormalizeMarkdownResponse,
)


def _get_ai_config() -> Dict[str, Any]:
    """Read AI configuration from environment variables."""
    return {
        "enabled": os.getenv("AI_NORMALIZER_ENABLED", "false").lower() == "true",
        "provider": os.getenv("AI_PROVIDER", "deepseek"),
        "api_key": os.getenv("AI_API_KEY", ""),
        "base_url": os.getenv("AI_BASE_URL", "https://api.deepseek.com"),
        "model": os.getenv("AI_MODEL", "deepseek-chat"),
        "timeout": int(os.getenv("AI_TIMEOUT_SECONDS", "30")),
    }


def is_ai_configured() -> Tuple[bool, str]:
    """Check if AI normalization is available.

    Returns (is_available, message).
    """
    config = _get_ai_config()
    if not config["enabled"]:
        return False, "AI 规范化未启用。请在后端 .env 中设置 AI_NORMALIZER_ENABLED=true 并重启服务。"
    if not config["api_key"]:
        return False, "AI API Key 未配置。请在后端 .env 中设置 AI_API_KEY 后重启服务。"
    return True, "ok"


def _build_system_prompt() -> str:
    """Build the system prompt for vocabulary normalization."""
    return """你是一个 CET-4/CET-6 英语词汇笔记整理助手。

你的任务是将用户输入的 Markdown 词汇笔记转换为结构化 JSON。只做格式规范化，不要扩写太多新内容。

规则：
1. 识别每个词条（term），提取释义、用法、例句、易错点、同义词、易混词对比、写作句。
2. 清洗 Markdown 格式符号（加粗、表格线、标题符号），但保留文字内容。
3. 如果某部分缺失，使用空数组 []。
4. 如果某行是文档标题（如"图片笔记扩展"、"词汇表"、"目录"、"复习表"），不要作为词条。
5. 不要凭空添加原文没有出现的大量信息。
6. 如果无法确定词性，pos 留空字符串。
7. 如果原始笔记中有音标信息，请分别提取英式(uk_phonetic)和美式(us_phonetic)；如果只有一种，填到 pronunciation_ipa；都没有则留空。
8. 不要包含任何真题全文、阅读文章全文、听力原文全文。

请严格按照以下 JSON schema 输出（不要输出 Markdown，只输出 JSON）：

{
  "title": "笔记标题",
  "entries": [
    {
      "term": "单词或短语",
      "entry_type": "word",
      "pronunciation_ipa": "/ˈsæmpəl/",
      "uk_phonetic": "/ˈsɑːmpəl/",
      "us_phonetic": "/ˈsæmpəl/",
      "meanings": [
        {"pos": "adj.", "zh": "中文释义", "en": "英文释义"}
      ],
      "usages": [
        {"pattern": "pending approval", "meaning": "等待批准"}
      ],
      "examples": [
        {"en": "The case is still pending.", "zh": "案件仍在审理中。"}
      ],
      "mistake_tips": ["易错点说明"],
      "synonyms": ["同义词"],
      "comparisons": [
        {"left": "pending", "right": "impending", "left_meaning": "待处理的", "right_meaning": "即将发生的"}
      ],
      "writing_sentences": ["写作可用句"]
    }
  ],
  "warnings": []
}"""


def _validate_entry(entry: NormalizedEntry) -> Optional[str]:
    """Validate a single normalized entry. Returns error message or None."""
    if not entry.term or not entry.term.strip():
        return "词条缺少 term 字段"
    if len(entry.term) > 200:
        return f"词条 term 过长: {entry.term[:50]}..."
    return None


async def normalize_markdown(raw_markdown: str, provider: str = "deepseek") -> Dict[str, Any]:
    """Call AI to normalize markdown into structured vocabulary entries.

    Returns a dict matching NormalizeMarkdownResponse schema.
    Falls back gracefully on any error.
    """
    config = _get_ai_config()
    available, message = is_ai_configured()

    if not available:
        return {
            "title": "",
            "entries": [],
            "warnings": [message],
            "source": "ai",
        }

    timeout = config["timeout"]

    try:
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
            }

            # Support OpenAI-compatible endpoints too
            api_url = f"{config['base_url'].rstrip('/')}/v1/chat/completions"

            payload = {
                "model": config["model"],
                "messages": [
                    {"role": "system", "content": _build_system_prompt()},
                    {"role": "user", "content": raw_markdown},
                ],
                "temperature": 0.1,
                "max_tokens": 16384,
            }

            response = await client.post(api_url, json=payload, headers=headers)

            if response.status_code != 200:
                return {
                    "title": "",
                    "entries": [],
                    "warnings": [f"AI API 返回错误 (HTTP {response.status_code})"],
                    "source": "ai",
                }

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not content:
                return {
                    "title": "",
                    "entries": [],
                    "warnings": ["AI 返回了空内容"],
                    "source": "ai",
                }

            # Extract JSON from the AI response (may be wrapped in ```json fences)
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
            if json_match:
                content = json_match.group(1).strip()
            else:
                # Try to find first { and last }
                start = content.find("{")
                end = content.rfind("}")
                if start >= 0 and end > start:
                    content = content[start:end + 1]

            parsed = json.loads(content)

            # Validate structure
            title = str(parsed.get("title", ""))[:200]
            raw_entries = parsed.get("entries", [])
            warnings = list(parsed.get("warnings", [])) if isinstance(parsed.get("warnings"), list) else []

            if not isinstance(raw_entries, list):
                return {
                    "title": title,
                    "entries": [],
                    "warnings": ["AI 返回的 entries 不是数组"],
                    "source": "ai",
                }

            # Validate each entry through Pydantic
            validated_entries: List[NormalizedEntry] = []
            for i, raw_entry in enumerate(raw_entries):
                if not isinstance(raw_entry, dict):
                    warnings.append(f"条目 {i} 格式无效，已跳过")
                    continue

                try:
                    # Normalize nested structures
                    meanings = []
                    for m in raw_entry.get("meanings", []) or []:
                        if isinstance(m, dict):
                            meanings.append(NormalizedMeaning(
                                pos=str(m.get("pos", "")),
                                zh=str(m.get("zh", "")),
                                en=str(m.get("en", "")),
                            ))
                        elif isinstance(m, str):
                            meanings.append(NormalizedMeaning(zh=m))

                    usages = []
                    for u in raw_entry.get("usages", []) or []:
                        if isinstance(u, dict):
                            usages.append(NormalizedUsage(
                                pattern=str(u.get("pattern", "")),
                                meaning=str(u.get("meaning", "")),
                            ))
                        elif isinstance(u, str):
                            usages.append(NormalizedUsage(pattern=u))

                    examples = []
                    for e in raw_entry.get("examples", []) or []:
                        if isinstance(e, dict):
                            examples.append(NormalizedExample(
                                en=str(e.get("en", "")),
                                zh=str(e.get("zh", "")),
                            ))

                    comparisons = []
                    for c in raw_entry.get("comparisons", []) or []:
                        if isinstance(c, dict):
                            comparisons.append(NormalizedComparison(
                                left=str(c.get("left", c.get("term_a", ""))),
                                right=str(c.get("right", c.get("term_b", ""))),
                                left_meaning=str(c.get("left_meaning", c.get("description", ""))),
                                right_meaning=str(c.get("right_meaning", "")),
                            ))

                    entry = NormalizedEntry(
                        term=str(raw_entry.get("term", "")),
                        entry_type=str(raw_entry.get("entry_type", "word")),
                        pronunciation_ipa=str(raw_entry.get("pronunciation_ipa", "")),
                        uk_phonetic=str(raw_entry.get("uk_phonetic", "")),
                        us_phonetic=str(raw_entry.get("us_phonetic", "")),
                        meanings=meanings,
                        usages=usages,
                        examples=examples,
                        mistake_tips=[str(s) for s in (raw_entry.get("mistake_tips") or [])],
                        synonyms=[str(s) for s in (raw_entry.get("synonyms") or [])],
                        comparisons=comparisons,
                        writing_sentences=[str(s) for s in (raw_entry.get("writing_sentences") or [])],
                    )

                    err = _validate_entry(entry)
                    if err:
                        warnings.append(f"跳过条目: {err}")
                        continue

                    validated_entries.append(entry)

                except Exception as e:
                    warnings.append(f"条目 {i} 校验失败: {str(e)}")
                    continue

            return {
                "title": title,
                "entries": [e.model_dump() for e in validated_entries],
                "warnings": warnings,
                "source": "ai",
            }

    except httpx.TimeoutException:
        return {
            "title": "",
            "entries": [],
            "warnings": [f"AI API 超时（{timeout}秒）"],
            "source": "ai",
        }
    except httpx.ConnectError:
        return {
            "title": "",
            "entries": [],
            "warnings": [f"无法连接到 AI API: {config['base_url']}"],
            "source": "ai",
        }
    except json.JSONDecodeError as e:
        return {
            "title": "",
            "entries": [],
            "warnings": [f"AI 返回的不是有效 JSON: {str(e)}"],
            "source": "ai",
        }
    except Exception as e:
        return {
            "title": "",
            "entries": [],
            "warnings": [f"AI 规范化失败: {str(e)}"],
            "source": "ai",
        }


# ── Word-list generation (v0.2.1) ──

def build_vocabulary_generation_prompt(
    words: List[str],
    exam_type: str,
    options: Dict[str, Any],
    title: str = "",
) -> str:
    """Build the user prompt for vocabulary generation from a word list."""
    detail_map = {
        "brief": "每个词条只包含 core 释义和 1 个例句",
        "standard": "每个词条包含释义、常见用法 1-2 条、例句 1-2 条、易错点、同义词、易混词对比",
        "detailed": "每个词条全面展开，释义详细、用法 2-3 条、例句 2-3 条、易错点、同义词、易混词对比、写作可用句 1-2 条",
    }
    detail_instruction = detail_map.get(options.get("detail_level", "standard"), detail_map["standard"])

    example_style_map = {
        "cet": "适合四六级学习者的校园和日常生活场景",
        "academic": "偏学术场景",
        "daily": "偏日常口语场景",
    }
    example_instruction = example_style_map.get(options.get("example_style", "cet"), example_style_map["cet"])

    include_writing = options.get("include_writing_sentences", True)
    include_comparisons = options.get("include_comparisons", True)

    title_line = f'笔记标题: "{title}"\n' if title else ""
    words_str = "\n".join(f"- {w}" for w in words)

    writing_instruction = ""
    if include_writing:
        writing_instruction = "\n- writing_sentences: 适合写作的句子 1-2 条，每个包含 en 和 zh"

    comparisons_instruction = ""
    if include_comparisons:
        comparisons_instruction = "\n- comparisons: 易混词对比"

    return f"""请根据以下单词或短语生成 CET 词汇学习笔记。

{title_line}
考试类型: {exam_type}
单词列表:
{words_str}

生成要求:
1. {detail_instruction}
2. 例句风格: {example_instruction}
3. 例句必须原创，适合 CET 学习者，不要复制真实考试原文
4. 中文解释面向中国大学生，简洁准确
5. 如果是短语，entry_type 使用 "phrase"
6. 如果是专有名词，entry_type 使用 "proper_noun"
7. 不确定词性时 pos 留空字符串 ""
8. 为每个词条生成 pronunciation_ipa、uk_phonetic、us_phonetic 字段，使用标准 IPA 音标（如 /ˈæpl/、/ˈstjuːdənt/）。uk_phonetic 为英式发音，us_phonetic 为美式发音。短语或专有名词无法确定时留空字符串。
9. standardized_markdown 必须使用稳定模板，包含所有章节标题:

# {{标题}}

## 1. {{term}}

### 发音
- {{pronunciation_ipa}}

### 释义
- {{pos}} {{zh}}
- English: {{en}}

### 常见用法
- {{pattern}}：{{meaning}}

### 例句
- {{en}}
  - {{zh}}

{writing_instruction}
### 易错点
- {{tip}}

### 同义替换
- {{synonym}}

{comparisons_instruction}

9. 必须输出严格 JSON（不要 Markdown 代码块，不要解释文字）
10. 如果某个字段没有内容，用空数组 []
11. 为每个词条生成 pronunciation_ipa 字段，使用标准 IPA 音标
"""

def _build_generation_system_prompt() -> str:
    """System prompt for vocabulary generation."""
    return """你是一个 CET-4/CET-6 英语词汇学习助手。根据用户提供的单词或短语列表，生成结构化词汇学习笔记。

必须输出严格 JSON，不要输出 Markdown 代码块，不要输出解释文字。

JSON 格式:
{
  "title": "...",
  "standardized_markdown": "...",
  "entries": [
    {
      "term": "...",
      "entry_type": "word",
      "pronunciation_ipa": "/.../",
      "uk_phonetic": "/.../",
      "us_phonetic": "/.../",
      "meanings": [
        {"pos": "adj.", "zh": "中文释义", "en": "English meaning"}
      ],
      "usages": [
        {"pattern": "phrase pattern", "meaning": "中文含义"}
      ],
      "examples": [
        {"en": "Example sentence.", "zh": "中文翻译"}
      ],
      "mistake_tips": ["常见错误或混淆点"],
      "synonyms": ["同义词"],
      "comparisons": [
        {"left": "word1", "right": "word2", "left_meaning": "含义1", "right_meaning": "含义2"}
      ],
      "writing_sentences": [
        {"en": "Writing sentence.", "zh": "中文翻译"}
      ],
      "tags": ["CET6", "reading"]
    }
  ],
  "warnings": []
}

要求:
1. 例句必须原创，适合 CET 学习者，不要复制真实考试原文。
2. 不要生成听力原文、阅读文章、题干、选项或官方解析。
3. 中文解释面向中国大学生，简洁准确。
4. 不确定词性时 pos 留空字符串。
5. 如果是短语，entry_type 使用 "phrase"。
6. 如果是专有名词，entry_type 使用 "proper_noun"。
7. 为每个词条生成 pronunciation_ipa 字段，使用标准 IPA 音标（如 /ˈkæmpəs/、/əˈbændən/），不确定时留空字符串。
8. 不要凭空添加原文没有出现的大量信息。
9. 如果字段没有内容，用空数组。
10. standardized_markdown 使用固定模板，包含 ## 释义 ###、## 常见用法 ###、## 例句 ### 等章节。"""


def _validate_generation_entry(entry: GeneratedVocabularyEntry) -> Optional[str]:
    """Validate a single generated entry."""
    if not entry.term or not entry.term.strip():
        return "词条缺少 term"
    if len(entry.term) > 200:
        return f"term 过长: {entry.term[:50]}..."
    if entry.entry_type not in ("word", "phrase", "proper_noun", "unknown"):
        return f"无效的 entry_type: {entry.entry_type}"
    for m in entry.meanings:
        if len(m.zh) > 500 or len(m.en) > 500:
            return f"term '{entry.term}' 释义过长"
    return None


async def generate_from_words(
    words: List[str],
    exam_type: str = "CET6",
    title: str = "",
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Call AI to generate structured vocabulary notes from a word list.

    Returns a dict matching GenerateFromWordsResponse schema.
    Does NOT save anything to the database.
    """
    config = _get_ai_config()
    available, message = is_ai_configured()

    if not available:
        return {
            "title": title,
            "standardized_markdown": "",
            "entries": [],
            "warnings": [message],
            "source": "ai",
            "code": "AI_NOT_CONFIGURED",
        }

    if options is None:
        options = {}

    timeout = config["timeout"]
    user_prompt = build_vocabulary_generation_prompt(
        words, exam_type, options, title
    )

    try:
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
            }
            api_url = f"{config['base_url'].rstrip('/')}/v1/chat/completions"

            payload = {
                "model": config["model"],
                "messages": [
                    {"role": "system", "content": _build_generation_system_prompt()},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 16384,
            }

            response = await client.post(api_url, json=payload, headers=headers)

            if response.status_code != 200:
                error_body = ""
                try:
                    error_body = response.text[:300]
                except Exception:
                    pass
                return {
                    "title": title,
                    "standardized_markdown": "",
                    "entries": [],
                    "warnings": [f"AI API 返回错误 (HTTP {response.status_code}): {error_body}"],
                    "source": "ai",
                }

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not content:
                return {
                    "title": title,
                    "standardized_markdown": "",
                    "entries": [],
                    "warnings": ["AI 返回了空内容"],
                    "source": "ai",
                }

            # Extract JSON
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
            if json_match:
                content = json_match.group(1).strip()
            else:
                start = content.find("{")
                end = content.rfind("}")
                if start >= 0 and end > start:
                    content = content[start:end + 1]

            parsed = json.loads(content)

            # Extract fields
            result_title = str(parsed.get("title", title))[:200]
            standardized_md = str(parsed.get("standardized_markdown", ""))
            raw_entries = parsed.get("entries", [])
            warnings = list(parsed.get("warnings", [])) if isinstance(parsed.get("warnings"), list) else []

            if not isinstance(raw_entries, list):
                return {
                    "title": result_title,
                    "standardized_markdown": standardized_md,
                    "entries": [],
                    "warnings": ["AI 返回的 entries 不是数组"],
                    "source": "ai",
                }

            # Validate and build entries
            validated_entries: List[GeneratedVocabularyEntry] = []
            for i, raw_entry in enumerate(raw_entries):
                if not isinstance(raw_entry, dict):
                    warnings.append(f"条目 {i} 格式无效，已跳过")
                    continue

                try:
                    meanings = []
                    for m in raw_entry.get("meanings", []) or []:
                        if isinstance(m, dict):
                            meanings.append(NormalizedMeaning(
                                pos=str(m.get("pos", "")),
                                zh=str(m.get("zh", "")),
                                en=str(m.get("en", "")),
                            ))

                    usages = []
                    for u in raw_entry.get("usages", []) or []:
                        if isinstance(u, dict):
                            usages.append(NormalizedUsage(
                                pattern=str(u.get("pattern", "")),
                                meaning=str(u.get("meaning", "")),
                            ))

                    examples = []
                    for e in raw_entry.get("examples", []) or []:
                        if isinstance(e, dict):
                            examples.append(NormalizedExample(
                                en=str(e.get("en", "")),
                                zh=str(e.get("zh", "")),
                            ))

                    comparisons = []
                    for c in raw_entry.get("comparisons", []) or []:
                        if isinstance(c, dict):
                            comparisons.append(NormalizedComparison(
                                left=str(c.get("left", "")),
                                right=str(c.get("right", "")),
                                left_meaning=str(c.get("left_meaning", "")),
                                right_meaning=str(c.get("right_meaning", "")),
                            ))

                    writing_sentences = []
                    for ws in raw_entry.get("writing_sentences", []) or []:
                        if isinstance(ws, dict):
                            writing_sentences.append(GeneratedWritingSentence(
                                en=str(ws.get("en", "")),
                                zh=str(ws.get("zh", "")),
                            ))
                        elif isinstance(ws, str):
                            writing_sentences.append(GeneratedWritingSentence(en=ws))

                    tags = [str(t) for t in (raw_entry.get("tags") or [])]

                    entry = GeneratedVocabularyEntry(
                        term=str(raw_entry.get("term", "")),
                        entry_type=str(raw_entry.get("entry_type", "word")),
                        pronunciation_ipa=str(raw_entry.get("pronunciation_ipa", "")),
                        uk_phonetic=str(raw_entry.get("uk_phonetic", "")),
                        us_phonetic=str(raw_entry.get("us_phonetic", "")),
                        meanings=meanings,
                        usages=usages,
                        examples=examples,
                        mistake_tips=[str(s) for s in (raw_entry.get("mistake_tips") or [])],
                        synonyms=[str(s) for s in (raw_entry.get("synonyms") or [])],
                        comparisons=comparisons,
                        writing_sentences=writing_sentences,
                        tags=tags,
                    )

                    err_msg = _validate_generation_entry(entry)
                    if err_msg:
                        warnings.append(f"条目 {i}: {err_msg}，已跳过")
                        continue

                    validated_entries.append(entry)

                except Exception as e:
                    warnings.append(f"条目 {i} 解析失败: {str(e)}")
                    continue

            return {
                "title": result_title,
                "standardized_markdown": standardized_md,
                "entries": [e.model_dump() for e in validated_entries],
                "warnings": warnings,
                "source": "ai",
            }

    except httpx.TimeoutException:
        return {
            "title": title,
            "standardized_markdown": "",
            "entries": [],
            "warnings": [f"AI API 超时（{timeout}秒）"],
            "source": "ai",
        }
    except httpx.ConnectError:
        return {
            "title": title,
            "standardized_markdown": "",
            "entries": [],
            "warnings": [f"无法连接到 AI API: {config['base_url']}"],
            "source": "ai",
        }
    except json.JSONDecodeError as e:
        return {
            "title": title,
            "standardized_markdown": "",
            "entries": [],
            "warnings": [f"AI 返回的不是有效 JSON: {str(e)}"],
            "source": "ai",
        }
    except Exception as e:
        return {
            "title": title,
            "standardized_markdown": "",
            "entries": [],
            "warnings": [f"AI 生成失败: {str(e)}"],
            "source": "ai",
        }


async def generate_single_word(
    word: str,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate vocabulary entry for a single word using AI.

    Returns a dict with 'entry' (GeneratedVocabularyEntry) and 'standardized_markdown'.
    Does NOT save to database.
    """
    config = _get_ai_config()
    available, message = is_ai_configured()

    if not available:
        return {"entry": None, "standardized_markdown": "", "warnings": [message], "source": "ai"}

    if options is None:
        options = {}

    timeout = config["timeout"]

    detail_map = {
        "brief": "只包含 core 释义和 1 个例句",
        "standard": "包含释义、常见用法、例句、易错点、同义词",
        "detailed": "全面展开所有字段",
    }
    detail_instruction = detail_map.get(options.get("detail_level", "standard"), detail_map["standard"])

    user_prompt = f"""请为以下单词或短语生成 CET 词汇学习笔记。

单词: {word}

要求: {detail_instruction}
例句必须原创，适合 CET 学习者。

输出严格 JSON（不要 Markdown 代码块）:
{{"entry": {{"term": "...", "entry_type": "word|phrase", "meanings": [{{"pos": "...", "zh": "...", "en": "..."}}], "usages": [{{"pattern": "...", "meaning": "..."}}], "examples": [{{"en": "...", "zh": "..."}}], "mistake_tips": ["..."], "synonyms": ["..."], "comparisons": [], "writing_sentences": [{{"en": "...", "zh": "..."}}], "tags": []}}, "standardized_markdown": "..."}}"""

    try:
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
            }
            api_url = f"{config['base_url'].rstrip('/')}/v1/chat/completions"

            payload = {
                "model": config["model"],
                "messages": [
                    {"role": "system", "content": _build_generation_system_prompt()},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            }

            response = await client.post(api_url, json=payload, headers=headers)

            if response.status_code != 200:
                return {"entry": None, "standardized_markdown": "", "warnings": [f"AI API HTTP {response.status_code}"], "source": "ai"}

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not content:
                return {"entry": None, "standardized_markdown": "", "warnings": ["AI 返回空内容"], "source": "ai"}

            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
            if json_match:
                content = json_match.group(1).strip()
            else:
                start = content.find("{")
                end = content.rfind("}")
                if start >= 0 and end > start:
                    content = content[start:end + 1]

            parsed = json.loads(content)
            entry_data = parsed.get("entry", {}) if isinstance(parsed, dict) else {}
            standardized_md = parsed.get("standardized_markdown", "") if isinstance(parsed, dict) else ""

            if not entry_data:
                return {"entry": None, "standardized_markdown": standardized_md, "warnings": ["AI 未返回有效词条"], "source": "ai"}

            entry = GeneratedVocabularyEntry(
                term=str(entry_data.get("term", word)),
                entry_type=str(entry_data.get("entry_type", "word")),
                pronunciation_ipa=str(entry_data.get("pronunciation_ipa", "")),
                uk_phonetic=str(entry_data.get("uk_phonetic", "")),
                us_phonetic=str(entry_data.get("us_phonetic", "")),
                meanings=[NormalizedMeaning(pos=str(m.get("pos", "")), zh=str(m.get("zh", "")), en=str(m.get("en", ""))) for m in (entry_data.get("meanings") or [])],
                usages=[NormalizedUsage(pattern=str(u.get("pattern", "")), meaning=str(u.get("meaning", ""))) for u in (entry_data.get("usages") or [])],
                examples=[NormalizedExample(en=str(e.get("en", "")), zh=str(e.get("zh", ""))) for e in (entry_data.get("examples") or [])],
                mistake_tips=[str(s) for s in (entry_data.get("mistake_tips") or [])],
                synonyms=[str(s) for s in (entry_data.get("synonyms") or [])],
                comparisons=[],
                writing_sentences=[GeneratedWritingSentence(en=str(ws.get("en", "")), zh=str(ws.get("zh", ""))) for ws in (entry_data.get("writing_sentences") or [])],
                tags=[str(t) for t in (entry_data.get("tags") or [])],
            )

            return {
                "entry": entry.model_dump(),
                "standardized_markdown": standardized_md,
                "warnings": [],
                "source": "ai",
            }

    except httpx.TimeoutException:
        return {"entry": None, "standardized_markdown": "", "warnings": [f"AI API 超时（{timeout}秒）"], "source": "ai"}
    except Exception as e:
        return {"entry": None, "standardized_markdown": "", "warnings": [f"生成失败: {str(e)}"], "source": "ai"}


def validate_word_input(raw_input: str) -> List[str]:
    """Parse and clean a word list from raw text input.

    Handles mixed delimiters: newlines, commas, semicolons, spaces.
    Deduplicates while preserving order.
    Filters empty strings and overly long entries.
    """
    if not raw_input or not raw_input.strip():
        return []

    # Split by newlines first
    lines = raw_input.strip().split("\n")
    words: List[str] = []
    seen: set = set()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Also split by comma or semicolon within a line
        parts = re.split(r"[,;，；]\s*", line)
        for part in parts:
            part = part.strip().strip("'\"").strip()
            # Skip empty, too long, or pure punctuation
            if not part or len(part) > 100:
                continue
            if re.match(r"^[\s\W_]+$", part):  # Pure symbols
                continue
            lower = part.lower()
            if lower not in seen:
                seen.add(lower)
                words.append(part)

    return words
