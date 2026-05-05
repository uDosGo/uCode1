"""
Tests for the uCode1 Snack Container Format (snack.yaml, loader, registry, snackpack).
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core_py.snack_container import (
    SnackManifest,
    SnackLoader,
    SnackRegistry,
    SnackpackManifest,
    SnackpackLoader,
    SnackId,
    OriginSpec,
    RuntimeSpec,
    LensConfig,
    SkinConfig,
    MCPConfig,
    MemoryRegion,
    MCPCommand,
    Dependency,
    load_manifest,
    save_manifest,
    validate_manifest,
    LoadError,
    RegistryError,
)


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────


@pytest.fixture
def sample_manifest_dict():
    """A complete snack.yaml as a dict."""
    return {
        "name": "Test Adventure",
        "version": "1.0.0",
        "lane": "ucode1",
        "container_type": "snack",
        "origin": {
            "platform": "apple2",
            "media": ["disks/test.dsk"],
            "checksum": "sha256:abc123",
            "preservation_level": "bit_accurate",
        },
        "runtime": {
            "emulator": "bbc_basic",
            "memory": "32K",
            "disk_drive_speed": "1x",
        },
        "lens": {
            "enabled": True,
            "capture_intervals": ["frame", "room_change"],
            "variable_patterns": ["^HP%$", "^GOLD%$"],
            "memory_regions": [
                {"name": "tilemap", "address": "0x6000", "size": 225, "description": "15x15 grid"}
            ],
            "export_format": "spool",
        },
        "skin": {
            "default": "teletext_classic",
            "available": ["teletext_classic", "paper_retro"],
            "targets": ["thinui", "ceefax_thinui"],
        },
        "mcp": {
            "commands": [
                {"name": "pause", "description": "Pause game"},
                {"name": "save", "description": "Save state"},
            ]
        },
        "depends_on": [
            {"name": "bbc_basic_runtime", "version": "1.0.0"}
        ],
        "entrypoint": "scripts/boot.bbc",
        "description": "A test adventure game",
        "tags": ["adventure", "test"],
    }


@pytest.fixture
def sample_manifest(sample_manifest_dict):
    """A complete SnackManifest object."""
    return SnackManifest.from_dict(sample_manifest_dict)


@pytest.fixture
def temp_dir():
    """A temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# ──────────────────────────────────────────────
# Manifest Tests
# ──────────────────────────────────────────────


