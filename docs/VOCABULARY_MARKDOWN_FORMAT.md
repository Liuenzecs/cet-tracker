# CET Tracker — Vocabulary Markdown Format

## Overview

Vocabulary is imported into CET Tracker via structured Markdown. The parser extracts terms, meanings, usages, examples, and other metadata from a predictable heading-and-list format. This document defines the supported structure, parsing rules, and edge cases.

The format is designed to be human-writable — students can type or paste vocabulary notes using a simple template in any text editor, then import them into the tracker.

---

## Supported Structure

Each vocabulary entry begins with a **level-2 heading** (`## `). Sections within an entry are marked with **level-3 headings** (`### `). List items use `- ` or `* ` prefixes.

### Minimal Example

```markdown
## 1. pending

### 释义
等待处理的；悬而未决的；即将发生的

### 例句
- The case is still pending. — 案件仍在审理中。
```

### Full Example (All Supported Sections)

```markdown
## 1. pending

### 释义
等待处理的；悬而未决的；即将发生的

### 常见用法
- pending decision — 待定的决定
- pending approval — 等待批准
- patent pending — 专利申请中

### 例句
- The case is still pending. — 案件仍在审理中。
- A final decision is pending. — 最终决定尚未作出。

### 易错点
- 不是"悬挂"的意思（那是 suspend）
- pending 常放在名词后面，不是前面

### 同义替换
- awaiting, undecided, unresolved, imminent

### 六级写作可用句
- With the final exam pending, students are under increasing pressure.
- The proposal is still pending approval from the committee.

### 易混词对比
- pending vs impending
  - pending = 等待决定/处理（中性）
  - impending = 即将发生的（通常指不好的事）
```

---

## Section Mapping

The parser matches level-3 heading text (after trimming whitespace) to known keywords. Sections are matched case-insensitively.

### 1. Meanings (释义 / 含义 / 意思)

**Mapped to**: `meanings_json` (array of strings)

**Input**:
```markdown
### 释义
等待处理的；悬而未决的；即将发生的
```

**Parsed**:
```json
["等待处理的", "悬而未决的", "即将发生的"]
```

**Rules**:
- If the content is a single semicolon-separated line, split by `；` or `;`.
- If the content uses bullet points (`- `), each bullet becomes an array element.
- If the content has `### 快速复习表`, it is stored as a special formatted review table but still placed in `meanings_json`.

**Quick Review Table handling**:
```markdown
### 快速复习表
| 英文 | 中文 |
|------|------|
| pending | 待定的 |
| approval | 批准 |
```
This is stored as a single string in `meanings_json`: `"快速复习表:\n| 英文 | 中文 |\n|------|------|\n| pending | 待定的 |\n| approval | 批准 |"`.

---

### 2. Usages (常见用法 / 用法 / 搭配)

**Mapped to**: `usages_json` (array of strings)

**Input**:
```markdown
### 常见用法
- pending decision — 待定的决定
- pending approval — 等待批准
- patent pending — 专利申请中
```

**Parsed**:
```json
[
  "pending decision — 待定的决定",
  "pending approval — 等待批准",
  "patent pending — 专利申请中"
]
```

**Rules**:
- Each `- ` or `* ` line becomes an array element.
- If no list items, the entire content is a single string.

---

### 3. Examples (例句 / 示例)

**Mapped to**: `examples_json` (array of `{en, zh}` objects)

**Input**:
```markdown
### 例句
- The case is still pending. — 案件仍在审理中。
- A final decision is pending. — 最终决定尚未作出。
```

**Parsed**:
```json
[
  {"en": "The case is still pending.", "zh": "案件仍在审理中。"},
  {"en": "A final decision is pending.", "zh": "最终决定尚未作出。"}
]
```

**Rules**:
- Each list item is split on the first occurrence of ` — ` (em-dash surrounded by spaces) or `—` (em-dash without spaces) or ` -- ` (double hyphen with spaces).
- The part before the separator is the English text (`en`). The part after is the Chinese text (`zh`).
- If no separator is found, the entire line is treated as English and `zh` is an empty string.
- Leading/trailing whitespace is trimmed from both parts.

---

### 4. Mistake Tips (易错点 / 注意点 / 注意事项)

**Mapped to**: `mistake_tips_json` (array of strings)

**Input**:
```markdown
### 易错点
- 不是"悬挂"的意思（那是 suspend）
- pending 常放在名词后面，不是前面
```

**Parsed**:
```json
[
  "不是\"悬挂\"的意思（那是 suspend）",
  "pending 常放在名词后面，不是前面"
]
```

