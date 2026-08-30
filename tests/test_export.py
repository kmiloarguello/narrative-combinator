"""Tests for src/export.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.export import export_to_json, export_to_markdown, story_to_dict
from src.fragments import Story


def _make_story(
    sid: str = "S001",
    score: int | None = None,
    issues: list[str] | None = None,
) -> Story:
    return Story(
        id=sid,
        opening_id="O01",
        middle_id="M01",
        ending_id="E01",
        full_text="A beginning. A middle. An end.",
        score=score,
        issues=issues or [],
    )


# ---------------------------------------------------------------------------
# story_to_dict
# ---------------------------------------------------------------------------


def test_story_to_dict_basic_fields() -> None:
    d = story_to_dict(_make_story())
    assert d["id"] == "S001"
    assert d["opening_id"] == "O01"
    assert d["middle_id"] == "M01"
    assert d["ending_id"] == "E01"
    assert "full_text" in d
    assert d["language"] == "en"


def test_story_to_dict_no_score_when_none() -> None:
    d = story_to_dict(_make_story(score=None))
    assert "score" not in d


def test_story_to_dict_score_included_when_set() -> None:
    d = story_to_dict(_make_story(score=85))
    assert d["score"] == 85


def test_story_to_dict_no_issues_when_empty() -> None:
    d = story_to_dict(_make_story(issues=[]))
    assert "issues" not in d


def test_story_to_dict_issues_included_when_present() -> None:
    d = story_to_dict(_make_story(issues=["Repeated keyword: 'silence'"]))
    assert "issues" in d
    assert len(d["issues"]) == 1


# ---------------------------------------------------------------------------
# export_to_json
# ---------------------------------------------------------------------------


def test_export_to_json_creates_file(tmp_path: Path) -> None:
    stories = [_make_story("S001"), _make_story("S002")]
    out = tmp_path / "stories.json"
    export_to_json(stories, out)
    assert out.exists()


def test_export_to_json_valid_json(tmp_path: Path) -> None:
    stories = [_make_story("S001", score=90)]
    out = tmp_path / "stories.json"
    export_to_json(stories, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "stories" in data
    assert len(data["stories"]) == 1


def test_export_to_json_creates_parent_dirs(tmp_path: Path) -> None:
    out = tmp_path / "nested" / "deep" / "stories.json"
    export_to_json([_make_story()], out)
    assert out.exists()


# ---------------------------------------------------------------------------
# export_to_markdown
# ---------------------------------------------------------------------------


def test_export_to_markdown_creates_file(tmp_path: Path) -> None:
    stories = [_make_story("S001")]
    out = tmp_path / "stories.md"
    export_to_markdown(stories, out)
    assert out.exists()


def test_export_to_markdown_contains_story_id(tmp_path: Path) -> None:
    stories = [_make_story("S007")]
    out = tmp_path / "stories.md"
    export_to_markdown(stories, out)
    content = out.read_text(encoding="utf-8")
    assert "S007" in content


def test_export_to_markdown_contains_score(tmp_path: Path) -> None:
    stories = [_make_story("S001", score=78)]
    out = tmp_path / "stories.md"
    export_to_markdown(stories, out)
    content = out.read_text(encoding="utf-8")
    assert "78/100" in content


def test_export_to_markdown_contains_issues(tmp_path: Path) -> None:
    stories = [_make_story("S001", issues=["Repeated keyword: 'light'"])]
    out = tmp_path / "stories.md"
    export_to_markdown(stories, out)
    content = out.read_text(encoding="utf-8")
    assert "light" in content


def test_export_to_markdown_creates_parent_dirs(tmp_path: Path) -> None:
    out = tmp_path / "sub" / "stories.md"
    export_to_markdown([_make_story()], out)
    assert out.exists()
