"""Fragment and Story data models, plus JSON loading utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .locales import get_language_rules

LAYER_OPENING = "opening"
LAYER_MIDDLE = "middle"
LAYER_ENDING = "ending"
LAYERS: list[str] = [LAYER_OPENING, LAYER_MIDDLE, LAYER_ENDING]


@dataclass
class Fragment:
    """A single text fragment belonging to one narrative layer."""

    id: str
    layer: str
    text: str
    tags: list[str] = field(default_factory=list)


@dataclass
class Story:
    """A combined story assembled from one fragment per layer."""

    id: str
    opening_id: str
    middle_id: str
    ending_id: str
    full_text: str
    language: str = "en"
    score: int | None = None
    issues: list[str] = field(default_factory=list)


def load_fragments(path: Path, language: str = "en") -> dict[str, list[Fragment]]:
    """Load fragments in *language* and return them keyed by narrative layer.

    Fragment text may be a legacy string or a mapping keyed by ISO 639-1 code.
    A requested translation must exist for every fragment.
    """
    get_language_rules(language)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    fragments: dict[str, list[Fragment]] = {layer: [] for layer in LAYERS}
    for item in data["fragments"]:
        text = item["text"]
        if isinstance(text, dict):
            try:
                text = text[language]
            except KeyError as exc:
                raise ValueError(
                    f"Fragment '{item['id']}' has no '{language}' translation."
                ) from exc
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Fragment '{item['id']}' has invalid text for '{language}'.")
        frag = Fragment(
            id=item["id"],
            layer=item["layer"],
            text=text,
            tags=item.get("tags", []),
        )
        if frag.layer in fragments:
            fragments[frag.layer].append(frag)

    return fragments


def fragment_by_id(
    fragments: dict[str, list[Fragment]], frag_id: str
) -> Fragment | None:
    """Find a fragment by its ID across all layers."""
    for layer_frags in fragments.values():
        for frag in layer_frags:
            if frag.id == frag_id:
                return frag
    return None


def all_fragments_flat(fragments: dict[str, list[Fragment]]) -> dict[str, Fragment]:
    """Return a flat id → Fragment mapping for quick lookups."""
    return {frag.id: frag for layer_frags in fragments.values() for frag in layer_frags}