**Rules**:
- Each `- ` or `* ` line becomes an array element.

---

### 5. Synonyms (同义替换 / 近义词)

**Mapped to**: `synonyms_json` (array of strings)

**Input**:
```markdown
### 同义替换
- awaiting, undecided, unresolved, imminent
```

**Parsed**:
```json
["awaiting", "undecided", "unresolved", "imminent"]
```

**Input (alternative — single word per line)**:
```markdown
### 同义替换
- awaiting
- undecided
- unresolved
```

**Parsed**:
```json
["awaiting", "undecided", "unresolved"]
```

**Rules**:
- If a single list item contains commas, split by comma and trim each part.
- If multiple list items, each becomes one array element.
- Non-list content is treated as a comma-separated single string.

---

### 6. Comparisons (易混词对比 / 近义词对比 / 对比)

**Mapped to**: `comparisons_json` (array of `{word, note}` objects or plain strings)

**Input**:
```markdown
### 易混词对比
- pending vs impending
  - pending = 等待决定/处理（中性）
  - impending = 即将发生的（通常指不好的事）
```

**Parsed**:
```json
[
  {"word": "pending", "note": "等待决定/处理（中性）"},
  {"word": "impending", "note": "即将发生的（通常指不好的事）"}
]
```

**Rules**:
- The parser looks for the pattern `- <word1> vs <word2>` to detect a comparison pair.
- Nested bullets (`  - `) are parsed as individual word-note pairs.
- The pattern `word = description` is split on the first `=`.
- If the format does not match any known pattern, each list item is stored as a plain string.

---

### 7. Writing Sentences (六级写作可用句 / 写作可用句 / 写作句)

**Mapped to**: `writing_sentences_json` (array of strings)

**Input**:
```markdown
### 六级写作可用句
- With the final exam pending, students are under increasing pressure.
- The proposal is still pending approval from the committee.
```

**Parsed**:
```json
[
  "With the final exam pending, students are under increasing pressure.",
  "The proposal is still pending approval from the committee."
]
```

**Rules**:
- Each list item becomes an array element.
- No translation splitting is performed here (unlike examples). The entire sentence is kept as-is.

---

## Term Extraction

The term is extracted from the level-2 heading text:

```markdown
## 1. pending
```

Extraction rules:
1. Strip the `## ` prefix.
2. Remove leading numbering patterns: `1. `, `1) `, `01. `, `1、`, `（1）`, `(1) `.
3. Trim whitespace.
4. The result is the `term` field.

**Examples**:

| Input heading | Extracted term |
|---------------|---------------|
| `## 1. pending` | `pending` |
| `## 25. sustainable development` | `sustainable development` |
| `## 3) take into account` | `take into account` |
| `## （12）comprehensive` | `comprehensive` |
| `## pending` | `pending` |
| `## 01. a piece of cake` | `a piece of cake` |

---

## Entry Type Detection

The `entry_type` field is determined heuristically:

| Condition | entry_type |
|-----------|------------|
| Term contains spaces AND is not a proper noun | `phrase` |
| Term starts with uppercase letter and contains no spaces | `word` (but could be proper_noun) |
| Term contains spaces AND first letters are uppercase | `proper_noun` |
| Term is a single word | `word` |
| Cannot determine | `unknown` |

The user can manually override the entry_type in the UI after import.

---

## Complete Example: Input and Output

### Input Markdown

```markdown
## 1. pending

### 释义
等待处理的；悬而未决的；即将发生的

### 常见用法
- pending decision — 待定的决定
- pending approval — 等待批准
- patent pending — 专利申请中

### 例句
- The case is still pending. — 案件仍在审理中。
- A final decision is pending. — 最终决定尚未作出。

### 易错点
- 不是"悬挂"的意思（那是 suspend）
- pending 常放在名词后面，不是前面

### 同义替换
- awaiting, undecided, unresolved, imminent

### 六级写作可用句
- With the final exam pending, students are under increasing pressure.
- The proposal is still pending approval from the committee.

### 易混词对比
- pending vs impending
  - pending = 等待决定/处理（中性）
  - impending = 即将发生的（通常指不好的事）

## 2. sustainable

### 释义
可持续的；能维持的

### 常见用法
- sustainable development — 可持续发展
- sustainable growth — 可持续增长

### 例句
- We need to find a sustainable solution. — 我们需要找到可持续的解决方案。

### 同义替换
- viable, maintainable, enduring

### 六级写作可用句
- Sustainable development is key to long-term economic growth.
```

