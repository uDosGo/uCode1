"""
Narrator & Lexicon CLI — Story generation and term mapping.

Usage:
  ucode narrator story <type> [--title <title>] [--detail <detail>]
  ucode narrator feed <path>
  ucode narrator to-md <path>
  ucode lexicon list [--lane <lane>] [--tag <tag>]
  ucode lexicon show <term>
  ucode lexicon search <query>
  ucode lexicon translate <term> --lane <lane>
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent dir for direct execution
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from narrator.narrator import NarratorEngine
    from narrator.lexicon import Lexicon, LANE_DEV, LANE_STORY, LANE_STUDENT
else:
    from .narrator import NarratorEngine
    from .lexicon import Lexicon, LANE_DEV, LANE_STORY, LANE_STUDENT


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode narrator", description="Story generation")
    sub = p.add_subparsers(dest="command")

    # narrator story
    story_p = sub.add_parser("story", help="Generate a story entry")
    story_p.add_argument("type", help="Event type (vault_init, note_create, snack_run, etc.)")
    story_p.add_argument("--title", help="Title or detail for the event")
    story_p.add_argument("--detail", help="Additional detail")
    story_p.add_argument("--format", choices=["text", "markdown", "ceefax"], default="text")

    # narrator feed
    feed_p = sub.add_parser("feed", help="Process a feed file into stories")
    feed_p.add_argument("path", help="Path to JSONL feed file")
    feed_p.add_argument("--format", choices=["text", "markdown", "json"], default="text")

    # narrator to-md
    md_p = sub.add_parser("to-md", help="Convert story JSON to markdown")
    md_p.add_argument("path", help="Path to story JSON file")
    md_p.add_argument("--output", "-o", help="Output markdown file")

    return p


def build_lexicon_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode lexicon", description="Term mapping (Lexicon)")
    sub = p.add_subparsers(dest="command")

    list_p = sub.add_parser("list", help="List all lexicon terms")
    list_p.add_argument("--lane", choices=[LANE_DEV, LANE_STORY, LANE_STUDENT], help="Filter by lane")
    list_p.add_argument("--tag", help="Filter by tag")

    show_p = sub.add_parser("show", help="Show a specific term")
    show_p.add_argument("term", help="Term ID")

    search_p = sub.add_parser("search", help="Search lexicon")
    search_p.add_argument("query", help="Search query")

    trans_p = sub.add_parser("translate", help="Translate a term into a lane")
    trans_p.add_argument("term", help="Term ID")
    trans_p.add_argument("--lane", required=True, choices=[LANE_DEV, LANE_STORY, LANE_STUDENT],
                         help="Target lane")

    return p


def main():
    # Detect narrator vs lexicon subcommand
    if len(sys.argv) > 1 and sys.argv[1] == "lexicon":
        run_lexicon()
        return

    parser = build_parser()
    args = parser.parse_args()
    engine = NarratorEngine()

    if args.command == "story":
        story = engine.generate_story(
            args.type,
            title=args.title or "Untitled",
            detail=args.detail or "",
        )
        if args.format == "markdown":
            print(engine.story_to_markdown(story))
        elif args.format == "ceefax":
            print(engine.story_to_ceefax(story))
        else:
            print(story["content"])

    elif args.command == "feed":
        stories = engine.process_feed_file(args.path)
        if args.format == "json":
            print(json.dumps(stories, indent=2))
        elif args.format == "markdown":
            for s in stories:
                print(engine.story_to_markdown(s))
                print()
        else:
            for s in stories:
                print(f"[{s['event']}] {s['content']}")
        print(f"\nProcessed {len(stories)} stories from {args.path}")

    elif args.command == "to-md":
        try:
            with open(args.path) as f:
                data = json.load(f)
            if isinstance(data, dict):
                stories = [data]
            else:
                stories = data
            output = "\n\n".join(engine.story_to_markdown(s) for s in stories)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(output)
                print(f"Written {len(stories)} stories to {args.output}")
            else:
                print(output)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error: {e}")
            sys.exit(1)

    else:
        parser.print_help()


def run_lexicon():
    parser = build_lexicon_parser()
    args = parser.parse_args(sys.argv[2:])
    lex = Lexicon()

    if args.command == "list":
        terms = lex.list_terms(lane=getattr(args, 'lane', None), tag=getattr(args, 'tag', None))
        if not terms:
            print("No terms found.")
            return
        print(f"Lexicon ({len(terms)} terms):")
        for t in terms:
            print(f"  {t.emoji} {t.term_id}")
            print(f"      Dev:     {t.dev}")
            print(f"      Story:   {t.story}")
            print(f"      Student: {t.student}")
            print()

    elif args.command == "show":
        entry = lex.get(args.term)
        if not entry:
            print(f"Term not found: {args.term}")
            sys.exit(1)
        print(f"Term:        {entry.term_id}")
        print(f"Dev:         {entry.dev}")
        print(f"Story:       {entry.story}")
        print(f"Student:     {entry.student}")
        print(f"Emoji:       {entry.emoji}")
        print(f"Description: {entry.description}")
        if entry.tags:
            print(f"Tags:        {', '.join(entry.tags)}")

    elif args.command == "search":
        results = lex.search(args.query)
        if not results:
            print(f"No results for '{args.query}'")
            return
        print(f"Found {len(results)} term(s) for '{args.query}':")
        for t in results:
            print(f"  {t.emoji} {t.term_id}: {t.dev} / {t.story} / {t.student}")

    elif args.command == "translate":
        translated = lex.translate(args.term, args.lane)
        print(translated)

    else:
        parser.print_help()
        return

    # Exit cleanly after lexicon runs so narrator doesn't also fire
    sys.exit(0)


if __name__ == "__main__":
    main()
