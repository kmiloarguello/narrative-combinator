"""Tests for src/generator.py."""

from __future__ import annotations

import random

import pytest

from src.fragments import Fragment, LAYER_ENDING, LAYER_MIDDLE, LAYER_OPENING
from src.generator import build_full_text, generate_all_stories, generate_random_story


def _make_fragments() -> dict[str, list[Fragment]]:
    return {
        LAYER_OPENING: [
            Fragment(id="O01", layer=LAYER_OPENING, text="Opening one."),
            Fragment(id="O02", layer=LAYER_OPENING, text="Opening two."),
            Fragment(id="O03", layer=LAYER_OPENING, text="Opening three."),
        ],
        LAYER_MIDDLE: [
            Fragment(id="M01", layer=LAYER_MIDDLE, text="Middle one."),
            Fragment(id="M02", layer=LAYER_MIDDLE, text="Middle two."),
            Fragment(id="M03", layer=LAYER_MIDDLE, text="Middle three."),
        ],
        LAYER_ENDING: [
            Fragment(id="E01", layer=LAYER_ENDING, text="Ending one."),
            Fragment(id="E02", layer=LAYER_ENDING, text="Ending two."),
            Fragment(id="E03", layer=LAYER_ENDING, text="Ending three."),
        ],
    }


def test_generate_all_stories_count() -> None:
    fragments = _make_fragments()
    stories = generate_all_stories(fragments)
    assert len(stories) == 27


def test_generate_all_stories_unique_ids() -> None:
    fragments = _make_fragments()
    stories = generate_all_stories(fragments)
    ids = [s.id for s in stories]
    assert len(ids) == len(set(ids))


def test_generate_all_stories_all_combinations_present() -> None:
    fragments = _make_fragments()
    stories = generate_all_stories(fragments)
    combos = {(s.opening_id, s.middle_id, s.ending_id) for s in stories}
    for o in ["O01", "O02", "O03"]:
        for m in ["M01", "M02", "M03"]:
            for e in ["E01", "E02", "E03"]:
                assert (o, m, e) in combos


def test_generate_all_stories_full_text_contains_all_parts() -> None:
    fragments = _make_fragments()
    stories = generate_all_stories(fragments)
    s = stories[0]
    assert "Opening" in s.full_text
    assert "Middle" in s.full_text
    assert "Ending" in s.full_text


def test_generate_all_stories_records_language() -> None:
    stories = generate_all_stories(_make_fragments(), language="es")
    assert all(story.language == "es" for story in stories)


def test_build_full_text() -> None:
    o = Fragment(id="O01", layer=LAYER_OPENING, text="A.")
    m = Fragment(id="M01", layer=LAYER_MIDDLE, text="B.")
    e = Fragment(id="E01", layer=LAYER_ENDING, text="C.")
    assert build_full_text(o, m, e) == "A. B. C."


def test_generate_random_story_valid_ids() -> None:
    fragments = _make_fragments()
    rng = random.Random(42)
    story = generate_random_story(fragments, rng=rng)
    assert story.opening_id in {"O01", "O02", "O03"}
    assert story.middle_id in {"M01", "M02", "M03"}
    assert story.ending_id in {"E01", "E02", "E03"}


def test_generate_random_story_reproducible() -> None:
    fragments = _make_fragments()
    story_a = generate_random_story(fragments, rng=random.Random(0))
    story_b = generate_random_story(fragments, rng=random.Random(0))
    assert story_a.opening_id == story_b.opening_id
    assert story_a.middle_id == story_b.middle_id
    assert story_a.ending_id == story_b.ending_id
