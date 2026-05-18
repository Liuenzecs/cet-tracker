"""
Seed script for CET Tracker demo data.

Inserts a realistic demo session with listening results, reading results,
and a vocabulary note with 9 entries parsed from a realistic Markdown note.

Usage:
    python scripts/seed_demo.py
    cd apps/api && python ../../scripts/seed_demo.py
"""

import json
import os
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve the project root and database path
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DB_PATH = PROJECT_ROOT / "data" / "cet_tracker.db"

# Ensure the data directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# SQL table definitions (mirrors models/tables)
# ---------------------------------------------------------------------------

DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS exam_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_type VARCHAR(10) NOT NULL,
        paper_name VARCHAR(200) NOT NULL,
        session_type VARCHAR(50) NOT NULL,
        date DATE NOT NULL,
        duration_minutes INTEGER NOT NULL,
        note TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS listening_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL REFERENCES exam_sessions(id) ON DELETE CASCADE,
        total_questions INTEGER NOT NULL,
        correct_count INTEGER NOT NULL,
        wrong_questions_text VARCHAR,
        wrong_questions_json TEXT DEFAULT '[]',
        mistake_tags_json TEXT DEFAULT '{}',
        reflection TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS reading_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL REFERENCES exam_sessions(id) ON DELETE CASCADE,
        question_type VARCHAR(50) NOT NULL,
        total_questions INTEGER NOT NULL,
        correct_count INTEGER NOT NULL,
        wrong_questions_text VARCHAR,
        wrong_questions_json TEXT DEFAULT '[]',
        mistake_tags_json TEXT DEFAULT '{}',
        reflection TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS vocabulary_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR NOT NULL,
        raw_markdown TEXT NOT NULL,
        source_session_id INTEGER REFERENCES exam_sessions(id) ON DELETE SET NULL,
        exam_type VARCHAR(10),
        paper_name VARCHAR(200),
        source_section VARCHAR(50) NOT NULL DEFAULT 'other',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS vocabulary_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER NOT NULL REFERENCES vocabulary_notes(id) ON DELETE CASCADE,
        term VARCHAR NOT NULL,
        entry_type VARCHAR(50) DEFAULT 'word',
        meanings_json TEXT DEFAULT '[]',
        usages_json TEXT DEFAULT '[]',
        examples_json TEXT DEFAULT '[]',
        mistake_tips_json TEXT DEFAULT '[]',
        synonyms_json TEXT DEFAULT '[]',
        comparisons_json TEXT DEFAULT '[]',
        writing_sentences_json TEXT DEFAULT '[]',
        familiarity VARCHAR(20) DEFAULT 'new',
        review_count INTEGER DEFAULT 0,
        last_reviewed_at DATETIME,
        next_review_at DATETIME,
        tags_json TEXT DEFAULT '[]',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
]

# ---------------------------------------------------------------------------
# Demo raw Markdown for the vocabulary note
# ---------------------------------------------------------------------------

