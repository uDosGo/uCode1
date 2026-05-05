"""
Snack Manifest — snack.yaml schema and validation

Defines the container manifest format for uCode1 snacks. A snack.yaml
packages an emulated game with LENS/SKIN/MCP configuration, disk images,
and metadata.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────


class Lane(str, Enum):
    """uCode lane identifier."""
    UCODE1 = "ucode1"
    UCODE2 = "ucode2"
    UCODE3 = "ucode3"


class ContainerType(str, Enum):
    """Type of container."""
    SNACK = "snack"
    SNACKPACK = "snackpack"


class CaptureInterval(str, Enum):
    """When LENS should capture data."""
    EVERY_FRAME = "frame"
    ON_ROOM_CHANGE = "room_change"
    ON_SAVE = "save"
    ON_EVENT = "event"
    MANUAL = "manual"


class SkinTarget(str, Enum):
    """Output target for SKIN rendering."""
    THINUI = "thinui"
    CEEFAX_THINUI = "ceefax_thinui"
    TAILWIND_PROSE = "tailwind_prose"
    MARP_SLIDES = "marp_slides"
    TYPEFORM_STORY = "typeform_story"
    USXD = "usxd"


class SpoolFormat(str, Enum):
    """Serialization format for spool data."""
    JSON = "json"
    JSON_GZIPPED = "json_gzipped"
    MESSAGEPACK = "messagepack"
    MESSAGEPACK_ZSTD = "messagepack_zstd"


# ──────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────


@dataclass
class OriginSpec:
    """Original code source metadata."""
    platform: str = ""
    media: List[str] = field(default_factory=list)
    checksum: str = ""
    preservation_level: str = "bit_accurate"


@dataclass
class RuntimeSpec:
    """Emulator / runtime configuration."""
    emulator: str = ""
    memory: str = ""
    disk_drive_speed: str = "1x"
    args: List[str] = field(default_factory=list)


@dataclass
class MemoryRegion:
    """A memory region to capture via LENS."""
    name: str = ""
    address: int = 0
    size: int = 0
    description: str = ""


@dataclass
class LensConfig:
    """LENS data extraction configuration."""
    enabled: bool = True
    capture_intervals: List[str] = field(default_factory=lambda: ["frame", "room_change", "save"])
    memory_regions: List[MemoryRegion] = field(default_factory=list)
    variable_patterns: List[str] = field(default_factory=list)
    export_format: str = "spool"


@dataclass
class SkinConfig:
    """SKIN visual transformation configuration."""
    default: str = "teletext_classic"
    available: List[str] = field(default_factory=lambda: ["teletext_classic", "paper_retro", "dark_mode"])
    targets: List[str] = field(default_factory=lambda: ["thinui", "ceefax_thinui"])


@dataclass
class MCPCommand:
    """An MCP command definition."""
    name: str = ""
    description: str = ""


@dataclass
class MCPConfig:
    """MCP command configuration."""
    commands: List[MCPCommand] = field(default_factory=list)


@dataclass
class Dependency:
    """A dependency on another snack or runtime."""
    name: str = ""
    version: str = ""
    lane: Optional[str] = None


@dataclass
class SnackManifest:
    """Complete snack.yaml manifest.

    Maps directly to the uCode1 spec's snack.yaml format.
    """
    name: str = ""
    version: str = ""
    lane: str = "ucode1"
    container_type: str = "snack"
    origin: OriginSpec = field(default_factory=OriginSpec)
    runtime: RuntimeSpec = field(default_factory=RuntimeSpec)
    lens: LensConfig = field(default_factory=LensConfig)
    skin: SkinConfig = field(default_factory=SkinConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)
    depends_on: List[Dependency] = field(default_factory=list)
    entrypoint: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)

    # ── Serialisation ────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to a plain dict for YAML/JSON serialisation."""
        d: Dict[str, Any] = {
            "name": self.name,
            "version": self.version,
            "lane": self.lane,
            "container_type": self.container_type,
        }

        # Origin
        origin = {}
        if self.origin.platform:
            origin["platform"] = self.origin.platform
        if self.origin.media:
            origin["media"] = self.origin.media
        if self.origin.checksum:
            origin["checksum"] = self.origin.checksum
        if self.origin.preservation_level:
            origin["preservation_level"] = self.origin.preservation_level
        if origin:
            d["origin"] = origin

        # Runtime
        runtime = {}
        if self.runtime.emulator:
            runtime["emulator"] = self.runtime.emulator
        if self.runtime.memory:
            runtime["memory"] = self.runtime.memory
        if self.runtime.disk_drive_speed:
            runtime["disk_drive_speed"] = self.runtime.disk_drive_speed
        if self.runtime.args:
            runtime["args"] = self.runtime.args
        if runtime:
            d["runtime"] = runtime

        # LENS
        lens: Dict[str, Any] = {"enabled": self.lens.enabled}
        if self.lens.capture_intervals:
            lens["capture_intervals"] = self.lens.capture_intervals
        if self.lens.memory_regions:
            lens["memory_regions"] = [
                {
                    "name": r.name,
                    "address": hex(r.address) if isinstance(r.address, int) else r.address,
                    "size": r.size,
                    "description": r.description,
                }
                for r in self.lens.memory_regions
            ]
        if self.lens.variable_patterns:
            lens["variable_patterns"] = self.lens.variable_patterns
        if self.lens.export_format:
            lens["export_format"] = self.lens.export_format
        d["lens"] = lens

        # SKIN
        skin: Dict[str, Any] = {"default": self.skin.default}
        if self.skin.available:
            skin["available"] = self.skin.available
        if self.skin.targets:
            skin["targets"] = self.skin.targets
        d["skin"] = skin

        # MCP
        if self.mcp.commands:
            d["mcp"] = {
                "commands": [
                    {"name": c.name, "description": c.description}
                    for c in self.mcp.commands
                ]
            }

        # Dependencies
        if self.depends_on:
            d["depends_on"] = [
                {"name": dep.name, "version": dep.version}
                for dep in self.depends_on
            ]

        # Misc
        if self.entrypoint:
            d["entrypoint"] = self.entrypoint
        if self.description:
            d["description"] = self.description
        if self.tags:
            d["tags"] = self.tags

        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SnackManifest":
        """Create a manifest from a parsed YAML/JSON dict."""
        m = cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            lane=data.get("lane", "ucode1"),
            container_type=data.get("container_type", "snack"),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            entrypoint=data.get("entrypoint", ""),
        )

        # Origin
        origin_data = data.get("origin", {})
        if origin_data:
            m.origin = OriginSpec(
                platform=origin_data.get("platform", ""),
                media=origin_data.get("media", []),
                checksum=origin_data.get("checksum", ""),
                preservation_level=origin_data.get("preservation_level", "bit_accurate"),
            )

        # Runtime
        runtime_data = data.get("runtime", {})
        if runtime_data:
            m.runtime = RuntimeSpec(
                emulator=runtime_data.get("emulator", ""),
                memory=runtime_data.get("memory", ""),
                disk_drive_speed=runtime_data.get("disk_drive_speed", "1x"),
                args=runtime_data.get("args", []),
            )

        # LENS
        lens_data = data.get("lens", {})
        if lens_data:
            regions = []
            for r in lens_data.get("memory_regions", []):
                addr = r.get("address", 0)
                if isinstance(addr, str) and addr.startswith("0x"):
                    addr = int(addr, 16)
                regions.append(MemoryRegion(
                    name=r.get("name", ""),
                    address=addr,
                    size=r.get("size", 0),
                    description=r.get("description", ""),
                ))
            m.lens = LensConfig(
                enabled=lens_data.get("enabled", True),
                capture_intervals=lens_data.get("capture_intervals", ["frame", "room_change", "save"]),
                memory_regions=regions,
                variable_patterns=lens_data.get("variable_patterns", []),
                export_format=lens_data.get("export_format", "spool"),
            )

        # SKIN
        skin_data = data.get("skin", {})
        if skin_data:
            m.skin = SkinConfig(
                default=skin_data.get("default", "teletext_classic"),
                available=skin_data.get("available", ["teletext_classic", "paper_retro", "dark_mode"]),
                targets=skin_data.get("targets", ["thinui", "ceefax_thinui"]),
            )

        # MCP
        mcp_data = data.get("mcp", {})
        if mcp_data:
            commands = []
            for c in mcp_data.get("commands", []):
                commands.append(MCPCommand(
                    name=c.get("name", ""),
                    description=c.get("description", ""),
                ))
            m.mcp = MCPConfig(commands=commands)

        # Dependencies
        deps_data = data.get("depends_on", [])
        if deps_data:
            m.depends_on = [
                Dependency(
                    name=d.get("name", ""),
                    version=d.get("version", ""),
                    lane=d.get("lane"),
                )
                for d in deps_data
            ]

        return m


# ──────────────────────────────────────────────
# I/O helpers
# ──────────────────────────────────────────────


def load_manifest(path: Path) -> SnackManifest:
    """Load a snack.yaml manifest from disk."""
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid manifest format in {path}")

    return SnackManifest.from_dict(data)


def save_manifest(manifest: SnackManifest, path: Path) -> None:
    """Save a snack.yaml manifest to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(manifest.to_dict(), f, default_flow_style=False, sort_keys=False)


def validate_manifest(manifest: SnackManifest) -> List[str]:
    """Validate a manifest and return a list of error messages (empty = valid)."""
    errors: List[str] = []

    if not manifest.name:
        errors.append("name is required")
    if not manifest.version:
        errors.append("version is required")
    if manifest.lane not in ("ucode1", "ucode2", "ucode3"):
        errors.append(f"lane must be one of: ucode1, ucode2, ucode3 (got {manifest.lane!r})")
    if manifest.container_type not in ("snack", "snackpack"):
        errors.append(f"container_type must be one of: snack, snackpack (got {manifest.container_type!r})")
    if not manifest.entrypoint:
        errors.append("entrypoint is required")
    if not manifest.runtime.emulator:
        errors.append("runtime.emulator is required")

    return errors
