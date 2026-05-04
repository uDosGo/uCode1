#!/usr/bin/env python3
"""
Vault CLI — vault file operations.

Usage:
  ucode vault list [<path>]
  ucode vault read <path>
  ucode vault write <path> <content>
  ucode vault search <query>
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode vault", description="Vault file operations")
    sub = p.add_subparsers(dest="command")

    vl = sub.add_parser("list", help="List vault contents")
    vl.add_argument("path", nargs="?", default="/", help="Vault path")

    vr = sub.add_parser("read", help="Read vault file")
    vr.add_argument("path", help="File path")

    vw = sub.add_parser("write", help="Write vault file")
    vw.add_argument("path", help="File path")
    vw.add_argument("content", help="Content to write")

    vs = sub.add_parser("search", help="Search vault")
    vs.add_argument("query", help="Search query")

    return p


def main():
    p = build_arg_parser()
    args = p.parse_args()

    vault_base = os.path.expanduser("$UDOS_VAULT")

    if args.command == "list":
        target = os.path.join(vault_base, args.path.lstrip("/"))
        if not os.path.exists(target):
            print(f"Path not found: {target}")
            sys.exit(1)
        for entry in sorted(os.listdir(target)):
            full = os.path.join(target, entry)
            kind = "d" if os.path.isdir(full) else "f"
            print(f"  [{kind}] {entry}")

    elif args.command == "read":
        target = os.path.join(vault_base, args.path.lstrip("/"))
        if not os.path.isfile(target):
            print(f"File not found: {target}")
            sys.exit(1)
        with open(target) as f:
            print(f.read(), end="")

    elif args.command == "write":
        target = os.path.join(vault_base, args.path.lstrip("/"))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w") as f:
            f.write(args.content)
        print(f"Written {len(args.content)} bytes to {args.path}")

    elif args.command == "search":
        target = os.path.expanduser("$UDOS_VAULT")
        results = []
        for root, dirs, files in os.walk(target):
            for f in files:
                if args.query.lower() in f.lower():
                    rel = os.path.relpath(os.path.join(root, f), target)
                    results.append(rel)
        for r in results[:50]:
            print(f"  {r}")

    else:
        p.print_help()


if __name__ == "__main__":
    main()
