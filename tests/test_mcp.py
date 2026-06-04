"""
Tests for CEETEX MCP protocol and controller.

Tests the MCP command protocol, command parsing, and controller
responses for the uCode1 + CEETEX integration.
"""

import pytest
import json
from ucode1.ceefax.mcp_protocol import (
    CeefaxMCPProtocol,
    CeefaxCommand,
    CeefaxCommandType,
    CeefaxResponse,
)


class TestMCPProtocol:
    """Tests for the CeefaxMCPProtocol class"""

    def test_initialization(self):
        """Protocol should initialize with default state"""
        protocol = CeefaxMCPProtocol()
        assert protocol.current_page == 100
        assert protocol.subtitle_visible is False
        assert protocol.reveal_visible is False
        assert protocol.hold_enabled is False
        assert protocol.double_height is False
        assert protocol.mix_mode is False

    def test_queue_command(self):
        """Queue command should add to pending queue"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("PAGE 101")
        assert cmd.command == "PAGE"
        assert cmd.command_type == CeefaxCommandType.PAGE
        assert cmd.args.get("value") == "101"

    def test_poll_returns_command(self):
        """Poll should return the next pending command"""
        protocol = CeefaxMCPProtocol()
        protocol.queue_command("NEXT")
        cmd = protocol.poll()
        assert cmd is not None
        assert cmd.command == "NEXT"

    def test_poll_empty_queue(self):
        """Poll on empty queue should return None"""
        protocol = CeefaxMCPProtocol()
        assert protocol.poll() is None

    def test_poll_all(self):
        """Poll all should return all pending commands"""
        protocol = CeefaxMCPProtocol()
        protocol.queue_command("NEXT")
        protocol.queue_command("PREV")
        protocol.queue_command("PAGE 200")
        commands = protocol.poll_all()
        assert len(commands) == 3

    def test_enable_disable(self):
        """Enable/disable should control command processing"""
        protocol = CeefaxMCPProtocol()
        protocol.queue_command("NEXT")
        protocol.disable()
        assert protocol.poll() is None
        protocol.enable()
        assert protocol.poll() is not None

    def test_command_history(self):
        """Command history should track all commands"""
        protocol = CeefaxMCPProtocol()
        protocol.queue_command("NEXT")
        protocol.queue_command("PAGE 101")
        history = protocol.get_history(limit=10)
        assert len(history) == 2
        assert history[0]["command"] == "NEXT"
        assert history[1]["command"] == "PAGE"

    def test_clear_commands(self):
        """Clear commands should empty the queue"""
        protocol = CeefaxMCPProtocol()
        protocol.queue_command("NEXT")
        protocol.queue_command("PREV")
        protocol.clear_commands()
        assert protocol.poll() is None


class TestMCPCommandParsing:
    """Tests for MCP command parsing"""

    def test_parse_next(self):
        """NEXT should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("NEXT")
        assert cmd.command_type == CeefaxCommandType.NEXT

    def test_parse_prev(self):
        """PREV should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("PREV")
        assert cmd.command_type == CeefaxCommandType.PREV

    def test_parse_page(self):
        """PAGE with number should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("PAGE 101")
        assert cmd.command_type == CeefaxCommandType.PAGE
        assert cmd.args.get("value") == "101"

    def test_parse_page_with_keyword(self):
        """PAGE with key=value should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("PAGE page=101")
        assert cmd.command_type == CeefaxCommandType.PAGE
        assert cmd.args.get("page") == "101"

    def test_parse_sub(self):
        """SUB should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("SUB")
        assert cmd.command_type == CeefaxCommandType.SUB

    def test_parse_index(self):
        """INDEX should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("INDEX")
        assert cmd.command_type == CeefaxCommandType.INDEX

    def test_parse_reveal(self):
        """REVEAL should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("REVEAL")
        assert cmd.command_type == CeefaxCommandType.REVEAL

    def test_parse_hold(self):
        """HOLD should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("HOLD")
        assert cmd.command_type == CeefaxCommandType.HOLD

    def test_parse_size(self):
        """SIZE should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("SIZE")
        assert cmd.command_type == CeefaxCommandType.SIZE

    def test_parse_mix(self):
        """MIX should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("MIX")
        assert cmd.command_type == CeefaxCommandType.MIX

    def test_parse_list(self):
        """LIST should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("LIST")
        assert cmd.command_type == CeefaxCommandType.LIST

    def test_parse_status(self):
        """STATUS should parse correctly"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("STATUS")
        assert cmd.command_type == CeefaxCommandType.STATUS

    def test_parse_unknown(self):
        """Unknown command should parse as UNKNOWN"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("BOGUS")
        assert cmd.command_type == CeefaxCommandType.UNKNOWN

    def test_parse_case_insensitive(self):
        """Commands should be case-insensitive"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("next")
        assert cmd.command_type == CeefaxCommandType.NEXT

    def test_parse_empty_string(self):
        """Empty string should not crash"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("")
        assert cmd.command_type == CeefaxCommandType.UNKNOWN


