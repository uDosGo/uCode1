"""
Tests for CEETEX MCP protocol and controller.

Tests the MCP command protocol, command parsing, and controller
responses for the uCode1 + CEETEX integration.
"""

import pytest
import json

try:
    from ucode1.ceefax.mcp_protocol import (
        CeefaxMCPProtocol,
        CeefaxCommand,
        CeefaxCommandType,
        CeefaxResponse,
    )
    HAS_CEETEX = True
except ImportError:
    HAS_CEETEX = False

pytestmark = pytest.mark.skipif(
    not HAS_CEETEX,
    reason="ceefax module not available (requires core_py.ceefax)"
)


class TestCeefaxMCPProtocol:
    """Tests for CeefaxMCPProtocol"""

    def test_protocol_initialization(self):
        """Protocol should initialize."""
        if not HAS_CEETEX:
            return
        protocol = CeefaxMCPProtocol()
        assert protocol is not None

    def test_command_parsing(self):
        """Protocol should parse commands."""
        if not HAS_CEETEX:
            return
        protocol = CeefaxMCPProtocol()
        result = protocol.parse_command("HELLO")
        assert result is not None


class TestCeefaxCommand:
    """Tests for CeefaxCommand"""

    def test_command_creation(self):
        """Command should be creatable."""
        if not HAS_CEETEX:
            return
        cmd = CeefaxCommand(
            type=CeefaxCommandType.QUERY,
            payload={"action": "status"}
        )
        assert cmd.type == CeefaxCommandType.QUERY
        assert cmd.payload["action"] == "status"


class TestCeefaxResponse:
    """Tests for CeefaxResponse"""

    def test_response_creation(self):
        """Response should be creatable."""
        if not HAS_CEETEX:
            return
        resp = CeefaxResponse(
            success=True,
            data={"status": "ok"}
        )
        assert resp.success is True
        assert resp.data["status"] == "ok"

    def test_response_to_json(self):
        """Response should serialize to JSON."""
        if not HAS_CEETEX:
            return
        resp = CeefaxResponse(
            success=True,
            data={"status": "ok"}
        )
        json_str = resp.to_json()
        parsed = json.loads(json_str)
        assert parsed["success"] is True
