"""Term normalization utilities for duplicate detection."""

import re


def normalize_term(term: str) -> str:
    """Normalize a vocabulary term for duplicate comparison.

    Rules:
    1. trim
    2. lowercase
    3. collapse consecutive spaces
    4. strip leading/trailing punctuation
    5. Does NOT merge British/American spellings
    """
    if not term:
        return ""

    term = term.strip()
    term = term.lower()
    term = re.sub(r"\s+", " ", term)
    term = term.strip(".,;:!?\"'()[]{}，。；：！？""''（）【】")

    return term
