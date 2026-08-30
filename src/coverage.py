"""Translation and editorial coverage reporting."""
from __future__ import annotations
import json
from pathlib import Path
from .reviews import load_reviews

def coverage_report(fragments_path: Path, reviews_path: Path) -> dict[str, object]:
    fragments = json.loads(fragments_path.read_text(encoding="utf-8"))["fragments"]
    languages = ("en", "fr", "es")
    translation = {language: sum(isinstance(item["text"], dict) and bool(item["text"].get(language)) for item in fragments) for language in languages}
    reviews = load_reviews(reviews_path)
    approved = sum(review.status == "approved" for review in reviews.values())
    return {"fragments": len(fragments), "translations": translation, "reviewed_stories": len(reviews), "approved_stories": approved, "review_coverage_percent": round(len(reviews) / 27 * 100, 1), "print_ready_percent": round(approved / 27 * 100, 1)}
