"""
uCode1 Snack Container Format

This module implements the uCode1-specific Snack container format as described
in the uCode1 specification. A Snack is a containerised emulation environment
that packages:

- The original game binary (disks, ROMs, or code)
- A minimal emulator (BBC BASIC runtime)
- LENS data extraction rules
- SKIN visual transformation layers
- MCP command handlers
- Metadata (name, lane, dependencies)

Key principle: The original code runs unchanged. Only the input/output is
intercepted, extracted, and reskinned.
"""

from .manifest import (
    SnackManifest,
    OriginSpec,
    RuntimeSpec,
    LensConfig,
    SkinConfig,
    MCPConfig,
    MCPCommand,
    MemoryRegion,
    Dependency,
    Lane,
    ContainerType,
    CaptureInterval,
    SkinTarget,
    SpoolFormat,
    load_manifest,
    save_manifest,
    validate_manifest,
)
from .loader import (
    SnackLoader,
    LoadedSnack,
    LoadError,
    MountError,
    HookError,
    SkinError,
    IpcError,
    SpawnError,
)
from .registry import (
    SnackRegistry,
    SnackId,
    RegistryError,
    DependencyError,
)
from .snackpack import (
    SnackpackManifest,
    SnackpackLoader,
    load_snackpack,
)

__all__ = [
    # Manifest
    "SnackManifest",
    "OriginSpec",
    "RuntimeSpec",
    "LensConfig",
    "SkinConfig",
    "MCPConfig",
    "MCPCommand",
    "MemoryRegion",
    "Dependency",
    "Lane",
    "ContainerType",
    "CaptureInterval",
    "SkinTarget",
    "SpoolFormat",
    "load_manifest",
    "save_manifest",
    "validate_manifest",
    # Loader
    "SnackLoader",
    "LoadedSnack",
    "LoadError",
    "MountError",
    "HookError",
    "SkinError",
    "IpcError",
    "SpawnError",
    # Registry
    "SnackRegistry",
    "SnackId",
    "RegistryError",
    "DependencyError",
    # Snackpack
    "SnackpackManifest",
    "SnackpackLoader",
    "load_snackpack",
]
