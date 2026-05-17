#!/usr/bin/env python3
"""
uCode2 Binder CLI — `ucode2-binder` command-line tool.

Implements the Vault Processing Standards §5 (Tooling).

Usage:
  ucode2-binder init <topic> --name <name> [--description <desc>]
  ucode2-binder status <topic>
  ucode2-binder process <topic> --pass <name>
  ucode2-binder process <topic> --all
  ucode2-binder feed <topic>
  ucode2-binder import <dir> --topic <topic> [--name <name>]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Usync.binder.models import Binder, ProcessingPass
from Usync.binder.passes import run_all_passes, run_pass
from Usync.binder.parser import scan_binder_documents


# Default vault path
VAULT_PATH = Path.home() / "Vault"


def cmd_init(args: argparse.Namespace):
    """Create a new binder with skeleton structure."""
    topic = args.topic
    if not topic.startswith("#"):
        topic = f"#{topic}"
    
    name = args.name or topic.lstrip("#").title()
    description = args.description or f"{name} binder"
    
    binder = Binder.create(VAULT_PATH, topic, name, description)
    
    # Create a sample document
    sample_path = binder.binder_dir / "01-intro.md"
    sample_content = f"""---
title: "{name} Introduction"
type: guide
status: draft
binder: "{topic}"
tags: []
created: {binder.manifest.created}
updated: {binder.manifest.created}
---

# {name}

Welcome to the {name} binder. This is a sample document.

## Getting Started

