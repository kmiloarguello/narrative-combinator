"""Tests for src/markov.py."""

from __future__ import annotations

import random

import pytest

from src.markov import build_chain, generate_text, tokenize, train_on_layer


def test_tokenize_basic() -> None:
    result = tokenize("Hello, world! This is a test.")
    assert result == ["hello", "world", "this", "is", "a", "test"]


def test_tokenize_strips_apostrophes() -> None:
    result = tokenize("'hello' world")
    assert "hello" in result
    assert "world" in result


def test_tokenize_contractions_kept() -> None:
    result = tokenize("don't stop")
    assert any("don" in w for w in result)


def test_tokenize_empty_string() -> None:
    assert tokenize("") == []


def test_build_chain_keys_are_tuples() -> None:
    chain = build_chain(["the cat sat on the mat"])
    for key in chain:
        assert isinstance(key, tuple)
        assert len(key) == 1


def test_build_chain_transitions() -> None:
    chain = build_chain(["the cat sat"])
    assert ("the",) in chain
    assert "cat" in chain[("the",)]


def test_build_chain_higher_order() -> None:
    chain = build_chain(["the big red cat sat"], order=2)
    for key in chain:
        assert len(key) == 2


def test_build_chain_empty_texts() -> None:
    chain = build_chain([])
    assert chain == {}


def test_build_chain_short_text_skipped() -> None:
    # Single-word text shorter than order; should produce no entries
    chain = build_chain(["cat"], order=1)
    assert chain == {}


def test_generate_text_returns_string() -> None:
    chain = build_chain(["the cat sat on the mat and the cat slept"])
    result = generate_text(chain, max_words=10, rng=random.Random(1))
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_text_ends_with_punctuation() -> None:
    chain = build_chain(["once upon a time there was a cat"])
    result = generate_text(chain, max_words=15, rng=random.Random(7))
    assert result[-1] in {".", "!", "?"}


def test_generate_text_capitalized() -> None:
    chain = build_chain(["once there was a light in the dark and it glowed"])
    result = generate_text(chain, max_words=10, rng=random.Random(3))
    assert result[0].isupper()


def test_generate_text_empty_chain() -> None:
    result = generate_text({}, max_words=20)
    assert result == ""


def test_generate_text_seed_word() -> None:
    texts = ["the morning light fell softly on the quiet room"]
    chain = build_chain(texts)
    result = generate_text(chain, max_words=10, seed_word="morning", rng=random.Random(5))
    assert isinstance(result, str)


def test_generate_text_max_words_respected() -> None:
    # Long repeating chain — word count should not exceed max_words
    texts = ["a b c d e f g h i j k l m n o p q r s t u v w x y z"] * 5
    chain = build_chain(texts)
    result = generate_text(chain, max_words=8, rng=random.Random(0))
    # Allow for punctuation mark at end; word count ≤ max_words
    word_count = len(result.split())
    assert word_count <= 8


def test_train_on_layer_returns_chain() -> None:
    texts = ["the light faded slowly", "the light returned at dawn"]
    chain = train_on_layer(texts)
    assert isinstance(chain, dict)
    assert len(chain) > 0
