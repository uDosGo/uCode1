#!/usr/bin/env python3
"""
Liquid CLI — template rendering for uCode1.

Usage:
    ucode liquid render <template> [--data KEY=VAL ...]
    ucode liquid render-file <name> [--data KEY=VAL ...]
    ucode liquid list
    ucode liquid render-snack <template> <snack-name>
    ucode liquid render-binder <template> <binder-name>
"""

import argparse
import json
import sys
import os

# Add parent dir so we can import core_py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_py.liquid_engine import LiquidEngine, TemplateRegistry


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucode liquid",
        description="Liquid template rendering for uCode1",
    )
    sub = parser.add_subparsers(dest="command", help="Sub-command")

    # render
    render_p = sub.add_parser("render", help="Render a Liquid template string")
    render_p.add_argument("template", help="Liquid template string (inline)")
    render_p.add_argument("--data", "-d", action="append", default=[],
                          help="Data as KEY=VAL pairs (can repeat)")

    # render-file
    rf_p = sub.add_parser("render-file", help="Render a template file")
    rf_p.add_argument("name", help="Template name (without .liquid)")
    rf_p.add_argument("--data", "-d", action="append", default=[],
                      help="Data as KEY=VAL pairs (can repeat)")

    # list
    list_p = sub.add_parser("list", help="List available templates")
    list_p.add_argument("--json", action="store_true",
                        help="Output as JSON")

    # render-snack
    rs_p = sub.add_parser("render-snack",
                          help="Render template with snack data")
    rs_p.add_argument("template", help="Liquid template string")
    rs_p.add_argument("snack_name", help="Name of the snack")

    # render-binder
    rb_p = sub.add_parser("render-binder",
                          help="Render template with binder data")
    rb_p.add_argument("template", help="Liquid template string")
    rb_p.add_argument("binder_name", help="Name of the binder")

    return parser


def parse_data_args(args: list[str]) -> dict:
    """Parse --data KEY=VAL arguments into a dict."""
    data = {}
    for arg in args:
        if "=" not in arg:
            print(f"Warning: ignoring malformed data arg: {arg}", file=sys.stderr)
            continue
        key, val = arg.split("=", 1)
        # Try to parse as JSON for complex values
        try:
            val = json.loads(val)
        except (json.JSONDecodeError, ValueError):
            pass  # Keep as string
        data[key] = val
    return data


def cmd_render(args: argparse.Namespace) -> int:
    """Render an inline Liquid template."""
    engine = LiquidEngine()
    data = parse_data_args(args.data)
    try:
        result = engine.render(args.template, data)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_render_file(args: argparse.Namespace) -> int:
    """Render a template file."""
    engine = LiquidEngine()
    data = parse_data_args(args.data)
    try:
        result = engine.render_file(args.name + ".liquid", data)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """List available templates."""
    registry = TemplateRegistry()
    templates = registry.list_templates()
    if args.json:
        print(json.dumps(templates, indent=2))
    else:
        if not templates:
            print("No templates found.")
            print("Create .liquid files in ~/.udos/templates/ or ./templates/")
            return 0
        print(f"{'Name':<20} {'Size':>8}  Path")
        print(f"{'─'*20} {'─'*8}  {'─'*40}")
        for t in templates:
            print(f"{t['name']:<20} {t['size']:>8}  {t['path']}")
    return 0


def cmd_render_snack(args: argparse.Namespace) -> int:
    """Render template with snack data."""
    engine = LiquidEngine()
    # Build mock snack data for now
    snack_data = {
        "name": args.snack_name,
        "output": f"<output from {args.snack_name}>",
        "status": "success",
        "duration": 0.0,
        "metadata": {},
    }
    try:
        result = engine.render_snack(args.template, snack_data)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_render_binder(args: argparse.Namespace) -> int:
    """Render template with binder data."""
    engine = LiquidEngine()
    # Build mock binder data for now
    binder_data = {
        "name": args.binder_name,
        "state": {},
        "variables": {},
    }
    try:
        result = engine.render_binder(args.template, binder_data)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "render": cmd_render,
        "render-file": cmd_render_file,
        "list": cmd_list,
        "render-snack": cmd_render_snack,
        "render-binder": cmd_render_binder,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