class TestSnackManifest:
    def test_from_dict_full(self, sample_manifest_dict):
        """Test creating a manifest from a full dict."""
        m = SnackManifest.from_dict(sample_manifest_dict)
        assert m.name == "Test Adventure"
        assert m.version == "1.0.0"
        assert m.lane == "ucode1"
        assert m.container_type == "snack"
        assert m.entrypoint == "scripts/boot.bbc"
        assert m.description == "A test adventure game"
        assert m.tags == ["adventure", "test"]

    def test_from_dict_origin(self, sample_manifest):
        """Test origin parsing."""
        assert sample_manifest.origin.platform == "apple2"
        assert sample_manifest.origin.media == ["disks/test.dsk"]
        assert sample_manifest.origin.checksum == "sha256:abc123"
        assert sample_manifest.origin.preservation_level == "bit_accurate"

    def test_from_dict_runtime(self, sample_manifest):
        """Test runtime parsing."""
        assert sample_manifest.runtime.emulator == "bbc_basic"
        assert sample_manifest.runtime.memory == "32K"
        assert sample_manifest.runtime.disk_drive_speed == "1x"

    def test_from_dict_lens(self, sample_manifest):
        """Test LENS config parsing."""
        assert sample_manifest.lens.enabled is True
        assert sample_manifest.lens.capture_intervals == ["frame", "room_change"]
        assert sample_manifest.lens.variable_patterns == ["^HP%$", "^GOLD%$"]
        assert sample_manifest.lens.export_format == "spool"
        assert len(sample_manifest.lens.memory_regions) == 1
        region = sample_manifest.lens.memory_regions[0]
        assert region.name == "tilemap"
        assert region.address == 0x6000
        assert region.size == 225

    def test_from_dict_skin(self, sample_manifest):
        """Test SKIN config parsing."""
        assert sample_manifest.skin.default == "teletext_classic"
        assert sample_manifest.skin.available == ["teletext_classic", "paper_retro"]
        assert sample_manifest.skin.targets == ["thinui", "ceefax_thinui"]

    def test_from_dict_mcp(self, sample_manifest):
        """Test MCP config parsing."""
        assert len(sample_manifest.mcp.commands) == 2
        assert sample_manifest.mcp.commands[0].name == "pause"
        assert sample_manifest.mcp.commands[1].name == "save"

    def test_from_dict_dependencies(self, sample_manifest):
        """Test dependency parsing."""
        assert len(sample_manifest.depends_on) == 1
        assert sample_manifest.depends_on[0].name == "bbc_basic_runtime"
        assert sample_manifest.depends_on[0].version == "1.0.0"

    def test_to_dict_roundtrip(self, sample_manifest_dict):
        """Test that to_dict produces the same structure as the input."""
        m = SnackManifest.from_dict(sample_manifest_dict)
        result = m.to_dict()
        assert result["name"] == sample_manifest_dict["name"]
        assert result["version"] == sample_manifest_dict["version"]
        assert result["lane"] == sample_manifest_dict["lane"]
        assert result["origin"]["platform"] == sample_manifest_dict["origin"]["platform"]
        assert result["runtime"]["emulator"] == sample_manifest_dict["runtime"]["emulator"]
        assert result["lens"]["enabled"] == sample_manifest_dict["lens"]["enabled"]
        assert result["skin"]["default"] == sample_manifest_dict["skin"]["default"]
        assert len(result["mcp"]["commands"]) == 2

    def test_from_dict_minimal(self):
        """Test creating a manifest with minimal fields."""
        m = SnackManifest.from_dict({
            "name": "Minimal",
            "version": "1.0.0",
            "entrypoint": "main.bbc",
        })
        assert m.name == "Minimal"
        assert m.version == "1.0.0"
        assert m.lane == "ucode1"  # default
        assert m.container_type == "snack"  # default
        assert m.entrypoint == "main.bbc"
        assert m.origin.platform == ""  # default
        assert m.runtime.emulator == ""  # default

    def test_hex_address_parsing(self):
        """Test that hex addresses are parsed correctly."""
        data = {
            "name": "Test",
            "version": "1.0.0",
            "entrypoint": "main.bbc",
            "lens": {
                "memory_regions": [
                    {"name": "test", "address": "0x6000", "size": 100},
                    {"name": "test2", "address": 24576, "size": 200},
                ]
            },
        }
        m = SnackManifest.from_dict(data)
        assert m.lens.memory_regions[0].address == 0x6000
        assert m.lens.memory_regions[1].address == 24576


class TestManifestIO:
    def test_save_and_load_yaml(self, sample_manifest, temp_dir):
        """Test saving and loading a manifest as YAML."""
        path = temp_dir / "snack.yaml"
        save_manifest(sample_manifest, path)
        assert path.exists()

        loaded = load_manifest(path)
        assert loaded.name == sample_manifest.name
        assert loaded.version == sample_manifest.version
        assert loaded.origin.platform == sample_manifest.origin.platform
        assert loaded.lens.enabled == sample_manifest.lens.enabled
        assert loaded.skin.default == sample_manifest.skin.default
        assert len(loaded.mcp.commands) == len(sample_manifest.mcp.commands)

    def test_load_nonexistent(self, temp_dir):
        """Test loading a nonexistent manifest."""
        with pytest.raises(FileNotFoundError):
            load_manifest(temp_dir / "nonexistent.yaml")

    def test_load_invalid_yaml(self, temp_dir):
        """Test loading invalid YAML raises an error."""
        path = temp_dir / "snack.yaml"
        with open(path, "w") as f:
            f.write("not: valid: yaml: [[[")
        with pytest.raises((ValueError, yaml.YAMLError)):
            load_manifest(path)


