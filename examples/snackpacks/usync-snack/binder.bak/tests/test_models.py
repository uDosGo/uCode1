"""
Tests for binder data models.
"""

import json
import tempfile
from pathlib import Path
from datetime import date

import pytest

from Usync.binder.models import (
    Binder,
    BinderDocument,
    BinderManifest,
    DocStatus,
    DocType,
    Frontmatter,
    ProcessingConfig,
    ProcessingPass,
    VendorConfig,
)


class TestFrontmatter:
    def test_minimal_frontmatter(self):
        fm = Frontmatter(title="Test", type=DocType.GUIDE, status=DocStatus.DRAFT, binder="#test")
        errors = fm.validate()
        assert len(errors) == 0

    def test_missing_title(self):
        fm = Frontmatter(title="", type=DocType.GUIDE, status=DocStatus.DRAFT, binder="#test")
        errors = fm.validate()
        assert any("title" in e for e in errors)

    def test_missing_type(self):
        fm = Frontmatter(title="Test", type="", status=DocStatus.DRAFT, binder="#test")  # type: ignore
        errors = fm.validate()
        assert any("type" in e for e in errors)

    def test_missing_binder(self):
        fm = Frontmatter(title="Test", type=DocType.GUIDE, status=DocStatus.DRAFT, binder="")
        errors = fm.validate()
        assert any("binder" in e for e in errors)

    def test_invalid_date_format(self):
        fm = Frontmatter(
            title="Test", type=DocType.GUIDE, status=DocStatus.DRAFT,
            binder="#test", created="invalid-date",
        )
        errors = fm.validate()
        assert any("created" in e for e in errors)

    def test_valid_date_format(self):
        fm = Frontmatter(
            title="Test", type=DocType.GUIDE, status=DocStatus.DRAFT,
            binder="#test", created="2026-05-04",
        )
        errors = fm.validate()
        assert len(errors) == 0

    def test_to_dict(self):
        fm = Frontmatter(
            title="Test Doc", type=DocType.SPEC, status=DocStatus.APPROVED,
            binder="#test", version="1.0.0", tags=["dev", "rust"],
            created="2026-05-01", author="fred",
        )
        d = fm.to_dict()
        assert d["title"] == "Test Doc"
        assert d["type"] == "spec"
        assert d["status"] == "approved"
        assert d["binder"] == "#test"
        assert d["version"] == "1.0.0"
        assert d["tags"] == ["dev", "rust"]

    def test_from_dict(self):
        data = {
            "title": "Test Doc",
            "type": "tutorial",
            "status": "draft",
            "binder": "#test",
            "tags": ["python"],
            "author": "fred",
        }
        fm = Frontmatter.from_dict(data)
        assert fm.title == "Test Doc"
        assert fm.type == DocType.TUTORIAL
        assert fm.status == DocStatus.DRAFT
        assert fm.binder == "#test"
        assert fm.tags == ["python"]


class TestBinderManifest:
    def test_default_manifest(self):
        manifest = BinderManifest(name="Test", description="A test binder")
        assert manifest.name == "Test"
        assert manifest.version == "1.0.0"
        assert len(manifest.processing.passes) == 4
        assert manifest.vendor is None

    def test_to_dict(self):
        manifest = BinderManifest(
            name="Test",
            description="A test binder",
            version="2.0.0",
            created="2026-05-04",
            maintainer="fred",
        )
        d = manifest.to_dict()
        assert d["name"] == "Test"
        assert d["version"] == "2.0.0"
        assert d["maintainer"] == "fred"

    def test_with_vendor(self):
        manifest = BinderManifest(
            name="Imported",
            description="Imported content",
            vendor=VendorConfig(
                source="../Vendor/some-docs",
                read_only=True,
                attribution="Original author: John",
            ),
        )
        d = manifest.to_dict()
        assert d["vendor"]["source"] == "../Vendor/some-docs"
        assert d["vendor"]["read_only"] is True

    def test_yaml_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "binder.yaml"
            manifest = BinderManifest(
                name="Roundtrip Test",
                description="Testing YAML serialization",
                version="1.0.0",
                created="2026-05-04",
            )
            import yaml
            with open(path, "w") as f:
                yaml.dump(manifest.to_dict(), f, default_flow_style=False, sort_keys=False)
            
            loaded = BinderManifest.from_yaml(path)
            assert loaded.name == "Roundtrip Test"
            assert loaded.version == "1.0.0"


class TestBinder:
    def test_create_binder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binder = Binder.create(root, "#test", "Test Binder", "A test binder")
            
            assert binder.binder_dir.exists()
            assert binder.index_dir.exists()
            assert binder.assets_dir.exists()
            assert binder.manifest_path.exists()
            
            # Verify manifest content
            import yaml
            with open(binder.manifest_path) as f:
                data = yaml.safe_load(f)
            assert data["name"] == "Test Binder"
            assert data["description"] == "A test binder"

    def test_load_binder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            Binder.create(root, "#test", "Test Binder")
            
            loaded = Binder.load(root, "#test")
            assert loaded.topic == "#test"
            assert loaded.manifest.name == "Test Binder"

    def test_load_nonexistent_binder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with pytest.raises(FileNotFoundError):
                Binder.load(root, "#nonexistent")


class TestProcessingPass:
    def test_all_passes_defined(self):
        """All processing passes should be defined in the enum."""
        expected = [
            "deduplicate",
            "frontmatter-enrich",
            "link-validate",
            "generate-index",
            "flatten",
            "extract-bbc-basic",
        ]
        actual = [p.value for p in ProcessingPass]
        assert sorted(actual) == sorted(expected)

    def test_default_passes(self):
        config = ProcessingConfig()
        assert len(config.passes) == 4
        assert ProcessingPass.DEDUPLICATE in config.passes
        assert ProcessingPass.FRONTMATTER_ENRICH in config.passes
        assert ProcessingPass.LINK_VALIDATE in config.passes
        assert ProcessingPass.GENERATE_INDEX in config.passes
