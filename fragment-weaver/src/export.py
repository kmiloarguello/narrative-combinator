"""Export stories to JSON and Markdown formats."""

from __future__ import annotations

import json
from pathlib import Path

from .fragments import Story


def story_to_dict(story: Story) -> dict:
    """Serialise a :class:`~fragments.Story` to a JSON-compatible dictionary."""
    d: dict = {
        "id": story.id,
        "opening_id": story.opening_id,
        "middle_id": story.middle_id,
        "ending_id": story.ending_id,
        "full_text": story.full_text,
    }
    if story.score is not None:
        d["score"] = story.score
    if story.issues:
        d["issues"] = story.issues
    return d


def export_to_json(stories: list[Story], output_path: Path) -> None:
    """Write *stories* to a JSON file at *output_path*.

    The output format is::

        {
          "stories": [ { "id": "S001", ... }, ... ]
        }
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"stories": [story_to_dict(s) for s in stories]}
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def export_to_markdown(stories: list[Story], output_path: Path) -> None:
    """Write *stories* to a Markdown file at *output_path*."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# Fragment Weaver — Generated Stories\n\n"]

    for story in stories:
        lines.append(f"## {story.id}\n\n")
        lines.append(
            f"**Opening:** {story.opening_id} | "
            f"**Middle:** {story.middle_id} | "
            f"**Ending:** {story.ending_id}\n\n"
        )
        if story.score is not None:
            lines.append(f"**Coherence Score:** {story.score}/100\n\n")
        if story.issues:
            lines.append("**Issues:**\n\n")
            for issue in story.issues:
                lines.append(f"- {issue}\n")
            lines.append("\n")
        lines.append(f"{story.full_text}\n\n")
        lines.append("---\n\n")

    with output_path.open("w", encoding="utf-8") as f:
        f.writelines(lines)
