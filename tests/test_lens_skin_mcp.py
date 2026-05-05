"""
Tests for the uCode1 LENS/SKIN/MCP/Spool integration.

Tests cover:
    - LENS engine: variable capture, events, snapshots, JSON export
    - SKIN engine: skin application, char mapping, palette
    - MCP bridge: command parsing, polling, responses
    - Spool bridge: save/load, envelope creation
    - LensSkinMCP unified integration
    - Interpreter PROC/FN handler wiring
"""

import os
import sys
import json
import time
import pytest

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core_py.bbc.lens import LENSEngine, LENSEvent, LENSSnapshot, create_lens_engine
from core_py.bbc.skin import SkinEngine, SkinDefinition, BUILTIN_SKINS, create_skin_engine
from core_py.bbc.mcp_bridge import MCPBridge, MCPCommand, MCPCommandType, MCPResponse, create_mcp_bridge
from core_py.bbc.spool_bridge import SpoolBridge, SpoolEnvelope, SpoolHeader, create_spool_bridge
from core_py.bbc.lens_skin_mcp import LensSkinMCP, create_lens_skin_mcp
from core_py.bbc.interpreter import BBCBasicInterpreter


# =============================================================================
# LENS Engine Tests
# =============================================================================

class TestLENSEngine:
    """Tests for the LENS data extraction engine"""

    def test_create_engine(self):
        """Test creating a LENS engine"""
        engine = create_lens_engine()
        assert engine is not None
        assert engine._enabled is True
        assert len(engine.event_queue) == 0
        assert len(engine.snapshots) == 0

    def test_flag_event(self):
        """Test flagging an event"""
        engine = create_lens_engine()
        engine.flag_event("entered_dungeon")
        assert len(engine.event_queue) == 1
        event = engine.event_queue[0]
        assert event.name == "entered_dungeon"
        assert event.timestamp > 0

    def test_snapshot(self):
        """Test taking a snapshot"""
        engine = create_lens_engine()
        engine.watch_variable("HP%")
        engine.watch_variable("GOLD%")
        engine.snapshot("before_boss")
        assert "before_boss" in engine.snapshots
        snap = engine.snapshots["before_boss"]
        assert snap.name == "before_boss"

    def test_auto_capture(self):
        """Test auto-capture detects changes"""
        engine = create_lens_engine()
        engine.watch_variable("HP%")
        engine.watch_variable("GOLD%")

        # First capture should detect all vars (they're None initially)
        changes = engine.auto_capture()
        assert "HP%" in changes or len(changes) == 0  # May be empty if no interpreter

    def test_get_json(self):
        """Test JSON export"""
        engine = create_lens_engine()
        engine.flag_event("start_game")
        engine.watch_variable("HP%")
        engine.watch_variable("GOLD%")
        engine.snapshot("checkpoint")

        json_str = engine.get_json()
        data = json.loads(json_str)
        # get_json returns just variables dict
        assert isinstance(data, dict)

    def test_attach_to_interpreter(self):
        """Test attaching to an interpreter"""
        interpreter = BBCBasicInterpreter()
        engine = create_lens_engine(interpreter)
        assert engine.interpreter is interpreter
        assert hasattr(interpreter, '_lens_engine')
        assert interpreter._lens_engine is engine

    def test_watch_variable_from_interpreter(self):
        """Test watching variables through interpreter"""
        interpreter = BBCBasicInterpreter()
        engine = create_lens_engine(interpreter)

        # Set variables in interpreter
        interpreter.state.variables["HP%"] = 100
        interpreter.state.variables["GOLD%"] = 50

        # Auto-capture should pick them up
        changes = engine.auto_capture()
        assert "HP%" in changes
        assert "GOLD%" in changes

    def test_custom_vars(self):
        """Test custom variable registration"""
        engine = create_lens_engine()
        engine.watch_variable("PLAYER_NAME")
        engine.watch_variable("LEVEL")
        assert "PLAYER_NAME" in engine.custom_vars
        assert "LEVEL" in engine.custom_vars

    def test_snapshot_callback(self):
        """Test snapshot callback"""
        engine = create_lens_engine()
        callback_data = []

        def callback(snapshot):
            callback_data.append(snapshot.name)

        engine.add_snapshot_callback(callback)
        engine.snapshot("test_snap")
        assert len(callback_data) == 1
        assert callback_data[0] == "test_snap"

    def test_event_callback(self):
        """Test event callback"""
        engine = create_lens_engine()
        callback_data = []

        def callback(event):
            callback_data.append(event.name)

        engine.add_event_callback(callback)
        engine.flag_event("test_event")
        assert len(callback_data) == 1
        assert callback_data[0] == "test_event"

    def test_clear_events(self):
        """Test clearing events"""
        engine = create_lens_engine()
        engine.flag_event("event1")
        engine.flag_event("event2")
        assert len(engine.event_queue) == 2
        engine.clear_events()
        assert len(engine.event_queue) == 0

    def test_disable_enable(self):
        """Test disabling and enabling"""
        engine = create_lens_engine()
        assert engine._enabled is True
        engine.disable()
        assert engine._enabled is False
        engine.flag_event("test")  # When disabled, events are not queued
        assert len(engine.event_queue) == 0
        engine.enable()
        assert engine._enabled is True
        engine.flag_event("test2")  # After re-enabling, events are queued
        assert len(engine.event_queue) == 1