RAW_MARKDOWN = """\
# CET6 示例训练词汇笔记

> 来源：虚构演示数据

## 1. pending

### 释义
等待处理的；悬而未决的；即将发生的

### 常见用法
- pending decision — 待定的决定
- pending approval — 等待批准
- patent pending — 专利申请中
- pending further investigation — 等待进一步调查

### 例句
- The case is still pending. — 案件仍在审理中。
- A final decision is pending. — 最终决定尚未作出。
- His application for the scholarship is pending. — 他的奖学金申请正在审核中。

### 易错点
- 不是"悬挂"的意思（那是 suspend / hang）
- pending 常放在名词后面修饰，不是前面（如 case pending，较少说 pending case）
- 不要和 impending 混淆（见下文对比）

### 同义替换
- awaiting, undecided, unresolved, imminent, forthcoming

### 六级写作可用句
- With the final exam pending, students are under increasing pressure.
- The proposal is still pending approval from the relevant authorities.
- Given the pending deadline, we need to accelerate our progress.

### 易混词对比
- pending vs impending
  - pending = 等待决定或处理（中性词）
  - impending = 即将发生的（通常指不好的事，如 impending disaster）
- pending vs suspending
  - pending = 等待中（状态）
  - suspending = 暂停、中止（动作）

---

## 2. someone at my end

### 释义
我这边的人；我这一端的人（电话/视频通话用语）

### 常见用法
- someone at my end — 我这边有人
- at this end — 在这边
- on my end — 在我这边（口语）

### 例句
- Sorry, there's someone at my end. Can I call you back? — 抱歉，我这边有人，我能稍后打给你吗？
- Everything is fine at this end. — 这边一切正常。

### 易错点
- 不是 '在我末端的人'，是电话/视频通话中的固定表达
- my end = 我所在的位置 / 我这一方

---

## 3. utmost

### 释义
最大的；极度的 (adj.)；最大限度 (n.)

### 常见用法
- utmost importance — 极其重要
- utmost respect — 最大的尊重
- do one's utmost — 竭尽全力
- of the utmost significance — 至关重要的

### 例句
- Safety is of the utmost importance in this project. — 安全在这个项目中至关重要。
- We should do our utmost to protect the environment. — 我们应竭尽全力保护环境。
- I have the utmost respect for her dedication. — 我对她的奉献精神怀有最大的敬意。

### 易错点
- 不要写成 "upmost"（常见拼写错误）
- utmost = ut + most，ut 是古英语 "out" 的变体

### 同义替换
- greatest, maximum, supreme, extreme, paramount

### 六级写作可用句
- It is of the utmost importance that we address climate change without delay.
- Every citizen should do their utmost to contribute to a sustainable future.
- Education plays a role of the utmost significance in personal development.

---

## 4. Middle East

### 释义
中东（地理区域专有名词）

### 常见用法
- the Middle East — 中东地区
- Middle Eastern — 中东的（形容词）
- Middle Eastern countries — 中东国家

### 例句
- The Middle East has a rich cultural heritage. — 中东有着丰富的文化遗产。
- Many Middle Eastern countries are major oil producers. — 许多中东国家是主要产油国。

### 易错点
- 必须大写首字母（专有名词）
- the Middle East 通常加 the
- 和 Near East（近东）、Far East（远东）区分

---

## 5. exclusively

### 释义
专门地；排外地；唯一地

### 常见用法
- exclusively for — 专门为……
- focus exclusively on — 专注于
- sold exclusively at — 仅在……有售

### 例句
- This offer is available exclusively to our members. — 此优惠仅限会员。
- She focuses exclusively on her research. — 她专注于研究。

### 易错点
- exclusive ≠ expensive（拼写和意思完全不同）
- exclusively = 排他性地 / 专门地；inclusively = 包含地

### 同义替换
- solely, only, entirely, uniquely, specifically

### 六级写作可用句
- This policy benefits urban residents almost exclusively, neglecting rural populations.
- We should not rely exclusively on technology to solve social problems.

---

## 6. materialise / materialize

### 释义
实现；发生；成为现实；（使）显形

### 常见用法
- fail to materialise — 未能实现
- hopes materialised — 希望成真了
- materialise into — 变成

### 例句
- The expected economic recovery did not materialise. — 预期的经济复苏没有实现。
- His dream of studying abroad finally materialised. — 他出国留学的梦想终于实现了。

### 易错点
- materialise (英式) = materialize (美式)
- 不是 "物质化"，常用比喻义——计划、希望等"变成现实"

### 同义替换
- happen, occur, come true, be realized, take shape

### 六级写作可用句
- Unfortunately, the promised reforms have yet to materialise.
- Without concrete action, these ambitious plans will never materialise.

---

## 7. real estate

### 释义
房地产；不动产

### 常见用法
- real estate market — 房地产市场
- real estate developer — 房地产开发商
- commercial real estate — 商业地产
- real estate agent — 房产中介

### 例句
- The real estate market has been booming in recent years. — 近年来房地产市场一直很繁荣。
- They invested heavily in real estate. — 他们在房地产上大量投资。

### 易错点
- real estate = real property（法律术语），不是 "真实的房产"
- estate 本身也是"地产、庄园"的意思

---

## 8. estate

### 释义
地产；庄园；财产；遗产

### 常见用法
- housing estate — 住宅区（英式）
- industrial estate — 工业园区（英式）
- real estate — 房地产（美式）
- estate agent — 房产经纪人（英式）
- estate tax — 遗产税

### 例句
- They live on a private estate in the countryside. — 他们住在乡下的一个私人庄园里。
- The family estate was divided among the heirs. — 家族财产被继承人分割了。

### 易错点
- estate 有三个主要含义：地产/庄园、财产/遗产、住宅区（英式）
- 英式英语中 estate 常用作"住宅区"，如 council estate

### 易混词对比
- estate vs property
  - estate = 通常指较大的地产、庄园，或有遗产含义
  - property = 通用词，任何形式的财产或房产

---

## 9. negligible

### 释义
可忽略不计的；微不足道的

### 常见用法
- negligible amount — 微不足道的数量
- negligible impact — 可忽略的影响
- far from negligible — 远远不能忽视

### 例句
- The cost difference is negligible. — 成本差异可以忽略不计。
- The impact of this factor on the results is negligible. — 这个因素对结果的影响微乎其微。

### 易错点
- 注意发音：/ˈneɡlɪdʒəbəl/，重音在第一音节
- 来自 neglect（忽视），negligible = 可以忽视的

### 同义替换
- insignificant, trivial, minimal, trifling, inconsequential

### 六级写作可用句
- Although the individual contribution may seem negligible, collective efforts can bring about substantial change.
- The negative effects of this policy are far from negligible.
"""

