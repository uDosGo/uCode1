#!/usr/bin/env python3
"""
Vault Scanner — uDos Vault Indexing & Consolidation Tool

Uses the .compost system and feed spool to:
  1. Scan all Vault docs and build a content index
  2. Extract locked specs (latest versions)
  3. Identify duplicates and redundant content
  4. Archive old versions to .compost/ (elastic trash)
  5. Generate a consolidated index

Usage:
  python vault-scanner.py scan          # Full scan + index
  python vault-scanner.py index         # Just rebuild index
  python vault-scanner.py dedup         # Find duplicates
  python vault-scanner.py archive       # Archive old versions to .compost/
  python vault-scanner.py report        # Generate consolidation report
  python vault-scanner.py feed          # Write scan results to feed spool
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ─── Configuration ───────────────────────────────────────────────────────────

VAULT_PATH = Path(os.path.expanduser("~/Vault"))
COMPOST_PATH = VAULT_PATH / ".compost"
LEGACY_PATH = VAULT_PATH / ".legacy"
FEED_SPOOL_PATH = Path(os.path.expanduser("~/.local/spool/feed"))
INDEX_PATH = VAULT_PATH / ".vault-index.json"
REPORT_PATH = VAULT_PATH / ".vault-consolidation-report.json"

# File types to scan
SCAN_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".rs", ".ts", ".js", ".swift"}

# Directories to skip
SKIP_DIRS = {".git", ".compost", ".legacy", ".vibe", ".udx", ".idea", "node_modules", "__pycache__", ".state"}


# ─── Feed System ─────────────────────────────────────────────────────────────

def write_feed_entry(project: str, source: str, level: str, message: str, data: Optional[Dict] = None):
    """Write a feed entry to the spool directory."""
    FEED_SPOOL_PATH.mkdir(parents=True, exist_ok=True)
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": project,
        "source": source,
        "level": level,
        "message": message,
        "data": data or {},
        "metadata": {
            "version": "1.0",
            "environment": "development"
        }
    }
    filename = f"{entry['id']}.json"
    filepath = FEED_SPOOL_PATH / filename
    with open(filepath, "w") as f:
        json.dump(entry, f, indent=2)
    return entry


# ─── Compost System ──────────────────────────────────────────────────────────

def ensure_compost_dirs():
    """Create .compost directory structure if it doesn't exist."""
    dirs = [
        COMPOST_PATH / "archive",
        COMPOST_PATH / "duplicates",
        COMPOST_PATH / "old-versions",
        COMPOST_PATH / "redundant",
        COMPOST_PATH / "index",
        LEGACY_PATH,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def archive_to_compost(filepath: Path, category: str = "archive") -> Path:
    """Move a file to the .compost/ directory (elastic trash)."""
    ensure_compost_dirs()
    dest_dir = COMPOST_PATH / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Preserve relative path structure
    rel_path = filepath.relative_to(VAULT_PATH)
    dest_path = dest_dir / rel_path
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add timestamp to avoid collisions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_path = dest_path.with_name(f"{dest_path.stem}_{timestamp}{dest_path.suffix}")
    
    shutil.move(str(filepath), str(dest_path))
    return dest_path


# ─── File Scanner ────────────────────────────────────────────────────────────

def scan_vault() -> List[Dict]:
    """Scan all files in the Vault and return metadata."""
    files = []
    for root, dirs, filenames in os.walk(VAULT_PATH):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for filename in filenames:
            filepath = Path(root) / filename
            ext = filepath.suffix.lower()
            
            if ext not in SCAN_EXTENSIONS:
                continue
            
            try:
                stat = filepath.stat()
                content_hash = hash_file(filepath)
                
                files.append({
                    "path": str(filepath.relative_to(VAULT_PATH)),
                    "absolute_path": str(filepath),
                    "extension": ext,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
                    "hash": content_hash,
                })
            except (OSError, PermissionError) as e:
                print(f"⚠️  Skipping {filepath}: {e}")
    
    return files


def hash_file(filepath: Path) -> str:
    """SHA-256 hash of file contents."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


# ─── Content Analysis ────────────────────────────────────────────────────────

def extract_locked_specs(files: List[Dict]) -> List[Dict]:
    """Extract files that appear to be locked specs (latest versions)."""
    specs = []
    spec_patterns = [
        r"SPEC\.md$",
        r"specification",
        r"\.spec\.",
        r"pipeline",
        r"release-",
        r"locked",
        r"architecture",
        r"design",
        r"schema",
    ]
    
    for f in files:
        path_lower = f["path"].lower()
        for pattern in spec_patterns:
            if re.search(pattern, path_lower):
                specs.append(f)
                break
    
    return specs


def find_duplicates(files: List[Dict]) -> List[Dict]:
    """Find files with identical content hashes."""
    hash_map: Dict[str, List[Dict]] = {}
    for f in files:
        h = f["hash"]
        if h not in hash_map:
            hash_map[h] = []
        hash_map[h].append(f)
    
    duplicates = []
    for h, group in hash_map.items():
        if len(group) > 1:
            # Sort by modification time (newest first)
            group.sort(key=lambda x: x["modified"], reverse=True)
            duplicates.append({
                "hash": h,
                "keeper": group[0],
                "duplicates": group[1:],
                "count": len(group),
            })
    
    return duplicates


def find_similar_by_name(files: List[Dict]) -> List[Dict]:
    """Find files with similar names (potential duplicates)."""
    name_map: Dict[str, List[Dict]] = {}
    for f in files:
        stem = Path(f["path"]).stem.lower()
        # Normalize: remove version numbers, dates, etc.
        stem_clean = re.sub(r"[-_][vV]\d+[\.\d]*", "", stem)
        stem_clean = re.sub(r"[-_]\d{4}[-_]\d{2}[-_]\d{2}", "", stem_clean)
        
        if stem_clean not in name_map:
            name_map[stem_clean] = []
        name_map[stem_clean].append(f)
    
    similar = []
    for name, group in name_map.items():
        if len(group) > 1:
            group.sort(key=lambda x: x["modified"], reverse=True)
            similar.append({
                "normalized_name": name,
                "keeper": group[0],
                "candidates": group[1:],
                "count": len(group),
            })
    
    return similar


def extract_tags(filepath: Path) -> List[str]:
    """Extract tags from a markdown file's frontmatter."""
    tags = []
    try:
        with open(filepath, "r") as f:
            content = f.read()
        
        # YAML frontmatter
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            tag_match = re.search(r"tags:\s*\[(.*?)\]", fm)
            if tag_match:
                tags = [t.strip().strip('"').strip("'") for t in tag_match.group(1).split(",")]
    except Exception:
        pass
    
    return tags


# ─── Index Builder ───────────────────────────────────────────────────────────

def build_index(files: List[Dict]) -> Dict:
    """Build a comprehensive vault index."""
    print(f"📊 Building index from {len(files)} files...")
    
    # Categorize files
    by_extension: Dict[str, List[Dict]] = {}
    by_directory: Dict[str, List[Dict]] = {}
    locked_specs = extract_locked_specs(files)
    duplicates = find_duplicates(files)
    similar = find_similar_by_name(files)
    
    for f in files:
        ext = f["extension"]
        if ext not in by_extension:
            by_extension[ext] = []
        by_extension[ext].append(f)
        
        dirname = str(Path(f["path"]).parent)
        if dirname not in by_directory:
            by_directory[dirname] = []
        by_directory[dirname].append(f)
    
    # Stats
    total_size = sum(f["size_bytes"] for f in files)
    
    index = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "vault_path": str(VAULT_PATH),
        "stats": {
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_human": format_size(total_size),
            "by_extension": {ext: len(flist) for ext, flist in sorted(by_extension.items())},
            "by_directory": {d: len(flist) for d, flist in sorted(by_directory.items())},
        },
        "locked_specs": {
            "count": len(locked_specs),
            "files": [f["path"] for f in locked_specs],
        },
        "duplicates": {
            "count": len(duplicates),
            "total_duplicate_files": sum(d["count"] - 1 for d in duplicates),
            "potential_savings_bytes": sum(
                sum(f["size_bytes"] for f in d["duplicates"]) for d in duplicates
            ),
            "groups": [
                {
                    "hash": d["hash"][:16],
                    "keeper": d["keeper"]["path"],
                    "duplicates": [f["path"] for f in d["duplicates"]],
                }
                for d in duplicates
            ],
        },
        "similar_names": {
            "count": len(similar),
            "groups": [
                {
                    "name": s["normalized_name"],
                    "keeper": s["keeper"]["path"],
                    "candidates": [f["path"] for f in s["candidates"]],
                }
                for s in similar
            ],
        },
    }
    
    return index


