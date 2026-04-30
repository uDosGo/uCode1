#!/usr/bin/env python3
"""
Feed CLI — Feed event archiving to Cells.

Usage:
  ucode feed archive <file> [--band <band>]
  ucode feed list [--band <band>] [--type <type>] [--limit <n>]
  ucode feed report [--band <band>]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core_py.cell import CellStore
    from core_py.feed import (
        FEED_BAND,
        archive_feed_entries,
        archive_feed_file,
        generate_feed_report,
        search_feed_cells,
    )
    CORE_AVAILABLE = True
except ImportError as e:
    CORE_AVAILABLE = False
    _import_error = str(e)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode feed", description="Feed event archiving")
    sub = p.add_subparsers(dest="command")

    ap = sub.add_parser("archive", help="Archive feed entries as Cells")
    ap.add_argument("file", help="JSONL feed file path")
    ap.add_argument("--band", type=int, default=FEED_BAND, help=f"Layer band (default: {FEED_BAND})")

    lp = sub.add_parser("list", help="List archived feed cells")
    lp.add_argument("--band", type=int, default=FEED_BAND, help="Layer band")
    lp.add_argument("--type", help="Filter by event type")
    lp.add_argument("--limit", type=int, default=100, help="Max results")

    rp = sub.add_parser("report", help="Generate feed archive report")
    rp.add_argument("--band", type=int, default=FEED_BAND, help="Layer band")

    return p


def main():
    p = build_arg_parser()
    args = p.parse_args()

    if not CORE_AVAILABLE:
        print(f"Error: core_py.feed not available: {_import_error}")
        sys.exit(1)

    store = CellStore()

    if args.command == "archive":
        if not os.path.isfile(args.file):
            print(f"❌ File not found: {args.file}")
            sys.exit(1)

        count, addresses = archive_feed_file(args.file, store, band=args.band)
        print(f"✅ Archived {count} feed event(s) as Cells")
        if addresses:
            print(f"   Band: L{args.band:03d}")
            print(f"   First cell: {addresses[0]}")
            print(f"   Last cell:  {addresses[-1]}")

    elif args.command == "list":
        results = search_feed_cells(
            store=store, band=args.band,
            event_type=getattr(args, 'type', None),
            limit=args.limit,
        )
        if not results:
            print("No archived feed cells found.")
            return

        print(f"Archived feed cells ({len(results)}):")
        for r in results:
            ts = r.get("timestamp", "?")[:19]
            mark = "✅" if r["verified"] else "⚠️"
            print(f"  {mark} [{r['event_type']:15s}] {ts}  {r['detail'][:60]}")
            print(f"       {r['address']}")

    elif args.command == "report":
        report = generate_feed_report(store=store, band=args.band)
        print(f"📊 Feed Archive Report (band L{report['band']:03d})")
        print(f"   Total cells: {report['total_cells']}")
        print(f"   Verified:    {'✅' if report['verified'] else '⚠️ partial'}")
        if report["earliest"]:
            print(f"   Earliest:    {report['earliest'][:19]}")
            print(f"   Latest:      {report['latest'][:19]}")
        print(f"\n   Event types:")
        for et, count in sorted(report["event_types"].items()):
            print(f"     {et:20s}  {count} cell(s)")

    else:
        p.print_help()


if __name__ == "__main__":
    main()