# ---------------------------------------------------------------------------
# Structured vocabulary entries
# ---------------------------------------------------------------------------

VOCAB_ENTRIES = [
    {
        "term": "pending",
        "entry_type": "word",
        "meanings_json": json.dumps(
            ["等待处理的；悬而未决的；即将发生的"], ensure_ascii=False
        ),
        "usages_json": json.dumps(
            [
                "pending decision — 待定的决定",
                "pending approval — 等待批准",
                "patent pending — 专利申请中",
                "pending further investigation — 等待进一步调查",
            ],
            ensure_ascii=False,
        ),
        "examples_json": json.dumps(
            [
                {"en": "The case is still pending.", "zh": "案件仍在审理中。"},
                {"en": "A final decision is pending.", "zh": "最终决定尚未作出。"},
                {
                    "en": "His application for the scholarship is pending.",
                    "zh": "他的奖学金申请正在审核中。",
                },
            ],
            ensure_ascii=False,
        ),
        "mistake_tips_json": json.dumps(
            [
                '不是"悬挂"的意思（那是 suspend / hang）',
                "pending 常放在名词后面修饰，不是前面（如 case pending，较少说 pending case）",
                "不要和 impending 混淆",
            ],
            ensure_ascii=False,
        ),
        "synonyms_json": json.dumps(
            ["awaiting", "undecided", "unresolved", "imminent", "forthcoming"],
            ensure_ascii=False,
        ),
        "comparisons_json": json.dumps(
            [
                {
                    "word": "impending",
                    "note": "即将发生的（通常指不好的事，如 impending disaster）",
                },
                {"word": "suspending", "note": "暂停、中止（动作）"},
            ],
            ensure_ascii=False,
        ),
        "writing_sentences_json": json.dumps(
            [
                "With the final exam pending, students are under increasing pressure.",
                "The proposal is still pending approval from the relevant authorities.",
                "Given the pending deadline, we need to accelerate our progress.",
            ],
            ensure_ascii=False,
        ),
        "familiarity": "new",
        "review_count": 0,
        "tags_json": json.dumps([], ensure_ascii=False),
    },
    {
        "term": "someone at my end",
        "entry_type": "phrase",
        "meanings_json": json.dumps(
            ["我这边的人；我这一端的人（电话/视频通话用语）"], ensure_ascii=False
        ),
        "usages_json": json.dumps(
            [
                "someone at my end — 我这边有人",
                "at this end — 在这边",
                "on my end — 在我这边（口语）",
            ],
            ensure_ascii=False,
        ),
        "examples_json": json.dumps(
            [
                {
                    "en": "Sorry, there's someone at my end. Can I call you back?",
                    "zh": "抱歉，我这边有人，我能稍后打给你吗？",
                },
                {
                    "en": "Everything is fine at this end.",
                    "zh": "这边一切正常。",
                },
            ],
            ensure_ascii=False,
        ),
        "mistake_tips_json": json.dumps(
            [
                "不是 '在我末端的人'，是电话/视频通话中的固定表达",
                "my end = 我所在的位置 / 我这一方",
            ],
            ensure_ascii=False,
        ),
        "synonyms_json": json.dumps([], ensure_ascii=False),
        "comparisons_json": json.dumps([], ensure_ascii=False),
        "writing_sentences_json": json.dumps([], ensure_ascii=False),
        "familiarity": "new",
        "review_count": 0,
        "tags_json": json.dumps([], ensure_ascii=False),
    },
    {
        "term": "utmost",
        "entry_type": "word",
        "meanings_json": json.dumps(
            ["最大的；极度的 (adj.)", "最大限度 (n.)"], ensure_ascii=False
        ),
        "usages_json": json.dumps(
            [
                "utmost importance — 极其重要",
                "utmost respect — 最大的尊重",
                "do one's utmost — 竭尽全力",
                "of the utmost significance — 至关重要的",
            ],
            ensure_ascii=False,
        ),
        "examples_json": json.dumps(
            [
                {
                    "en": "Safety is of the utmost importance in this project.",
                    "zh": "安全在这个项目中至关重要。",
                },
                {
                    "en": "We should do our utmost to protect the environment.",
                    "zh": "我们应竭尽全力保护环境。",
                },
                {
                    "en": "I have the utmost respect for her dedication.",
                    "zh": "我对她的奉献精神怀有最大的敬意。",
                },
            ],
            ensure_ascii=False,
        ),
        "mistake_tips_json": json.dumps(
            [
                "不要写成 'upmost'（常见拼写错误）",
                "utmost = ut + most，ut 是古英语 'out' 的变体",
            ],
            ensure_ascii=False,
        ),
        "synonyms_json": json.dumps(
            ["greatest", "maximum", "supreme", "extreme", "paramount"],
            ensure_ascii=False,
        ),
        "comparisons_json": json.dumps([], ensure_ascii=False),
        "writing_sentences_json": json.dumps(
            [
                "It is of the utmost importance that we address climate change without delay.",
                "Every citizen should do their utmost to contribute to a sustainable future.",
                "Education plays a role of the utmost significance in personal development.",
            ],
            ensure_ascii=False,
        ),
        "familiarity": "new",
        "review_count": 0,
        "tags_json": json.dumps([], ensure_ascii=False),
    },
    {
        "term": "Middle East",
        "entry_type": "phrase",
        "meanings_json": json.dumps(
            ["中东（地理区域专有名词）"], ensure_ascii=False
        ),
        "usages_json": json.dumps(
            [
                "the Middle East — 中东地区",
                "Middle Eastern — 中东的（形容词）",
                "Middle Eastern countries — 中东国家",
            ],
            ensure_ascii=False,
        ),
        "examples_json": json.dumps(
            [
                {
                    "en": "The Middle East has a rich cultural heritage.",
                    "zh": "中东有着丰富的文化遗产。",
                },
                {
                    "en": "Many Middle Eastern countries are major oil producers.",
                    "zh": "许多中东国家是主要产油国。",
                },
            ],
            ensure_ascii=False,
        ),
        "mistake_tips_json": json.dumps(
            [
                "必须大写首字母（专有名词）",
                "the Middle East 通常加 the",
                "和 Near East（近东）、Far East（远东）区分",
            ],
            ensure_ascii=False,
        ),
        "synonyms_json": json.dumps([], ensure_ascii=False),
        "comparisons_json": json.dumps([], ensure_ascii=False),
        "writing_sentences_json": json.dumps([], ensure_ascii=False),
        "familiarity": "new",
        "review_count": 0,
        "tags_json": json.dumps(["geography", "proper-noun"], ensure_ascii=False),
    },
    {
        "term": "exclusively",
        "entry_type": "word",
        "meanings_json": json.dumps(
            ["专门地；排外地；唯一地"], ensure_ascii=False
        ),
        "usages_json": json.dumps(
            [
                "exclusively for — 专门为……",
                "focus exclusively on — 专注于",
                "sold exclusively at — 仅在……有售",
            ],
            ensure_ascii=False,
        ),
        "examples_json": json.dumps(
            [
                {
                    "en": "This offer is available exclusively to our members.",
                    "zh": "此优惠仅限会员。",
                },
                {
                    "en": "She focuses exclusively on her research.",
                    "zh": "她专注于研究。",
                },
            ],
            ensure_ascii=False,
        ),
        "mistake_tips_json": json.dumps(
            [
                "exclusive ≠ expensive（拼写和意思完全不同）",
                "exclusively = 排他性地 / 专门地；inclusively = 包含地",
            ],
            ensure_ascii=False,
        ),
        "synonyms_json": json.dumps(
            ["solely", "only", "entirely", "uniquely", "specifically"],
            ensure_ascii=False,
        ),
        "comparisons_json": json.dumps([], ensure_ascii=False),
        "writing_sentences_json": json.dumps(
            [
                "This policy benefits urban residents almost exclusively, neglecting rural populations.",
                "We should not rely exclusively on technology to solve social problems.",
            ],
            ensure_ascii=False,
        ),
        "familiarity": "new",
        "review_count": 0,
        "tags_json": json.dumps([], ensure_ascii=False),
    },
    {
        "term": "materialise / materialize",
        "entry_type": "word",
        "meanings_json": json.dumps(
            ["实现；发生；成为现实；（使）显形"], ensure_ascii=False
        ),
        "usages_json": json.dumps(
            [
                "fail to materialise — 未能实现",
                "hopes materialised — 希望成真了",
                "materialise into — 变成",
            ],
            ensure_ascii=False,
        ),
        "examples_json": json.dumps(
            [
                {
                    "en": "The expected economic recovery did not materialise.",
                    "zh": "预期的经济复苏没有实现。",
                },
                {
                    "en": "His dream of studying abroad finally materialised.",
                    "zh": "他出国留学的梦想终于实现了。",
                },
            ],
            ensure_ascii=False,
        ),
        "mistake_tips_json": json.dumps(
            [
                "materialise (英式) = materialize (美式)",
                '不是 "物质化"，常用比喻义——计划、希望等"变成现实"',
            ],
            ensure_ascii=False,
        ),
        "synonyms_json": json.dumps(
            ["happen", "occur", "come true", "be realized", "take shape"],
            ensure_ascii=False,
        ),
        "comparisons_json": json.dumps([], ensure_ascii=False),
        "writing_sentences_json": json.dumps(
            [
                "Unfortunately, the promised reforms have yet to materialise.",
                "Without concrete action, these ambitious plans will never materialise.",
            ],
            ensure_ascii=False,
        ),
        "familiarity": "new",
        "review_count": 0,
        "tags_json": json.dumps(["spelling"], ensure_ascii=False),
    },
    {
        "term": "real estate",
        "entry_type": "phrase",
        "meanings_json": json.dumps(["房地产；不动产"], ensure_ascii=False),
        "usages_json": json.dumps(
            [
                "real estate market — 房地产市场",
                "real estate developer — 房地产开发商",
                "commercial real estate — 商业地产",
                "real estate agent — 房产中介",
            ],
            ensure_ascii=False,
        ),
        "examples_json": json.dumps(
            [
                {
                    "en": "The real estate market has been booming in recent years.",
                    "zh": "近年来房地产市场一直很繁荣。",
                },
                {
                    "en": "They invested heavily in real estate.",
                    "zh": "他们在房地产上大量投资。",
                },
            ],
            ensure_ascii=False,
        ),
        "mistake_tips_json": json.dumps(
            [
                "real estate = real property（法律术语），不是 '真实的房产'",
                "estate 本身也是'地产、庄园'的意思",
            ],
            ensure_ascii=False,
        ),
        "synonyms_json": json.dumps([], ensure_ascii=False),
        "comparisons_json": json.dumps([], ensure_ascii=False),
        "writing_sentences_json": json.dumps([], ensure_ascii=False),
        "familiarity": "learning",
        "review_count": 0,
        "tags_json": json.dumps(["business", "economy"], ensure_ascii=False),
    },
    {
        "term": "estate",
        "entry_type": "word",
        "meanings_json": json.dumps(
            ["地产；庄园；财产；遗产"], ensure_ascii=False
        ),
        "usages_json": json.dumps(
            [
                "housing estate — 住宅区（英式）",
                "industrial estate — 工业园区（英式）",
                "real estate — 房地产（美式）",
                "estate agent — 房产经纪人（英式）",
                "estate tax — 遗产税",
            ],
            ensure_ascii=False,
        ),
        "examples_json": json.dumps(
            [
                {
                    "en": "They live on a private estate in the countryside.",
                    "zh": "他们住在乡下的一个私人庄园里。",
                },
                {
                    "en": "The family estate was divided among the heirs.",
                    "zh": "家族财产被继承人分割了。",
                },
            ],
            ensure_ascii=False,
        ),
        "mistake_tips_json": json.dumps(
            [
                "estate 有三个主要含义：地产/庄园、财产/遗产、住宅区（英式）",
                "英式英语中 estate 常用作'住宅区'，如 council estate",
            ],
            ensure_ascii=False,
        ),
        "synonyms_json": json.dumps([], ensure_ascii=False),
        "comparisons_json": json.dumps(
            [
                {
                    "word": "property",
                    "note": "通用词，任何形式的财产或房产",
                },
            ],
            ensure_ascii=False,
        ),
        "writing_sentences_json": json.dumps([], ensure_ascii=False),
        "familiarity": "learning",
        "review_count": 1,
        "tags_json": json.dumps(["business", "legal"], ensure_ascii=False),
    },
    {
        "term": "negligible",
        "entry_type": "word",
        "meanings_json": json.dumps(
            ["可忽略不计的；微不足道的"], ensure_ascii=False
        ),
        "usages_json": json.dumps(
            [
                "negligible amount — 微不足道的数量",
                "negligible impact — 可忽略的影响",
                "far from negligible — 远远不能忽视",
            ],
            ensure_ascii=False,
        ),
        "examples_json": json.dumps(
            [
                {
                    "en": "The cost difference is negligible.",
                    "zh": "成本差异可以忽略不计。",
                },
                {
                    "en": "The impact of this factor on the results is negligible.",
                    "zh": "这个因素对结果的影响微乎其微。",
                },
            ],
            ensure_ascii=False,
        ),
        "mistake_tips_json": json.dumps(
            [
                "注意发音：/ˈneɡlɪdʒəbəl/，重音在第一音节",
                "来自 neglect（忽视），negligible = 可以忽视的",
            ],
            ensure_ascii=False,
        ),
        "synonyms_json": json.dumps(
            ["insignificant", "trivial", "minimal", "trifling", "inconsequential"],
            ensure_ascii=False,
        ),
        "comparisons_json": json.dumps([], ensure_ascii=False),
        "writing_sentences_json": json.dumps(
            [
                "Although the individual contribution may seem negligible, collective efforts can bring about substantial change.",
                "The negative effects of this policy are far from negligible.",
            ],
            ensure_ascii=False,
        ),
        "familiarity": "new",
        "review_count": 0,
        "tags_json": json.dumps(["advanced"], ensure_ascii=False),
    },
]


