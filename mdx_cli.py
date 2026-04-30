#!/usr/bin/env python3
"""
uCode1 MDX CLI — MDX document processing with Snack shortcode execution.

Usage:
  mdx process <file> [--output <path>] [--snack-dir <dir>]
  mdx render  <file> [--output <path>] [--snack-dir <dir>]
  mdx list    <file> [--snack-dir <dir>]
  mdx help
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core_py.mdx import MDXProcessor, MDXRuntimeError, SnackResolutionError
    from core_py.snack import Snack
    CORE_AVAILABLE = True
except ImportError as e:
    CORE_AVAILABLE = False
    _import_error = str(e)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode mdx", description="MDX document processing")
    sub = p.add_subparsers(dest="command")

    pp = sub.add_parser("process", help="Process MDX → resolve & execute Snack shortcodes")
    pp.add_argument("file", help="Input .mdx file")
    pp.add_argument("--output", "-o", help="Output file (default: input path with .md extension)")
    pp.add_argument("--snack-dir", help="Directory containing .snack files")

    rp = sub.add_parser("render", help="Render MDX to final output (alias for process)")
    rp.add_argument("file", help="Input .mdx file")
    rp.add_argument("--output", "-o", help="Output file")
    rp.add_argument("--snack-dir", help="Directory containing .snack files")

    lp = sub.add_parser("list", help="List Snack shortcodes found in an MDX file")
    lp.add_argument("file", help="Input .mdx file")
    lp.add_argument("--snack-dir", help="Directory containing .snack files for resolution check")

    return p


def extract_shortcodes(content: str) -> list:
    """Extract all <Snack> shortcodes from MDX content without executing."""
    from core_py.mdx import SNACK_SHORTCODE_RE
    shortcodes = []
    for match in SNACK_SHORTCODE_RE.finditer(content):
        shortcodes.append({
            "id": match.group(1),
            "inputs": match.group(2),
            "output": match.group(3) or "text",
            "position": match.start(),
            "self_closing": content[match.end() - 2:match.end()] == "/>",
        })
    return shortcodes


def main():
    p = build_arg_parser()
    args = p.parse_args()

    if not CORE_AVAILABLE:
        print(f"Error: core_py.mdx not available: {_import_error}")
        sys.exit(1)

    if not args.command:
        p.print_help()
        return

    if not os.path.exists(args.file):
        print(f"Error: file not found: {args.file}")
        sys.exit(1)

    with open(args.file) as f:
        content = f.read()

    if args.command == "list":
        shortcodes = extract_shortcodes(content)
        if not shortcodes:
            print(f"No <Snack> shortcodes found in {args.file}")
            return

        print(f"Found {len(shortcodes)} Snack shortcode(s) in {args.file}:")
        print()
        for sc in shortcodes:
            print(f"  🍿 <Snack id=\"{sc['id']}\"", end="")
            if sc["inputs"]:
                print(f" inputs='{sc['inputs']}'", end="")
            if sc["output"] != "text":
                print(f" output=\"{sc['output']}\"", end="")
            print(" />" if sc["self_closing"] else ">")

        # Check resolution if snack-dir provided
        if args.snack_dir and os.path.isdir(args.snack_dir):
            proc = MDXProcessor(snack_dir=args.snack_dir)
            proc.load_from_directory()
            print()
            for sc in shortcodes:
                if sc["id"] in proc.snack_registry:
                    snack = proc.snack_registry[sc["id"]]
                    print(f"     ✅ Resolves to: {snack.name} ({snack.runtime})")
                else:
                    print(f"     ❌ Not found in registry")

    elif args.command in ("process", "render"):
        proc = MDXProcessor(snack_dir=args.snack_dir)

        # Load snacks if directory specified
        if args.snack_dir:
            if not os.path.isdir(args.snack_dir):
                print(f"Warning: snack dir not found: {args.snack_dir}")
            else:
                count = proc.load_from_directory(args.snack_dir)
                print(f"📦 Loaded {count} snack(s) from {args.snack_dir}")

        # List shortcodes found
        shortcodes = extract_shortcodes(content)
        if shortcodes:
            print(f"🍿 Found {len(shortcodes)} Snack shortcode(s)")

        # Process
        try:
            output_path = args.output or args.file.replace(".mdx", ".md")
            result = proc.process_file(args.file, output_path)
            print(f"✅ Processed → {output_path}")
        except SnackResolutionError as e:
            print(f"❌ {e}")
            print("   Tip: Use --snack-dir to point to .snack files")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    else:
        p.print_help()


if __name__ == "__main__":
    main()
