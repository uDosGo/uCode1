"""
Markdown frontmatter parser — reads/writes YAML frontmatter from .md files.

Implements the Vault Processing Standards §3 (Frontmatter Schema).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import List, Optional, Tuple

import yaml

from .models import BinderDocument, DocStatus, DocType, Frontmatter


def parse_frontmatter(content: str) -> Tuple[Optional[dict], str]:
    """
    Parse YAML frontmatter from markdown content.
    
    Returns (frontmatter_dict, body_content).
    If no frontmatter found, returns (None, content).
    """
    # Match content between --- delimiters at start of file
    # Handles: ---\n...\n---, ---\n---, and ---\n...\n---\n variants
    match = re.match(r"^---\n(.*?)(?:\n---\n?|---)\n?", content, re.DOTALL)



    if not match:
        return None, content
    
    fm_text = match.group(1)
    body = content[match.end():]
    
    try:
        fm_data = yaml.safe_load(fm_text) if fm_text.strip() else {}
        if fm_data is None:
            # Empty frontmatter (---\n---)
            return {}, body
        if not isinstance(fm_data, dict):
            return None, content
        return fm_data, body
    except yaml.YAMLError:
        return None, content




def build_frontmatter_yaml(frontmatter: Frontmatter) -> str:
    """Build YAML frontmatter string from a Frontmatter object."""
    data = frontmatter.to_dict()
    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}
    # Format tags as inline list
    if data.get("tags"):
        data["tags"] = data["tags"]
    # Format related as list
    if data.get("related"):
        data["related"] = data["related"]
    
    fm_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False).strip()
    return f"---\n{fm_yaml}\n---\n"


def read_document(filepath: Path) -> BinderDocument:
    """Read a markdown file and parse its frontmatter."""
    raw_content = filepath.read_text(encoding="utf-8")
    content_hash = hashlib.sha256(raw_content.encode()).hexdigest()
    size_bytes = filepath.stat().st_size
    
    fm_data, body = parse_frontmatter(raw_content)
    
    if fm_data:
        frontmatter = Frontmatter.from_dict(fm_data)
    else:
        # Create minimal frontmatter from filename
        title = filepath.stem.replace("-", " ").replace("_", " ").title()
        frontmatter = Frontmatter(
            title=title,
            type=DocType.GUIDE,
            status=DocStatus.DRAFT,
            binder="",
        )
    
    return BinderDocument(
        path=filepath,
        frontmatter=frontmatter,
        content=body,
        raw_content=raw_content,
        hash=content_hash,
        size_bytes=size_bytes,
    )


def write_document(doc: BinderDocument):
    """Write a BinderDocument back to its file with updated frontmatter."""
    fm_yaml = build_frontmatter_yaml(doc.frontmatter)
    new_content = fm_yaml + doc.content
    doc.path.write_text(new_content, encoding="utf-8")
    doc.raw_content = new_content


def scan_binder_documents(binder_dir: Path) -> List[BinderDocument]:
    """Scan a binder directory for all markdown documents."""
    documents = []
    for md_file in sorted(binder_dir.glob("*.md")):
        # Skip files in .index/
        if ".index" in md_file.parts:
            continue
        doc = read_document(md_file)
        documents.append(doc)
    return documents