Edit this file to add your content.
"""
    sample_path.write_text(sample_content)
    
    print(f"✅ Created binder '{topic}' at {binder.binder_dir}")
    print(f"   Name: {name}")
    print(f"   Description: {description}")
    print(f"   Manifest: {binder.manifest_path}")
    print(f"   Sample doc: {sample_path}")


def cmd_status(args: argparse.Namespace):
    """Show processing stats for a binder."""
    topic = args.topic
    if not topic.startswith("#"):
        topic = f"#{topic}"
    
    try:
        binder = Binder.load(VAULT_PATH, topic)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    
    # Scan documents
    binder.documents = scan_binder_documents(binder.binder_dir)
    
    # Gather stats
    total = len(binder.documents)
    missing_frontmatter = sum(1 for d in binder.documents if not d.frontmatter.title)
    missing_binder = sum(1 for d in binder.documents if not d.frontmatter.binder)
    missing_type = sum(1 for d in binder.documents if not d.frontmatter.type)
    missing_status = sum(1 for d in binder.documents if not d.frontmatter.status)
    
    # Check for duplicates
    from collections import Counter
    hash_counts = Counter(d.hash for d in binder.documents)
    duplicates = sum(1 for h, c in hash_counts.items() if c > 1)
    
    # Check links
    import re
    broken_links = 0
    for doc in binder.documents:
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", doc.raw_content)
        for text, link in links:
            if not link.startswith(("http://", "https://", "#")):
                link_target = link.split("#")[0]
                if link_target:
                    link_path = binder.binder_dir / link_target
                    if not link_path.exists():
                        broken_links += 1
    
    print(f"\n📊 Binder Status: {topic}")
    print(f"{'=' * 50}")
    print(f"  Name:        {binder.manifest.name}")
    print(f"  Description: {binder.manifest.description}")
    print(f"  Version:     {binder.manifest.version}")
    print(f"  Created:     {binder.manifest.created or 'N/A'}")
    print(f"  Maintainer:  {binder.manifest.maintainer or 'N/A'}")
    print()
    print(f"  Documents:       {total}")
    print(f"  Missing title:   {missing_frontmatter}")
    print(f"  Missing binder:  {missing_binder}")
    print(f"  Missing type:    {missing_type}")
    print(f"  Missing status:  {missing_status}")
    print(f"  Duplicates:      {duplicates}")
    print(f"  Broken links:    {broken_links}")
    print()
    
    # Show configured passes
    passes = binder.manifest.processing.passes
    print(f"  Configured passes ({len(passes)}):")
    for p in passes:
        print(f"    - {p.value}")
    
    # Overall health
    errors = missing_frontmatter + missing_binder + missing_type + missing_status + duplicates + broken_links
    if errors == 0:
        print(f"\n  ✅ Health: All clear — {total} documents, 0 errors")
    else:
        print(f"\n  ⚠️  Health: {errors} issues found")


def cmd_process(args: argparse.Namespace):
    """Run processing passes on a binder."""
    topic = args.topic
    if not topic.startswith("#"):
        topic = f"#{topic}"
    
    try:
        binder = Binder.load(VAULT_PATH, topic)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    
    # Scan documents
    binder.documents = scan_binder_documents(binder.binder_dir)
    
    if args.all:
        print(f"🔄 Running all configured passes on {topic}...")
        results = run_all_passes(binder, interactive=args.interactive)
        for result in results:
            _print_pass_result(result)
    elif args.pass_name:
        pass_name = args.pass_name
        try:
            pass_enum = ProcessingPass(pass_name)
        except ValueError:
            valid = ", ".join(p.value for p in ProcessingPass)
            print(f"❌ Unknown pass '{pass_name}'. Valid passes: {valid}")
            return
        
        print(f"🔄 Running pass '{pass_name}' on {topic}...")
        
        kwargs = {}
        if pass_enum == ProcessingPass.DEDUPLICATE:
            kwargs["interactive"] = args.interactive
        if pass_enum == ProcessingPass.FLATTEN:
            print("❌ 'flatten' pass requires a source directory. Use 'import' command instead.")
            return
        
        result = run_pass(binder, pass_enum, **kwargs)
        _print_pass_result(result)
    else:
        print("❌ Specify --pass <name> or --all")


def _print_pass_result(result: dict):
    """Print a processing pass result in a readable format."""
    pass_name = result.get("pass", "unknown")
    print(f"\n  📋 Pass: {pass_name}")
    
    if pass_name == "deduplicate":
        print(f"     Groups found: {result.get('groups_found', 0)}")
        print(f"     Total duplicates: {result.get('total_duplicates', 0)}")
        for group in result.get("groups", []):
            print(f"       Hash {group['hash']}: keeper={group['keeper']}")
            for dup in group.get("duplicates", []):
                print(f"         ⤷ {dup}")
    
    elif pass_name == "frontmatter-enrich":
        print(f"     Enriched: {result.get('enriched', 0)}")
        if result.get("error_count", 0) > 0:
            print(f"     Errors: {result['error_count']}")
            for err in result.get("errors", []):
                print(f"       ⚠️  {err['path']}: {', '.join(err['errors'])}")
    
    elif pass_name == "link-validate":
        print(f"     Valid links: {result.get('valid_links', 0)}")
        print(f"     Broken links: {result.get('broken_links', 0)}")
        for broken in result.get("broken", []):
            print(f"       🔗 {broken['source']} → '{broken['link']}' ({broken['text']})")
    
    elif pass_name == "generate-index":
        print(f"     Documents indexed: {result.get('documents_indexed', 0)}")
        print(f"     Search index: {result.get('search_index', 'N/A')}")
        print(f"     Feed path: {result.get('feed_path', 'N/A')}")
        print(f"     Feed items: {result.get('feed_items', 0)}")
    
    elif pass_name == "flatten":
        print(f"     Imported: {result.get('imported', 0)}")
        print(f"     Skipped: {result.get('skipped', 0)}")
        print(f"     Source: {result.get('source', 'N/A')}")
        print(f"     Destination: {result.get('destination', 'N/A')}")
    
    elif pass_name == "extract-bbc-basic":
        print(f"     Examples found: {result.get('examples_found', 0)}")
        if result.get("output"):
            print(f"     Output: {result['output']}")


def cmd_feed(args: argparse.Namespace):
    """Generate JSON feed for a binder."""
    topic = args.topic
    if not topic.startswith("#"):
        topic = f"#{topic}"
    
    try:
        binder = Binder.load(VAULT_PATH, topic)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    
    binder.documents = scan_binder_documents(binder.binder_dir)
    
    from Usync.binder.passes import _generate_json_feed
    feed = _generate_json_feed(binder)
    
    print(json.dumps(feed, indent=2))


def cmd_import(args: argparse.Namespace):
    """Import a flat directory into a binder."""
    source_dir = Path(args.dir).expanduser().resolve()
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return
    
    topic = args.topic
    if not topic.startswith("#"):
        topic = f"#{topic}"
    
    name = args.name or topic.lstrip("#").title()
    
    # Create binder if it doesn't exist
    binder_dir = VAULT_PATH / f"binder/{topic}"
    if binder_dir.exists():
        binder = Binder.load(VAULT_PATH, topic)
        print(f"📂 Using existing binder: {topic}")
    else:
        binder = Binder.create(VAULT_PATH, topic, name)
        print(f"📂 Created new binder: {topic}")
    
    # Run flatten pass
    from Usync.binder.passes import pass_flatten
    result = pass_flatten(binder, source_dir)
    
    print(f"\n✅ Import complete:")
    print(f"   Imported: {result['imported']} files")
    print(f"   Source: {result['source']}")
    print(f"   Destination: {result['destination']}")


def main():
    parser = argparse.ArgumentParser(
        description="uCode2 Binder — Vault Processing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ucode2-binder init "#udos" --name "uDos Core" --description "Core uDos architecture"
  ucode2-binder status "#udos"
  ucode2-binder process "#udos" --pass deduplicate --interactive
  ucode2-binder process "#udos" --pass frontmatter-enrich
  ucode2-binder process "#udos" --all
  ucode2-binder feed "#udos" > feed.json
  ucode2-binder import ~/Downloads/docs --topic "#tmp" --name "Temp Import"
        """,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # init
    init_parser = subparsers.add_parser("init", help="Create a new binder with skeleton")
    init_parser.add_argument("topic", help="Binder topic (e.g. '#udos')")
    init_parser.add_argument("--name", help="Human-readable name")
    init_parser.add_argument("--description", help="Binder description")
    
    # status
    status_parser = subparsers.add_parser("status", help="Show processing stats")
    status_parser.add_argument("topic", help="Binder topic (e.g. '#udos')")
    
    # process
    process_parser = subparsers.add_parser("process", help="Run processing passes")
    process_parser.add_argument("topic", help="Binder topic (e.g. '#udos')")
    process_parser.add_argument("--pass", dest="pass_name", help="Single pass to run")
    process_parser.add_argument("--all", action="store_true", help="Run all configured passes")
    process_parser.add_argument("--interactive", action="store_true", help="Interactive mode (for dedup)")
    
    # feed
    feed_parser = subparsers.add_parser("feed", help="Generate JSON feed")
    feed_parser.add_argument("topic", help="Binder topic (e.g. '#udos')")
    
    # import
    import_parser = subparsers.add_parser("import", help="Import flat directory into binder")
    import_parser.add_argument("dir", help="Source directory of markdown files")
    import_parser.add_argument("--topic", required=True, help="Target binder topic")
    import_parser.add_argument("--name", help="Binder name (optional)")
    
    args = parser.parse_args()
    
    commands = {
        "init": cmd_init,
        "status": cmd_status,
        "process": cmd_process,
        "feed": cmd_feed,
        "import": cmd_import,
    }
    
    commands[args.command](args)


if __name__ == "__main__":
    main()
