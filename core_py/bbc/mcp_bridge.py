"""
MCP Bridge — Master Control Protocol for uCode1

MCP commands control the snack externally (from CLI, another snack, or a UI).
This bridge allows BBC BASIC programs to poll for and respond to MCP commands.

BBC BASIC extensions:

    FN_MCP_Poll()           — Check for pending MCP command, returns string
    PROC_MCP_Respond(result$) — Send response back to MCP caller

MCP commands from external sources:
    PAUSE, RESUME, SAVE, RESTORE, EXPORT_SPOOL, INSPECT, EVAL, QUIT
"""

import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class MCPCommandType(Enum):
    """Standard MCP command types"""
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    SAVE = "SAVE"
    RESTORE = "RESTORE"
    EXPORT_SPOOL = "EXPORT_SPOOL"
    INSPECT = "INSPECT"
    EVAL = "EVAL"
    QUIT = "QUIT"
    SKIN = "SKIN"
    STEP = "STEP"
    LIST_SNACKS = "LIST_SNACKS"
    UNKNOWN = "UNKNOWN"


@dataclass
class MCPCommand:
    """A parsed MCP command"""
    command: str
    command_type: MCPCommandType
    args: Dict[str, str] = field(default_factory=dict)
    raw: str = ""
    source: str = "external"
    request_id: str = ""


@dataclass
class MCPResponse:
    """A response to an MCP command"""
    success: bool
    result: str = ""
    error: str = ""
    request_id: str = ""


