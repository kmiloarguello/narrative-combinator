"""Transparent, local quality metrics for generated stories."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from .coherence import _extract_keywords, score_story
from .fragments import Fragment, Story

@dataclass
class StoryQuality:
    story_id: str; score: int; word_count: int; sentence_count: int
    repeated_keywords: list[str]; review_priority: str

def analyze_story(story: Story, fragments: dict[str, Fragment], language: str) -> StoryQuality:
    parts = [fragments[story.opening_id], fragments[story.middle_id], fragments[story.ending_id]]
    score = score_story(*parts, language=language).score
    counts = Counter(word for part in parts for word in set(_extract_keywords(part.text, language)))
    repeated = sorted(word for word, count in counts.items() if count > 1)
    return StoryQuality(story.id, score, len(story.full_text.split()), sum(story.full_text.count(x) for x in '.!?'), repeated, 'review' if score < 90 or len(repeated) >= 2 else 'ready')

def summarize(items: list[StoryQuality]) -> dict[str, object]:
    scores = [item.score for item in items]
    return {'story_count': len(items), 'average_score': round(sum(scores) / len(scores), 1) if scores else 0, 'ready_count': sum(i.review_priority == 'ready' for i in items), 'review_count': sum(i.review_priority == 'review' for i in items)}