class TestValidateManifest:
    def test_valid_manifest(self, sample_manifest):
        """Test that a valid manifest passes validation."""
        errors = validate_manifest(sample_manifest)
        assert errors == []

    def test_missing_name(self):
        """Test validation catches missing name."""
        m = SnackManifest(version="1.0.0", entrypoint="main.bbc")
        errors = validate_manifest(m)
        assert "name is required" in errors

    def test_missing_version(self):
        """Test validation catches missing version."""
        m = SnackManifest(name="Test", entrypoint="main.bbc")
        errors = validate_manifest(m)
        assert "version is required" in errors

    def test_invalid_lane(self):
        """Test validation catches invalid lane."""
        m = SnackManifest(name="Test", version="1.0.0", lane="invalid", entrypoint="main.bbc")
        errors = validate_manifest(m)
        assert any("lane" in e for e in errors)

    def test_missing_entrypoint(self):
        """Test validation catches missing entrypoint."""
        m = SnackManifest(name="Test", version="1.0.0")
        errors = validate_manifest(m)
        assert "entrypoint is required" in errors

    def test_missing_emulator(self):
        """Test validation catches missing runtime.emulator."""
        m = SnackManifest(name="Test", version="1.0.0", entrypoint="main.bbc")
        errors = validate_manifest(m)
        assert "runtime.emulator is required" in errors


# ──────────────────────────────────────────────
# SnackId Tests
# ──────────────────────────────────────────────


class TestSnackId:
    def test_from_string(self):
        """Test parsing a snack ID from string."""
        sid = SnackId.from_string("eamon@1.0.0")
        assert sid.name == "eamon"
        assert sid.version == "1.0.0"

    def test_from_string_invalid(self):
        """Test parsing an invalid snack ID."""
        with pytest.raises(ValueError):
            SnackId.from_string("invalid")

    def test_str(self):
        """Test string representation."""
        sid = SnackId(name="eamon", version="1.0.0")
        assert str(sid) == "eamon@1.0.0"

    def test_hash(self):
        """Test that SnackId is hashable."""
        sid1 = SnackId(name="eamon", version="1.0.0")
        sid2 = SnackId(name="eamon", version="1.0.0")
        assert hash(sid1) == hash(sid2)
        assert sid1 == sid2


# ──────────────────────────────────────────────
# SnackRegistry Tests
# ──────────────────────────────────────────────


class TestSnackRegistry:
    def test_register_and_find(self, temp_dir, sample_manifest_dict):
        """Test registering a snack and finding it."""
        snack_dir = temp_dir / "snacks" / "test_adventure"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        registry = SnackRegistry()
        sid = registry.register(manifest_path)
        assert sid.name == "Test Adventure"
        assert sid.version == "1.0.0"

        entry = registry.find("Test Adventure")
        assert entry is not None
        assert entry.id.name == "Test Adventure"

        entry = registry.find("Test Adventure", "1.0.0")
        assert entry is not None

        assert registry.find("Nonexistent") is None

    def test_register_and_unregister(self, temp_dir, sample_manifest_dict):
        """Test unregistering a snack."""
        snack_dir = temp_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        registry = SnackRegistry()
        sid = registry.register(manifest_path)
        assert registry.find("Test Adventure") is not None

        result = registry.unregister(sid)
        assert result is True
        assert registry.find("Test Adventure") is None

    def test_list(self, temp_dir):
        """Test listing snacks."""
        registry = SnackRegistry()

        for name in ["Game1", "Game2"]:
            d = {
                "name": name,
                "version": "1.0.0",
                "lane": "ucode1",
                "entrypoint": "main.bbc",
                "runtime": {"emulator": "bbc_basic"},
            }
            snack_dir = temp_dir / "snacks" / name
            snack_dir.mkdir(parents=True)
            manifest_path = snack_dir / "snack.yaml"
            with open(manifest_path, "w") as f:
                yaml.safe_dump(d, f)
            registry.register(manifest_path)

        entries = registry.list()
        assert len(entries) == 2
        names = [e.id.name for e in entries]
        assert "Game1" in names
        assert "Game2" in names

    def test_list_by_lane(self, temp_dir):
        """Test listing snacks filtered by lane."""
        registry = SnackRegistry()

        for name, lane in [("Game1", "ucode1"), ("Game2", "ucode2")]:
            d = {
                "name": name,
                "version": "1.0.0",
                "lane": lane,
                "entrypoint": "main.bbc",
                "runtime": {"emulator": "bbc_basic"},
            }
            snack_dir = temp_dir / "snacks" / name
            snack_dir.mkdir(parents=True)
            manifest_path = snack_dir / "snack.yaml"
            with open(manifest_path, "w") as f:
                yaml.safe_dump(d, f)
            registry.register(manifest_path)

        ucode1_entries = registry.list(lane="ucode1")
        assert len(ucode1_entries) == 1
        assert ucode1_entries[0].id.name == "Game1"

    def test_scan_directory(self, temp_dir, sample_manifest_dict):
        """Test scanning a directory for snack manifests."""
        for name in ["snack_a", "snack_b"]:
            d = dict(sample_manifest_dict)
            d["name"] = name
            snack_dir = temp_dir / "games" / name
            snack_dir.mkdir(parents=True)
            manifest_path = snack_dir / "snack.yaml"
            with open(manifest_path, "w") as f:
                yaml.safe_dump(d, f)

        registry = SnackRegistry()
        count = registry.scan(temp_dir / "games")
        assert count == 2

    def test_save_and_load_index(self, temp_dir, sample_manifest_dict):
        """Test saving and loading the registry index."""
        snack_dir = temp_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        registry = SnackRegistry()
        registry.register(manifest_path)

        index_path = temp_dir / "index.json"
        registry.save_index(index_path)
        assert index_path.exists()

        registry2 = SnackRegistry()
        count = registry2.load_index(index_path)
        assert count == 1
        assert registry2.find("Test Adventure") is not None


