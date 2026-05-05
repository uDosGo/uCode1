"""
Snack Registry — discover, register, and manage snacks.

The SnackRegistry maintains a catalog of available snacks and snackpacks,
providing search, validation, and dependency resolution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from .manifest import SnackManifest, load_manifest, validate_manifest


# ──────────────────────────────────────────────
# Custom exceptions
# ──────────────────────────────────────────────


class RegistryError(Exception):
    """Raised when a registry operation fails."""
    pass


class DependencyError(RegistryError):
    """Raised when snack dependencies cannot be satisfied."""
    pass


# ──────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────


@dataclass
class SnackId:
    """Unique identifier for a snack."""
    name: str
    version: str

    def __str__(self) -> str:
        return f"{self.name}@{self.version}"

    def __hash__(self) -> int:
        return hash(str(self))

    @classmethod
    def from_string(cls, s: str) -> "SnackId":
        """Parse a snack ID from 'name@version' format."""
        parts = s.split("@", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid snack ID format: {s!r} (expected 'name@version')")
        return cls(name=parts[0], version=parts[1])


@dataclass
class RegistryEntry:
    """An entry in the snack registry."""
    id: SnackId
    manifest: SnackManifest
    manifest_path: Path
    snack_dir: Path


# ──────────────────────────────────────────────
# SnackRegistry
# ──────────────────────────────────────────────


class SnackRegistry:
    """Registry of available snacks.

    Scans directories for snack.yaml files and provides lookup/search.

    Usage:
        registry = SnackRegistry()
        registry.scan("snacks/")
        registry.scan("snackpacks/")

        snack = registry.find("eamon")
        for s in registry.list():
            print(s.id, s.manifest.description)
    """

    def __init__(self):
        self._entries: Dict[str, RegistryEntry] = {}  # id string -> entry
        self._by_name: Dict[str, List[RegistryEntry]] = {}  # name -> versions

    # ── Scanning ─────────────────────────────

    def scan(self, directory: Path) -> int:
        """Scan a directory recursively for snack.yaml files.

        Returns the number of snacks registered.
        """
        directory = Path(directory).resolve()
        if not directory.exists():
            return 0

        count = 0
        for manifest_path in directory.rglob("snack.yaml"):
            try:
                self._register(manifest_path)
                count += 1
            except (RegistryError, Exception) as e:
                # Skip invalid manifests
                import warnings
                warnings.warn(f"Skipping {manifest_path}: {e}")
                continue

        return count

    def _register(self, manifest_path: Path) -> None:
        """Register a single snack from its manifest path."""
        manifest = load_manifest(manifest_path)

        errors = validate_manifest(manifest)
        if errors:
            raise RegistryError(f"Invalid manifest: {'; '.join(errors)}")

        snack_id = SnackId(name=manifest.name, version=manifest.version)
        snack_dir = manifest_path.parent.resolve()

        entry = RegistryEntry(
            id=snack_id,
            manifest=manifest,
            manifest_path=manifest_path,
            snack_dir=snack_dir,
        )

        key = str(snack_id)
        self._entries[key] = entry

        if snack_id.name not in self._by_name:
            self._by_name[snack_id.name] = []
        self._by_name[snack_id.name].append(entry)

    # ── Registration ─────────────────────────

    def register(self, manifest_path: Path) -> SnackId:
        """Register a single snack from its manifest path.

        Returns the SnackId of the registered snack.
        """
        self._register(manifest_path)
        manifest = load_manifest(manifest_path)
        return SnackId(name=manifest.name, version=manifest.version)

    def unregister(self, snack_id: SnackId) -> bool:
        """Remove a snack from the registry.

        Returns True if the snack was found and removed.
        """
        key = str(snack_id)
        if key in self._entries:
            del self._entries[key]
            # Clean up by_name index
            if snack_id.name in self._by_name:
                self._by_name[snack_id.name] = [
                    e for e in self._by_name[snack_id.name]
                    if e.id.version != snack_id.version
                ]
                if not self._by_name[snack_id.name]:
                    del self._by_name[snack_id.name]
            return True
        return False

    # ── Lookup ───────────────────────────────

    def find(self, name: str, version: Optional[str] = None) -> Optional[RegistryEntry]:
        """Find a snack by name and optional version.

        If version is None, returns the latest version.
        """
        if name not in self._by_name:
            return None

        entries = self._by_name[name]
        if version:
            for e in entries:
                if e.id.version == version:
                    return e
            return None

        # Return the latest version (simple string comparison)
        return max(entries, key=lambda e: e.id.version)

    def get(self, snack_id: SnackId) -> Optional[RegistryEntry]:
        """Get a snack by its full ID."""
        return self._entries.get(str(snack_id))

    # ── Listing ──────────────────────────────

    def list(self, lane: Optional[str] = None) -> List[RegistryEntry]:
        """List all registered snacks, optionally filtered by lane."""
        entries = list(self._entries.values())
        if lane:
            entries = [e for e in entries if e.manifest.lane == lane]
        return sorted(entries, key=lambda e: str(e.id))

    def list_names(self) -> List[str]:
        """List all unique snack names."""
        return sorted(self._by_name.keys())

    # ── Validation ───────────────────────────

    def validate_dependencies(self, snack_id: SnackId) -> List[str]:
        """Check that all dependencies of a snack are available.

        Returns a list of missing dependency names (empty = all satisfied).
        """
        entry = self.get(snack_id)
        if not entry:
            return [f"Snack not found: {snack_id}"]

        missing: List[str] = []
        for dep in entry.manifest.depends_on:
            if dep.name not in self._by_name:
                missing.append(f"{dep.name}@{dep.version}")
        return missing

    def resolve_dependency_order(self, snack_id: SnackId) -> List[SnackId]:
        """Resolve the dependency order for a snack (topological sort).

        Returns a list of SnackIds in dependency order (dependencies first).
        Raises DependencyError if a circular dependency is detected.
        """
        from collections import defaultdict, deque

        # Build adjacency list
        graph: Dict[str, Set[str]] = defaultdict(set)
        in_degree: Dict[str, int] = defaultdict(int)

        def add_deps(sid: SnackId, visited: Set[str]) -> None:
            key = str(sid)
            if key in visited:
                return
            visited.add(key)

            entry = self.get(sid)
            if not entry:
                return

            for dep in entry.manifest.depends_on:
                dep_id = SnackId(name=dep.name, version=dep.version)
                dep_key = str(dep_id)
                graph[dep_key].add(key)
                if dep_key not in in_degree:
                    in_degree[dep_key] = 0
                in_degree[key] += 1
                add_deps(dep_id, visited)

        visited: Set[str] = set()
        add_deps(snack_id, visited)

        # Kahn's algorithm
        queue = deque([n for n, d in in_degree.items() if d == 0])
        # Also add nodes with no dependencies
        for key in visited:
            if key not in in_degree:
                queue.append(key)

        result: List[str] = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(visited):
            raise DependencyError("Circular dependency detected")

        return [SnackId.from_string(s) for s in result]

    # ── Persistence ──────────────────────────

    def save_index(self, path: Path) -> None:
        """Save the registry index to a JSON file."""
        index = []
        for entry in self._entries.values():
            index.append({
                "id": str(entry.id),
                "name": entry.id.name,
                "version": entry.id.version,
                "lane": entry.manifest.lane,
                "description": entry.manifest.description,
                "tags": entry.manifest.tags,
                "manifest_path": str(entry.manifest_path),
            })

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(index, f, indent=2)

    def load_index(self, path: Path) -> int:
        """Load a previously saved registry index.

        Returns the number of entries loaded.
        """
        if not path.exists():
            return 0

        with open(path, "r") as f:
            index = json.load(f)

        count = 0
        for item in index:
            manifest_path = Path(item["manifest_path"])
            if manifest_path.exists():
                try:
                    self._register(manifest_path)
                    count += 1
                except Exception:
                    continue

        return count
