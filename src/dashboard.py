"""Self-contained HTML dashboard export."""
from __future__ import annotations
from html import escape
from pathlib import Path
from .quality import StoryQuality, summarize

def export_dashboard(items: list[StoryQuality], language: str, path: Path) -> None:
    summary = summarize(items)
    cards = ''.join(f'<article><strong>{v}</strong><small>{k}</small></article>' for k,v in summary.items())
    bars = ''.join(f"<p><label>{i.story_id}</label><i style='width:{i.score}%'></i><b>{i.score}</b></p>" for i in items)
    rows = ''.join(f"<tr><td>{i.story_id}</td><td title='{escape('; '.join(f'{name}: -{value}' for name, value in i.penalties.items()) or 'No penalties'}'>{i.score}</td><td>{i.word_count}</td><td>{i.sentence_count}</td><td>{escape(', '.join(i.repeated_keywords) or '—')}</td><td>{escape('; '.join(f'{name}: -{value}' for name, value in i.penalties.items()) or 'None')}</td><td>{i.review_priority}</td></tr>" for i in items)
    html = f"""<!doctype html><meta charset='utf-8'><title>Quality dashboard</title><style>body{{font:16px system-ui;margin:40px;background:#faf8f4;color:#17202a}}section{{display:flex;gap:12px;flex-wrap:wrap}}article{{background:#fff;padding:16px;border-radius:8px;min-width:120px}}strong{{display:block;font-size:28px}}small{{color:#567}}p{{display:flex;gap:8px;align-items:center;margin:5px 0}}label{{width:42px}}i{{height:15px;background:#357266;border-radius:3px}}table{{border-collapse:collapse;background:#fff;width:100%}}th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}th{{background:#e7f0ed}}</style><h1>Story quality dashboard</h1><p>Language: <b>{escape(language)}</b>. Scores guide editorial review; they do not automatically judge literary quality.</p><section>{cards}</section><h2>Coherence scores</h2>{bars}<h2>Review queue</h2><table><tr><th>ID</th><th>Score</th><th>Words</th><th>Sentences</th><th>Repeated keywords</th><th>Action</th></tr>{rows}</table>"""
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(html, encoding='utf-8')
