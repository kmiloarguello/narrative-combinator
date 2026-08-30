"""Fragment Weaver — CLI entry point.

Usage examples::

    python main.py generate
    python main.py random
    python main.py score
    python main.py markov --layer opening
    python main.py markov --layer middle --max-words 40
    python main.py export
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure the project root is on sys.path so ``src`` is importable
sys.path.insert(0, str(Path(__file__).parent))

from src.coherence import score_story
from src.export import export_to_json, export_to_markdown, story_to_dict
from src.fragments import LAYERS, all_fragments_flat, load_fragments
from src.generator import generate_all_stories, generate_random_story
from src.markov import generate_text, train_on_layer
from src.dashboard import export_dashboard
from src.quality import analyze_story, fragment_score_stats

DATA_PATH = Path(__file__).parent / "data" / "fragments.json"
OUTPUT_DIR = Path(__file__).parent / "output"


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


def cmd_generate(args: argparse.Namespace) -> None:  # noqa: ARG001
    """Print all 27 story combinations."""
    fragments = load_fragments(DATA_PATH, args.language)
    stories = generate_all_stories(fragments, args.language)
    print(f"Generated {len(stories)} stories:\n")
    for story in stories:
        print(
            f"  {story.id}: {story.opening_id} + {story.middle_id} + {story.ending_id}"
        )


def cmd_random(args: argparse.Namespace) -> None:  # noqa: ARG001
    """Generate and print one random story as JSON."""
    fragments = load_fragments(DATA_PATH, args.language)
    story = generate_random_story(fragments, language=args.language)
    print(json.dumps(story_to_dict(story), indent=2, ensure_ascii=False))


def cmd_score(args: argparse.Namespace) -> None:  # noqa: ARG001
    """Score all 27 stories and print results."""
    fragments = load_fragments(DATA_PATH, args.language)
    flat = all_fragments_flat(fragments)
    stories = generate_all_stories(fragments, args.language)

    for story in stories:
        result = score_story(flat[story.opening_id], flat[story.middle_id], flat[story.ending_id], args.language)
        story.score = result.score
        story.issues = result.issues

    for story in stories:
        issue_str = f"  [{'; '.join(story.issues)}]" if story.issues else ""
        print(f"{story.id}: {story.score}/100{issue_str}")


def cmd_markov(args: argparse.Namespace) -> None:
    """Generate a Markov-chain candidate fragment for a given layer."""
    layer: str = args.layer
    if layer not in LAYERS:
        print(f"Error: --layer must be one of {LAYERS}", file=sys.stderr)
        sys.exit(1)

    fragments = load_fragments(DATA_PATH, args.language)
    texts = [f.text for f in fragments[layer]]

    if not texts:
        print(f"No fragments found for layer '{layer}'.", file=sys.stderr)
        sys.exit(1)

    chain = train_on_layer(texts)
    candidate = generate_text(chain, max_words=args.max_words)
    print(f"Markov candidate [{layer}]:\n\n{candidate}")


def cmd_export(args: argparse.Namespace) -> None:  # noqa: ARG001
    """Export all scored stories to JSON and Markdown."""
    fragments = load_fragments(DATA_PATH, args.language)
    flat = all_fragments_flat(fragments)
    stories = generate_all_stories(fragments, args.language)

    for story in stories:
        result = score_story(flat[story.opening_id], flat[story.middle_id], flat[story.ending_id], args.language)
        story.score = result.score
        story.issues = result.issues

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / f"stories.{args.language}.json"
    md_path = OUTPUT_DIR / f"stories.{args.language}.md"

    export_to_json(stories, json_path)
    export_to_markdown(stories, md_path)

    print(f"Exported {len(stories)} stories:")
    print(f"  JSON     → {json_path}")
    print(f"  Markdown → {md_path}")

def cmd_dashboard(args: argparse.Namespace) -> None:
    fragments = load_fragments(DATA_PATH, args.language)
    flat = all_fragments_flat(fragments)
    stories = generate_all_stories(fragments, args.language)
    path = OUTPUT_DIR / f"quality-dashboard.{args.language}.html"
    export_dashboard([analyze_story(story, flat, args.language) for story in stories], args.language, path)
    print(f"Exported quality dashboard → {path}")


def cmd_fragment_stats(args: argparse.Namespace) -> None:
    """Print average quality scores grouped by source fragment."""
    fragments = load_fragments(DATA_PATH, args.language)
    flat = all_fragments_flat(fragments)
    stories = generate_all_stories(fragments, args.language)
    qualities = [analyze_story(story, flat, args.language) for story in stories]
    print(json.dumps(fragment_score_stats(stories, qualities), indent=2))


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fragment-weaver",
        description="Fragment Weaver — combinatorial storytelling engine (v0.1–v0.3)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_language_option(command: argparse.ArgumentParser) -> None:
        command.add_argument(
            "--language", choices=("en", "fr", "es"), default="en",
            help="Story language (default: en)",
        )

    for name, help_text in (
        ("generate", "List all story combinations"),
        ("random", "Print one random story as JSON"),
        ("score", "Score all stories for heuristic coherence"),
        ("export", "Write all scored stories to JSON and Markdown"),
        ("dashboard", "Write an HTML quality dashboard"),
        ("fragment-stats", "Show average score by source fragment"),
    ):
        add_language_option(sub.add_parser(name, help=help_text))

    markov_p = sub.add_parser(
        "markov", help="Generate a Markov-chain candidate fragment"
    )
    markov_p.add_argument(
        "--layer",
        required=True,
        choices=LAYERS,
        help="Fragment layer to train on (opening | middle | ending)",
    )
    markov_p.add_argument(
        "--max-words",
        type=int,
        default=30,
        dest="max_words",
        help="Maximum words to generate (default: 30)",
    )
    add_language_option(markov_p)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "generate": cmd_generate,
        "random": cmd_random,
        "score": cmd_score,
        "markov": cmd_markov,
        "export": cmd_export,
        "dashboard": cmd_dashboard,
        "fragment-stats": cmd_fragment_stats,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
