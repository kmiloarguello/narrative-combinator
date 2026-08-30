# Fragment Weaver

A combinatorial storytelling engine for a physical split-page book.

Fragment Weaver generates stories by combining **one fragment from each of three narrative layers** — opening, middle, and ending. With 3 fragments per layer, the engine produces **27 unique stories**.

The initial multilingual edition supports English (`en`), French (`fr`), and Spanish (`es`). Each story is generated entirely in the selected language; fragments are never mixed across languages.

---

## Project structure

```
├── README.md
├── main.py                # CLI entry point
├── data/
│   └── fragments.json     # 9 hand-written literary fragments
├── output/                # Generated exports land here
└── src/
    ├── __init__.py
    ├── fragments.py       # Data models + JSON loader
    ├── generator.py       # Combination engine
    ├── markov.py          # Markov chain text generator (v0.2)
    ├── coherence.py       # Heuristic coherence scoring (v0.3)
    └── export.py          # JSON + Markdown export
```

---

## Requirements

- Python 3.11+
- Standard library only (no external dependencies)

---

## Quick start

```bash
# List all 27 story combinations
python main.py generate

# Print one random story as JSON
python main.py random

# Score every story for heuristic coherence
python main.py score

# Generate a Markov-chain candidate fragment
python main.py markov --layer opening
python main.py markov --layer middle --max-words 40
python main.py markov --layer ending

# Export all scored stories to JSON and Markdown
python main.py export

# Generate French or Spanish stories
python main.py random --language fr
python main.py score --language es
python main.py export --language fr
python main.py dashboard --language es
```

After `export`, check `output/stories.json` and `output/stories.md`.

---

## CLI reference

| Command                  | Description                                 |
| ------------------------ | ------------------------------------------- |
| `generate`               | List all 27 story combinations              |
| `random`                 | Print one random story as JSON              |
| `score`                  | Heuristic coherence score for all stories   |
| `markov --layer <layer>` | Generate a Markov-chain candidate text      |
| `export`                 | Write all scored stories to JSON + Markdown |

All commands accept `--language en|fr|es` (default: `en`). Language-specific exports are written as `output/stories.<language>.json` and `output/stories.<language>.md`.

## Quality dashboard

Create a self-contained HTML report for editorial review:

```bash
python main.py dashboard --language en
open output/quality-dashboard.en.html
```

The dashboard shows the score, word and sentence counts, repeated keywords, and a `ready`/`review` recommendation for all 27 combinations. Use it to prioritize human editorial review; it does not replace literary judgment.

## Fragment quality statistics

```bash
python main.py fragment-stats --language es
```

This shows the average score and number of combinations for each opening, middle, and ending fragment, helping you identify which source text most needs revision.

`markov` options:

| Flag          | Default      | Description                      |
| ------------- | ------------ | -------------------------------- |
| `--layer`     | _(required)_ | `opening`, `middle`, or `ending` |
| `--max-words` | `30`         | Maximum words to generate        |

---

## Output format

### Story object (JSON)

```json
{
  "id": "S001",
  "opening_id": "O01",
  "middle_id": "M01",
  "ending_id": "E01",
  "full_text": "The morning arrived without ceremony...",
  "score": 85,
  "issues": [
    "Repeated keyword: 'nothing'",
    "Tonally incompatible keywords: 'morning' and 'night'"
  ]
}
```

### Coherence score

Starts at **100** and deductions are applied:

| Issue                                  | Deduction      |
| -------------------------------------- | -------------- |
| Repeated keyword across fragments      | −5 per keyword |
| Tense mismatch (past + future markers) | −8             |
| Tonally incompatible word pairing      | −10            |
| Fragment length imbalance (>3× ratio)  | −5             |

---

## Version roadmap

| Version | Status     | Features                                                           |
| ------- | ---------- | ------------------------------------------------------------------ |
| v0.1    | ✅ Done    | Manual fragments, combination generator, JSON/Markdown export, CLI |
| v0.2    | ✅ Done    | Markov chain generator trained on existing fragments               |
| v0.3    | ✅ Done    | Heuristic coherence scoring with explanations                      |
| v0.4    | 🔜 Planned | Optional LLM-based evaluation, emotional tone classification       |
| v0.5    | 🔜 Planned | Print-layout planning file for physical book                       |

---

## Running the tests

```bash
# Install pytest (only external dependency, for testing)
pip install pytest

cd fragment-weaver
python -m pytest tests/ -v
```

---

## Fragments

The nine sample fragments in `data/fragments.json` are written with a literary tone.
They are intentionally **modular**: they avoid over-specific biographical facts so
every combination of opening + middle + ending remains coherent.

To add your own fragments, edit `data/fragments.json` and follow the existing schema:

```json
{
  "id": "O04",
  "layer": "opening",
  "text": {
    "en": "Your English fragment text here.",
    "fr": "Votre fragment français ici.",
    "es": "Tu fragmento en español aquí."
  },
  "tags": ["optional", "keywords"]
}
```

Valid `layer` values: `opening`, `middle`, `ending`.

A combinatorial storytelling engine for a future physical split-page book.

See [`fragment-weaver/README.md`](fragment-weaver/README.md) for full documentation.

## Quick start

```bash
cd fragment-weaver
python main.py generate
python main.py random
python main.py score
python main.py markov --layer opening
python main.py export
```
