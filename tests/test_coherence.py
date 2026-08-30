"""Tests for src/coherence.py."""

from __future__ import annotations

import pytest

from src.coherence import (
    CoherenceResult,
    _detect_incompatible_keywords,
    _detect_length_imbalance,
    _detect_repeated_keywords,
    _detect_tense_mismatch,
    _extract_keywords,
    score_story,
)
from src.fragments import Fragment, LAYER_ENDING, LAYER_MIDDLE, LAYER_OPENING


def _frag(layer: str, text: str, fid: str = "X01") -> Fragment:
    return Fragment(id=fid, layer=layer, text=text)


# ---------------------------------------------------------------------------
# _extract_keywords
# ---------------------------------------------------------------------------


def test_extract_keywords_removes_stop_words() -> None:
    kws = _extract_keywords("the cat sat on the mat")
    assert "the" not in kws
    assert "on" not in kws
    assert "cat" in kws
    assert "mat" in kws


def test_extract_keywords_short_words_excluded() -> None:
    kws = _extract_keywords("a an it is be")
    assert all(len(w) > 2 for w in kws)


# ---------------------------------------------------------------------------
# _detect_repeated_keywords
# ---------------------------------------------------------------------------


def test_detect_repeated_keywords_finds_repeat() -> None:
    texts = ["silence fell over the valley", "the silence was absolute", "nothing"]
    repeated = _detect_repeated_keywords(texts, threshold=2)
    assert "silence" in repeated


def test_detect_repeated_keywords_no_repeat() -> None:
    texts = ["light faded", "stranger arrived", "nothing remained"]
    repeated = _detect_repeated_keywords(texts, threshold=2)
    assert repeated == []


# ---------------------------------------------------------------------------
# _detect_tense_mismatch
# ---------------------------------------------------------------------------


def test_detect_tense_mismatch_found() -> None:
    texts = ["yesterday she walked", "tomorrow she will arrive"]
    issues = _detect_tense_mismatch(texts)
    assert len(issues) == 1
    assert "mismatch" in issues[0].lower()


def test_detect_tense_mismatch_none() -> None:
    texts = ["the light faded", "a stranger appeared"]
    issues = _detect_tense_mismatch(texts)
    assert issues == []


def test_detect_tense_mismatch_in_french() -> None:
    issues = _detect_tense_mismatch(
        ["Hier elle était au pont.", "Demain elle sera ici."], language="fr"
    )
    assert len(issues) == 1


def test_spanish_morning_is_not_treated_as_future() -> None:
    issues = _detect_tense_mismatch(
        ["La mañana llegó sin ceremonia.", "Había silencio."], language="es"
    )
    assert issues == []


def test_spanish_future_marker_is_detected() -> None:
    issues = _detect_tense_mismatch(
        ["Ayer ella estaba aquí.", "Pronto será diferente."], language="es"
    )
    assert len(issues) == 1


# ---------------------------------------------------------------------------
# _detect_incompatible_keywords
# ---------------------------------------------------------------------------


def test_detect_incompatible_keywords_morning_night() -> None:
    texts = ["at dawn the morning light appeared", "darkness and midnight swallowed all"]
    issues = _detect_incompatible_keywords(texts)
    assert len(issues) >= 1


def test_detect_incompatible_keywords_none() -> None:
    texts = ["she walked quietly", "the stranger waited", "nothing resolved"]
    issues = _detect_incompatible_keywords(texts)
    assert issues == []


# ---------------------------------------------------------------------------
# _detect_length_imbalance
# ---------------------------------------------------------------------------


def test_detect_length_imbalance_triggered() -> None:
    short = "Yes."
    long_text = " ".join(["word"] * 30)
    issues = _detect_length_imbalance([short, long_text, short])
    assert len(issues) == 1


def test_detect_length_imbalance_ok() -> None:
    texts = ["Short text here.", "Another short text.", "Third short text."]
    issues = _detect_length_imbalance(texts)
    assert issues == []


# ---------------------------------------------------------------------------
# score_story
# ---------------------------------------------------------------------------


def test_score_story_perfect_score() -> None:
    o = _frag(LAYER_OPENING, "The light appeared at the edge of the horizon.", "O01")
    m = _frag(LAYER_MIDDLE, "A stranger arrived carrying news from afar.", "M01")
    e = _frag(LAYER_ENDING, "She accepted what remained without question.", "E01")
    result = score_story(o, m, e)
    assert isinstance(result, CoherenceResult)
    assert result.score == 100
    assert result.issues == []


def test_score_story_repeated_keyword_deducted() -> None:
    o = _frag(LAYER_OPENING, "The silence spread across the field.", "O01")
    m = _frag(LAYER_MIDDLE, "Silence filled every corner of the room.", "M01")
    e = _frag(LAYER_ENDING, "She found silence at last.", "E01")
    result = score_story(o, m, e)
    assert result.score < 100
    assert any("silence" in issue for issue in result.issues)


def test_score_story_tense_mismatch_deducted() -> None:
    o = _frag(LAYER_OPENING, "Yesterday she had crossed the bridge.", "O01")
    m = _frag(LAYER_MIDDLE, "Tomorrow she will arrive again.", "M01")
    e = _frag(LAYER_ENDING, "The journey ended quietly.", "E01")
    result = score_story(o, m, e)
    assert result.score < 100
    assert any("mismatch" in issue.lower() for issue in result.issues)


def test_score_story_clamped_to_zero() -> None:
    # Construct a pathological story with many issues
    text_a = "morning yesterday silence"
    text_b = "midnight tomorrow silence"
    text_c = "silence joy grief"
    o = _frag(LAYER_OPENING, text_a, "O01")
    m = _frag(LAYER_MIDDLE, text_b, "M01")
    e = _frag(LAYER_ENDING, text_c, "E01")
    result = score_story(o, m, e)
    assert result.score >= 0


def test_score_story_clamped_to_hundred() -> None:
    o = _frag(LAYER_OPENING, "A bright day began.", "O01")
    m = _frag(LAYER_MIDDLE, "The traveller rested.", "M01")
    e = _frag(LAYER_ENDING, "Peace was found.", "E01")
    result = score_story(o, m, e)
    assert result.score <= 100
