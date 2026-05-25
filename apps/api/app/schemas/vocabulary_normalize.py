"""Schemas for AI-powered vocabulary normalization."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class NormalizedMeaning(BaseModel):
    pos: str = ""
    zh: str = ""
    en: str = ""


class NormalizedUsage(BaseModel):
    pattern: str = ""
    meaning: str = ""


class NormalizedExample(BaseModel):
    en: str = ""
    zh: str = ""


class NormalizedComparison(BaseModel):
    left: str = ""
    right: str = ""
    left_meaning: str = ""
    right_meaning: str = ""


class NormalizedEntry(BaseModel):
    term: str
    entry_type: str = "word"
    pronunciation_ipa: str = ""
    uk_phonetic: str = ""
    us_phonetic: str = ""
    meanings: List[NormalizedMeaning] = []
    usages: List[NormalizedUsage] = []
    examples: List[NormalizedExample] = []
    mistake_tips: List[str] = []
    synonyms: List[str] = []
    comparisons: List[NormalizedComparison] = []
    writing_sentences: List[str] = []


class NormalizeMarkdownRequest(BaseModel):
    raw_markdown: str
    provider: str = "deepseek"


class NormalizeMarkdownResponse(BaseModel):
    title: str = ""
    entries: List[NormalizedEntry] = []
    warnings: List[str] = []
    source: str = "ai"


class AIProviderStatus(BaseModel):
    enabled: bool
    provider: str = ""
    configured: bool = False
    message: str = ""


# ── Word-list generation schemas (v0.2.1) ──

class GenerationOptions(BaseModel):
    detail_level: str = "standard"  # brief / standard / detailed
    example_style: str = "cet"  # cet / academic / daily
    include_writing_sentences: bool = True
    include_comparisons: bool = True
    language: str = "zh-CN"


class GenerateFromWordsRequest(BaseModel):
    title: str = ""
    exam_type: str = "CET6"
    paper_name: str = ""
    source_section: str = "other"
    source_session_id: Optional[int] = None
    words: List[str] = Field(..., min_length=1, max_length=50)
    options: GenerationOptions = Field(default_factory=GenerationOptions)


class GeneratedWritingSentence(BaseModel):
    en: str = ""
    zh: str = ""


class GeneratedVocabularyEntry(BaseModel):
    term: str
    entry_type: str = "word"
    pronunciation_ipa: str = ""
    uk_phonetic: str = ""
    us_phonetic: str = ""
    meanings: List[NormalizedMeaning] = []
    usages: List[NormalizedUsage] = []
    examples: List[NormalizedExample] = []
    mistake_tips: List[str] = []
    synonyms: List[str] = []
    comparisons: List[NormalizedComparison] = []
    writing_sentences: List[GeneratedWritingSentence] = []
    tags: List[str] = []


class GenerateFromWordsResponse(BaseModel):
    title: str = ""
    standardized_markdown: str = ""
    entries: List[GeneratedVocabularyEntry] = []
    warnings: List[str] = []
    source: str = "ai"


class SaveGeneratedNoteRequest(BaseModel):
    title: str
    raw_input: str = ""
    standardized_markdown: str = ""
    source_session_id: Optional[int] = None
    exam_type: Optional[str] = None
    paper_name: Optional[str] = None
    source_section: str = "other"
    entries: List[GeneratedVocabularyEntry] = Field(default_factory=list)
