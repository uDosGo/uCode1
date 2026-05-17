"""
Tests for binder processing passes.
"""

import tempfile
from pathlib import Path

import pytest

from Usync.binder.models import Binder, ProcessingPass
from Usync.binder.parser import scan_binder_documents
from Usync.binder.passes import (
    pass_deduplicate,
    pass_frontmatter_enrich,
    pass_generate_index,
    pass_link_validate,
    pass_extract_bbc_basic,
    pass_flatten,
    run_pass,
    run_all_passes,
)


def _create_test_binder(tmp: Path, topic: str = "#test") -> Binder:
    """Helper to create a test binder with sample documents."""
    binder = Binder.create(Path(tmp), topic, "Test Binder")
    
    # Create sample documents
    docs = {
        "01-intro.md": """---
title: Introduction
type: guide
status: draft
binder: "#test"
tags: [intro]
created: 2026-05-01
---

# Introduction

Welcome to the test binder.
""",
        "02-concepts.md": """---
title: Core Concepts
type: reference
status: draft
binder: "#test"
tags: [concepts]
created: 2026-05-02
---

# Core Concepts

See [Introduction](01-intro.md) for details.
Also see [External](https://example.com).
""",
        "03-bbc.md": """---
title: BBC BASIC Examples
type: tutorial
status: draft
binder: "#test"
tags: [bbc, basic]
created: 2026-05-03
---

# BBC BASIC

Here's an example:

```bbcbasic
10 PRINT "Hello World"
20 GOTO 10
```

And another:

```bbcbasic
REM This is a comment
PRINT "Done"
```
""",
    }
    
    for filename, content in docs.items():
        (binder.binder_dir / filename).write_text(content)
    
    binder.documents = scan_binder_documents(binder.binder_dir)
    return binder


class TestPassDeduplicate:
    def test_no_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            result = pass_deduplicate(binder)
            assert result["groups_found"] == 0
            assert result["total_duplicates"] == 0

    def test_exact_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            
            # Add an exact duplicate
            dup_content = (binder.binder_dir / "01-intro.md").read_text()
            (binder.binder_dir / "01-intro-copy.md").write_text(dup_content)
            
            binder.documents = scan_binder_documents(binder.binder_dir)
            result = pass_deduplicate(binder)
            
            assert result["groups_found"] >= 1


class TestPassFrontmatterEnrich:
    def test_enriches_missing_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            
            # Add a document without frontmatter
            (binder.binder_dir / "no-fm.md").write_text("# No Frontmatter\n")
            
            binder.documents = scan_binder_documents(binder.binder_dir)
            result = pass_frontmatter_enrich(binder)
            
            assert result["enriched"] >= 1

    def test_validates_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            
            # Add a document with invalid frontmatter
            (binder.binder_dir / "invalid.md").write_text("""---
title: Invalid
type: spec
status: draft
binder: ""
---

# Content
""")
            
            binder.documents = scan_binder_documents(binder.binder_dir)
            result = pass_frontmatter_enrich(binder)
            
            # The empty binder should be enriched
            assert result["enriched"] >= 1


class TestPassLinkValidate:
    def test_valid_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            result = pass_link_validate(binder)
            assert result["broken_links"] == 0
            assert result["valid_links"] > 0

    def test_broken_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            
            # Add a document with a broken link
            (binder.binder_dir / "broken.md").write_text("""---
title: Broken Links
type: guide
status: draft
binder: "#test"
---

See [Missing](nonexistent.md) for details.
""")
            
            binder.documents = scan_binder_documents(binder.binder_dir)
            result = pass_link_validate(binder)
            assert result["broken_links"] >= 1


class TestPassGenerateIndex:
    def test_generates_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            result = pass_generate_index(binder)
            
            assert result["documents_indexed"] == 3
            assert (binder.index_dir / "search.json").exists()
            assert (binder.index_dir / "feed.json").exists()
            
            # Verify search index content
            import json
            with open(binder.index_dir / "search.json") as f:
                index = json.load(f)
            assert index["binder"] == "#test"
            assert index["document_count"] == 3

    def test_feed_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            result = pass_generate_index(binder)
            
            import json
            with open(binder.index_dir / "feed.json") as f:
                feed = json.load(f)
            
            assert feed["version"] == "https://jsonfeed.org/version/1.1"
            assert len(feed["items"]) == 3
            assert feed["items"][0]["title"] == "Introduction"


class TestPassExtractBBCBasic:
    def test_extracts_bbc_basic(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            result = pass_extract_bbc_basic(binder)
            
            assert result["examples_found"] == 2
            assert result["output"] is not None
            
            import json
            with open(result["output"]) as f:
                index = json.load(f)
            assert index["example_count"] == 2
            assert "PRINT" in index["examples"][0]["code"]

    def test_no_bbc_basic(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            
            # Remove the BBC BASIC doc
            (binder.binder_dir / "03-bbc.md").unlink()
            binder.documents = scan_binder_documents(binder.binder_dir)
            
            result = pass_extract_bbc_basic(binder)
            assert result["examples_found"] == 0


class TestPassFlatten:
    def test_imports_flat_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            
            # Create source directory with loose markdown files
            source = root / "source"
            source.mkdir()
            
            (source / "note1.md").write_text("""---
title: Note 1
type: guide
status: draft
binder: "#test"
---

# Note 1
""")
            (source / "note2.md").write_text("""---
title: Note 2
type: reference
status: draft
binder: "#test"
---

# Note 2
""")
            
            # Create binder and run flatten
            binder = Binder.create(root, "#imported", "Imported Binder")
            result = pass_flatten(binder, source)
            
            assert result["imported"] == 2
            assert (binder.binder_dir / "note1.md").exists()
            assert (binder.binder_dir / "note2.md").exists()


class TestRunPass:
    def test_run_single_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            result = run_pass(binder, ProcessingPass.GENERATE_INDEX)
            assert result["pass"] == "generate-index"
            assert result["documents_indexed"] == 3

    def test_run_all_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            results = run_all_passes(binder)
            assert len(results) == 4  # Default passes
            assert results[0]["pass"] == "deduplicate"
            assert results[-1]["pass"] == "generate-index"

    def test_run_unknown_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            binder = _create_test_binder(Path(tmp))
            import pytest
            with pytest.raises(ValueError):
                run_pass(binder, "unknown-pass")  # type: ignore

            