# ──────────────────────────────────────────────
# SnackLoader Tests
# ──────────────────────────────────────────────


class TestSnackLoader:
    def test_load_manifest(self, temp_dir, sample_manifest_dict):
        """Test loading a snack from a manifest path."""
        snack_dir = temp_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        loader = SnackLoader(sandbox_root=temp_dir / "sandbox")
        loaded = loader.load(manifest_path)
        assert loaded.manifest.name == "Test Adventure"
        assert loaded.manifest.version == "1.0.0"
        assert loaded.snack_dir == snack_dir.resolve()
        assert loaded.sandbox_root.exists()

    def test_load_nonexistent(self, temp_dir):
        """Test loading a nonexistent manifest."""
        loader = SnackLoader()
        with pytest.raises(LoadError):
            loader.load(temp_dir / "nonexistent.yaml")

    def test_load_invalid_manifest(self, temp_dir):
        """Test loading an invalid manifest."""
        path = temp_dir / "snack.yaml"
        with open(path, "w") as f:
            yaml.safe_dump({"name": "Test"}, f)

        loader = SnackLoader()
        with pytest.raises(LoadError, match="Invalid manifest"):
            loader.load(path)

    def test_setup_ipc(self, temp_dir, sample_manifest_dict):
        """Test IPC channel setup."""
        snack_dir = temp_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        loader = SnackLoader(sandbox_root=temp_dir / "sandbox")
        loaded = loader.load(manifest_path)
        loaded = loader.setup_ipc(loaded)

        assert loaded.ipc is not None
        assert loaded.ipc.feed_dir.exists()
        assert loaded.ipc.spool_dir.exists()
        assert loaded.ipc.mcp_dir.exists()

    def test_inject_lens_hooks(self, temp_dir, sample_manifest_dict):
        """Test LENS hook injection."""
        snack_dir = temp_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        loader = SnackLoader(sandbox_root=temp_dir / "sandbox")
        loaded = loader.load(manifest_path)
        loaded = loader.inject_lens_hooks(loaded)

        config_path = loaded.sandbox_root / "lens" / "lens_config.json"
        assert config_path.exists()

        with open(config_path) as f:
            config = json.load(f)
        assert config["enabled"] is True
        assert config["variable_patterns"] == ["^HP%$", "^GOLD%$"]

    def test_setup_skin_pipeline(self, temp_dir, sample_manifest_dict):
        """Test SKIN pipeline setup."""
        snack_dir = temp_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        loader = SnackLoader(sandbox_root=temp_dir / "sandbox")
        loaded = loader.load(manifest_path)
        loaded = loader.setup_skin_pipeline(loaded)

        config_path = loaded.sandbox_root / "skin" / "skin_config.json"
        assert config_path.exists()

        with open(config_path) as f:
            config = json.load(f)
        assert config["default"] == "teletext_classic"

    def test_setup_mcp(self, temp_dir, sample_manifest_dict):
        """Test MCP setup."""
        snack_dir = temp_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        loader = SnackLoader(sandbox_root=temp_dir / "sandbox")
        loaded = loader.load(manifest_path)
        loaded = loader.setup_mcp(loaded)

        config_path = loaded.sandbox_root / "mcp" / "mcp_config.json"
        assert config_path.exists()

        with open(config_path) as f:
            config = json.load(f)
        assert len(config["commands"]) == 2

    def test_mount_disks(self, temp_dir, sample_manifest_dict):
        """Test disk image mounting."""
        snack_dir = temp_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)

        disks_dir = snack_dir / "disks"
        disks_dir.mkdir()
        disk_path = disks_dir / "test.dsk"
        disk_path.write_text("fake disk data")

        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        loader = SnackLoader(sandbox_root=temp_dir / "sandbox")
        loaded = loader.load(manifest_path)
        loaded = loader.mount_disks(loaded)

        assert len(loaded.mounts) == 1
        assert loaded.mounts[0].source == disk_path.resolve()
        assert loaded.mounts[0].writable is False

    def test_mount_disks_missing(self, temp_dir, sample_manifest_dict):
        """Test mounting a missing disk image raises an error."""
        snack_dir = temp_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        loader = SnackLoader(sandbox_root=temp_dir / "sandbox")
        loaded = loader.load(manifest_path)
        with pytest.raises(LoadError, match="Disk image not found"):
            loader.mount_disks(loaded)

    def test_spawn_missing_entrypoint(self, temp_dir, sample_manifest_dict):
        """Test spawning with a missing entrypoint."""
        snack_dir = temp_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        loader = SnackLoader(sandbox_root=temp_dir / "sandbox")
        loaded = loader.load(manifest_path)
        with pytest.raises(LoadError, match="Entrypoint not found"):
            loader.spawn(loaded)

    def test_full_pipeline(self, temp_dir, sample_manifest_dict):
        """Test the full load pipeline (without spawning)."""
        snack_dir = temp_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)

        scripts_dir = snack_dir / "scripts"
        scripts_dir.mkdir()
        entrypoint = scripts_dir / "boot.bbc"
        entrypoint.write_text('10 PRINT "Hello"\n')

        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        loader = SnackLoader(sandbox_root=temp_dir / "sandbox")
        loaded = loader.load(manifest_path)
        loaded = loader.setup_ipc(loaded)
        loaded = loader.inject_lens_hooks(loaded)
        loaded = loader.setup_skin_pipeline(loaded)
        loaded = loader.setup_mcp(loaded)

        assert loaded.ipc is not None
        assert (loaded.sandbox_root / "lens" / "lens_config.json").exists()
        assert (loaded.sandbox_root / "skin" / "skin_config.json").exists()
        assert (loaded.sandbox_root / "mcp" / "mcp_config.json").exists()