def format_size(bytes_val: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"


# ─── Report Generator ────────────────────────────────────────────────────────

def generate_report(index: Dict) -> Dict:
    """Generate a human-readable consolidation report."""
    stats = index["stats"]
    dups = index["duplicates"]
    similar = index["similar_names"]
    specs = index["locked_specs"]
    
    report = {
        "generated": index["generated"],
        "summary": {
            "total_files": stats["total_files"],
            "total_size": stats["total_size_human"],
            "locked_specs_found": specs["count"],
            "duplicate_groups": dups["count"],
            "duplicate_files": dups["total_duplicate_files"],
            "potential_savings": format_size(dups["potential_savings_bytes"]),
            "similar_name_groups": similar["count"],
        },
        "recommendations": [],
    }
    
    # Generate recommendations
    if dups["total_duplicate_files"] > 0:
        report["recommendations"].append({
            "priority": "high",
            "action": "deduplicate",
            "detail": f"Found {dups['total_duplicate_files']} duplicate files ({dups['count']} groups). "
                      f"Potential savings: {report['summary']['potential_savings']}.",
        })
    
    if similar["count"] > 0:
        report["recommendations"].append({
            "priority": "medium",
            "action": "review_similar",
            "detail": f"Found {similar['count']} groups of files with similar names. "
                      f"These may be versioned copies that can be consolidated.",
        })
    
    if specs["count"] > 0:
        report["recommendations"].append({
            "priority": "info",
            "action": "locked_specs",
            "detail": f"Found {specs['count']} potential locked specs. "
                      f"These should be reviewed and moved to DevStudio/specs/.",
        })
    
    return report


# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_scan():
    """Full scan + index."""
    print("🔍 Scanning Vault...")
    files = scan_vault()
    print(f"   Found {len(files)} files")
    
    print("📊 Building index...")
    index = build_index(files)
    
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)
    print(f"   Index saved to {INDEX_PATH}")
    
    print("📋 Generating report...")
    report = generate_report(index)
    
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    print(f"   Report saved to {REPORT_PATH}")
    
    # Print summary
    s = report["summary"]
    print()
    print("┌─ Vault Scan Summary ──────────────────────────────")
    print(f"│ Files:          {s['total_files']}")
    print(f"│ Size:           {s['total_size']}")
    print(f"│ Locked Specs:   {s['locked_specs_found']}")
    print(f"│ Duplicates:     {s['duplicate_files']} files in {s['duplicate_groups']} groups")
    print(f"│ Similar Names:  {s['similar_name_groups']} groups")
    print(f"│ Potential Save: {s['potential_savings']}")
    print("└──────────────────────────────────────────────────")
    
    # Write to feed
    write_feed_entry(
        project="vault-scanner",
        source="scan",
        level="info",
        message=f"Vault scan complete: {s['total_files']} files, {s['duplicate_files']} duplicates found",
        data={"summary": s},
    )
    
    return index


