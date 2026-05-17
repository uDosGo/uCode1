"""
Tests for markdown frontmatter parser.
"""

import tempfile
from pathlib import Path

import pytest

from Usync.binder.parser import (
    build_frontmatter_yaml,
    parse_frontmatter,
    read_document,
    scan_binder_documents,
    write_document,
)
from Usync.binder.models import DocStatus, DocType, Frontmatter


class TestParseFrontmatter:
    def test_parse_valid_frontmatter(self):
        content = """---
title: Test Doc
type: spec
status: draft
binder: "#test"
tags: [dev, python]
---

# Content here
"""
        fm_data, body = parse_frontmatter(content)
        assert fm_data is not None
        assert fm_data["title"] == "Test Doc"
        assert fm_data["type"] == "spec"
        assert fm_data["tags"] == ["dev", "python"]
        assert "# Content here" in body

    def test_parse_no_frontmatter(self):
        content = "# Just a heading\n\nSome content."
        fm_data, body = parse_frontmatter(content)
        assert fm_data is None
        assert body == content

    def test_parse_empty_frontmatter(self):
        content = """---
---

# Content
"""
        fm_data, body = parse_frontmatter(content)
        assert fm_data is not None
        assert "# Content" in body

    def test_parse_invalid_yaml(self):
        content = """---
invalid: [unclosed
---

# Content
"""
        fm_data, body = parse_frontmatter(content)
        assert fm_data is None  # Should gracefully handle YAML errors

    def test_parse_complex_frontmatter(self):
        content = """---
title: "Complex: Doc"
type: reference
status: reviewed
version: 2.1.0
binder: "#udos"
tags: [rust, mcp, architecture]
created: 2026-05-01
updated: 2026-05-04
author: fred
related:
  - "../other/README.md"
  - "https://example.com"
---

# Body
"""
        fm_data, body = parse_frontmatter(content)
        assert fm_data is not None
        assert fm_data["title"] == "Complex: Doc"
        assert fm_data["version"] == "2.1.0"
        assert len(fm_data["related"]) == 2


class TestBuildFrontmatterYaml:
    def test_build_minimal(self):
        fm = Frontmatter(title="Test", type=DocType.GUIDE, status=DocStatus.DRAFT, binder="#test")
        yaml_str = build_frontmatter_yaml(fm)
        assert yaml_str.startswith("---")
        assert yaml_str.endswith("---\n")
        assert "title: Test" in yaml_str
        assert "type: guide" in yaml_str

    def test_build_with_tags(self):
        fm = Frontmatter(
            title="Test", type=DocType.SPEC, status=DocStatus.APPROVED,
            binder="#test", tags=["dev", "rust"],
        )
        yaml_str = build_frontmatter_yaml(fm)
        assert "tags:" in yaml_str

    def test_roundtrip(self):
        original = """---
title: Roundtrip Test
type: tutorial
status: draft
binder: "#test"
tags: [python, testing]
---

# Content
"""
        fm_data, body = parse_frontmatter(original)
        fm = Frontmatter.from_dict(fm_data)
        rebuilt = build_frontmatter_yaml(fm) + body
        
        # Re-parse
        fm_data2, body2 = parse_frontmatter(rebuilt)
        assert fm_data2["title"] == "Roundtrip Test"
        assert fm_data2["type"] == "tutorial"
        assert "# Content" in body2


class TestReadWriteDocument:
    def test_read_document_with_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.md"
            content = """---
title: Test Doc
type: spec
status: draft
binder: "#test"
---

# Hello
"""
            path.write_text(content)
            
            doc = read_document(path)
            assert doc.frontmatter.title == "Test Doc"
            assert doc.frontmatter.type == DocType.SPEC
            assert doc.frontmatter.binder == "#test"
            assert "# Hello" in doc.content
            assert doc.hash != ""

    def test_read_document_without_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "no-fm.md"
            content = "# Just content\n\nNo frontmatter here."
            path.write_text(content)
            
            doc = read_document(path)
            assert doc.frontmatter.title == "No Fm"  # Auto-generated from filename
            assert doc.frontmatter.type == DocType.GUIDE  # Default
            assert doc.frontmatter.binder == ""  # Empty

    def test_write_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "write-test.md"
            content = "# Original\n"
            path.write_text(content)
            
            doc = read_document(path)
            doc.frontmatter.title = "Updated Title"
            doc.frontmatter.binder = "#test"
            write_document(doc)
            
            # Re-read
            doc2 = read_document(path)
            assert doc2.frontmatter.title == "Updated Title"
            assert doc2.frontmatter.binder == "#test"

    def test_scan_binder_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder_dir = Path(tmp)
            
            # Create some markdown files
            (binder_dir / "01-intro.md").write_text("""---
title: Intro
type: guide
status: draft
binder: "#test"
---

# Intro
""")
            (binder_dir / "02-details.md").write_text("""---
title: Details
type: reference
status: draft
binder: "#test"
---

# Details
""")
            # Create a non-markdown file (should be ignored)
            (binder_dir / "notes.txt").write_text("Not markdown")
            
            docs = scan_binder_documents(binder_dir)
            assert len(docs) == 2
            assert docs[0].frontmatter.title == "Intro"
            assert docs[1].frontmatter.title == "Details"
