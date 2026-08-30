"""Structured, self-contained HTML dashboard rendering."""
from __future__ import annotations

from collections import Counter
from html import escape
from pathlib import Path

from .quality import StoryQuality, summarize


def dashboard_payload(items: list[StoryQuality], language: str) -> dict[str, object]:
    """Return the serialisable data contract used by all dashboard sections."""
    return {"language": language, "summary": summarize(items), "stories": items}


def render_summary_cards(summary: dict[str, object]) -> str:
    return "".join(f"<article><strong>{value}</strong><small>{escape(key.replace('_', ' '))}</small></article>" for key, value in summary.items())


def render_score_bars(items: list[StoryQuality]) -> str:
    return "".join(f"<div class='bar'><label>{item.story_id}</label><i style='width:{item.score}%'></i><b>{item.score}</b></div>" for item in items)


def render_review_table(items: list[StoryQuality]) -> str:
    rows = []
    for item in items:
        penalties = "; ".join(f"{name}: -{value}" for name, value in item.penalties.items()) or "None"
        rows.append(f"<tr><td>{item.story_id}</td><td title='{escape(penalties)}'>{item.score}</td><td>{item.word_count}</td><td>{item.sentence_count}</td><td>{escape(', '.join(item.repeated_keywords) or '—')}</td><td>{escape(penalties)}</td><td>{item.review_priority}</td></tr>")
    return "<table><thead><tr><th>ID</th><th>Score</th><th>Words</th><th>Sentences</th><th>Repeated keywords</th><th>Penalty breakdown</th><th>Action</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"


def render_keyword_chart(items: list[StoryQuality]) -> str:
    counts = Counter(word for item in items for word in item.repeated_keywords)
    return "".join(f"<div class='bar'><label>{escape(word)}</label><i style='width:{count * 20}px'></i><b>{count}</b></div>" for word, count in counts.most_common(12)) or "<p>No meaningful repeated keywords.</p>"


def export_dashboard(items: list[StoryQuality], language: str, path: Path) -> None:
    payload = dashboard_payload(items, language)
    summary = render_summary_cards(payload["summary"])  # type: ignore[arg-type]
    html = f"""<!doctype html><html lang='{escape(language)}'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Story quality dashboard</title><style>:root{{color-scheme:light}}body{{font:16px system-ui;margin:0;background:#f7f5f0;color:#17202a}}main{{max-width:1200px;margin:auto;padding:32px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}}article,section{{background:#fff;border-radius:10px;padding:18px;margin:16px 0}}strong{{display:block;font-size:28px}}small{{color:#587}}.bar{{display:flex;gap:8px;align-items:center;margin:6px 0}}label{{width:70px}}i{{height:15px;background:#357266;border-radius:3px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}@media(max-width:700px){{main{{padding:16px}}table{{font-size:12px}}}}</style><main><header><h1>Story quality dashboard</h1><p>Language: <b>{escape(language)}</b>. Automated signals prioritize editorial review; they do not replace it.</p></header><div class='cards'>{summary}</div><section><h2>Coherence score by story</h2>{render_score_bars(items)}</section><section><h2>Repeated keyword frequency</h2>{render_keyword_chart(items)}</section><section><h2>Review queue</h2>{render_review_table(items)}</section></main></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