def cmd_index():
    """Just rebuild index from existing scan data."""
    if not INDEX_PATH.exists():
        print("❌ No existing scan data. Run 'scan' first.")
        return
    
    with open(INDEX_PATH) as f:
        index = json.load(f)
    
    print(f"📊 Rebuilding index from {INDEX_PATH}...")
    print(f"   Last scan: {index['generated']}")
    print(f"   Files: {index['stats']['total_files']}")
    print(f"   Duplicates: {index['duplicates']['count']} groups")


def cmd_dedup():
    """Find and report duplicates."""
    if not INDEX_PATH.exists():
        print("❌ No index found. Run 'scan' first.")
        return
    
    with open(INDEX_PATH) as f:
        index = json.load(f)
    
    dups = index["duplicates"]
    if dups["count"] == 0:
        print("✅ No duplicates found.")
        return
    
    print(f"🔁 Found {dups['count']} duplicate groups ({dups['total_duplicate_files']} files):")
    print()
    for group in dups["groups"]:
        print(f"  Hash: {group['hash']}")
        print(f"  Keeper: {group['keeper']}")
        for dup in group["duplicates"]:
            print(f"    ⤷ {dup}")
        print()


def cmd_archive():
    """Archive old versions to .compost/."""
    if not INDEX_PATH.exists():
        print("❌ No index found. Run 'scan' first.")
        return
    
    with open(INDEX_PATH) as f:
        index = json.load(f)
    
    ensure_compost_dirs()
    
    # Archive duplicates (keep the newest)
    dups = index["duplicates"]
    archived_count = 0
    
    for group in dups["groups"]:
        for dup_info in group["duplicates"]:
            filepath = VAULT_PATH / dup_info
            if filepath.exists():
                dest = archive_to_compost(filepath, "duplicates")
                print(f"📦 Archived: {dup_info} → {dest}")
                archived_count += 1
    
    # Archive similar-name candidates (keep the newest)
    similar = index["similar_names"]
    for group in similar["groups"]:
        for candidate in group["candidates"]:
            filepath = VAULT_PATH / candidate
            if filepath.exists():
                dest = archive_to_compost(filepath, "old-versions")
                print(f"📦 Archived: {candidate} → {dest}")
                archived_count += 1
    
    print(f"\n📦 Archived {archived_count} files to .compost/")
    
    write_feed_entry(
        project="vault-scanner",
        source="archive",
        level="info",
        message=f"Archived {archived_count} files to .compost/",
        data={"archived_count": archived_count},
    )