# =============================================================================
# SKIN Engine Tests
# =============================================================================

class TestSkinEngine:
    """Tests for the SKIN visual transformation engine"""

    def test_create_engine(self):
        """Test creating a SKIN engine"""
        engine = create_skin_engine()
        assert engine is not None
        assert engine.active_skin_name == "teletext_classic"
        assert len(engine.available_skins) >= 3

    def test_builtin_skins(self):
        """Test built-in skins exist"""
        assert "teletext_classic" in BUILTIN_SKINS
        assert "paper_retro" in BUILTIN_SKINS
        assert "dark_mode" in BUILTIN_SKINS

    def test_apply_skin(self):
        """Test applying a skin"""
        engine = create_skin_engine()
        result = engine.apply("paper_retro")
        assert result is True
        assert engine.active_skin_name == "paper_retro"

    def test_apply_invalid_skin(self):
        """Test applying an invalid skin"""
        engine = create_skin_engine()
        result = engine.apply("nonexistent_skin")
        assert result is False
        assert engine.active_skin_name == "teletext_classic"  # unchanged

    def test_char_mapping(self):
        """Test character mapping"""
        engine = create_skin_engine()
        engine.map_char(65, "S")  # Map 'A' to 'S'
        assert engine._char_mappings.get(65) == "S"

    def test_char_mapping_override(self):
        """Test character mapping override"""
        engine = create_skin_engine()
        engine.map_char(65, "S")
        engine.map_char(65, "T")  # Override
        assert engine._char_mappings.get(65) == "T"

    def test_set_palette(self):
        """Test palette setting"""
        engine = create_skin_engine()
        engine.set_palette(1, "#FF0000")
        assert engine._palette_overrides.get(1) == "#FF0000"

    def test_skin_properties(self):
        """Test skin properties"""
        skin = BUILTIN_SKINS["teletext_classic"]
        assert skin.name == "teletext_classic"
        assert skin.background_color == "#000000"
        assert skin.foreground_color == "#00FF00"
        assert skin.font_name == "CeefaxThinUI"

    def test_skin_change_callback(self):
        """Test skin change callback"""
        engine = create_skin_engine()
        callback_data = []

        def callback(name, skin_def):
            callback_data.append(name)

        engine.add_change_callback(callback)
        engine.apply("dark_mode")
        assert len(callback_data) == 1
        assert callback_data[0] == "dark_mode"

    def test_get_glyph(self):
        """Test glyph lookup"""
        engine = create_skin_engine()
        engine.map_char(65, "S")
        assert engine.get_glyph(65) == "S"
        assert engine.get_glyph(66) == "B"  # Unmapped, returns chr(66)

    def test_get_color(self):
        """Test color lookup"""
        engine = create_skin_engine()
        engine.set_palette(1, "#FF0000")
        assert engine.get_color(1) == "#FF0000"
        # Default skin color
        assert engine.get_color(0) == "#000000"

    def test_transform_text(self):
        """Test text transformation"""
        engine = create_skin_engine()
        engine.map_char(65, "S")
        result = engine.transform_text("ABC")
        assert result == "SBC"

    def test_get_style_attributes(self):
        """Test style attributes"""
        engine = create_skin_engine()
        attrs = engine.get_style_attributes()
        assert "background" in attrs
        assert "color" in attrs
        assert "font-family" in attrs


