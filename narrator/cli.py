"""
Narrator & Lexicon CLI — Story generation, term mapping, and character system.

Usage:
  ucode narrator story <type> [--title <title>] [--detail <detail>]
  ucode narrator feed <path>
  ucode narrator to-md <path>
  ucode lexicon list [--lane <lane>] [--tag <tag>]
  ucode lexicon show <term>
  ucode lexicon search <query>
  ucode lexicon translate <term> --lane <lane>
  ucode character list [--range <range>]
  ucode character show <slot>
  ucode character render <slots> [--priority <p>]
  ucode character assign <slot> --term <term>
  ucode character alias <slot> <alias>
  ucode character emoji <slot> <emoji>
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
    from narrator.character import (
        CharacterSystem, SlotEntry, ansi_char, slot_range_name,
        SLOT_COMMAND_START, SLOT_COMMAND_END,
        SLOT_SNACK_START, SLOT_SNACK_END,
        SLOT_ALIAS_START, SLOT_ALIAS_END, SLOT_TOTAL,
    )
else:
    from .narrator import NarratorEngine
    from .lexicon import Lexicon, LANE_DEV, LANE_STORY, LANE_STUDENT
    from .character import (
        CharacterSystem, SlotEntry, ansi_char, slot_range_name,
        SLOT_COMMAND_START, SLOT_COMMAND_END,
        SLOT_SNACK_START, SLOT_SNACK_END,
        SLOT_ALIAS_START, SLOT_ALIAS_END, SLOT_TOTAL,
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode narrator", description="Story generation")
    sub = p.add_subparsers(dest="command")

    story_p = sub.add_parser("story", help="Generate a story entry")
    story_p.add_argument("type", help="Event type (vault_init, note_create, snack_run, etc.)")
    story_p.add_argument("--title", help="Title or detail for the event")
    story_p.add_argument("--detail", help="Additional detail")
    story_p.add_argument("--format", choices=["text", "markdown", "ceefax"], default="text")

    feed_p = sub.add_parser("feed", help="Process a feed file into stories")
    feed_p.add_argument("path", help="Path to JSONL feed file")
    feed_p.add_argument("--format", choices=["text", "markdown", "json"], default="text")

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


def build_character_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode character",
                                description="128-slot character system with emoji/alias overlays")
    sub = p.add_subparsers(dest="command")

    list_p = sub.add_parser("list", help="List assigned character slots")
    list_p.add_argument("--range", choices=["command", "snack", "reserved", "alias"],
                        help="Filter by slot range")

    show_p = sub.add_parser("show", help="Show a specific slot")
    show_p.add_argument("slot", type=int, help="Slot number (0-127)")

    render_p = sub.add_parser("render", help="Render a line of slots")
    render_p.add_argument("slots", help="Comma-separated slot numbers, or expression like '0-4,32'")
    render_p.add_argument("--priority", choices=["emoji", "word", "teletext", "ansi"],
                          default="emoji", help="Rendering priority")

    assign_p = sub.add_parser("assign", help="Assign a term to a slot")
    assign_p.add_argument("slot", type=int, help="Slot number (0-127)")
    assign_p.add_argument("--term", required=True, help="Lexicon term ID")

    alias_p = sub.add_parser("alias", help="Set a word alias for a slot")
    alias_p.add_argument("slot", type=int, help="Slot number (0-127)")
    alias_p.add_argument("alias", help="Word alias")

    emoji_p = sub.add_parser("emoji", help="Set an emoji overlay for a slot")
    emoji_p.add_argument("slot", type=int, help="Slot number (0-127)")
    emoji_p.add_argument("emoji", help="Emoji character(s)")

    return p


def parse_slot_expr(expr: str) -> list[int]:
    """Parse a slot expression like '0-4,32,35-37' into a list of slot numbers."""
    slots = []
    for part in expr.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            slots.extend(range(int(a.strip()), int(b.strip()) + 1))
        else:
            slots.append(int(part))
    return slots


def main():
    # Detect narrator vs lexicon vs character subcommand
    if len(sys.argv) > 1:
        if sys.argv[1] == "lexicon":
            run_lexicon()
            return
        if sys.argv[1] == "character":
            run_character()
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

    sys.exit(0)


def run_character():
    parser = build_character_parser()
    args = parser.parse_args(sys.argv[2:])
    cs = CharacterSystem()

    if args.command == "list":
        entries = cs.list_slots(range_name=getattr(args, 'range', None))
        if not entries:
            print("No slots assigned.")
            return
        print(f"Character System ({len(entries)}/{SLOT_TOTAL} slots assigned):")
        print()
        for e in entries:
            rendered = e.render("emoji")
            print(f"  [{e.slot:3d}] {e.range_name:8s}  {rendered:4s}  {e.label or e.term_id}")
            if e.word_alias and e.word_alias != e.term_id:
                print(f"         alias: {e.word_alias}")

    elif args.command == "show":
        entry = cs.get(args.slot)
        if not entry:
            print(f"Slot {args.slot} is unassigned.")
            print(f"  ANSI char: {ansi_char(args.slot)}")
            print(f"  Range:     {slot_range_name(args.slot)}")
            return
        print(f"Slot:        {entry.slot}")
        print(f"Range:       {entry.range_name}")
        print(f"Term:        {entry.term_id}")
        print(f"Label:       {entry.label}")
        print(f"ANSI char:   {entry.ansi_char}")
        print(f"Emoji:       {entry.emoji or '(none)'}")
        print(f"Word alias:  {entry.word_alias or '(none)'}")
        print(f"Description: {entry.description}")
        print(f"\nRendered at each priority:")
        for p in ["emoji", "word", "teletext", "ansi"]:
            print(f"  {p:10s}: {entry.render(p)}")

    elif args.command == "render":
        slots = parse_slot_expr(args.slots)
        rendered = cs.render_line(slots, priority=args.priority)
        print(rendered)

    elif args.command == "assign":
        entry = SlotEntry(slot=args.slot, term_id=args.term, label=args.term)
        cs.assign(entry)
        print(f"✅ Assigned term '{args.term}' to slot {args.slot}")

    elif args.command == "alias":
        cs.assign_alias(args.slot, args.alias)
        print(f"✅ Set alias '{args.alias}' for slot {args.slot}")

    elif args.command == "emoji":
        cs.assign_emoji(args.slot, args.emoji)
        print(f"✅ Set emoji '{args.emoji}' for slot {args.slot}")

    else:
        parser.print_help()
        return

    sys.exit(0)


if __name__ == "__main__":
    main()
