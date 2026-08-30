"""Structured, self-contained HTML dashboard rendering."""
from __future__ import annotations

from collections import Counter
from html import escape
from pathlib import Path

from .quality import StoryQuality, summarize
from .reviews import EditorialReview


def dashboard_payload(items: list[StoryQuality], language: str) -> dict[str, object]:
    """Return the serialisable data contract used by all dashboard sections."""
    return {"language": language, "summary": summarize(items), "stories": items}


def render_summary_cards(summary: dict[str, object]) -> str:
    return "".join(f"<article><strong>{value}</strong><small>{escape(key.replace('_', ' '))}</small></article>" for key, value in summary.items())


def render_score_bars(items: list[StoryQuality]) -> str:
    return "".join(f"<div class='bar'><label>{item.story_id}</label><i style='width:{item.score}%'></i><b>{item.score}</b></div>" for item in items)


def render_histogram(items: list[StoryQuality]) -> str:
    buckets = {"<80": 0, "80–89": 0, "90–99": 0, "100": 0}
    for item in items:
        buckets["<80" if item.score < 80 else "80–89" if item.score < 90 else "90–99" if item.score < 100 else "100"] += 1
    return "".join(f"<div class='bar'><label>{band}</label><i style='width:{count * 28}px'></i><b>{count}</b></div>" for band, count in buckets.items())


def render_length_distribution(items: list[StoryQuality]) -> str:
    return "".join(f"<div class='bar'><label>{item.story_id}</label><i class='{'in-target' if 70 <= item.word_count <= 90 else 'out-target'}' style='width:{item.word_count * 2}px'></i><b>{item.word_count}</b></div>" for item in items)


def render_heatmap(items: list[StoryQuality]) -> str:
    """Render rows as openings and columns as middle/ending combinations."""
    columns = "".join(f"<th>M{middle}/E{ending}</th>" for middle in range(1, 4) for ending in range(1, 4))
    rows = []
    for opening in range(3):
        cells = []
        for item in items[opening * 9:(opening + 1) * 9]:
            tone = "good" if item.score >= 90 else "warn" if item.score >= 80 else "poor"
            cells.append(f"<td class='{tone}' title='{item.story_id}: {item.score}'>{item.score}</td>")
        rows.append(f"<tr><th>O{opening + 1:02d}</th>{''.join(cells)}</tr>")
    return f"<table class='heatmap'><thead><tr><th>Opening</th>{columns}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def render_review_table(items: list[StoryQuality]) -> str:
    rows = []
    for item in items:
        penalties = "; ".join(f"{name}: -{value}" for name, value in item.penalties.items()) or "None"
        rows.append(f"<tr><td>{item.story_id}</td><td title='{escape(penalties)}'>{item.score}</td><td>{item.word_count}</td><td>{item.sentence_count}</td><td>{escape(', '.join(item.repeated_keywords) or '—')}</td><td>{escape(penalties)}</td><td>{item.review_priority}</td></tr>")
    return "<table><thead><tr><th>ID</th><th>Score</th><th>Words</th><th>Sentences</th><th>Repeated keywords</th><th>Penalty breakdown</th><th>Action</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"


def render_keyword_chart(items: list[StoryQuality]) -> str:
    counts = Counter(word for item in items for word in item.repeated_keywords)
    return "".join(f"<div class='bar'><label>{escape(word)}</label><i style='width:{count * 20}px'></i><b>{count}</b></div>" for word, count in counts.most_common(12)) or "<p>No meaningful repeated keywords.</p>"


def export_dashboard(items: list[StoryQuality], language: str, path: Path, reviews: dict[str, EditorialReview] | None = None, fragment_stats: dict[str, dict[str, float]] | None = None) -> None:
    payload = dashboard_payload(items, language)
    summary = render_summary_cards(payload["summary"])  # type: ignore[arg-type]
    html = f"""<!doctype html><html lang='{escape(language)}'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Story quality dashboard</title><style>:root{{color-scheme:light}}body{{font:16px system-ui;margin:0;background:#f7f5f0;color:#17202a}}main{{max-width:1200px;margin:auto;padding:32px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}}article,section{{background:#fff;border-radius:10px;padding:18px;margin:16px 0}}strong{{display:block;font-size:28px}}small{{color:#587}}.bar{{display:flex;gap:8px;align-items:center;margin:6px 0}}label{{width:70px}}i{{height:15px;background:#357266;border-radius:3px}}.out-target{{background:#e9a23b}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}.good{{background:#cce8d5}}.warn{{background:#ffe7a3}}.poor{{background:#f7b7ad}}@media(max-width:700px){{main{{padding:16px}}table{{font-size:12px}}}}</style><main><header><h1>Story quality dashboard</h1><p>Language: <b>{escape(language)}</b>. Automated signals prioritize editorial review; they do not replace it.</p></header><div class='cards'>{summary}</div><section><h2>Combination heatmap</h2><p>Rows are openings; columns pair each middle and ending. Green: 90+, amber: 80–89, red: below 80.</p>{render_heatmap(items)}</section><section><h2>Score distribution</h2>{render_histogram(items)}</section><section><h2>Page-length distribution</h2><p>Green is within the 70–90 word target; amber needs layout review.</p>{render_length_distribution(items)}</section><section><h2>Coherence score by story</h2>{render_score_bars(items)}</section><section><h2>Repeated keyword frequency</h2>{render_keyword_chart(items)}</section><section><h2>Review queue</h2>{render_review_table(items)}</section></main></html>"""
    stat_rows = "".join(f"<tr><td>{fragment}</td><td>{values['average_score']}</td><td>{values['story_count']}</td></tr>" for fragment, values in sorted((fragment_stats or {}).items())) or "<tr><td colspan='3'>No statistics available.</td></tr>"
    review_rows = "".join(f"<tr><td>{escape(story_id)}</td><td>{escape(review.status)}</td><td>{escape(review.reviewer)}</td><td>{escape(review.reviewed_on)}</td><td>{escape(review.note)}</td></tr>" for story_id, review in (reviews or {}).items()) or "<tr><td colspan='5'>No human reviews recorded yet.</td></tr>"
    insights = f"<section><h2>Fragment statistics</h2><table><tr><th>Fragment</th><th>Average score</th><th>Stories</th></tr>{stat_rows}</table></section><section><h2>Editorial decisions</h2><table><tr><th>Story</th><th>Status</th><th>Reviewer</th><th>Date</th><th>Note</th></tr>{review_rows}</table></section>"
    html = html.replace("<section><h2>Review queue</h2>", insights + "<section><h2>Review queue</h2>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