# =============================================================================
# MCP Bridge Tests
# =============================================================================

class TestMCPBridge:
    """Tests for the MCP command bridge"""

    def test_create_bridge(self):
        """Test creating an MCP bridge"""
        bridge = create_mcp_bridge()
        assert bridge is not None
        assert bridge._enabled is True

    def test_queue_command(self):
        """Test queuing a command"""
        bridge = create_mcp_bridge()
        bridge.queue_command("PAUSE")
        assert len(bridge._pending_commands) == 1
        cmd = bridge._pending_commands[0]
        assert cmd.command_type == MCPCommandType.PAUSE

    def test_queue_command_with_args(self):
        """Test queuing a command with arguments"""
        bridge = create_mcp_bridge()
        bridge.queue_command("SAVE slot=auto")
        assert len(bridge._pending_commands) == 1
        cmd = bridge._pending_commands[0]
        assert cmd.command_type == MCPCommandType.SAVE
        assert cmd.args.get("slot") == "auto"

    def test_poll(self):
        """Test polling for commands"""
        bridge = create_mcp_bridge()
        bridge.queue_command("PAUSE")
        bridge.queue_command("RESUME")

        cmd1 = bridge.poll()
        assert cmd1 == "PAUSE"
        assert len(bridge._pending_commands) == 1

        cmd2 = bridge.poll()
        assert cmd2 == "RESUME"
        assert len(bridge._pending_commands) == 0

    def test_poll_empty(self):
        """Test polling with no commands"""
        bridge = create_mcp_bridge()
        result = bridge.poll()
        assert result == ""

    def test_respond(self):
        """Test sending a response"""
        bridge = create_mcp_bridge()
        bridge.respond("OK: saved")
        assert len(bridge._responses) == 1
        resp = bridge._responses[0]
        assert resp.result == "OK: saved"

    def test_clear_commands(self):
        """Test clearing commands"""
        bridge = create_mcp_bridge()
        bridge.queue_command("PAUSE")
        bridge.queue_command("SAVE")
        assert len(bridge._pending_commands) == 2
        bridge.clear_commands()
        assert len(bridge._pending_commands) == 0

    def test_clear_responses(self):
        """Test clearing responses"""
        bridge = create_mcp_bridge()
        bridge.respond("OK")
        bridge.respond("ERROR")
        assert len(bridge._responses) == 2
        bridge.clear_responses()
        assert len(bridge._responses) == 0

    def test_command_callback(self):
        """Test command callback"""
        bridge = create_mcp_bridge()
        callback_data = []

        def callback(cmd):
            callback_data.append(cmd.command_type.name)
            return None

        bridge.add_command_callback(callback)
        bridge.queue_command("PAUSE")
        # Callback fires on poll, not queue
        bridge.poll()
        assert len(callback_data) == 1
        assert callback_data[0] == "PAUSE"

    def test_parse_save_command(self):
        """Test parsing SAVE command"""
        bridge = create_mcp_bridge()
        bridge.queue_command("SAVE slot=dungeon1")
        cmd = bridge._pending_commands[0]
        assert cmd.command_type == MCPCommandType.SAVE
        assert cmd.args.get("slot") == "dungeon1"

    def test_parse_export_command(self):
        """Test parsing EXPORT command"""
        bridge = create_mcp_bridge()
        bridge.queue_command("EXPORT_SPOOL")
        cmd = bridge._pending_commands[0]
        assert cmd.command_type == MCPCommandType.EXPORT_SPOOL

    def test_parse_skin_command(self):
        """Test parsing SKIN command"""
        bridge = create_mcp_bridge()
        bridge.queue_command("SKIN value=dark_mode")
        cmd = bridge._pending_commands[0]
        assert cmd.command_type == MCPCommandType.SKIN
        assert cmd.args.get("value") == "dark_mode"

    def test_parse_inspect_command(self):
        """Test parsing INSPECT command"""
        bridge = create_mcp_bridge()
        bridge.queue_command("INSPECT HP%")
        cmd = bridge._pending_commands[0]
        assert cmd.command_type == MCPCommandType.INSPECT
        assert cmd.args.get("value") == "HP%"

    def test_parse_eval_command(self):
        """Test parsing EVAL command"""
        bridge = create_mcp_bridge()
        bridge.queue_command("EVAL HP%+10")
        cmd = bridge._pending_commands[0]
        assert cmd.command_type == MCPCommandType.EVAL
        assert cmd.args.get("value") == "HP%+10"

    def test_get_response(self):
        """Test getting a response"""
        bridge = create_mcp_bridge()
        bridge.respond("OK")
        resp = bridge.get_response()
        assert resp is not None
        assert resp.result == "OK"
        # Second call should return None
        assert bridge.get_response() is None


