"""Tests for src/fragments.py."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.fragments import (
    Fragment,
    Story,
    LAYER_ENDING,
    LAYER_MIDDLE,
    LAYER_OPENING,
    LAYERS,
    all_fragments_flat,
    fragment_by_id,
    load_fragments,
)

SAMPLE_DATA = {
    "fragments": [
        {"id": "O01", "layer": "opening", "text": "Once there was light.", "tags": ["light"]},
        {"id": "O02", "layer": "opening", "text": "The door stood open.", "tags": []},
        {"id": "O03", "layer": "opening", "text": "Rain fell without pause.", "tags": []},
        {"id": "M01", "layer": "middle", "text": "Time passed slowly.", "tags": []},
        {"id": "M02", "layer": "middle", "text": "A voice called out.", "tags": []},
        {"id": "M03", "layer": "middle", "text": "The stranger waited.", "tags": []},
        {"id": "E01", "layer": "ending", "text": "All became still.", "tags": []},
        {"id": "E02", "layer": "ending", "text": "Nothing remained.", "tags": []},
        {"id": "E03", "layer": "ending", "text": "She walked away.", "tags": []},
    ]
}

MULTILINGUAL_SAMPLE_DATA = {
    "fragments": [
        {
            "id": "O01",
            "layer": "opening",
            "text": {"en": "English opening.", "fr": "Ouverture française.", "es": "Inicio español."},
        }
    ]
}


@pytest.fixture()
def fragments_file(tmp_path: Path) -> Path:
    p = tmp_path / "fragments.json"
    p.write_text(json.dumps(SAMPLE_DATA), encoding="utf-8")
    return p


def test_load_fragments_returns_three_layers(fragments_file: Path) -> None:
    frags = load_fragments(fragments_file)
    assert set(frags.keys()) == set(LAYERS)


def test_load_fragments_counts(fragments_file: Path) -> None:
    frags = load_fragments(fragments_file)
    assert len(frags[LAYER_OPENING]) == 3
    assert len(frags[LAYER_MIDDLE]) == 3
    assert len(frags[LAYER_ENDING]) == 3


def test_load_fragments_tags(fragments_file: Path) -> None:
    frags = load_fragments(fragments_file)
    o01 = frags[LAYER_OPENING][0]
    assert o01.id == "O01"
    assert o01.tags == ["light"]


def test_fragment_by_id_found(fragments_file: Path) -> None:
    frags = load_fragments(fragments_file)
    frag = fragment_by_id(frags, "M02")
    assert frag is not None
    assert frag.layer == LAYER_MIDDLE


def test_fragment_by_id_not_found(fragments_file: Path) -> None:
    frags = load_fragments(fragments_file)
    assert fragment_by_id(frags, "X99") is None


def test_all_fragments_flat(fragments_file: Path) -> None:
    frags = load_fragments(fragments_file)
    flat = all_fragments_flat(frags)
    assert len(flat) == 9
    assert "E03" in flat
    assert flat["E03"].layer == LAYER_ENDING


def test_fragment_dataclass_defaults() -> None:
    f = Fragment(id="T01", layer="opening", text="Hello world.")
    assert f.tags == []


def test_story_dataclass_defaults() -> None:
    s = Story(id="S001", opening_id="O01", middle_id="M01", ending_id="E01", full_text="text")
    assert s.score is None
    assert s.issues == []


def test_load_fragments_selects_requested_translation(tmp_path: Path) -> None:
    path = tmp_path / "multilingual.json"
    path.write_text(json.dumps(MULTILINGUAL_SAMPLE_DATA), encoding="utf-8")

    frags = load_fragments(path, language="fr")

    assert frags[LAYER_OPENING][0].text == "Ouverture française."


def test_load_fragments_rejects_unsupported_language(tmp_path: Path) -> None:
    path = tmp_path / "multilingual.json"
    path.write_text(json.dumps(MULTILINGUAL_SAMPLE_DATA), encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported language 'de'"):
        load_fragments(path, language="de")