# ──────────────────────────────────────────────
# Snackpack Tests
# ──────────────────────────────────────────────


class TestSnackpackManifest:
    def test_from_dict_full(self):
        """Test creating a snackpack manifest from a full dict."""
        data = {
            "name": "Classic Adventures",
            "version": "1.0.0",
            "snacks": ["eamon@1.0.0", "nethack@1.0.0"],
            "shared_lens": {
                "variable_patterns": ["^HP%$", "^GOLD%$"],
                "memory_regions": [{"name": "tilemap", "address": "0x6000", "size": 225}],
            },
            "shared_skins": {
                "available": ["teletext_classic", "paper_retro"],
                "targets": ["thinui", "ceefax_thinui"],
            },
            "meta_export": {
                "collection_spool": "adventures.spool",
                "combined_feed": True,
            },
            "launcher": {
                "type": "bbc_basic",
                "script": "launcher.bbc",
            },
            "description": "A collection of adventures",
            "tags": ["adventure", "collection"],
        }
        m = SnackpackManifest.from_dict(data)
        assert m.name == "Classic Adventures"
        assert m.version == "1.0.0"
        assert len(m.snacks) == 2
        assert m.shared_lens.variable_patterns == ["^HP%$", "^GOLD%$"]
        assert m.shared_skins.available == ["teletext_classic", "paper_retro"]
        assert m.meta_export.collection_spool == "adventures.spool"
        assert m.meta_export.combined_feed is True
        assert m.launcher.type == "bbc_basic"
        assert m.launcher.script == "launcher.bbc"

    def test_to_dict_roundtrip(self):
        """Test to_dict roundtrip for snackpack."""
        data = {
            "name": "Test Pack",
            "version": "1.0.0",
            "snacks": ["game1@1.0.0"],
            "description": "A test pack",
        }
        m = SnackpackManifest.from_dict(data)
        result = m.to_dict()
        assert result["name"] == "Test Pack"
        assert result["version"] == "1.0.0"
        assert result["snacks"] == ["game1@1.0.0"]

    def test_minimal(self):
        """Test creating a minimal snackpack manifest."""
        m = SnackpackManifest(name="Minimal", version="1.0.0")
        assert m.name == "Minimal"
        assert m.version == "1.0.0"
        assert m.snacks == []