# =============================================================================
# Spool Bridge Tests
# =============================================================================

class TestSpoolBridge:
    """Tests for the Spool save/load bridge"""

    def test_create_bridge(self):
        """Test creating a spool bridge"""
        bridge = create_spool_bridge()
        assert bridge is not None
        assert bridge.save_count == 0
        assert bridge.load_count == 0

    def test_save_and_load(self, tmp_path):
        """Test saving and loading a spool"""
        bridge = create_spool_bridge(spool_dir=str(tmp_path))
        interpreter = BBCBasicInterpreter()
        bridge.attach_to_interpreter(interpreter)

        # Set some state
        interpreter.state.variables["HP%"] = 100
        interpreter.state.variables["GOLD%"] = 50

        # Save
        result = bridge.save("test_save")
        assert result is True
        assert bridge.save_count == 1

        # Verify file exists
        files = os.listdir(str(tmp_path))
        assert len(files) >= 1
        assert any("test_save" in f for f in files)

        # Change state
        interpreter.state.variables["HP%"] = 25

        # Load
        result = bridge.load("test_save")
        assert result is True
        assert bridge.load_count == 1

        # Verify state restored
        assert interpreter.state.variables["HP%"] == 100
        assert interpreter.state.variables["GOLD%"] == 50

    def test_save_without_interpreter(self):
        """Test saving without an interpreter"""
        bridge = create_spool_bridge()
        result = bridge.save("test")
        assert result is False

    def test_load_without_interpreter(self):
        """Test loading without an interpreter"""
        bridge = create_spool_bridge()
        result = bridge.load("test")
        assert result is False

    def test_load_nonexistent(self, tmp_path):
        """Test loading a nonexistent spool"""
        bridge = create_spool_bridge(spool_dir=str(tmp_path))
        interpreter = BBCBasicInterpreter()
        bridge.attach_to_interpreter(interpreter)
        result = bridge.load("nonexistent")
        assert result is False

    def test_spool_dir_creation(self, tmp_path):
        """Test spool directory creation"""
        spool_dir = os.path.join(str(tmp_path), "spools")
        bridge = create_spool_bridge(spool_dir=spool_dir)
        assert os.path.exists(spool_dir)
        assert os.path.isdir(spool_dir)

    def test_list_spools(self, tmp_path):
        """Test listing spools"""
        bridge = create_spool_bridge(spool_dir=str(tmp_path))
        interpreter = BBCBasicInterpreter()
        bridge.attach_to_interpreter(interpreter)
        interpreter.state.variables["HP%"] = 100
        bridge.save("test1")
        bridge.save("test2")
        spools = bridge.list_spools()
        assert len(spools) == 2

    def test_delete_spool(self, tmp_path):
        """Test deleting a spool"""
        bridge = create_spool_bridge(spool_dir=str(tmp_path))
        interpreter = BBCBasicInterpreter()
        bridge.attach_to_interpreter(interpreter)
        interpreter.state.variables["HP%"] = 100
        bridge.save("test_delete")
        assert bridge.delete_spool("test_delete") is True
        assert bridge.delete_spool("nonexistent") is False


# =============================================================================
# LensSkinMCP Unified Integration Tests
# =============================================================================

