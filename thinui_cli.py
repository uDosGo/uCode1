#!/usr/bin/env python3
"""
ThinUI CLI — ThinUI bridge operations.

Usage:
  ucode thinui parse <text> [--title <title>]
  ucode thinui render [--file <grid.txt> | --text <ascii>]
  ucode thinui themes
  ucode thinui api [--port <port>]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core_py.thinui import ThinUIGridBridge
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode thinui", description="ThinUI bridge operations")
    sub = p.add_subparsers(dest="command")

    tp = sub.add_parser("parse", help="Parse ASCII grid to ThinUI format")
    tp.add_argument("--text", help="ASCII grid text")
    tp.add_argument("--file", help="Read grid from file")
    tp.add_argument("--title", default="ThinUI Grid")

    tr = sub.add_parser("render", help="Render grid via ThinUI bridge")
    tr.add_argument("--file", help="Grid file")
    tr.add_argument("--text", help="ASCII grid text")

    tt = sub.add_parser("themes", help="List available themes")

    ta = sub.add_parser("api", help="Start ThinUI API server")
    ta.add_argument("--port", type=int, default=4687, help="Port to listen on")

    return p


def main():
    p = build_arg_parser()
    args = p.parse_args()

    if not CORE_AVAILABLE:
        print("Error: core_py.thinui not available")
        sys.exit(1)

    if args.command == "parse":
        bridge = ThinUIGridBridge()
        text = args.text
        if args.file:
            with open(args.file) as f:
                text = f.read()
        if not text:
            print("Error: provide --text or --file")
            sys.exit(1)
        data = bridge.parse_to_thinui(text, title=args.title)
        print(json.dumps(data.to_dict(), indent=2))

    elif args.command == "render":
        bridge = ThinUIGridBridge()
        text = args.text
        if args.file:
            with open(args.file) as f:
                text = f.read()
        if not text:
            print("Error: provide --text or --file")
            sys.exit(1)
        data = bridge.parse_to_thinui(text)
        print(json.dumps(data.to_dict(), indent=2))

    elif args.command == "themes":
        print("Available ThinUI themes:")
        print("  • bbcbasic  - BBC BASIC / C64 terminal")
        print("  • nesdash   - NES.css dashboard")
        print("  • retro     - Retro mix")
        print("  • ceefax    - Teletext viewer")

    elif args.command == "api":
        from core_py.thinui.api import run_api_server
        print(f"Starting ThinUI API server on port {args.port}...")
        run_api_server(host="127.0.0.1", port=args.port)

    else:
        p.print_help()


if __name__ == "__main__":
    main()
