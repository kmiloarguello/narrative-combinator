"""Simple first-order Markov chain text generator (standard library only)."""

from __future__ import annotations

import random
import re
from collections import defaultdict


def tokenize(text: str) -> list[str]:
    """Split text into lowercase word tokens, stripping punctuation."""
    words = re.findall(r"[^\W\d_]+(?:'[^\W\d_]+)?", text.lower(), flags=re.UNICODE)
    # Strip surrounding apostrophes (keep inner ones for contractions)
    return [w.strip("'") for w in words if w.strip("'")]


def build_chain(
    texts: list[str], order: int = 1
) -> dict[tuple[str, ...], list[str]]:
    """Build a Markov transition dictionary from a list of texts.

    Args:
        texts: Source texts to train on.
        order: Number of words used as the state key (chain order).

    Returns:
        Mapping from word-tuple state to list of possible next words.
    """
    chain: dict[tuple[str, ...], list[str]] = defaultdict(list)

    for text in texts:
        words = tokenize(text)
        if len(words) <= order:
            continue
        for i in range(len(words) - order):
            key = tuple(words[i : i + order])
            chain[key].append(words[i + order])

    return dict(chain)


def generate_text(
    chain: dict[tuple[str, ...], list[str]],
    max_words: int = 30,
    seed_word: str | None = None,
    rng: random.Random | None = None,
) -> str:
    """Generate a text fragment from a trained Markov chain.

    Args:
        chain: Transition dictionary produced by :func:`build_chain`.
        max_words: Maximum number of words to generate.
        seed_word: Optional starting word. Falls back to a random key.
        rng: Optional :class:`random.Random` instance for reproducibility.

    Returns:
        Generated text string, capitalised with a trailing period.
    """
    if not chain:
        return ""

    r = rng or random
    keys = list(chain.keys())
    order = len(keys[0]) if keys else 1

    if seed_word:
        seed_lower = seed_word.lower()
        matching = [k for k in keys if k[0] == seed_lower]
        start: tuple[str, ...] = r.choice(matching) if matching else r.choice(keys)
    else:
        start = r.choice(keys)

    words: list[str] = list(start)

    for _ in range(max_words - order):
        key = tuple(words[-order:])
        nexts = chain.get(key)
        if not nexts:
            break
        words.append(r.choice(nexts))

    if not words:
        return ""

    words[0] = words[0].capitalize()
    text = " ".join(words)
    if not text.endswith((".", "!", "?")):
        text += "."
    return text


def train_on_layer(
    fragment_texts: list[str], order: int = 1
) -> dict[tuple[str, ...], list[str]]:
    """Convenience wrapper: train a Markov chain on a list of fragment texts."""
    return build_chain(fragment_texts, order=order)