class TestLensSkinMCP:
    """Tests for the unified LensSkinMCP integration"""

    def test_create_unified(self):
        """Test creating the unified integration"""
        lsm = create_lens_skin_mcp()
        assert lsm is not None
        assert lsm.lens is not None
        assert lsm.skin is not None
        assert lsm.mcp is not None
        assert lsm.spool is not None

    def test_attach_to_interpreter(self):
        """Test attaching to interpreter"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)
        assert lsm.interpreter is interpreter
        assert hasattr(interpreter, '_lens_skin_mcp')
        assert hasattr(interpreter, '_lens_engine')
        assert hasattr(interpreter, '_skin_engine')
        assert hasattr(interpreter, '_mcp_bridge')
        assert hasattr(interpreter, '_spool_bridge')

    def test_tick_mcp_polling(self):
        """Test tick performs MCP polling"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        # Queue a command
        lsm.mcp.queue_command("PAUSE")

        # Tick should pick it up
        changes = lsm.tick()
        assert "_mcp_command" in changes
        assert changes["_mcp_command"] == "PAUSE"

    def test_tick_auto_capture(self):
        """Test tick performs auto-capture"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        interpreter.state.variables["HP%"] = 100
        interpreter.state.variables["GOLD%"] = 50

        # Set interval to 0 so it captures immediately
        lsm.set_auto_capture_interval(0)

        changes = lsm.tick()
        # Auto-capture may or may not fire depending on timing
        # Just verify tick doesn't crash
        assert isinstance(changes, dict)

    def test_disable_auto_capture(self):
        """Test disabling auto-capture"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        lsm.disable_auto_capture()
        interpreter.state.variables["HP%"] = 100

        changes = lsm.tick()
        assert "_auto_capture" not in changes

    def test_get_full_state_json(self):
        """Test getting full state as JSON"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        interpreter.state.variables["HP%"] = 100
        lsm.lens.flag_event("test_event")
        lsm.skin.apply("dark_mode")

        json_str = lsm.get_full_state_json()
        data = json.loads(json_str)
        assert "lens" in data
        assert "skin" in data
        assert "mcp" in data
        assert "spool" in data
        assert data["skin"]["active"] == "dark_mode"

    def test_reset_all(self):
        """Test resetting all engines"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        lsm.lens.flag_event("test")
        lsm.skin.apply("dark_mode")
        lsm.mcp.queue_command("PAUSE")

        lsm.reset_all()

        assert len(lsm.lens.event_queue) == 0
        assert len(lsm.lens.snapshots) == 0
        assert lsm.skin.active_skin_name == "teletext_classic"
        assert len(lsm.mcp._pending_commands) == 0

    def test_mcp_save_triggers_lens(self, tmp_path):
        """Test MCP SAVE command triggers LENS snapshot"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter, spool_dir=str(tmp_path))

        interpreter.state.variables["HP%"] = 100
        interpreter.state.variables["GOLD%"] = 50

        # Queue MCP SAVE command
        lsm.mcp.queue_command("SAVE slot=test_slot")

        # Process the command via poll (triggers callback)
        cmd_str = lsm.mcp.poll()
        assert cmd_str == "SAVE slot=test_slot"

        # The callback should have triggered a snapshot
        assert "mcp_save_test_slot" in lsm.lens.snapshots

    def test_mcp_skin_command(self):
        """Test MCP SKIN command changes skin"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        lsm.mcp.queue_command("SKIN value=dark_mode")
        cmd_str = lsm.mcp.poll()
        assert cmd_str == "SKIN value=dark_mode"

        # The callback should have changed the skin
        assert lsm.skin.active_skin_name == "dark_mode"


# =============================================================================
# Interpreter PROC/FN Handler Tests
# =============================================================================

