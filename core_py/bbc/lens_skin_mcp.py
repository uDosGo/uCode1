"""
LENS/SKIN/MCP — Unified Integration for uCode1

This module ties together the LENS, SKIN, MCP, and Spool engines
into a single integration point for the BBC BASIC interpreter.

Provides:
    - LensSkinMCP class that wires all four engines together
    - attach_to_interpreter() convenience method
    - Event loop integration for MCP polling
    - Auto-capture on game loop iterations
"""

from typing import Optional, Any, Dict, List
import time

from .lens import LENSEngine, create_lens_engine
from .skin import SkinEngine, create_skin_engine
from .mcp_bridge import MCPBridge, create_mcp_bridge, MCPCommand, MCPCommandType
from .spool_bridge import SpoolBridge, create_spool_bridge


class LensSkinMCP:
    """
    Unified integration of LENS, SKIN, MCP, and Spool engines.

    Provides a single point of attachment to the BBC BASIC interpreter,
    with automatic event loop integration and cross-engine coordination.
    """

    def __init__(self, interpreter=None, spool_dir: Optional[str] = None):
        """
        Initialize all four engines.

        Args:
            interpreter: Optional BBCBasicInterpreter to attach to
            spool_dir: Directory for spool files
        """
        self.lens: LENSEngine = create_lens_engine(interpreter)
        self.skin: SkinEngine = create_skin_engine()
        self.mcp: MCPBridge = create_mcp_bridge(interpreter)
        self.spool: SpoolBridge = create_spool_bridge(interpreter, spool_dir)
        self.interpreter = interpreter

        # If interpreter provided, attach all engines and store self reference
        if interpreter is not None:
            self.attach_to_interpreter(interpreter)

        # Wire MCP to LENS: when MCP SAVE command comes in, auto-snapshot
        self.mcp.add_command_callback(self._handle_mcp_command)

        # Wire LENS to Spool: when LENS snapshot is taken, optionally save
        self.lens.add_snapshot_callback(self._handle_lens_snapshot)

        # Auto-capture tracking
        self._auto_capture_enabled: bool = True
        self._auto_capture_interval: float = 1.0  # seconds
        self._last_auto_capture: float = 0.0

    # ── Attachment ────────────────────────────────────────────────

    def attach_to_interpreter(self, interpreter) -> None:
        """
        Attach all engines to a BBC BASIC interpreter.

        This wires up all PROC_* and FN_* handlers in one call.

        Args:
            interpreter: BBCBasicInterpreter instance
        """
        self.interpreter = interpreter
        self.lens.attach_to_interpreter(interpreter)
        self.skin.attach_to_interpreter(interpreter)
        self.mcp.attach_to_interpreter(interpreter)
        self.spool.attach_to_interpreter(interpreter)

        # Store reference to self on interpreter for easy access
        interpreter._lens_skin_mcp = self

    # ── MCP Command Handling ──────────────────────────────────────

    def _handle_mcp_command(self, cmd: MCPCommand) -> Optional[str]:
        """Handle MCP commands that coordinate across engines"""
        if cmd.command_type == MCPCommandType.SAVE:
            slot = cmd.args.get("slot", "auto")
            # Take a LENS snapshot first
            self.lens.snapshot(f"mcp_save_{slot}")
            # Then save to Spool
            success = self.spool.save(slot)
            return f"OK: saved to slot '{slot}'" if success else "ERROR: save failed"

        elif cmd.command_type == MCPCommandType.RESTORE:
            slot = cmd.args.get("slot", "auto")
            success = self.spool.load(slot)
            return f"OK: restored from slot '{slot}'" if success else "ERROR: restore failed"

        elif cmd.command_type == MCPCommandType.EXPORT_SPOOL:
            # Export current state as JSON
            json_data = self.lens.get_json(pretty=True)
            return f"OK: spool data ({len(json_data)} bytes)"

        elif cmd.command_type == MCPCommandType.SKIN:
            skin_name = cmd.args.get("value", "")
            if skin_name:
                success = self.skin.apply(skin_name)
                if success:
                    return f"OK: skin changed to '{skin_name}'"
                return f"ERROR: skin '{skin_name}' not found"
            return f"OK: current skin is '{self.skin.active_skin_name}'"

        # Let the MCP bridge handle standard commands
        return None

    def _handle_lens_snapshot(self, snapshot) -> None:
        """Handle LENS snapshot events"""
        # Could auto-save to spool here if configured
        pass

    # ── Auto-Capture ──────────────────────────────────────────────

    def enable_auto_capture(self) -> None:
        """Enable automatic state capture on game loop iterations"""
        self._auto_capture_enabled = True

    def disable_auto_capture(self) -> None:
        """Disable automatic state capture"""
        self._auto_capture_enabled = False

    def set_auto_capture_interval(self, seconds: float) -> None:
        """Set the minimum interval between auto-captures"""
        self._auto_capture_interval = seconds

    def tick(self) -> Dict[str, Any]:
        """
        Called on each game loop iteration.

        Performs:
            1. MCP polling (check for external commands)
            2. Auto-capture (if enough time has passed)
            3. Change detection

        Returns:
            Dict of changes detected (empty if none)
        """
        changes: Dict[str, Any] = {}

        # 1. Poll MCP
        if self.mcp._enabled:
            cmd_str = self.mcp.poll()
            if cmd_str:
                changes['_mcp_command'] = cmd_str

        # 2. Auto-capture
        if self._auto_capture_enabled and self.lens._enabled:
            now = time.time()
            if now - self._last_auto_capture >= self._auto_capture_interval:
                detected = self.lens.auto_capture()
                if detected:
                    changes['_auto_capture'] = detected
                self._last_auto_capture = now

        return changes

    # ── State Export ──────────────────────────────────────────────

    def get_full_state_json(self, pretty: bool = False) -> str:
        """
        Get complete state as JSON (LENS + SKIN + MCP + Spool).

        Args:
            pretty: If True, pretty-print the JSON

        Returns:
            JSON string of full state
        """
        import json

        state = {
            "lens": {
                "events": len(self.lens.event_queue),
                "snapshots": list(self.lens.snapshots.keys()),
                "watched_vars": list(self.lens.watched_vars | self.lens.custom_vars),
            },
            "skin": {
                "active": self.skin.active_skin_name,
                "available": self.skin.available_skins,
                "mappings": {str(k): v for k, v in self.skin._char_mappings.items()},
            },
            "mcp": {
                "pending_commands": len(self.mcp._pending_commands),
                "responses": len(self.mcp._responses),
            },
            "spool": {
                "save_count": self.spool.save_count,
                "load_count": self.spool.load_count,
                "directory": self.spool.spool_dir,
            },
        }

        indent = 2 if pretty else None
        return json.dumps(state, indent=indent)

    # ── Convenience ───────────────────────────────────────────────

    def reset_all(self) -> None:
        """Reset all engines to their initial state"""
        self.lens.event_queue.clear()
        self.lens.snapshots.clear()
        self.lens._previous_state.clear()
        self.skin.apply("teletext_classic")
        self.mcp.clear_commands()
        self.mcp.clear_responses()
        self._last_auto_capture = 0.0


# Convenience function

def create_lens_skin_mcp(interpreter=None, spool_dir: Optional[str] = None) -> LensSkinMCP:
    """Create and return a unified LensSkinMCP instance"""
    return LensSkinMCP(interpreter, spool_dir)