class MCPBridge:
    """
    MCP command bridge for BBC BASIC programs.

    Provides a polling interface for BASIC programs to check for
    and respond to external MCP commands.
    """

    # Standard MCP commands that can be parsed
    STANDARD_COMMANDS = {
        "PAUSE": MCPCommandType.PAUSE,
        "RESUME": MCPCommandType.RESUME,
        "SAVE": MCPCommandType.SAVE,
        "RESTORE": MCPCommandType.RESTORE,
        "EXPORT_SPOOL": MCPCommandType.EXPORT_SPOOL,
        "INSPECT": MCPCommandType.INSPECT,
        "EVAL": MCPCommandType.EVAL,
        "QUIT": MCPCommandType.QUIT,
        "SKIN": MCPCommandType.SKIN,
        "STEP": MCPCommandType.STEP,
        "LIST_SNACKS": MCPCommandType.LIST_SNACKS,
    }

    def __init__(self, interpreter=None):
        """
        Initialize MCP bridge.

        Args:
            interpreter: Optional BBCBasicInterpreter to attach to
        """
        self.interpreter = interpreter
        self._pending_commands: List[MCPCommand] = []
        self._responses: List[MCPResponse] = []
        self._external_command_source: Optional[Callable[[], Optional[str]]] = None
        self._on_command_callbacks: List[Callable[[MCPCommand], Optional[str]]] = []
        self._enabled: bool = True

        # Auto-attach if interpreter provided
        if interpreter is not None:
            self.attach_to_interpreter(interpreter)

    # ── Configuration ──────────────────────────────────────────────

    def enable(self) -> None:
        """Enable MCP polling"""
        self._enabled = True

    def disable(self) -> None:
        """Disable MCP polling"""
        self._enabled = False

    def set_external_source(self, source_fn: Callable[[], Optional[str]]) -> None:
        """
        Set an external function that provides MCP commands.

        This can be connected to a gRPC server, Unix socket, or stdin.

        Args:
            source_fn: Function that returns a command string or None
        """
        self._external_command_source = source_fn

    def add_command_callback(self, callback: Callable[[MCPCommand], Optional[str]]) -> None:
        """
        Register a callback for when commands are received.

        The callback receives the MCPCommand and can return a response string.

        Args:
            callback: Function that processes a command and returns optional response
        """
        self._on_command_callbacks.append(callback)

    # ── Command Queue ─────────────────────────────────────────────

    def queue_command(self, command_str: str, source: str = "external") -> MCPCommand:
        """
        Queue an MCP command for the BASIC program to poll.

        Args:
            command_str: Raw command string (e.g., "PAUSE" or "SAVE slot=dungeon1")
            source: Source identifier

        Returns:
            The parsed MCPCommand
        """
        cmd = self._parse_command(command_str, source)
        self._pending_commands.append(cmd)
        return cmd

    def _parse_command(self, raw: str, source: str = "external") -> MCPCommand:
        """Parse a raw command string into an MCPCommand"""
        raw = raw.strip()
        parts = raw.split(None, 1)  # Split on first whitespace
        cmd_name = parts[0].upper() if parts else ""
        args_str = parts[1] if len(parts) > 1 else ""

        # Parse args (key=value pairs)
        args: Dict[str, str] = {}
        if args_str:
            for arg_part in args_str.split():
                if "=" in arg_part:
                    key, value = arg_part.split("=", 1)
                    args[key] = value
                else:
                    # Positional argument
                    args["value"] = arg_part

        cmd_type = self.STANDARD_COMMANDS.get(cmd_name, MCPCommandType.UNKNOWN)

        return MCPCommand(
            command=cmd_name,
            command_type=cmd_type,
            args=args,
            raw=raw,
            source=source,
            request_id=f"mcp_{int(time.time() * 1000)}"
        )

    # ── Polling (for BBC BASIC) ───────────────────────────────────

    def poll(self) -> str:
        """
        Check for a pending MCP command.

        This is the implementation of FN_MCP_Poll.
        Returns the command string if available, or empty string if none.

        Returns:
            Command string (e.g., "PAUSE", "SAVE slot=dungeon1") or ""
        """
        if not self._enabled:
            return ""

        # Check external source first
        if self._external_command_source:
            try:
                ext_cmd = self._external_command_source()
                if ext_cmd:
                    self.queue_command(ext_cmd, source="external")
            except Exception:
                pass

        # Return next pending command
        if self._pending_commands:
            cmd = self._pending_commands.pop(0)

            # Notify callbacks
            response = None
            for cb in self._on_command_callbacks:
                try:
                    result = cb(cmd)
                    if result is not None:
                        response = result
                except Exception:
                    pass

            # If there's a response, queue it
            if response is not None:
                self._responses.append(MCPResponse(
                    success=True,
                    result=response,
                    request_id=cmd.request_id
                ))

            return cmd.raw

        return ""

    def respond(self, result: str) -> None:
        """
        Send a response back to the MCP caller.

        This is the implementation of PROC_MCP_Respond.

        Args:
            result: Response string
        """
        self._responses.append(MCPResponse(
            success=True,
            result=result,
            request_id=f"resp_{int(time.time() * 1000)}"
        ))

    # ── Command Processing ────────────────────────────────────────

    def process_command(self, cmd: MCPCommand) -> Optional[str]:
        """
        Process a command and return a response.

        This handles standard commands that don't need BASIC program involvement.

        Args:
            cmd: The MCP command to process

        Returns:
            Response string or None if the command needs BASIC handling
        """
        if cmd.command_type == MCPCommandType.PAUSE:
            if self.interpreter:
                self.interpreter.stop()
            return "OK: paused"

        elif cmd.command_type == MCPCommandType.RESUME:
            if self.interpreter:
                self.interpreter.state.running = True
            return "OK: resumed"

        elif cmd.command_type == MCPCommandType.QUIT:
            if self.interpreter:
                self.interpreter.stop()
            return "OK: quit"

        elif cmd.command_type == MCPCommandType.INSPECT:
            var_name = cmd.args.get("value", "")
            if self.interpreter and var_name:
                value = self.interpreter.state.variables.get(var_name, "undefined")
                return f"{var_name} = {value}"
            return "ERROR: variable not found"

        elif cmd.command_type == MCPCommandType.EVAL:
            expr = cmd.args.get("value", "")
            if self.interpreter and expr:
                try:
                    result = self.interpreter.evaluate(expr)
                    return f"= {result}"
                except Exception as e:
                    return f"ERROR: {e}"
            return "ERROR: no expression"

        elif cmd.command_type == MCPCommandType.LIST_SNACKS:
            return "OK: snack listing not implemented in BASIC mode"

        # Commands that need BASIC program handling
        return None

    # ── Response Queue ────────────────────────────────────────────

    def get_response(self) -> Optional[MCPResponse]:
        """Get the next pending response"""
        if self._responses:
            return self._responses.pop(0)
        return None

    def get_responses_json(self) -> str:
        """Get all responses as JSON"""
        return json.dumps([
            {"success": r.success, "result": r.result, "error": r.error}
            for r in self._responses
        ], indent=2)

    def clear_responses(self) -> None:
        """Clear all pending responses"""
        self._responses.clear()

    def clear_commands(self) -> None:
        """Clear all pending commands"""
        self._pending_commands.clear()

    # ── Integration ───────────────────────────────────────────────

    def attach_to_interpreter(self, interpreter) -> None:
        """
        Attach this MCP bridge to a BBC BASIC interpreter.

        This wires up the FN_MCP_Poll and PROC_MCP_Respond handlers.

        Args:
            interpreter: BBCBasicInterpreter instance
        """
        self.interpreter = interpreter
        interpreter._mcp_bridge = self

        # Add MCP keywords to interpreter's keyword list
        mcp_keywords = [
            "FN_MCP_Poll",
            "PROC_MCP_Respond",
        ]
        for kw in mcp_keywords:
            if kw not in interpreter._keywords:
                interpreter._keywords.append(kw)


# Convenience functions

def create_mcp_bridge(interpreter=None) -> MCPBridge:
    """Create and return a new MCP bridge"""
    return MCPBridge(interpreter)