class TestMCPCommandProcessing:
    """Tests for MCP command processing"""

    def test_process_next(self):
        """NEXT should increment page"""
        protocol = CeefaxMCPProtocol()
        protocol.current_page = 100
        cmd = protocol.queue_command("NEXT")
        response = protocol.process_command(cmd)
        assert response is not None
        assert response.success is True
        assert response.page_number == 101

    def test_process_prev(self):
        """PREV should decrement page"""
        protocol = CeefaxMCPProtocol()
        protocol.current_page = 200
        cmd = protocol.queue_command("PREV")
        response = protocol.process_command(cmd)
        assert response.success is True
        assert response.page_number == 199

    def test_process_prev_minimum(self):
        """PREV should not go below page 100"""
        protocol = CeefaxMCPProtocol()
        protocol.current_page = 100
        cmd = protocol.queue_command("PREV")
        response = protocol.process_command(cmd)
        assert response.success is True
        assert response.page_number == 100

    def test_process_page(self):
        """PAGE should navigate to specific page"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("PAGE 500")
        response = protocol.process_command(cmd)
        assert response.success is True
        assert response.page_number == 500

    def test_process_page_invalid(self):
        """PAGE with invalid number should fail"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("PAGE ABC")
        response = protocol.process_command(cmd)
        assert response.success is False
        assert "Invalid" in response.error

    def test_process_sub(self):
        """SUB should toggle subtitle"""
        protocol = CeefaxMCPProtocol()
        assert protocol.subtitle_visible is False
        cmd = protocol.queue_command("SUB")
        response = protocol.process_command(cmd)
        assert response.success is True
        assert protocol.subtitle_visible is True

    def test_process_sub_toggle(self):
        """SUB should toggle back off"""
        protocol = CeefaxMCPProtocol()
        protocol._subtitle_visible = True
        cmd = protocol.queue_command("SUB")
        protocol.process_command(cmd)
        assert protocol.subtitle_visible is False

    def test_process_index(self):
        """INDEX should go to page 100"""
        protocol = CeefaxMCPProtocol()
        protocol.current_page = 500
        cmd = protocol.queue_command("INDEX")
        response = protocol.process_command(cmd)
        assert response.success is True
        assert response.page_number == 100

    def test_process_reveal(self):
        """REVEAL should toggle reveal"""
        protocol = CeefaxMCPProtocol()
        assert protocol.reveal_visible is False
        cmd = protocol.queue_command("REVEAL")
        protocol.process_command(cmd)
        assert protocol.reveal_visible is True

    def test_process_hold(self):
        """HOLD should toggle hold"""
        protocol = CeefaxMCPProtocol()
        assert protocol.hold_enabled is False
        cmd = protocol.queue_command("HOLD")
        protocol.process_command(cmd)
        assert protocol.hold_enabled is True

    def test_process_size(self):
        """SIZE should toggle double height"""
        protocol = CeefaxMCPProtocol()
        assert protocol.double_height is False
        cmd = protocol.queue_command("SIZE")
        protocol.process_command(cmd)
        assert protocol.double_height is True

    def test_process_mix(self):
        """MIX should toggle mix mode"""
        protocol = CeefaxMCPProtocol()
        assert protocol.mix_mode is False
        cmd = protocol.queue_command("MIX")
        protocol.process_command(cmd)
        assert protocol.mix_mode is True

    def test_process_status(self):
        """STATUS should return current state"""
        protocol = CeefaxMCPProtocol()
        protocol.current_page = 300
        cmd = protocol.queue_command("STATUS")
        response = protocol.process_command(cmd)
        assert response.success is True
        state = json.loads(response.result)
        assert state["current_page"] == 300

    def test_process_unknown(self):
        """Unknown command should return None"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("BOGUS")
        response = protocol.process_command(cmd)
        assert response is None


class TestMCPState:
    """Tests for MCP state management"""

    def test_get_state(self):
        """get_state should return full state dict"""
        protocol = CeefaxMCPProtocol()
        protocol.current_page = 500
        protocol._subtitle_visible = True
        state = protocol.get_state()
        assert state["current_page"] == 500
        assert state["subtitle"] is True
        assert "pending_commands" in state
        assert "pending_responses" in state
        assert "command_history" in state

    def test_set_current_page(self):
        """Setting current_page should update state"""
        protocol = CeefaxMCPProtocol()
        protocol.current_page = 777
        assert protocol.current_page == 777

    def test_response_queue(self):
        """Responses should be queued and retrievable"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("NEXT")
        protocol.process_command(cmd)
        response = protocol.get_response()
        assert response is not None
        assert response.success is True

    def test_clear_responses(self):
        """Clear responses should empty the queue"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("NEXT")
        protocol.process_command(cmd)
        protocol.clear_responses()
        assert protocol.get_response() is None

    def test_get_responses_json(self):
        """get_responses_json should return valid JSON"""
        protocol = CeefaxMCPProtocol()
        cmd = protocol.queue_command("NEXT")
        protocol.process_command(cmd)
        json_str = protocol.get_responses_json()
        data = json.loads(json_str)
        assert len(data) == 1
        assert data[0]["success"] is True

    def test_add_callback(self):
        """Callbacks should be invoked on poll"""
        results = []
        protocol = CeefaxMCPProtocol()

        def callback(cmd):
            results.append(cmd.command)
            return "handled"

        protocol.add_callback(callback)
        protocol.queue_command("NEXT")
        protocol.poll()
        assert len(results) == 1
        assert results[0] == "NEXT"