def cmd_report():
    """Print the consolidation report."""
    if not REPORT_PATH.exists():
        print("❌ No report found. Run 'scan' first.")
        return
    
    with open(REPORT_PATH) as f:
        report = json.load(f)
    
    print("📋 Vault Consolidation Report")
    print("=" * 50)
    print(f"Generated: {report['generated']}")
    print()
    
    s = report["summary"]
    print("Summary:")
    print(f"  Total Files:     {s['total_files']}")
    print(f"  Total Size:      {s['total_size']}")
    print(f"  Locked Specs:    {s['locked_specs_found']}")
    print(f"  Duplicates:      {s['duplicate_files']} files")
    print(f"  Similar Names:   {s['similar_name_groups']} groups")
    print(f"  Potential Save:  {s['potential_savings']}")
    print()
    
    if report["recommendations"]:
        print("Recommendations:")
        for rec in report["recommendations"]:
            priority_icon = {"high": "🔴", "medium": "🟡", "info": "🔵"}
            print(f"  {priority_icon.get(rec['priority'], '⚪')} [{rec['priority'].upper()}] {rec['action']}")
            print(f"     {rec['detail']}")
            print()


def cmd_feed():
    """Write scan results to feed spool."""
    if not INDEX_PATH.exists():
        print("❌ No index found. Run 'scan' first.")
        return
    
    with open(INDEX_PATH) as f:
        index = json.load(f)
    
    entry = write_feed_entry(
        project="vault-scanner",
        source="feed",
        level="info",
        message="Vault index written to feed spool",
        data={"index": index},
    )
    print(f"📝 Feed entry written: {entry['id']}")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Vault Scanner — uDos Vault Indexing & Consolidation Tool"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("scan", help="Full scan + index + report")
    subparsers.add_parser("index", help="Just rebuild index from existing data")
    subparsers.add_parser("dedup", help="Find and report duplicates")
    subparsers.add_parser("archive", help="Archive old versions to .compost/")
    subparsers.add_parser("report", help="Print consolidation report")
    subparsers.add_parser("feed", help="Write scan results to feed spool")
    
    args = parser.parse_args()
    
    commands = {
        "scan": cmd_scan,
        "index": cmd_index,
        "dedup": cmd_dedup,
        "archive": cmd_archive,
        "report": cmd_report,
        "feed": cmd_feed,
    }
    
    commands[args.command]()


if __name__ == "__main__":
    main()