### Expected Parsed Output

```json
{
  "entries": [
    {
      "term": "pending",
      "entry_type": "word",
      "meanings_json": ["等待处理的", "悬而未决的", "即将发生的"],
      "usages_json": [
        "pending decision — 待定的决定",
        "pending approval — 等待批准",
        "patent pending — 专利申请中"
      ],
      "examples_json": [
        {"en": "The case is still pending.", "zh": "案件仍在审理中。"},
        {"en": "A final decision is pending.", "zh": "最终决定尚未作出。"}
      ],
      "mistake_tips_json": [
        "不是\"悬挂\"的意思（那是 suspend）",
        "pending 常放在名词后面，不是前面"
      ],
      "synonyms_json": ["awaiting", "undecided", "unresolved", "imminent"],
      "comparisons_json": [
        {"word": "pending", "note": "等待决定/处理（中性）"},
        {"word": "impending", "note": "即将发生的（通常指不好的事）"}
      ],
      "writing_sentences_json": [
        "With the final exam pending, students are under increasing pressure.",
        "The proposal is still pending approval from the committee."
      ]
    },
    {
      "term": "sustainable",
      "entry_type": "word",
      "meanings_json": ["可持续的", "能维持的"],
      "usages_json": [
        "sustainable development — 可持续发展",
        "sustainable growth — 可持续增长"
      ],
      "examples_json": [
        {"en": "We need to find a sustainable solution.", "zh": "我们需要找到可持续的解决方案。"}
      ],
      "mistake_tips_json": [],
      "synonyms_json": ["viable", "maintainable", "enduring"],
      "comparisons_json": [],
      "writing_sentences_json": [
        "Sustainable development is key to long-term economic growth."
      ]
    }
  ],
  "entry_count": 2
}
```

---

## Edge Cases and Graceful Degradation

### H2 with No H3 Sections

If a `## heading` has content but no `###` subsections, the term is captured and ALL content between this H2 and the next H2 (or end of document) is placed into `meanings_json` as a single string.

```markdown
## miscellaneous

Some unformatted notes about vocabulary here.
```

**Parsed**:
```json
{
  "term": "miscellaneous",
  "entry_type": "word",
  "meanings_json": ["Some unformatted notes about vocabulary here."],
  "usages_json": [],
  "examples_json": [],
  ...
}
```

### H3 with No List Items

If a `###` section has content but no `- ` lines, the entire content is treated as a single string (for array fields, it becomes a single-element array).

```markdown
### 释义
The meaning without bullet points.
```

**Parsed**: `meanings_json: ["The meaning without bullet points."]`

### Mixed Formatting

If a section mixes bullet points and plain text, the parser collects bullet items only. Non-bullet lines are ignored (not an error).

### Empty Sections

If a `###` section exists but has no content (immediately followed by another `###` or `##`), the corresponding field remains an empty array `[]`.

### Empty Markdown

If the entire input is empty or whitespace-only, the parser returns `{ entries: [], entry_count: 0 }`. No error is thrown.

### Malformed Markdown

The parser uses best-effort extraction. It will never throw an error or reject the input. If a section cannot be parsed:

1. The raw content is logged at debug level on the server.
2. That section's field defaults to an empty array.
3. The entry is still created with whatever was successfully parsed.
4. The note is ALWAYS saved, even if zero entries are successfully parsed.

### Duplicate Terms

If two `## ` headings produce the same term, both entries are created. No deduplication is performed during import. Users can manually merge or delete duplicates in the UI.

### Unicode and Special Characters

The parser handles full Unicode. Chinese characters, em-dashes (`—`), and special punctuation are all preserved. The separator for examples (` — `) is matched in this priority order:

1. ` — ` (space, em-dash, space)
2. `—` (em-dash without spaces)
3. ` -- ` (space, two hyphens, space)

### Maximum Input Size

The server should accept Markdown inputs up to 1 MB (approximately 250,000 words). If a larger input is submitted, return HTTP 413 with an appropriate error message.

---

## Markdown Template for Users

The UI should provide this template to users as a starting point:

```markdown
## 1. <word>

### 释义
<Chinese meaning>

### 常见用法
- <phrase> — <translation>

### 例句
- <English sentence> — <Chinese translation>

### 易错点
- <common mistake or note>

### 同义替换
- <synonym1>, <synonym2>

### 六级写作可用句
- <sentence suitable for CET writing>

### 易混词对比
- <word1> vs <word2>
  - <word1> = <description>
  - <word2> = <description>
```