# ---------------------------------------------------------------------------
# Main seeding logic
# ---------------------------------------------------------------------------

def seed() -> None:
    """Connect to SQLite, create tables, clear existing data, insert demo data."""

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        # 1. Create tables
        for ddl in DDL_STATEMENTS:
            cursor.execute(ddl)

        # 2. Clear existing data (order respects foreign keys)
        cursor.execute("DELETE FROM vocabulary_entries")
        cursor.execute("DELETE FROM vocabulary_notes")
        cursor.execute("DELETE FROM reading_results")
        cursor.execute("DELETE FROM listening_results")
        cursor.execute("DELETE FROM exam_sessions")

        now = datetime.now(timezone.utc).isoformat()

        # 3. Insert exam session
        cursor.execute(
            """
            INSERT INTO exam_sessions (exam_type, paper_name, session_type, date,
                                       duration_minutes, note, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "CET6",
                "CET6 示例训练套卷",
                "full_mock",
                "2024-12-15",
                120,
                "虚构演示：完整模考记录",
                now,
                now,
            ),
        )
        session_id = cursor.lastrowid

        # 4. Insert listening result
        listening_wrong = [1, 5, 8, 12, 15, 17, 18, 20, 23]
        listening_tags = {
            "1": ["关键词没抓住"],
            "5": ["单词不认识"],
            "8": ["同义替换没反应过来"],
            "12": ["走神"],
            "15": ["数字/时间/地点漏听"],
            "17": ["选项干扰"],
            "18": ["选项干扰"],
            "20": ["转折词没抓住"],
            "23": ["文章结构没听懂"],
        }
        cursor.execute(
            """
            INSERT INTO listening_results
                (session_id, total_questions, correct_count,
                 wrong_questions_text, wrong_questions_json,
                 mistake_tags_json, reflection, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                25,
                16,
                "1,5,8,12,15,17,18,20,23",
                json.dumps(listening_wrong, ensure_ascii=False),
                json.dumps(listening_tags, ensure_ascii=False),
                "Section C 的长对话错得最多，需要加强长对话训练。走神问题也要注意，Section B 时注意力下降明显。",
                now,
                now,
            ),
        )

        # 5. Insert reading result
        reading_wrong = [2, 5, 8, 9]
        reading_tags = {
            "2": ["定位错误"],
            "5": ["同义替换没看出"],
            "8": ["句子结构没读懂"],
            "9": ["选项比较不细"],
        }
        cursor.execute(
            """
            INSERT INTO reading_results
                (session_id, question_type, total_questions, correct_count,
                 wrong_questions_text, wrong_questions_json,
                 mistake_tags_json, reflection, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                "仔细阅读",
                10,
                6,
                "2,5,8,9",
                json.dumps(reading_wrong, ensure_ascii=False),
                json.dumps(reading_tags, ensure_ascii=False),
                "仔细阅读部分需要提高定位速度和选项比较能力。",
                now,
                now,
            ),
        )

        # 6. Insert vocabulary note
        cursor.execute(
            """
            INSERT INTO vocabulary_notes
                (title, raw_markdown, source_session_id, exam_type, paper_name,
                 source_section, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "CET6 示例训练词汇笔记",
                RAW_MARKDOWN,
                session_id,
                "CET6",
                "CET6 示例训练套卷",
                "reading",
                now,
                now,
            ),
        )
        note_id = cursor.lastrowid

        # 7. Insert vocabulary entries
        for entry in VOCAB_ENTRIES:
            cursor.execute(
                """
                INSERT INTO vocabulary_entries
                    (note_id, term, entry_type, meanings_json, usages_json,
                     examples_json, mistake_tips_json, synonyms_json,
                     comparisons_json, writing_sentences_json,
                     familiarity, review_count, tags_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    note_id,
                    entry["term"],
                    entry["entry_type"],
                    entry["meanings_json"],
                    entry["usages_json"],
                    entry["examples_json"],
                    entry["mistake_tips_json"],
                    entry["synonyms_json"],
                    entry["comparisons_json"],
                    entry["writing_sentences_json"],
                    entry["familiarity"],
                    entry["review_count"],
                    entry["tags_json"],
                    now,
                    now,
                ),
            )

        conn.commit()

        # 8. Print summary
        print("Seed data created successfully!")
        print("- 1 exam session")
        print("- 1 listening result (25 questions, 16 correct)")
        print("- 1 reading result (10 questions, 6 correct)")
        print(f"- 1 vocabulary note with {len(VOCAB_ENTRIES)} entries")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print(f"Database path: {DB_PATH}")
    seed()
