"""
Processing passes for the binder pipeline (§4).

Each pass is a function that reads markdown files, transforms them,
and writes back (or updates a sidecar index).
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .models import (
    Binder,
    BinderDocument,
    BinderManifest,
    DocStatus,
    DocType,
    Frontmatter,
    ProcessingPass,
)
from .parser import build_frontmatter_yaml, read_document, scan_binder_documents, write_document


# ─── Pass 1: Deduplicate ──────────────────────────────────────────────────────

def pass_deduplicate(binder: Binder, interactive: bool = False) -> Dict:
    """
    Find near-duplicate content within the same binder using content hashing.
    
    Uses SHA-256 for exact duplicates. For semantic similarity, would need
    embedding model integration (future enhancement).
    
    Returns a report of duplicates found.
    """
    from collections import defaultdict
    
    hash_map: Dict[str, List[BinderDocument]] = defaultdict(list)
    for doc in binder.documents:
        hash_map[doc.hash].append(doc)
    
    duplicates = []
    for content_hash, docs in hash_map.items():
        if len(docs) > 1:
            # Sort by modification time (newest first)
            docs.sort(key=lambda d: d.path.stat().st_mtime, reverse=True)
            keeper = docs[0]
            dups = docs[1:]
            
            duplicates.append({
                "hash": content_hash[:16],
                "keeper": str(keeper.path),
                "duplicates": [str(d.path) for d in dups],
                "count": len(dups),
            })
            
            if interactive:
                print(f"\n🔁 Duplicate group (hash: {content_hash[:16]}):")
                print(f"  Keeper: {keeper.path}")
                for d in dups:
                    print(f"  Duplicate: {d.path}")
                response = input("  Auto-merge? [Y/n]: ").strip().lower()
                if response != "n":
                    for d in dups:
                        # Merge frontmatter from duplicate into keeper
                        _merge_frontmatter(keeper, d)
                        # Remove duplicate file
                        d.path.unlink()
                        print(f"    Removed: {d.path}")
    
    return {
        "pass": "deduplicate",
        "groups_found": len(duplicates),
        "total_duplicates": sum(d["count"] for d in duplicates),
        "groups": duplicates,
    }


def _merge_frontmatter(keeper: BinderDocument, duplicate: BinderDocument):
    """Merge frontmatter from duplicate into keeper (keeper takes priority)."""
    k_fm = keeper.frontmatter
    d_fm = duplicate.frontmatter
    
    # Merge tags
    all_tags = set(k_fm.tags) | set(d_fm.tags)
    k_fm.tags = sorted(all_tags)
    
    # Merge related links
    all_related = set(k_fm.related) | set(d_fm.related)
    k_fm.related = sorted(all_related)
    
    # Keep keeper's title, type, status, version
    # Update updated date
    k_fm.updated = date.today().isoformat()


# ─── Pass 2: Frontmatter Enrich ───────────────────────────────────────────────

def pass_frontmatter_enrich(binder: Binder) -> Dict:
    """
    Add missing frontmatter fields (automatic from filename, binder, etc.).
    Validates required fields; warns if missing.
    """
    enriched_count = 0
    errors = []
    
    for doc in binder.documents:
        fm = doc.frontmatter
        changed = False
        
        # Auto-fill binder topic if missing
        if not fm.binder:
            fm.binder = binder.topic
            changed = True
        
        # Auto-fill title from filename if missing
        if not fm.title:
            fm.title = doc.path.stem.replace("-", " ").replace("_", " ").title()
            changed = True
        
        # Auto-fill created date if missing
        if not fm.created:
            fm.created = date.today().isoformat()
            changed = True
        
        # Auto-fill updated date
        fm.updated = date.today().isoformat()
        changed = True
        
        # Validate
        validation_errors = fm.validate()
        if validation_errors:
            errors.append({
                "path": str(doc.path),
                "errors": validation_errors,
            })
        
        if changed:
            write_document(doc)
            enriched_count += 1
    
    return {
        "pass": "frontmatter-enrich",
        "enriched": enriched_count,
        "errors": errors,
        "error_count": len(errors),
    }


# ─── Pass 3: Link Validate ────────────────────────────────────────────────────

def pass_link_validate(binder: Binder) -> Dict:
    """
    Check internal binder links and binder cross-links.
    Reports broken links.
    """
    broken_links = []
    valid_links = 0
    
    # Build set of valid document paths within the binder
    valid_paths: Set[str] = set()
    for doc in binder.documents:
        valid_paths.add(doc.path.name)
        valid_paths.add(doc.path.stem)
    
    for doc in binder.documents:
        content = doc.raw_content
        
        # Find markdown links: [text](path)
        md_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        for text, link in md_links:
            # Skip external URLs
            if link.startswith(("http://", "https://", "ftp://")):
                valid_links += 1
                continue
            
            # Skip anchors-only links
            if link.startswith("#"):
                valid_links += 1
                continue
            
            # Check internal binder links
            link_target = link.split("#")[0]  # Remove anchor
            if link_target:
                link_name = Path(link_target).name
                link_stem = Path(link_target).stem
                
                if link_name not in valid_paths and link_stem not in valid_paths:
                    broken_links.append({
                        "source": str(doc.path),
                        "link": link,
                        "text": text,
                        "type": "internal",
                    })
                else:
                    valid_links += 1
        
        # Find binder cross-links: [see auth](#authentication)
        cross_links = re.findall(r"\[([^\]]+)\]\(#([^)]+)\)", content)
        for text, target in cross_links:
            # Check if target exists as a binder topic
            target_binder = f"#{target}"
            target_dir = binder.root_path / f"binder/{target_binder}"
            if not target_dir.exists():
                broken_links.append({
                    "source": str(doc.path),
                    "link": f"#{target}",
                    "text": text,
                    "type": "cross-binder",
                })
            else:
                valid_links += 1
    
    return {
        "pass": "link-validate",
        "valid_links": valid_links,
        "broken_links": len(broken_links),
        "broken": broken_links,
    }


# ─── Pass 4: Generate Index ───────────────────────────────────────────────────

def pass_generate_index(binder: Binder) -> Dict:
    """
    Create .index/search.json for quick browsing.
    Also generates a JSON feed of the binder content.
    """
    binder.ensure_dirs()
    
    # Build search index
    search_index = []
    for doc in binder.documents:
        search_index.append(doc.to_dict())
    
    # Write search index
    search_path = binder.index_dir / "search.json"
    with open(search_path, "w") as f:
        json.dump({
            "binder": binder.topic,
            "name": binder.manifest.name,
            "description": binder.manifest.description,
            "generated": date.today().isoformat(),
            "document_count": len(search_index),
            "documents": search_index,
        }, f, indent=2)
    
    # Generate JSON feed
    feed = _generate_json_feed(binder)
    feed_path = binder.index_dir / "feed.json"
    with open(feed_path, "w") as f:
        json.dump(feed, f, indent=2)
    
    # Write to destination if configured
    if binder.manifest.processing.output.destination:
        dest = Path(binder.manifest.processing.output.destination).expanduser()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w") as f:
            json.dump(feed, f, indent=2)
    
    return {
        "pass": "generate-index",
        "documents_indexed": len(search_index),
        "search_index": str(search_path),
        "feed_path": str(feed_path),
        "feed_items": len(feed.get("items", [])),
    }


def _generate_json_feed(binder: Binder) -> Dict:
    """Generate a JSON Feed (https://jsonfeed.org) for the binder."""
    items = []
    for doc in binder.documents:
        item = {
            "id": doc.hash[:16] if doc.hash else str(abs(hash(str(doc.path)))),
            "url": f"vault://binder/{binder.topic}/{doc.path.name}",
            "title": doc.frontmatter.title,
            "content_text": doc.content[:500] if doc.content else "",
            "summary": doc.content[:200] if doc.content else "",
            "date_published": doc.frontmatter.created,
            "date_modified": doc.frontmatter.updated,
            "tags": doc.frontmatter.tags,
            "author": {"name": doc.frontmatter.author} if doc.frontmatter.author else None,
            "_binder": binder.topic,
            "_type": doc.frontmatter.type.value,
            "_status": doc.frontmatter.status.value,
        }
        items.append(item)
    
    return {
        "version": "https://jsonfeed.org/version/1.1",
        "title": binder.manifest.name,
        "description": binder.manifest.description,
        "home_page_url": f"vault://binder/{binder.topic}",
        "feed_url": f"vault://binder/{binder.topic}/feed.json",
        "items": items,
    }


# ─── Pass 5: Flatten (Legacy Import) ──────────────────────────────────────────

def pass_flatten(binder: Binder, source_dir: Path) -> Dict:
    """
    Take a flat directory of loose markdown files, organise them into a binder
    by detecting topics from #tags in content.
    """
    imported = 0
    skipped = 0
    
    for md_file in sorted(source_dir.glob("*.md")):
        doc = read_document(md_file)
        
        # Detect topic from tags if binder is not set
        if not doc.frontmatter.binder:
            # Check content for #topic tags
            topic_tags = re.findall(r"#(\w+)", doc.content)
            if topic_tags:
                # Use the most common tag as the binder topic
                from collections import Counter
                tag_counts = Counter(topic_tags)
                most_common = tag_counts.most_common(1)[0][0]
                doc.frontmatter.binder = f"#{most_common}"
            else:
                doc.frontmatter.binder = binder.topic
        
        # Set binder topic
        doc.frontmatter.binder = binder.topic
        
        # Ensure frontmatter is valid
        if not doc.frontmatter.title:
            doc.frontmatter.title = md_file.stem.replace("-", " ").replace("_", " ").title()
        if not doc.frontmatter.created:
            doc.frontmatter.created = date.today().isoformat()
        doc.frontmatter.updated = date.today().isoformat()
        
        # Write to binder directory
        dest_path = binder.binder_dir / md_file.name
        doc.path = dest_path
        write_document(doc)
        imported += 1
    
    # Create/update binder.yaml
    binder.save_manifest()
    
    return {
        "pass": "flatten",
        "imported": imported,
        "skipped": skipped,
        "source": str(source_dir),
        "destination": str(binder.binder_dir),
    }


# ─── Pass 6: Extract BBC BASIC ────────────────────────────────────────────────

def pass_extract_bbc_basic(binder: Binder) -> Dict:
    """
    Scan markdown for BBC BASIC code blocks.
    Generates a JSON index of examples for the uCode1 assistant.
    """
    examples = []
    
    for doc in binder.documents:
        # Find BBC BASIC code blocks
        blocks = re.findall(
            r"```bbcbasic\n(.*?)```",
            doc.raw_content,
            re.DOTALL,
        )
        
        for i, code in enumerate(blocks):
            # Extract a title from the preceding heading or line
            title = _extract_block_title(doc.raw_content, code)
            
            example = {
                "id": f"{doc.path.stem}-bbc-{i+1}",
                "title": title,
                "code": code.strip(),
                "source": str(doc.path),
                "binder": binder.topic,
                "language": "bbcbasic",
            }
            examples.append(example)
    
    # Write BBC BASIC index
    if examples:
        bbc_path = binder.index_dir / "bbc-basic.json"
        with open(bbc_path, "w") as f:
            json.dump({
                "binder": binder.topic,
                "generated": date.today().isoformat(),
                "example_count": len(examples),
                "examples": examples,
            }, f, indent=2)
    
    return {
        "pass": "extract-bbc-basic",
        "examples_found": len(examples),
        "output": str(binder.index_dir / "bbc-basic.json") if examples else None,
    }


def _extract_block_title(content: str, code_block: str) -> str:
    """Extract a title for a code block from surrounding context."""
    lines = content.split("\n")
    code_start = content.find(code_block)
    
    # Look backwards for a heading
    before = content[:code_start]
    headings = re.findall(r"^#{1,3}\s+(.+)$", before, re.MULTILINE)
    if headings:
        return headings[-1].strip()
    
    # Look for a line immediately before the block
    before_lines = before.strip().split("\n")
    if before_lines:
        last_line = before_lines[-1].strip()
        if last_line and not last_line.startswith("```"):
            return last_line
    
    return "BBC BASIC Example"


# ─── Pass Router ──────────────────────────────────────────────────────────────

PASS_FUNCTIONS = {
    ProcessingPass.DEDUPLICATE: pass_deduplicate,
    ProcessingPass.FRONTMATTER_ENRICH: pass_frontmatter_enrich,
    ProcessingPass.LINK_VALIDATE: pass_link_validate,
    ProcessingPass.GENERATE_INDEX: pass_generate_index,
    ProcessingPass.FLATTEN: pass_flatten,
    ProcessingPass.EXTRACT_BBC_BASIC: pass_extract_bbc_basic,
}


def run_pass(binder: Binder, pass_name: ProcessingPass, **kwargs) -> Dict:
    """Run a single processing pass."""
    pass_fn = PASS_FUNCTIONS.get(pass_name)
    if not pass_fn:
        raise ValueError(f"Unknown pass: {pass_name}")
    
    # Re-scan documents before each pass
    binder.documents = scan_binder_documents(binder.binder_dir)
    
    return pass_fn(binder, **kwargs)


def run_all_passes(binder: Binder, **kwargs) -> List[Dict]:
    """Run all configured passes in order."""
    results = []
    for pass_name in binder.manifest.processing.passes:
        result = run_pass(binder, pass_name, **kwargs)
        results.append(result)
    return results
