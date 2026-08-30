"""Human editorial decisions; these take precedence over automated signals."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path

STATUSES = ("approved", "revise", "rejected")

@dataclass(frozen=True)
class EditorialReview:
    status: str
    reviewer: str
    note: str
    reviewed_on: str

def load_reviews(path: Path) -> dict[str, EditorialReview]:
    if not path.exists(): return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = {}
    for story_id, item in payload.get("reviews", {}).items():
        if item["status"] not in STATUSES: raise ValueError(f"Invalid review status for {story_id}")
        result[story_id] = EditorialReview(item["status"], item.get("reviewer", ""), item.get("note", ""), item.get("reviewed_on", ""))
    return result
