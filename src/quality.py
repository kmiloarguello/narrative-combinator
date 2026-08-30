"""Transparent, local quality metrics for generated stories."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from .coherence import _extract_keywords, score_story
from .fragments import Fragment, Story

@dataclass
class StoryQuality:
    story_id: str; score: int; word_count: int; sentence_count: int
    repeated_keywords: list[str]; review_priority: str; penalties: dict[str, int]

def analyze_story(story: Story, fragments: dict[str, Fragment], language: str) -> StoryQuality:
    parts = [fragments[story.opening_id], fragments[story.middle_id], fragments[story.ending_id]]
    result = score_story(*parts, language=language)
    counts = Counter(word for part in parts for word in set(_extract_keywords(part.text, language)))
    repeated = sorted(word for word, count in counts.items() if count > 1)
    return StoryQuality(story.id, result.score, len(story.full_text.split()), sum(story.full_text.count(x) for x in '.!?'), repeated, 'review' if result.score < 90 or len(repeated) >= 2 else 'ready', result.penalties)

def summarize(items: list[StoryQuality]) -> dict[str, object]:
    scores = [item.score for item in items]
    return {'story_count': len(items), 'average_score': round(sum(scores) / len(scores), 1) if scores else 0, 'ready_count': sum(i.review_priority == 'ready' for i in items), 'review_count': sum(i.review_priority == 'review' for i in items)}

def fragment_score_stats(stories: list[Story], items: list[StoryQuality]) -> dict[str, dict[str, float]]:
    """Average score contributed by each opening, middle, and ending fragment."""
    scores = {item.story_id: item.score for item in items}
    groups: dict[str, list[int]] = {}
    for story in stories:
        for fragment_id in (story.opening_id, story.middle_id, story.ending_id):
            groups.setdefault(fragment_id, []).append(scores[story.id])
    return {fragment_id: {"average_score": round(sum(values) / len(values), 1), "story_count": len(values)} for fragment_id, values in groups.items()}
