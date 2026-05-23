"""
Ceefax MCP Protocol — Remote control for teletext pages

Provides MCP (Master Control Protocol) commands for Ceefax teletext:
    NEXT       — Next page
    PREV       — Previous page
    SUB        — Toggle subtitle/reveal
    INDEX      — Go to index page
    REVEAL     — Toggle hidden content reveal
    PAGE <n>   — Go to specific page number
    HOLD       — Toggle page hold (stop auto-refresh)
    SIZE       — Toggle double-height mode
    MIX        — Toggle mixed text/graphics mode
    LIST       — List available pages
    STATUS     — Show current page status

Usage:
    protocol = CeefaxMCPProtocol()
    protocol.queue_command("PAGE 101")
    protocol.queue_command("NEXT")
    cmd = protocol.poll()
"""

import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class CeefaxCommandType(Enum):
    """Ceefax-specific MCP command types"""
    NEXT = "NEXT"
    PREV = "PREV"
    SUB = "SUB"
    INDEX = "INDEX"
    REVEAL = "REVEAL"
    PAGE = "PAGE"
    HOLD = "HOLD"
    SIZE = "SIZE"
    MIX = "MIX"
    LIST = "LIST"
    STATUS = "STATUS"
    UNKNOWN = "UNKNOWN"


@dataclass
class CeefaxCommand:
    """A parsed Ceefax MCP command"""
    command: str
    command_type: CeefaxCommandType
    args: Dict[str, str] = field(default_factory=dict)
    raw: str = ""
    source: str = "mcp"
    request_id: str = ""


@dataclass
class CeefaxResponse:
    """A response to a Ceefax MCP command"""
    success: bool
    result: str = ""
    error: str = ""
    request_id: str = ""
    page_number: Optional[int] = None


