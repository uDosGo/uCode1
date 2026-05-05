"""
Snack Loader — loads, isolates, and spawns a snack container.

The SnackLoader is responsible for:
1. Reading a snack.yaml manifest
2. Mounting disk images (read-only for originals)
3. Injecting LENS memory hooks
4. Setting up the SKIN pipeline
5. Creating IPC channels (Feed/Spool/MCP)
6. Spawning the snack process with isolation
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .manifest import (
    SnackManifest,
    LensConfig,
    SkinConfig,
    MCPConfig,
    load_manifest,
    validate_manifest,
)


# ──────────────────────────────────────────────
# Custom exceptions
# ──────────────────────────────────────────────


class LoadError(Exception):
    """Raised when a snack cannot be loaded."""
    pass


class MountError(LoadError):
    """Raised when disk images cannot be mounted."""
    pass


class HookError(LoadError):
    """Raised when LENS hooks cannot be injected."""
    pass


class SkinError(LoadError):
    """Raised when the SKIN pipeline cannot be set up."""
    pass


class IpcError(LoadError):
    """Raised when IPC channels cannot be created."""
    pass


class SpawnError(LoadError):
    """Raised when the snack process cannot be spawned."""
    pass


# ──────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────


@dataclass
class MountPoint:
    """A mounted disk image or directory."""
    source: Path
    target: str
    writable: bool = False


@dataclass
class IpcChannels:
    """IPC channels for Feed/Spool/MCP communication."""
    feed_dir: Path
    spool_dir: Path
    mcp_dir: Path


@dataclass
class LoadedSnack:
    """A fully loaded and ready-to-run snack."""
    id: str
    manifest: SnackManifest
    snack_dir: Path
    sandbox_root: Path
    mounts: List[MountPoint] = field(default_factory=list)
    ipc: Optional[IpcChannels] = None
    process: Optional[subprocess.Popen] = None


# ──────────────────────────────────────────────
# SnackLoader
# ──────────────────────────────────────────────


class SnackLoader:
    """Loads, isolates, and spawns a snack container.

    Usage:
        loader = SnackLoader()
        loaded = loader.load("snacks/eamon/snack.yaml")
        loaded = loader.mount_disks(loaded)
        loaded = loader.setup_ipc(loaded)
        loaded = loader.spawn(loaded)
    """

    def __init__(self, sandbox_root: Optional[Path] = None):
        self.sandbox_root = sandbox_root or Path(tempfile.gettempdir()) / "udos-snacks"
        self.sandbox_root.mkdir(parents=True, exist_ok=True)

    # ── Load ─────────────────────────────────

    def load(self, manifest_path: Path) -> LoadedSnack:
        """Load a snack.yaml manifest and prepare the sandbox directory."""
        manifest_path = Path(manifest_path).resolve()
        if not manifest_path.exists():
            raise LoadError(f"Manifest not found: {manifest_path}")

        manifest = load_manifest(manifest_path)

        # Validate
        errors = validate_manifest(manifest)
        if errors:
            raise LoadError(f"Invalid manifest: {'; '.join(errors)}")

        # Create a unique sandbox directory
        snack_id = f"{manifest.name}@{manifest.version}".replace(" ", "_")
        sandbox = self.sandbox_root / snack_id
        sandbox.mkdir(parents=True, exist_ok=True)

        # The snack directory is the parent of the manifest
        snack_dir = manifest_path.parent.resolve()

        return LoadedSnack(
            id=snack_id,
            manifest=manifest,
            snack_dir=snack_dir,
            sandbox_root=sandbox,
        )

    # ── Mount disks ──────────────────────────

    def mount_disks(self, loaded: LoadedSnack) -> LoadedSnack:
        """Prepare disk image mounts (symlinks or copies).

        In a real implementation this would use FUSE mounts or loopback
        devices. For now we symlink the disk images into the sandbox.
        """
        manifest = loaded.manifest
        disks_dir = loaded.sandbox_root / "disks"
        disks_dir.mkdir(parents=True, exist_ok=True)

        for media_path in manifest.origin.media:
            source = loaded.snack_dir / media_path
            if not source.exists():
                # Try relative to the manifest directory
                alt = loaded.snack_dir.parent / media_path
                if alt.exists():
                    source = alt
                else:
                    raise MountError(f"Disk image not found: {media_path} (tried {source}, {alt})")

            target = disks_dir / source.name
            if not target.exists():
                os.symlink(str(source), str(target))

            loaded.mounts.append(MountPoint(
                source=source,
                target=str(target),
                writable=False,
            ))

        return loaded

    # ── Setup IPC channels ───────────────────

    def setup_ipc(self, loaded: LoadedSnack) -> LoadedSnack:
        """Create IPC channel directories for Feed/Spool/MCP."""
        ipc_root = loaded.sandbox_root / "ipc"
        ipc_root.mkdir(parents=True, exist_ok=True)

        feed_dir = ipc_root / "feed"
        spool_dir = ipc_root / "spool"
        mcp_dir = ipc_root / "mcp"

        for d in (feed_dir, spool_dir, mcp_dir):
            d.mkdir(parents=True, exist_ok=True)

        loaded.ipc = IpcChannels(
            feed_dir=feed_dir,
            spool_dir=spool_dir,
            mcp_dir=mcp_dir,
        )

        return loaded

    # ── Inject LENS hooks ────────────────────

    def inject_lens_hooks(self, loaded: LoadedSnack) -> LoadedSnack:
        """Write LENS configuration into the sandbox for the interpreter to pick up.

        The BBC BASIC interpreter (core_py/bbc/interpreter.py) reads this
        config at startup to know which variables to watch and which memory
        regions to capture.
        """
        lens_config = loaded.manifest.lens
        config_dir = loaded.sandbox_root / "lens"
        config_dir.mkdir(parents=True, exist_ok=True)

        # Write LENS config as JSON
        import json
        config = {
            "enabled": lens_config.enabled,
            "capture_intervals": lens_config.capture_intervals,
            "variable_patterns": lens_config.variable_patterns,
            "memory_regions": [
                {
                    "name": r.name,
                    "address": r.address,
                    "size": r.size,
                    "description": r.description,
                }
                for r in lens_config.memory_regions
            ],
            "export_format": lens_config.export_format,
        }
        with open(config_dir / "lens_config.json", "w") as f:
            json.dump(config, f, indent=2)

        return loaded

    # ── Setup SKIN pipeline ──────────────────

    def setup_skin_pipeline(self, loaded: LoadedSnack) -> LoadedSnack:
        """Write SKIN configuration into the sandbox."""
        skin_config = loaded.manifest.skin
        config_dir = loaded.sandbox_root / "skin"
        config_dir.mkdir(parents=True, exist_ok=True)

        import json
        config = {
            "default": skin_config.default,
            "available": skin_config.available,
            "targets": skin_config.targets,
        }
        with open(config_dir / "skin_config.json", "w") as f:
            json.dump(config, f, indent=2)

        return loaded

    # ── Setup MCP ────────────────────────────

    def setup_mcp(self, loaded: LoadedSnack) -> LoadedSnack:
        """Write MCP command configuration into the sandbox."""
        mcp_config = loaded.manifest.mcp
        config_dir = loaded.sandbox_root / "mcp"
        config_dir.mkdir(parents=True, exist_ok=True)

        import json
        config = {
            "commands": [
                {"name": c.name, "description": c.description}
                for c in mcp_config.commands
            ],
        }
        with open(config_dir / "mcp_config.json", "w") as f:
            json.dump(config, f, indent=2)

        return loaded

    # ── Spawn ────────────────────────────────

    def spawn(self, loaded: LoadedSnack) -> LoadedSnack:
        """Spawn the snack process.

        For uCode1, this runs the BBC BASIC interpreter with the snack's
        entrypoint script. The interpreter is configured to use the LENS,
        SKIN, MCP, and Spool configs from the sandbox.
        """
        manifest = loaded.manifest
        entrypoint = loaded.snack_dir / manifest.entrypoint

        if not entrypoint.exists():
            raise SpawnError(f"Entrypoint not found: {entrypoint}")

        # Build environment
        env = os.environ.copy()
        env["UDOS_SNACK_ID"] = loaded.id
        env["UDOS_SNACK_NAME"] = manifest.name
        env["UDOS_SNACK_VERSION"] = manifest.version
        env["UDOS_SNACK_DIR"] = str(loaded.snack_dir)
        env["UDOS_SANDBOX_ROOT"] = str(loaded.sandbox_root)

        if loaded.ipc:
            env["UDOS_FEED_DIR"] = str(loaded.ipc.feed_dir)
            env["UDOS_SPOOL_DIR"] = str(loaded.ipc.spool_dir)
            env["UDOS_MCP_DIR"] = str(loaded.ipc.mcp_dir)

        # Determine the interpreter command
        # For uCode1, we use the BBC BASIC interpreter
        cmd = self._build_command(manifest, entrypoint)

        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                cwd=str(loaded.snack_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            loaded.process = process
        except FileNotFoundError as e:
            raise SpawnError(f"Failed to spawn snack process: {e}")

        return loaded

    def _build_command(self, manifest: SnackManifest, entrypoint: Path) -> List[str]:
        """Build the command to run the snack based on its runtime."""
        runtime = manifest.runtime.emulator

        if runtime == "matrix_brandy":
            return ["brandy", str(entrypoint)]
        elif runtime == "bbc_basic":
            return ["python", "-m", "core_py.bbc.interpreter", str(entrypoint)]
        elif runtime == "python":
            return [sys.executable, str(entrypoint)]
        elif runtime == "bash":
            return ["bash", str(entrypoint)]
        else:
            # Default: try to run the entrypoint directly
            return [str(entrypoint)]

    # ── Full pipeline ────────────────────────

    def load_and_spawn(self, manifest_path: Path) -> LoadedSnack:
        """Convenience method: load, mount, setup IPC, inject LENS, spawn."""
        loaded = self.load(manifest_path)
        loaded = self.mount_disks(loaded)
        loaded = self.setup_ipc(loaded)
        loaded = self.inject_lens_hooks(loaded)
        loaded = self.setup_skin_pipeline(loaded)
        loaded = self.setup_mcp(loaded)
        loaded = self.spawn(loaded)
        return loaded

    # ── Cleanup ──────────────────────────────

    def stop(self, loaded: LoadedSnack) -> None:
        """Stop the snack process and clean up."""
        if loaded.process and loaded.process.poll() is None:
            loaded.process.terminate()
            try:
                loaded.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                loaded.process.kill()

    def cleanup(self, loaded: LoadedSnack) -> None:
        """Remove the sandbox directory."""
        self.stop(loaded)
        if loaded.sandbox_root.exists():
            shutil.rmtree(loaded.sandbox_root, ignore_errors=True)
