"""
Tests for Lens-Skin-MCP integration.

Tests the combined Lens, Skin, and MCP bridge integration
for the uCode1 + CEETEX system.
"""

import os
import sys
import json
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from core_py.bbc.lens import LENSEngine, LENSEvent, LENSSnapshot, create_lens_engine
    from core_py.bbc.skin import SkinEngine, SkinDefinition, BUILTIN_SKINS, create_skin_engine
    from core_py.bbc.mcp_bridge import MCPBridge, MCPCommand, MCPCommandType, MCPResponse, create_mcp_bridge
    from core_py.bbc.spool_bridge import SpoolBridge, SpoolEnvelope, SpoolHeader, create_spool_bridge
    from core_py.bbc.lens_skin_mcp import LensSkinMCP, create_lens_skin_mcp
    from core_py.bbc.interpreter import BBCBasicInterpreter
    HAS_BBC = True
except ImportError:
    HAS_BBC = False

pytestmark = pytest.mark.skipif(
    not HAS_BBC,
    reason="BBC modules not available (requires core_py.bbc)"
)


class TestLENSEngine:
    """Tests for LENS engine"""

    def test_engine_creation(self):
        """LENS engine should initialize."""
        if not HAS_BBC:
            return
        engine = create_lens_engine()
        assert engine is not None

    def test_event_creation(self):
        """LENS events should be creatable."""
        if not HAS_BBC:
            return
        event = LENSEvent(type="view", data={"target": "test"})
        assert event.type == "view"
        assert event.data["target"] == "test"


class TestSkinEngine:
    """Tests for Skin engine"""

    def test_engine_creation(self):
        """Skin engine should initialize."""
        if not HAS_BBC:
            return
        engine = create_skin_engine()
        assert engine is not None

    def test_builtin_skins(self):
        """Built-in skins should be available."""
        if not HAS_BBC:
            return
        assert len(BUILTIN_SKINS) > 0


class TestMCPBridge:
    """Tests for MCP bridge"""

    def test_bridge_creation(self):
        """MCP bridge should initialize."""
        if not HAS_BBC:
            return
        bridge = create_mcp_bridge()
        assert bridge is not None

    def test_command_creation(self):
        """MCP commands should be creatable."""
        if not HAS_BBC:
            return
        cmd = MCPCommand(
            type=MCPCommandType.QUERY,
            payload={"action": "ping"}
        )
        assert cmd.type == MCPCommandType.QUERY


class TestSpoolBridge:
    """Tests for Spool bridge"""

    def test_bridge_creation(self):
        """Spool bridge should initialize."""
        if not HAS_BBC:
            return
        bridge = create_spool_bridge()
        assert bridge is not None

    def test_envelope_creation(self):
        """Spool envelopes should be creatable."""
        if not HAS_BBC:
            return
        envelope = SpoolEnvelope(
            header=SpoolHeader(version="1.0", type="test"),
            payload={"data": "test"}
        )
        assert envelope.header.version == "1.0"


class TestLensSkinMCP:
    """Tests for Lens-Skin-MCP integration"""

    def test_integration_creation(self):
        """LensSkinMCP should initialize."""
        if not HAS_BBC:
            return
        integration = create_lens_skin_mcp()
        assert integration is not None


class TestBBCBasicInterpreter:
    """Tests for BBC Basic interpreter"""

    def test_interpreter_creation(self):
        """Interpreter should initialize."""
        if not HAS_BBC:
            return
        interpreter = BBCBasicInterpreter()
        assert interpreter is not None
