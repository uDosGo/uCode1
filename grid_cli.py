#!/usr/bin/env python3
"""
Grid CLI — ASCII grid operations.

Usage:
  ucode grid parse [--text <ascii> | --file <path>] [--title <title>]
  ucode grid render <file> [--title <title>]
  ucode grid interactive <file>
  ucode grid to-usxd <file> --output <path>
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core_py.usxd import ASCIIGridParser, GridFormat
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode grid", description="ASCII grid operations")
    sub = p.add_subparsers(dest="command")

    gp = sub.add_parser("parse", help="Parse ASCII grid text")
    gp.add_argument("--text", help="ASCII grid text to parse")
    gp.add_argument("--file", help="Read grid from file")
    gp.add_argument("--title", default="Untitled", help="Grid title")
    gp.add_argument("--format", choices=["simple", "box", "markdown", "csv", "teletext"],
                    help="Force grid format (auto-detected if omitted)")

    gr = sub.add_parser("render", help="Render grid to terminal")
    gr.add_argument("file", help="Grid file to render")
    gr.add_argument("--title", default="Grid", help="Grid title")

    gi = sub.add_parser("interactive", help="Run interactive grid viewer")
    gi.add_argument("file", nargs="?", help="Grid file to load")

    gu = sub.add_parser("to-usxd", help="Convert grid to USXD document")
    gu.add_argument("file", help="Grid file")
    gu.add_argument("--output", "-o", required=True, help="Output USXD file")

    return p


def main():
    p = build_arg_parser()
    args = p.parse_args()

    if not CORE_AVAILABLE:
        print("Error: core_py modules not available")
        sys.exit(1)

    parser = ASCIIGridParser()

    if args.command == "parse":
        text = args.text
        if args.file:
            with open(args.file) as f:
                text = f.read()
        if not text:
            print("Error: provide --text or --file")
            sys.exit(1)
        parsed = parser.parse_grid(text, title=args.title)
        print(f"Parsed grid: {parsed.rows}×{parsed.cols}")
        print(f"Format: {parsed.format or 'auto-detected'}")
        print(f"Cells: {parsed.rows * parsed.cols}")
        print(parsed.to_ascii())

    elif args.command == "render":
        if not os.path.exists(args.file):
            print(f"Error: file not found: {args.file}")
            sys.exit(1)
        with open(args.file) as f:
            text = f.read()
        parsed = parser.parse_grid(text, title=args.title)
        print(parsed.to_ascii())
        print(f"\n--- {parsed.title} ({parsed.rows}×{parsed.cols}) ---")

    elif args.command == "interactive":
        from core_py.usxd import GridRenderer
        renderer = GridRenderer()
        text = ""
        if args.file and os.path.exists(args.file):
            with open(args.file) as f:
                text = f.read()
        if text:
            parsed = parser.parse_grid(text)
        else:
            parsed = parser.parse_grid("Hello\nWorld", title="Interactive")
        print("Grid interactive mode (basic display)")
        print(renderer.render_simple(parsed))

    elif args.command == "to-usxd":
        from core_py.usxd import USXDDocument, USXDMetadata
        with open(args.file) as f:
            text = f.read()
        parsed = parser.parse_grid(text)
        doc = USXDDocument(
            metadata=USXDMetadata(
                id=f"grid-{os.path.basename(args.file)}",
                title=parsed.title,
                version="1.0.0",
            ),
            sections=[],
        )
        from core_py.usxd import USXDSection
        doc.add_section(USXDSection(
            name="grid",
            section_type="grid",
            content=parsed.to_dict(),
        ))
        doc.save_to_file(args.output)
        print(f"Saved USXD document to {args.output}")

    else:
        p.print_help()


if __name__ == "__main__":
    main()
