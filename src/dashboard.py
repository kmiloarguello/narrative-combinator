"""Self-contained HTML dashboard export."""
from __future__ import annotations
from html import escape
from pathlib import Path
from .quality import StoryQuality, summarize

def export_dashboard(items: list[StoryQuality], language: str, path: Path) -> None:
    summary = summarize(items)
    cards = ''.join(f'<article><strong>{v}</strong><small>{k}</small></article>' for k, v in summary.items())
    def penalty_text(item: StoryQuality) -> str:
        return '; '.join(f'{name}: -{value}' for name, value in item.penalties.items()) or 'None'
    heatmap = ''.join(f"<span class='cell {'green' if i.score >= 90 else 'yellow' if i.score >= 80 else 'red'}' title='{i.story_id}: {i.score}'>{i.story_id}<b>{i.score}</b></span>" for i in items)
    rows = ''.join(f"<tr><td>{i.story_id}</td><td title='{escape(penalty_text(i))}'>{i.score}</td><td>{i.word_count}</td><td>{i.sentence_count}</td><td>{escape(', '.join(i.repeated_keywords) or '—')}</td><td>{escape(penalty_text(i))}</td><td>{i.review_priority}</td></tr>" for i in items)
    html = f"""<!doctype html><meta charset='utf-8'><title>Quality dashboard</title><style>body{{font:16px system-ui;margin:40px;background:#faf8f4}}section{{display:flex;gap:12px;flex-wrap:wrap}}article{{background:#fff;padding:16px;border-radius:8px;min-width:120px}}strong{{display:block;font-size:28px}}.heatmap{{display:grid;grid-template-columns:repeat(9,62px);gap:4px}}.cell{{padding:8px 3px;text-align:center}}.cell b{{display:block}}.green{{background:#cce8d5}}.yellow{{background:#ffe7a3}}.red{{background:#f7b7ad}}table{{border-collapse:collapse;background:#fff;width:100%}}th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}</style><h1>Story quality dashboard</h1><p>Language: <b>{escape(language)}</b>.</p><section>{cards}</section><h2>Combination heatmap</h2><div class='heatmap'>{heatmap}</div><h2>Review queue</h2><table><tr><th>ID</th><th>Score</th><th>Words</th><th>Sentences</th><th>Repeated keywords</th><th>Penalty breakdown</th><th>Action</th></tr>{rows}</table>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding='utf-8')
