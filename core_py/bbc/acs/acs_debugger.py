"""
ACS Debugger — Debugging Interface for ACS Emulator

Provides breakpoints, single-stepping, memory inspection, and
register state display for the ACS emulator.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
import time


@dataclass
class Breakpoint:
    """A breakpoint in the emulator"""
    address: int
    enabled: bool = True
    condition: Optional[str] = None
    hit_count: int = 0
    description: str = ""


class ACS_Debugger:
    """
    Debugger for the ACS emulator.

    Provides breakpoints, single-stepping, memory inspection,
    and register state display.
    """

    def __init__(self):
        """Initialize the debugger."""
        self._breakpoints: Dict[int, Breakpoint] = {}
        self._stepping: bool = False
        self._paused: bool = False
        self._step_count: int = 0
        self._max_steps: int = 0

        # Callbacks
        self._on_breakpoint_hit: Optional[Callable[[int, Breakpoint], None]] = None
        self._on_step: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_pause: Optional[Callable[[], None]] = None
        self._on_resume: Optional[Callable[[], None]] = None

        # Execution trace
        self._trace: List[Dict[str, Any]] = []
        self._tracing_enabled: bool = False
        self._max_trace_entries: int = 1000

    # ── Breakpoints ────────────────────────────────────────────────

    def set_breakpoint(self, address: int, description: str = "",
                       condition: Optional[str] = None) -> Breakpoint:
        """Set a breakpoint at an address.

        Args:
            address: Memory address to break at
            description: Optional description
            condition: Optional condition string

        Returns:
            The created Breakpoint
        """
        bp = Breakpoint(
            address=address,
            description=description or f"BP @ 0x{address:04X}",
            condition=condition,
        )
        self._breakpoints[address] = bp
        return bp

    def remove_breakpoint(self, address: int) -> None:
        """Remove a breakpoint."""
        self._breakpoints.pop(address, None)

    def clear_breakpoints(self) -> None:
        """Clear all breakpoints."""
        self._breakpoints.clear()

    def enable_breakpoint(self, address: int) -> None:
        """Enable a breakpoint."""
        if address in self._breakpoints:
            self._breakpoints[address].enabled = True

    def disable_breakpoint(self, address: int) -> None:
        """Disable a breakpoint."""
        if address in self._breakpoints:
            self._breakpoints[address].enabled = False

    def get_breakpoints(self) -> Dict[int, Breakpoint]:
        """Get all breakpoints."""
        return dict(self._breakpoints)

    def check_breakpoints(self, address: int) -> Optional[Breakpoint]:
        """Check if there's a hit breakpoint at an address.

        Args:
            address: Current execution address

        Returns:
            Hit Breakpoint, or None
        """
        bp = self._breakpoints.get(address)
        if bp and bp.enabled:
            bp.hit_count += 1
            if self._on_breakpoint_hit:
                self._on_breakpoint_hit(address, bp)
            return bp
        return None

    # ── Stepping ───────────────────────────────────────────────────

    def step_into(self) -> None:
        """Step into the next instruction."""
        self._stepping = True
        self._paused = False

    def step_over(self) -> None:
        """Step over the next instruction."""
        self._stepping = True
        self._paused = False

    def step_out(self) -> None:
        """Step out of the current subroutine."""
        self._stepping = True
        self._paused = False

    def continue_execution(self) -> None:
        """Continue execution after a breakpoint."""
        self._paused = False
        self._stepping = False
        if self._on_resume:
            self._on_resume()

    def pause(self) -> None:
        """Pause execution."""
        self._paused = True
        if self._on_pause:
            self._on_pause()

    # ── Execution Control ──────────────────────────────────────────

    def should_step(self) -> bool:
        """Check if we should step (for the execution loop)."""
        return self._stepping

    def is_paused(self) -> bool:
        """Check if execution is paused."""
        return self._paused

    def record_step(self, cpu_state: Dict[str, Any]) -> None:
        """Record a CPU step for tracing.

        Args:
            cpu_state: Dictionary of CPU register state
        """
        self._step_count += 1
        if self._tracing_enabled:
            entry = dict(cpu_state)
            entry["step"] = self._step_count
            entry["timestamp"] = time.time()
            self._trace.append(entry)
            if len(self._trace) > self._max_trace_entries:
                self._trace.pop(0)

        if self._on_step:
            self._on_step(cpu_state)

    # ── Tracing ────────────────────────────────────────────────────

    def enable_tracing(self) -> None:
        """Enable execution tracing."""
        self._tracing_enabled = True

    def disable_tracing(self) -> None:
        """Disable execution tracing."""
        self._tracing_enabled = False

    def clear_trace(self) -> None:
        """Clear the execution trace."""
        self._trace.clear()

    def get_trace(self) -> List[Dict[str, Any]]:
        """Get the execution trace."""
        return list(self._trace)

    def get_trace_summary(self) -> str:
        """Get a summary of the execution trace."""
        if not self._trace:
            return "No trace data"
        first = self._trace[0]
        last = self._trace[-1]
        return (
            f"Trace: {len(self._trace)} entries, "
            f"0x{first.get('pc', 0):04X} -> 0x{last.get('pc', 0):04X}, "
            f"{self._step_count} total steps"
        )

    # ── Callbacks ──────────────────────────────────────────────────

    def on_breakpoint_hit(self, callback: Callable[[int, Breakpoint], None]) -> None:
        """Register a callback for breakpoint hits."""
        self._on_breakpoint_hit = callback

    def on_step(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback for each CPU step."""
        self._on_step = callback

    def on_pause(self, callback: Callable[[], None]) -> None:
        """Register a callback for pause."""
        self._on_pause = callback

    def on_resume(self, callback: Callable[[], None]) -> None:
        """Register a callback for resume."""
        self._on_resume = callback

    # ── State ──────────────────────────────────────────────────────

    def get_state(self) -> Dict[str, Any]:
        """Get the current debugger state."""
        return {
            "paused": self._paused,
            "stepping": self._stepping,
            "step_count": self._step_count,
            "breakpoints": {
                addr: {
                    "enabled": bp.enabled,
                    "hit_count": bp.hit_count,
                    "description": bp.description,
                }
                for addr, bp in self._breakpoints.items()
            },
            "tracing": self._tracing_enabled,
            "trace_entries": len(self._trace),
        }

    def reset(self) -> None:
        """Reset the debugger state."""
        self._breakpoints.clear()
        self._stepping = False
        self._paused = False
        self._step_count = 0
        self._max_steps = 0
        self._trace.clear()
        self._tracing_enabled = False