class TestSnackpackLoader:
    def test_load(self, temp_dir):
        """Test loading a snackpack manifest."""
        pack_dir = temp_dir / "packs" / "test"
        pack_dir.mkdir(parents=True)
        manifest_path = pack_dir / "snackpack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump({
                "name": "Test Pack",
                "version": "1.0.0",
                "snacks": ["game1@1.0.0"],
            }, f)

        loader = SnackpackLoader()
        pack = loader.load(manifest_path)
        assert pack.name == "Test Pack"
        assert pack.version == "1.0.0"

    def test_load_nonexistent(self, temp_dir):
        """Test loading a nonexistent snackpack."""
        loader = SnackpackLoader()
        with pytest.raises(FileNotFoundError):
            loader.load(temp_dir / "nonexistent.yaml")

    def test_register_all(self, temp_dir, sample_manifest_dict):
        """Test registering all snacks in a pack."""
        pack_dir = temp_dir / "packs" / "test"
        pack_dir.mkdir(parents=True)

        snack_dir = pack_dir / "snacks" / "test"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        pack_manifest_path = pack_dir / "snackpack.yaml"
        with open(pack_manifest_path, "w") as f:
            yaml.safe_dump({
                "name": "Test Pack",
                "version": "1.0.0",
                "snacks": ["Test Adventure@1.0.0"],
            }, f)

        loader = SnackpackLoader()
        pack = loader.load(pack_manifest_path)
        count = loader.register_all(pack, pack_dir)
        assert count == 1

        entry = loader.registry.find("Test Adventure")
        assert entry is not None


# ──────────────────────────────────────────────
# Integration Tests
# ──────────────────────────────────────────────


class TestIntegration:
    def test_manifest_to_loader_to_registry(self, temp_dir, sample_manifest_dict):
        """End-to-end test: create manifest, load it, register it."""
        snack_dir = temp_dir / "games" / "my_adventure"
        snack_dir.mkdir(parents=True)
        (snack_dir / "disks").mkdir()
        (snack_dir / "scripts").mkdir()
        (snack_dir / "scripts" / "boot.bbc").write_text('10 PRINT "Hello"\n')

        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        loader = SnackLoader(sandbox_root=temp_dir / "sandbox")
        loaded = loader.load(manifest_path)
        assert loaded.manifest.name == "Test Adventure"

        registry = SnackRegistry()
        sid = registry.register(manifest_path)
        assert sid.name == "Test Adventure"

        entry = registry.find("Test Adventure")
        assert entry is not None
        assert entry.manifest.entrypoint == "scripts/boot.bbc"

    def test_snackpack_with_registry(self, temp_dir, sample_manifest_dict):
        """End-to-end test: snackpack with registry integration."""
        snack_dir = temp_dir / "packs" / "classic" / "snacks" / "my_adventure"
        snack_dir.mkdir(parents=True)
        manifest_path = snack_dir / "snack.yaml"
        with open(manifest_path, "w") as f:
            yaml.safe_dump(sample_manifest_dict, f)

        pack_dir = temp_dir / "packs" / "classic"
        pack_manifest_path = pack_dir / "snackpack.yaml"
        with open(pack_manifest_path, "w") as f:
            yaml.safe_dump({
                "name": "Classic Pack",
                "version": "1.0.0",
                "snacks": ["Test Adventure@1.0.0"],
            }, f)

        loader = SnackpackLoader()
        pack = loader.load(pack_manifest_path)
        count = loader.register_all(pack, pack_dir)
        assert count == 1

        ids = loader.get_snack_ids(pack)
        assert len(ids) == 1
        assert ids[0].name == "Test Adventure"
