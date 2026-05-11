"""Story generation: all combinations and random selection."""

from __future__ import annotations

import random
from itertools import product

from .fragments import Fragment, Story, LAYER_OPENING, LAYER_MIDDLE, LAYER_ENDING


def _make_story_id(index: int) -> str:
    return f"S{index:03d}"


def build_full_text(opening: Fragment, middle: Fragment, ending: Fragment) -> str:
    """Concatenate three fragments into a single story text."""
    return f"{opening.text} {middle.text} {ending.text}"


def generate_all_stories(fragments: dict[str, list[Fragment]]) -> list[Story]:
    """Generate all possible story combinations (3×3×3 = 27)."""
    openings = fragments[LAYER_OPENING]
    middles = fragments[LAYER_MIDDLE]
    endings = fragments[LAYER_ENDING]

    stories: list[Story] = []
    for index, (o, m, e) in enumerate(product(openings, middles, endings), start=1):
        story = Story(
            id=_make_story_id(index),
            opening_id=o.id,
            middle_id=m.id,
            ending_id=e.id,
            full_text=build_full_text(o, m, e),
        )
        stories.append(story)

    return stories


def generate_random_story(
    fragments: dict[str, list[Fragment]],
    rng: random.Random | None = None,
) -> Story:
    """Pick one random opening, middle, and ending and combine them."""
    r = rng or random
    o = r.choice(fragments[LAYER_OPENING])
    m = r.choice(fragments[LAYER_MIDDLE])
    e = r.choice(fragments[LAYER_ENDING])

    # Compute a stable index for the story id
    openings = fragments[LAYER_OPENING]
    middles = fragments[LAYER_MIDDLE]
    endings = fragments[LAYER_ENDING]
    o_idx = openings.index(o)
    m_idx = middles.index(m)
    e_idx = endings.index(e)
    index = o_idx * len(middles) * len(endings) + m_idx * len(endings) + e_idx + 1

    return Story(
        id=_make_story_id(index),
        opening_id=o.id,
        middle_id=m.id,
        ending_id=e.id,
        full_text=build_full_text(o, m, e),
    )