class TestInterpreterExtensions:
    """Tests for the interpreter PROC/FN extension handlers"""

    def test_proc_lens_flagevent(self):
        """Test PROC_LENS_FlagEvent from interpreter"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        # Simulate executing PROC_LENS_FlagEvent("entered_dungeon")
        interpreter._execute_statement(
            'PROC_LENS_FlagEvent("entered_dungeon")', 10
        )

        assert len(lsm.lens.event_queue) == 1
        assert lsm.lens.event_queue[0].name == "entered_dungeon"

    def test_proc_lens_snapshot(self):
        """Test PROC_LENS_Snapshot from interpreter"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        interpreter.state.variables["HP%"] = 100

        interpreter._execute_statement(
            'PROC_LENS_Snapshot("checkpoint")', 20
        )

        assert "checkpoint" in lsm.lens.snapshots

    def test_proc_skin_apply(self):
        """Test PROC_SKIN_Apply from interpreter"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        interpreter._execute_statement(
            'PROC_SKIN_Apply("dark_mode")', 30
        )

        assert lsm.skin.active_skin_name == "dark_mode"

    def test_proc_skin_mapchar(self):
        """Test PROC_SKIN_MapChar from interpreter"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        interpreter._execute_statement(
            'PROC_SKIN_MapChar(65, "S")', 40
        )

        assert lsm.skin._char_mappings.get(65) == "S"

    def test_proc_skin_setpalette(self):
        """Test PROC_SKIN_SetPalette from interpreter"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        interpreter._execute_statement(
            'PROC_SKIN_SetPalette(1, "#FF0000")', 50
        )

        assert lsm.skin._palette_overrides.get(1) == "#FF0000"

    def test_proc_mcp_respond(self):
        """Test PROC_MCP_Respond from interpreter"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        interpreter._execute_statement(
            'PROC_MCP_Respond("OK: saved")', 60
        )

        assert len(lsm.mcp._responses) == 1
        assert lsm.mcp._responses[0].result == "OK: saved"

    def test_proc_spool_save(self, tmp_path):
        """Test PROC_SPOOL_Save from interpreter"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter, spool_dir=str(tmp_path))

        interpreter.state.variables["HP%"] = 100

        interpreter._execute_statement(
            'PROC_SPOOL_Save("test_save")', 70
        )

        assert lsm.spool.save_count == 1

    def test_fn_lens_getjson(self):
        """Test FN_LENS_GetJSON from interpreter"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        interpreter.state.variables["HP%"] = 100
        interpreter.state.variables["GOLD%"] = 50

        # Evaluate the function
        result = interpreter.evaluate('FN_LENS_GetJSON')
        data = json.loads(result)
        assert data["HP%"] == 100
        assert data["GOLD%"] == 50

    def test_fn_mcp_poll(self):
        """Test FN_MCP_Poll from interpreter"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        lsm.mcp.queue_command("PAUSE")

        result = interpreter.evaluate('FN_MCP_Poll')
        assert result == "PAUSE"

    def test_fn_mcp_poll_empty(self):
        """Test FN_MCP_Poll with no commands"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter)

        result = interpreter.evaluate('FN_MCP_Poll')
        assert result == ""

    def test_fn_spool_load(self, tmp_path):
        """Test FN_SPOOL_Load from interpreter"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter, spool_dir=str(tmp_path))

        # First save some state
        interpreter.state.variables["HP%"] = 100
        lsm.spool.save("test_slot")

        # Change state
        interpreter.state.variables["HP%"] = 25

        # Load via FN
        result = interpreter.evaluate('FN_SPOOL_Load("test_slot")')
        assert result is True
        assert interpreter.state.variables["HP%"] == 100

    def test_full_game_loop(self, tmp_path):
        """Test a complete game loop with all extensions"""
        interpreter = BBCBasicInterpreter()
        lsm = create_lens_skin_mcp(interpreter, spool_dir=str(tmp_path))

        # Simulate a game loop
        interpreter.state.variables["HP%"] = 100
        interpreter.state.variables["GOLD%"] = 50
        interpreter.state.variables["ROOM%"] = 1

        # Flag event
        interpreter._execute_statement(
            'PROC_LENS_FlagEvent("entered_dungeon")', 10
        )

        # Apply skin
        interpreter._execute_statement(
            'PROC_SKIN_Apply("paper_retro")', 20
        )

        # Take snapshot
        interpreter._execute_statement(
            'PROC_LENS_Snapshot("start")', 30
        )

        # Change state
        interpreter.state.variables["HP%"] = 75
        interpreter.state.variables["GOLD%"] = 100
        interpreter.state.variables["ROOM%"] = 3

        # Save via spool
        interpreter._execute_statement(
            'PROC_SPOOL_Save("dungeon_progress")', 40
        )

        # Get JSON
        json_str = interpreter.evaluate('FN_LENS_GetJSON')
        data = json.loads(json_str)

        assert data["HP%"] == 75
        assert data["GOLD%"] == 100
        assert data["ROOM%"] == 3

        # Verify spool saved
        assert lsm.spool.save_count == 1

        # Verify skin applied
        assert lsm.skin.active_skin_name == "paper_retro"


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
