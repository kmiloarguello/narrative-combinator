"""Heuristic coherence scoring for generated stories (v0.3)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .fragments import Fragment

# ---------------------------------------------------------------------------
# Stop-word list used when extracting keywords
# ---------------------------------------------------------------------------
_STOP_WORDS: frozenset[str] = frozenset(
    {
        "a", "an", "the", "and", "but", "or", "nor", "for", "yet", "so",
        "in", "on", "at", "to", "of", "up", "by", "as", "is", "was",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might", "shall", "can",
        "not", "no", "it", "its", "itself", "that", "this", "these",
        "those", "with", "from", "into", "through", "during", "before",
        "after", "above", "below", "between", "out", "off", "over", "under",
        "again", "further", "then", "once", "here", "there", "when", "where",
        "why", "how", "all", "both", "each", "few", "more", "most", "other",
        "some", "such", "own", "same", "than", "too", "very", "just",
        "she", "he", "her", "him", "his", "they", "them", "their",
        "we", "our", "you", "your", "i", "me", "my",
        "what", "which", "who", "whom",
        "if", "while", "about", "against", "without", "within", "along",
        "following", "across", "behind", "beyond", "plus", "except",
        "were", "are", "also", "s", "t",
    }
)

# ---------------------------------------------------------------------------
# Tense-indicator vocabularies
# ---------------------------------------------------------------------------
_PAST_INDICATORS: frozenset[str] = frozenset(
    {"yesterday", "ago", "had", "was", "were", "before", "once", "last", "long"}
)
_FUTURE_INDICATORS: frozenset[str] = frozenset(
    {"tomorrow", "will", "soon", "eventually", "someday", "next"}
)

# ---------------------------------------------------------------------------
# Tonally incompatible word pairs (set-A, set-B)
# ---------------------------------------------------------------------------
_INCOMPATIBLE_PAIRS: list[tuple[frozenset[str], frozenset[str]]] = [
    (
        frozenset({"dawn", "morning", "sunrise", "awakening"}),
        frozenset({"midnight", "night", "darkness", "dusk"}),
    ),
    (
        frozenset({"joy", "celebration", "laughter", "festive"}),
        frozenset({"grief", "mourning", "funeral", "sorrow"}),
    ),
]

# Score deductions
_DEDUCT_REPEATED_KEYWORD = 5
_DEDUCT_TENSE_MISMATCH = 8
_DEDUCT_INCOMPATIBLE = 10
_DEDUCT_LENGTH_IMBALANCE = 5


@dataclass
class CoherenceResult:
    """Result of a coherence evaluation."""

    score: int
    issues: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_keywords(text: str) -> list[str]:
    """Return non-stop-word tokens longer than two characters from *text*."""
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if w not in _STOP_WORDS and len(w) > 2]


def _detect_repeated_keywords(texts: list[str], threshold: int = 2) -> list[str]:
    """Return keywords that appear in *threshold* or more distinct fragments."""
    word_fragment_count: dict[str, int] = {}
    for text in texts:
        for word in set(_extract_keywords(text)):
            word_fragment_count[word] = word_fragment_count.get(word, 0) + 1
    return [w for w, cnt in word_fragment_count.items() if cnt >= threshold]


def _detect_tense_mismatch(texts: list[str]) -> list[str]:
    """Return issue strings when past and future tense markers co-occur."""
    all_words: set[str] = set()
    for text in texts:
        all_words.update(re.findall(r"[a-zA-Z]+", text.lower()))

    past = all_words & _PAST_INDICATORS
    future = all_words & _FUTURE_INDICATORS

    if past and future:
        past_ex = next(iter(past))
        future_ex = next(iter(future))
        return [
            f"Potential tense mismatch: '{past_ex}' (past) alongside '{future_ex}' (future)"
        ]
    return []


def _detect_incompatible_keywords(texts: list[str]) -> list[str]:
    """Return issue strings for tonally incompatible word pairings."""
    issues: list[str] = []
    all_words: set[str] = set()
    for text in texts:
        all_words.update(re.findall(r"[a-zA-Z]+", text.lower()))

    for group_a, group_b in _INCOMPATIBLE_PAIRS:
        found_a = all_words & group_a
        found_b = all_words & group_b
        if found_a and found_b:
            issues.append(
                f"Tonally incompatible keywords: '{next(iter(found_a))}' and '{next(iter(found_b))}'"
            )
    return issues


def _detect_length_imbalance(texts: list[str]) -> list[str]:
    """Flag when the longest fragment is more than 3× the shortest."""
    lengths = [len(text.split()) for text in texts]
    if max(lengths) > min(lengths) * 3:
        return ["Fragment length imbalance: one fragment is much longer than the others"]
    return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def score_story(
    opening: Fragment, middle: Fragment, ending: Fragment
) -> CoherenceResult:
    """Score a story for heuristic coherence, returning a :class:`CoherenceResult`.

    Scoring starts at 100 and deductions are applied for each detected issue:

    * Repeated keyword across fragments: −5 per keyword
    * Tense mismatch (past + future markers): −8
    * Tonally incompatible word pairing: −10
    * Fragment length imbalance (>3× ratio): −5
    """
    texts = [opening.text, middle.text, ending.text]
    issues: list[str] = []
    score = 100

    repeated = _detect_repeated_keywords(texts, threshold=2)
    for word in repeated:
        issues.append(f"Repeated keyword: '{word}'")
        score -= _DEDUCT_REPEATED_KEYWORD

    tense_issues = _detect_tense_mismatch(texts)
    issues.extend(tense_issues)
    score -= len(tense_issues) * _DEDUCT_TENSE_MISMATCH

    incompat_issues = _detect_incompatible_keywords(texts)
    issues.extend(incompat_issues)
    score -= len(incompat_issues) * _DEDUCT_INCOMPATIBLE

    length_issues = _detect_length_imbalance(texts)
    issues.extend(length_issues)
    score -= len(length_issues) * _DEDUCT_LENGTH_IMBALANCE

    score = max(0, min(100, score))
    return CoherenceResult(score=score, issues=issues)
