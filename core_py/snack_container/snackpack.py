"""
Snackpack — collections of snacks with shared LENS/SKIN rules.

A Snackpack bundles related snacks together with shared configuration,
providing a unified launcher and cross-snack data sharing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .manifest import (
    SnackManifest,
    LensConfig,
    SkinConfig,
    MCPConfig,
    Dependency,
    load_manifest,
)
from .registry import SnackRegistry, SnackId


# ──────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────


@dataclass
class SharedLensConfig:
    """Shared LENS configuration for all snacks in a pack."""
    variable_patterns: List[str] = field(default_factory=list)
    memory_regions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SharedSkinConfig:
    """Shared SKIN configuration for all snacks in a pack."""
    available: List[str] = field(default_factory=list)
    targets: List[str] = field(default_factory=list)


@dataclass
class MetaExportConfig:
    """Meta-export configuration for the snackpack."""
    collection_spool: str = ""
    combined_feed: bool = False


@dataclass
class LauncherConfig:
    """Launcher configuration for the snackpack."""
    type: str = "bbc_basic"
    script: str = ""


@dataclass
class SnackpackManifest:
    """A snackpack.yaml manifest.

    Bundles multiple snacks with shared LENS/SKIN rules and a launcher.
    """
    name: str = ""
    version: str = ""
    snacks: List[str] = field(default_factory=list)
    shared_lens: SharedLensConfig = field(default_factory=SharedLensConfig)
    shared_skins: SharedSkinConfig = field(default_factory=SharedSkinConfig)
    meta_export: MetaExportConfig = field(default_factory=MetaExportConfig)
    launcher: LauncherConfig = field(default_factory=LauncherConfig)
    description: str = ""
    tags: List[str] = field(default_factory=list)

    # ── Serialisation ────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a plain dict for YAML serialisation."""
        d: Dict[str, Any] = {
            "name": self.name,
            "version": self.version,
            "snacks": self.snacks,
        }

        if self.shared_lens.variable_patterns or self.shared_lens.memory_regions:
            lens: Dict[str, Any] = {}
            if self.shared_lens.variable_patterns:
                lens["variable_patterns"] = self.shared_lens.variable_patterns
            if self.shared_lens.memory_regions:
                lens["memory_regions"] = self.shared_lens.memory_regions
            if lens:
                d["shared_lens"] = lens

        if self.shared_skins.available or self.shared_skins.targets:
            skin: Dict[str, Any] = {}
            if self.shared_skins.available:
                skin["available"] = self.shared_skins.available
            if self.shared_skins.targets:
                skin["targets"] = self.shared_skins.targets
            if skin:
                d["shared_skins"] = skin

        if self.meta_export.collection_spool or self.meta_export.combined_feed:
            export: Dict[str, Any] = {}
            if self.meta_export.collection_spool:
                export["collection_spool"] = self.meta_export.collection_spool
            if self.meta_export.combined_feed:
                export["combined_feed"] = True
            if export:
                d["meta_export"] = export

        if self.launcher.type or self.launcher.script:
            launcher: Dict[str, Any] = {}
            if self.launcher.type:
                launcher["type"] = self.launcher.type
            if self.launcher.script:
                launcher["script"] = self.launcher.script
            if launcher:
                d["launcher"] = launcher

        if self.description:
            d["description"] = self.description
        if self.tags:
            d["tags"] = self.tags

        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SnackpackManifest":
        """Create from a parsed YAML/JSON dict."""
        m = cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            snacks=data.get("snacks", []),
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )

        # Shared LENS
        lens_data = data.get("shared_lens", {})
        if lens_data:
            m.shared_lens = SharedLensConfig(
                variable_patterns=lens_data.get("variable_patterns", []),
                memory_regions=lens_data.get("memory_regions", []),
            )

        # Shared SKIN
        skin_data = data.get("shared_skins", {})
        if skin_data:
            m.shared_skins = SharedSkinConfig(
                available=skin_data.get("available", []),
                targets=skin_data.get("targets", []),
            )

        # Meta export
        export_data = data.get("meta_export", {})
        if export_data:
            m.meta_export = MetaExportConfig(
                collection_spool=export_data.get("collection_spool", ""),
                combined_feed=export_data.get("combined_feed", False),
            )

        # Launcher
        launcher_data = data.get("launcher", {})
        if launcher_data:
            m.launcher = LauncherConfig(
                type=launcher_data.get("type", "bbc_basic"),
                script=launcher_data.get("script", ""),
            )

        return m


# ──────────────────────────────────────────────
# SnackpackLoader
# ──────────────────────────────────────────────


class SnackpackLoader:
    """Loads and manages a snackpack.

    Usage:
        loader = SnackpackLoader()
        pack = loader.load("snackpacks/classic_adventures/snackpack.yaml")
        loader.register_all(pack, registry)
        loader.launch(pack, registry)
    """

    def __init__(self):
        self.registry = SnackRegistry()

    def load(self, manifest_path: Path) -> SnackpackManifest:
        """Load a snackpack.yaml manifest from disk."""
        manifest_path = Path(manifest_path).resolve()
        if not manifest_path.exists():
            raise FileNotFoundError(f"Snackpack manifest not found: {manifest_path}")

        with open(manifest_path, "r") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid snackpack manifest format in {manifest_path}")

        return SnackpackManifest.from_dict(data)

    def register_all(self, pack: SnackpackManifest, pack_dir: Path) -> int:
        """Register all snacks in the pack with the registry.

        Scans the pack directory for snack.yaml files.
        Returns the number of snacks registered.
        """
        return self.registry.scan(pack_dir)

    def get_snack_ids(self, pack: SnackpackManifest) -> List[SnackId]:
        """Get the SnackIds for all snacks referenced in the pack."""
        ids: List[SnackId] = []
        for snack_ref in pack.snacks:
            try:
                ids.append(SnackId.from_string(snack_ref))
            except ValueError:
                # Just a name without version — look it up
                entry = self.registry.find(snack_ref)
                if entry:
                    ids.append(entry.id)
        return ids

    def launch(self, pack: SnackpackManifest, registry: SnackRegistry) -> List[SnackId]:
        """Resolve and return the launch order for all snacks in the pack.

        Returns a list of SnackIds in dependency order.
        """
        all_ids: List[SnackId] = []
        for snack_ref in pack.snacks:
            try:
                sid = SnackId.from_string(snack_ref)
            except ValueError:
                entry = registry.find(snack_ref)
                if entry:
                    sid = entry.id
                else:
                    continue

            # Resolve dependencies
            try:
                order = registry.resolve_dependency_order(sid)
                for oid in order:
                    if oid not in all_ids:
                        all_ids.append(oid)
            except Exception:
                # If dependency resolution fails, just add the snack itself
                if sid not in all_ids:
                    all_ids.append(sid)

        return all_ids


# ──────────────────────────────────────────────
# Convenience
# ──────────────────────────────────────────────


def load_snackpack(path: Path) -> SnackpackManifest:
    """Convenience function to load a snackpack manifest."""
    loader = SnackpackLoader()
    return loader.load(path)
