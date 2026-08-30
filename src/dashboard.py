"""Self-contained HTML dashboard export."""
from __future__ import annotations
from html import escape
from pathlib import Path
from .quality import StoryQuality, summarize

def export_dashboard(items: list[StoryQuality], language: str, path: Path) -> None:
    summary = summarize(items)
    cards = ''.join(f'<article><strong>{v}</strong><small>{k}</small></article>' for k, v in summary.items())
    def penalties(i: StoryQuality) -> str: return '; '.join(f'{k}: -{v}' for k,v in i.penalties.items()) or 'None'
    heatmap = ''.join(f"<span class='cell {'green' if i.score >= 90 else 'yellow' if i.score >= 80 else 'red'}'>{i.story_id}<b>{i.score}</b></span>" for i in items)
    buckets = {'<80': 0, '80–89': 0, '90–99': 0, '100': 0}
    for i in items: buckets['<80' if i.score < 80 else '80–89' if i.score < 90 else '90–99' if i.score < 100 else '100'] += 1
    histogram = ''.join(f"<p><label>{k}</label><i style='width:{v*20}px'></i><b>{v}</b></p>" for k,v in buckets.items())
    rows = ''.join(f"<tr><td>{i.story_id}</td><td title='{escape(penalties(i))}'>{i.score}</td><td>{i.word_count}</td><td>{i.sentence_count}</td><td>{escape(', '.join(i.repeated_keywords) or '—')}</td><td>{escape(penalties(i))}</td><td>{i.review_priority}</td></tr>" for i in items)
    html = f"""<!doctype html><meta charset='utf-8'><title>Quality dashboard</title><style>body{{font:16px system-ui;margin:40px;background:#faf8f4}}section{{display:flex;gap:12px;flex-wrap:wrap}}article{{background:#fff;padding:16px;border-radius:8px;min-width:120px}}.heatmap{{display:grid;grid-template-columns:repeat(9,62px);gap:4px}}.cell{{padding:8px;text-align:center}}.green{{background:#cce8d5}}.yellow{{background:#ffe7a3}}.red{{background:#f7b7ad}}i{{display:inline-block;height:15px;background:#357266}}table{{border-collapse:collapse;background:#fff;width:100%}}th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}</style><h1>Story quality dashboard</h1><section>{cards}</section><h2>Combination heatmap</h2><div class='heatmap'>{heatmap}</div><h2>Score distribution</h2>{histogram}<h2>Review queue</h2><table><tr><th>ID</th><th>Score</th><th>Words</th><th>Sentences</th><th>Repeated keywords</th><th>Penalty breakdown</th><th>Action</th></tr>{rows}</table>"""
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(html, encoding='utf-8')
