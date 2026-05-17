"""
Binder data models — frontmatter schema, manifest, and processing config.

Implements the Vault Processing Standards §3 (Frontmatter Schema) and §2 (Binder Structure).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


# ─── Enums ────────────────────────────────────────────────────────────────────

class DocType(str, Enum):
    SPEC = "spec"
    GUIDE = "guide"
    REFERENCE = "reference"
    TUTORIAL = "tutorial"
    ROADMAP = "roadmap"


class DocStatus(str, Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    ARCHIVED = "archived"


class ProcessingPass(str, Enum):
    DEDUPLICATE = "deduplicate"
    FRONTMATTER_ENRICH = "frontmatter-enrich"
    LINK_VALIDATE = "link-validate"
    GENERATE_INDEX = "generate-index"
    FLATTEN = "flatten"
    EXTRACT_BBC_BASIC = "extract-bbc-basic"


# ─── Frontmatter ──────────────────────────────────────────────────────────────

@dataclass
class Frontmatter:
    """Required frontmatter schema for all binder documents (§3)."""
    title: str
    type: DocType
    status: DocStatus
    binder: str  # topic name, e.g. "#udos"
    version: Optional[str] = None  # semver, optional for non-code docs
    tags: List[str] = field(default_factory=list)
    created: Optional[str] = None  # YYYY-MM-DD
    updated: Optional[str] = None  # YYYY-MM-DD
    author: Optional[str] = None
    related: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        """Validate required fields. Returns list of error messages."""
        errors = []
        if not self.title:
            errors.append("title is required")
        if not self.type:
            errors.append("type is required (spec|guide|reference|tutorial|roadmap)")
        if not self.status:
            errors.append("status is required (draft|reviewed|approved|archived)")
        if not self.binder:
            errors.append("binder is required (e.g. '#udos')")
        if self.created:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", self.created):
                errors.append(f"created must be YYYY-MM-DD format, got '{self.created}'")
        if self.updated:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", self.updated):
                errors.append(f"updated must be YYYY-MM-DD format, got '{self.updated}'")
        return errors

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "type": self.type.value,
            "status": self.status.value,
            "version": self.version,
            "binder": self.binder,
            "tags": self.tags,
            "created": self.created,
            "updated": self.updated,
            "author": self.author,
            "related": self.related,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Frontmatter":
        # Convert date objects to strings (YAML may parse YYYY-MM-DD as date)
        created = data.get("created")
        if created is not None and not isinstance(created, str):
            created = str(created)
        updated = data.get("updated")
        if updated is not None and not isinstance(updated, str):
            updated = str(updated)
        
        return cls(
            title=data.get("title", ""),
            type=DocType(data["type"]) if data.get("type") else DocType.GUIDE,
            status=DocStatus(data["status"]) if data.get("status") else DocStatus.DRAFT,
            version=data.get("version"),
            binder=data.get("binder", ""),
            tags=data.get("tags", []),
            created=created,
            updated=updated,
            author=data.get("author"),
            related=data.get("related", []),
        )



# ─── Binder Manifest ──────────────────────────────────────────────────────────

@dataclass
class BinderManifest:
    """binder.yaml manifest (§2)."""
    name: str
    description: str
    version: str = "1.0.0"
    created: Optional[str] = None
    maintainer: Optional[str] = None
    processing: ProcessingConfig = field(default_factory=lambda: ProcessingConfig())
    vendor: Optional[VendorConfig] = None

    @classmethod
    def from_yaml(cls, path: Path) -> "BinderManifest":
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> "BinderManifest":
        proc = data.get("processing", {})
        passes = [ProcessingPass(p) for p in proc.get("passes", [])]
        output = proc.get("output", {})
        vendor_data = data.get("vendor")
        vendor = VendorConfig(**vendor_data) if vendor_data else None
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            created=data.get("created"),
            maintainer=data.get("maintainer"),
            processing=ProcessingConfig(
                passes=passes,
                output=OutputConfig(**output) if output else OutputConfig(),
            ),
            vendor=vendor,
        )

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created": self.created,
            "maintainer": self.maintainer,
            "processing": {
                "passes": [p.value for p in self.processing.passes],
                "output": {
                    "format": self.processing.output.format,
                    "destination": self.processing.output.destination,
                },
            },
        }
        if self.vendor:
            result["vendor"] = {
                "source": self.vendor.source,
                "read_only": self.vendor.read_only,
                "attribution": self.vendor.attribution,
            }
        return result


@dataclass
class ProcessingConfig:
    passes: List[ProcessingPass] = field(default_factory=lambda: [
        ProcessingPass.DEDUPLICATE,
        ProcessingPass.FRONTMATTER_ENRICH,
        ProcessingPass.LINK_VALIDATE,
        ProcessingPass.GENERATE_INDEX,
    ])
    output: OutputConfig = field(default_factory=lambda: OutputConfig())


@dataclass
class OutputConfig:
    format: str = "json-feed"
    destination: str = ""


@dataclass
class VendorConfig:
    source: str = ""
    read_only: bool = True
    attribution: str = ""


# ─── Binder Document ──────────────────────────────────────────────────────────

@dataclass
class BinderDocument:
    """A single markdown document within a binder."""
    path: Path
    frontmatter: Frontmatter
    content: str
    raw_content: str  # original content before processing
    hash: str = ""
    size_bytes: int = 0

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def relative_path(self) -> str:
        return str(self.path)

    def to_dict(self) -> dict:
        return {
            "path": self.relative_path,
            "filename": self.filename,
            "frontmatter": self.frontmatter.to_dict(),
            "content_preview": self.content[:200] if self.content else "",
            "hash": self.hash,
            "size_bytes": self.size_bytes,
        }


# ─── Binder ───────────────────────────────────────────────────────────────────

@dataclass
class Binder:
    """A curated, indexed collection of markdown files around a single topic (§1)."""
    topic: str  # e.g. "#udos"
    root_path: Path
    manifest: BinderManifest
    documents: List[BinderDocument] = field(default_factory=list)

    @property
    def binder_dir(self) -> Path:
        return self.root_path / f"binder/{self.topic}"

    @property
    def index_dir(self) -> Path:
        return self.binder_dir / ".index"

    @property
    def assets_dir(self) -> Path:
        return self.binder_dir / "assets"

    @property
    def manifest_path(self) -> Path:
        return self.binder_dir / "binder.yaml"

    def ensure_dirs(self):
        """Create binder directory structure if it doesn't exist."""
        self.binder_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def save_manifest(self):
        """Write binder.yaml manifest."""
        import yaml
        self.ensure_dirs()
        with open(self.manifest_path, "w") as f:
            yaml.dump(self.manifest.to_dict(), f, default_flow_style=False, sort_keys=False)

    @classmethod
    def load(cls, root_path: Path, topic: str) -> "Binder":
        """Load a binder from disk."""
        binder_dir = root_path / f"binder/{topic}"
        manifest_path = binder_dir / "binder.yaml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"No binder.yaml found at {manifest_path}")
        manifest = BinderManifest.from_yaml(manifest_path)
        return cls(topic=topic, root_path=root_path, manifest=manifest)

    @classmethod
    def create(cls, root_path: Path, topic: str, name: str, description: str = "") -> "Binder":
        """Create a new binder with skeleton structure."""
        manifest = BinderManifest(
            name=name,
            description=description,
            created=date.today().isoformat(),
        )
        binder = cls(topic=topic, root_path=root_path, manifest=manifest)
        binder.ensure_dirs()
        binder.save_manifest()
        return binder
