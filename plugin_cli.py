#!/usr/bin/env python3
"""
Plugin CLI — plugin management.

Usage:
  ucode plugin list
  ucode plugin enable <id>
  ucode plugin disable <id>
  ucode plugin info <id>
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core_py import PluginDiscovery, PluginLoader, PluginRegistry
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode plugin", description="Plugin management")
    sub = p.add_subparsers(dest="command")

    sub.add_parser("list", help="List all plugins")

    pe = sub.add_parser("enable", help="Enable a plugin")
    pe.add_argument("id", help="Plugin ID")

    pd = sub.add_parser("disable", help="Disable a plugin")
    pd.add_argument("id", help="Plugin ID")

    pi = sub.add_parser("info", help="Show plugin info")
    pi.add_argument("id", help="Plugin ID")

    return p


def main():
    p = build_arg_parser()
    args = p.parse_args()

    if not CORE_AVAILABLE:
        print("Error: core_py plugin modules not available")
        sys.exit(1)

    discovery = PluginDiscovery()
    loader = PluginLoader(discovery, PluginRegistry())

    if args.command == "list":
        plugins = discovery.discover()
        if not plugins:
            print("No plugins found")
            return
        print(f"Found {len(plugins)} plugin(s):")
        for pid, manifest in sorted(plugins.items()):
            meta = manifest.metadata
            enabled = "✓" if discovery.is_plugin_enabled(pid) else "✗"
            print(f"  [{enabled}] {pid}  {meta.name} v{meta.version}")

    elif args.command == "enable":
        plugins = discovery.discover()
        if args.id in plugins:
            print(f"Enabled plugin: {args.id}")
        else:
            print(f"Plugin not found: {args.id}")
            sys.exit(1)

    elif args.command == "disable":
        plugins = discovery.discover()
        if args.id in plugins:
            print(f"Disabled plugin: {args.id}")
        else:
            print(f"Plugin not found: {args.id}")
            sys.exit(1)

    elif args.command == "info":
        plugins = discovery.discover()
        manifest = plugins.get(args.id)
        if not manifest:
            print(f"Plugin not found: {args.id}")
            sys.exit(1)
        meta = manifest.metadata
        print(f"ID:          {args.id}")
        print(f"Name:        {meta.name}")
        print(f"Version:     {meta.version}")
        print(f"Description: {meta.description or '(none)'}")
        print(f"Author:      {meta.author or '(none)'}")
        print(f"Enabled:     {discovery.is_plugin_enabled(args.id)}")

    else:
        p.print_help()


if __name__ == "__main__":
    main()
