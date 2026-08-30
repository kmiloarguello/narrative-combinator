from src.fragments import Fragment, Story
from src.quality import analyze_story, summarize


def test_analysis_identifies_repeated_keywords() -> None:
    fragments = {
        "O01": Fragment("O01", "opening", "A silence fell."),
        "M01": Fragment("M01", "middle", "Silence returned."),
        "E01": Fragment("E01", "ending", "She left."),
    }
    story = Story("S001", "O01", "M01", "E01", "A silence fell. Silence returned. She left.")
    quality = analyze_story(story, fragments, "en")
    assert "silence" in quality.repeated_keywords
    assert summarize([quality])["story_count"] == 1