class CeefaxMCPProtocol:
    """
    MCP command protocol for Ceefax teletext remote control.

    Provides a command queue that can be polled by the Ceefax
    renderer or CLI, with standard Ceefax remote control commands.

    Features:
        - Queue commands from MCP, CLI, or programmatic sources
        - Poll for pending commands
        - Register command callbacks
        - Parse raw command strings
        - Track command history
    """

    # Standard Ceefax commands
    STANDARD_COMMANDS = {
        "NEXT": CeefaxCommandType.NEXT,
        "PREV": CeefaxCommandType.PREV,
        "SUB": CeefaxCommandType.SUB,
        "INDEX": CeefaxCommandType.INDEX,
        "REVEAL": CeefaxCommandType.REVEAL,
        "PAGE": CeefaxCommandType.PAGE,
        "HOLD": CeefaxCommandType.HOLD,
        "SIZE": CeefaxCommandType.SIZE,
        "MIX": CeefaxCommandType.MIX,
        "LIST": CeefaxCommandType.LIST,
        "STATUS": CeefaxCommandType.STATUS,
    }

    def __init__(self):
        """Initialize the MCP protocol handler"""
        self._pending_commands: List[CeefaxCommand] = []
        self._responses: List[CeefaxResponse] = []
        self._command_history: List[CeefaxCommand] = []
        self._on_command_callbacks: List[Callable[[CeefaxCommand], Optional[str]]] = []
        self._enabled: bool = True
        self._current_page: int = 100
        self._subtitle_visible: bool = False
        self._reveal_visible: bool = False
        self._hold_enabled: bool = False
        self._double_height: bool = False
        self._mix_mode: bool = False

    # ── Configuration ──────────────────────────────────────────────

    def enable(self) -> None:
        """Enable command processing"""
        self._enabled = True

    def disable(self) -> None:
        """Disable command processing"""
        self._enabled = False

    def add_callback(self, callback: Callable[[CeefaxCommand], Optional[str]]) -> None:
        """
        Register a callback for when commands are received.

        The callback receives the CeefaxCommand and can return a response string.

        Args:
            callback: Function that processes a command and returns optional response
        """
        self._on_command_callbacks.append(callback)

    # ── Command Queue ──────────────────────────────────────────────

    def queue_command(self, command_str: str, source: str = "mcp") -> CeefaxCommand:
        """
        Queue a Ceefax MCP command for processing.

        Args:
            command_str: Raw command string (e.g., "PAGE 101", "NEXT")
            source: Source identifier

        Returns:
            The parsed CeefaxCommand
        """
        cmd = self._parse_command(command_str, source)
        self._pending_commands.append(cmd)
        self._command_history.append(cmd)
        return cmd

    def _parse_command(self, raw: str, source: str = "mcp") -> CeefaxCommand:
        """Parse a raw command string into a CeefaxCommand"""
        raw = raw.strip().upper()
        parts = raw.split(None, 1)
        cmd_name = parts[0] if parts else ""
        args_str = parts[1] if len(parts) > 1 else ""

        # Parse args (key=value pairs or positional)
        args: Dict[str, str] = {}
        if args_str:
            for arg_part in args_str.split():
                if "=" in arg_part:
                    key, value = arg_part.split("=", 1)
                    args[key] = value
                else:
                    # Positional argument (e.g., page number)
                    args["value"] = arg_part

        cmd_type = self.STANDARD_COMMANDS.get(cmd_name, CeefaxCommandType.UNKNOWN)

        return CeefaxCommand(
            command=cmd_name,
            command_type=cmd_type,
            args=args,
            raw=raw,
            source=source,
            request_id=f"ceefax_{int(time.time() * 1000)}"
        )

    # ── Polling ────────────────────────────────────────────────────

    def poll(self) -> Optional[CeefaxCommand]:
        """
        Check for a pending command.

        Returns:
            The next pending CeefaxCommand, or None if queue is empty
        """
        if not self._enabled or not self._pending_commands:
            return None

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
            self._responses.append(CeefaxResponse(
                success=True,
                result=response,
                request_id=cmd.request_id,
            ))

        return cmd

    def poll_all(self) -> List[CeefaxCommand]:
        """
        Poll all pending commands at once.

        Returns:
            List of all pending CeefaxCommands
        """
        commands = []
        while True:
            cmd = self.poll()
            if cmd is None:
                break
            commands.append(cmd)
        return commands

    # ── Command Processing ─────────────────────────────────────────

    def process_command(self, cmd: CeefaxCommand) -> Optional[CeefaxResponse]:
        """
        Process a command and return a response.

        Args:
            cmd: The Ceefax command to process

        Returns:
            CeefaxResponse or None if the command needs external handling
        """
        if cmd.command_type == CeefaxCommandType.NEXT:
            self._current_page += 1
            return CeefaxResponse(
                success=True,
                result=f"OK: page {self._current_page}",
                page_number=self._current_page,
            )

        elif cmd.command_type == CeefaxCommandType.PREV:
            self._current_page = max(100, self._current_page - 1)
            return CeefaxResponse(
                success=True,
                result=f"OK: page {self._current_page}",
                page_number=self._current_page,
            )

        elif cmd.command_type == CeefaxCommandType.SUB:
            self._subtitle_visible = not self._subtitle_visible
            state = "on" if self._subtitle_visible else "off"
            return CeefaxResponse(
                success=True,
                result=f"OK: subtitle {state}",
            )

        elif cmd.command_type == CeefaxCommandType.INDEX:
            self._current_page = 100
            return CeefaxResponse(
                success=True,
                result="OK: index page 100",
                page_number=100,
            )

        elif cmd.command_type == CeefaxCommandType.REVEAL:
            self._reveal_visible = not self._reveal_visible
            state = "on" if self._reveal_visible else "off"
            return CeefaxResponse(
                success=True,
                result=f"OK: reveal {state}",
            )

        elif cmd.command_type == CeefaxCommandType.PAGE:
            page_str = cmd.args.get("value", "")
            if page_str.isdigit():
                self._current_page = int(page_str)
                return CeefaxResponse(
                    success=True,
                    result=f"OK: page {self._current_page}",
                    page_number=self._current_page,
                )
            return CeefaxResponse(
                success=False,
                error=f"Invalid page number: {page_str}",
            )

        elif cmd.command_type == CeefaxCommandType.HOLD:
            self._hold_enabled = not self._hold_enabled
            state = "on" if self._hold_enabled else "off"
            return CeefaxResponse(
                success=True,
                result=f"OK: hold {state}",
            )

        elif cmd.command_type == CeefaxCommandType.SIZE:
            self._double_height = not self._double_height
            state = "double" if self._double_height else "normal"
            return CeefaxResponse(
                success=True,
                result=f"OK: size {state}",
            )

        elif cmd.command_type == CeefaxCommandType.MIX:
            self._mix_mode = not self._mix_mode
            state = "on" if self._mix_mode else "off"
            return CeefaxResponse(
                success=True,
                result=f"OK: mix {state}",
            )

        elif cmd.command_type == CeefaxCommandType.LIST:
            return CeefaxResponse(
                success=True,
                result="OK: use LIST command with page store",
            )

        elif cmd.command_type == CeefaxCommandType.STATUS:
            return CeefaxResponse(
                success=True,
                result=json.dumps({
                    "current_page": self._current_page,
                    "subtitle": self._subtitle_visible,
                    "reveal": self._reveal_visible,
                    "hold": self._hold_enabled,
                    "double_height": self._double_height,
                    "mix_mode": self._mix_mode,
                }),
                page_number=self._current_page,
            )

        return None  # Unknown command

    # ── Response Queue ─────────────────────────────────────────────

    def get_response(self) -> Optional[CeefaxResponse]:
        """Get the next pending response"""
        if self._responses:
            return self._responses.pop(0)
        return None

    def get_responses_json(self) -> str:
        """Get all responses as JSON"""
        return json.dumps([
            {
                "success": r.success,
                "result": r.result,
                "error": r.error,
                "page_number": r.page_number,
            }
            for r in self._responses
        ], indent=2)

    def clear_responses(self) -> None:
        """Clear all pending responses"""
        self._responses.clear()

    def clear_commands(self) -> None:
        """Clear all pending commands"""
        self._pending_commands.clear()

    # ── State ──────────────────────────────────────────────────────

    @property
    def current_page(self) -> int:
        """Current page number"""
        return self._current_page

    @current_page.setter
    def current_page(self, page: int) -> None:
        """Set current page number"""
        self._current_page = page

    @property
    def subtitle_visible(self) -> bool:
        """Whether subtitle is visible"""
        return self._subtitle_visible

    @property
    def reveal_visible(self) -> bool:
        """Whether reveal is visible"""
        return self._reveal_visible

    @property
    def hold_enabled(self) -> bool:
        """Whether hold is enabled"""
        return self._hold_enabled

    @property
    def double_height(self) -> bool:
        """Whether double-height mode is active"""
        return self._double_height

    @property
    def mix_mode(self) -> bool:
        """Whether mix mode is active"""
        return self._mix_mode

    def get_state(self) -> Dict[str, Any]:
        """Get full current state as dict"""
        return {
            "current_page": self._current_page,
            "subtitle": self._subtitle_visible,
            "reveal": self._reveal_visible,
            "hold": self._hold_enabled,
            "double_height": self._double_height,
            "mix_mode": self._mix_mode,
            "pending_commands": len(self._pending_commands),
            "pending_responses": len(self._responses),
            "command_history": len(self._command_history),
        }

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent command history"""
        return [
            {
                "command": c.command,
                "type": c.command_type.value,
                "args": c.args,
                "source": c.source,
                "timestamp": c.request_id,
            }
            for c in self._command_history[-limit:]
        ]


# Convenience function
def create_ceefax_mcp() -> CeefaxMCPProtocol:
    """Create and return a CeefaxMCPProtocol instance"""
    return CeefaxMCPProtocol()
