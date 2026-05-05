"""
LENS — Data Extraction Engine for uCode1

LENS reads the emulated game's memory/variables and emits structured data
to the Feed or Spool. It provides BBC BASIC extensions:

    PROC_LENS_FlagEvent("event_name")   — Send event to LENS feed
    FN_LENS_GetJSON                     — Return current game state as JSON string
    PROC_LENS_Snapshot("name")          — Save a named snapshot to Spool

Auto-capture watches common variables (HP%, GOLD%, ROOM%) and emits
events when they change.
"""

import json
import time
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field, asdict


@dataclass
class LENSEvent:
    """A single LENS-captured event"""
    name: str
    timestamp: float
    state: Dict[str, Any]
    event_type: str = "game_event"


@dataclass
class LENSSnapshot:
    """A named snapshot of game state"""
    name: str
    timestamp: float
    state: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class LENSEngine:
    """
    LENS data extraction engine.

    Captures game state variables, records events, and produces
    structured data for Feed/Spool export.
    """

    # Default variables to auto-watch in BBC BASIC programs
    DEFAULT_WATCHED_VARS: Set[str] = {
        "HP%", "GOLD%", "ROOM%", "LEVEL%", "SCORE%",
        "STR%", "DEX%", "INT%", "WIS%", "CON%",
        "XP%", "AC%", "DMG%", "TURN%", "DEPTH%",
    }

    def __init__(self, interpreter=None):
        """
        Initialize LENS engine.

        Args:
            interpreter: Optional BBCBasicInterpreter to attach to
        """
        self.interpreter = interpreter
        self.watched_vars: Set[str] = set(self.DEFAULT_WATCHED_VARS)
        self.custom_vars: Set[str] = set()
        self.event_queue: List[LENSEvent] = []
        self.snapshots: Dict[str, LENSSnapshot] = {}
        self._previous_state: Dict[str, Any] = {}
        self._on_event_callbacks: List[Callable[[LENSEvent], None]] = []
        self._on_snapshot_callbacks: List[Callable[[LENSSnapshot], None]] = []
        self._enabled: bool = True

        # Auto-attach if interpreter provided
        if interpreter is not None:
            self.attach_to_interpreter(interpreter)

    # ── Configuration ──────────────────────────────────────────────

    def watch_variable(self, var_name: str) -> None:
        """Add a variable to the auto-watch list"""
        self.custom_vars.add(var_name)

    def unwatch_variable(self, var_name: str) -> None:
        """Remove a variable from the auto-watch list"""
        self.custom_vars.discard(var_name)
        self.watched_vars.discard(var_name)

    def enable(self) -> None:
        """Enable LENS capture"""
        self._enabled = True

    def disable(self) -> None:
        """Disable LENS capture"""
        self._enabled = False

    def add_event_callback(self, callback: Callable[[LENSEvent], None]) -> None:
        """Register a callback for when events are captured"""
        self._on_event_callbacks.append(callback)

    def add_snapshot_callback(self, callback: Callable[[LENSSnapshot], None]) -> None:
        """Register a callback for when snapshots are taken"""
        self._on_snapshot_callbacks.append(callback)

    # ── State Capture ─────────────────────────────────────────────

    def capture_state(self) -> Dict[str, Any]:
        """
        Capture current values of all watched variables.

        Returns:
            Dict mapping variable names to their current values
        """
        state: Dict[str, Any] = {}
        all_watched = self.watched_vars | self.custom_vars

        if self.interpreter:
            for var_name in all_watched:
                if var_name in self.interpreter.state.variables:
                    val = self.interpreter.state.variables[var_name]
                    state[var_name] = val

        # Add interpreter state metadata
        if self.interpreter:
            state["_line"] = self.interpreter.state.current_line
            state["_mode"] = self.interpreter.state.screen_mode

        return state

    def capture_all_state(self) -> Dict[str, Any]:
        """
        Capture ALL variables from the interpreter (not just watched).

        Returns:
            Dict of all variables
        """
        if not self.interpreter:
            return {}
        return dict(self.interpreter.state.variables)

    def detect_changes(self) -> Dict[str, Any]:
        """
        Detect which watched variables have changed since last capture.

        Returns:
            Dict of changed variable names -> (old_value, new_value)
        """
        current = self.capture_state()
        changes: Dict[str, Any] = {}

        for var_name, new_val in current.items():
            old_val = self._previous_state.get(var_name)
            if old_val != new_val:
                changes[var_name] = (old_val, new_val)

        self._previous_state = current
        return changes

    # ── Events ────────────────────────────────────────────────────

    def flag_event(self, event_name: str) -> LENSEvent:
        """
        Record a game event with current state snapshot.

        This is the implementation of PROC_LENS_FlagEvent.

        Args:
            event_name: Name of the event (e.g., "entered_dungeon")

        Returns:
            The created LENSEvent
        """
        if not self._enabled:
            return LENSEvent(name=event_name, timestamp=time.time(), state={})

        event = LENSEvent(
            name=event_name,
            timestamp=time.time(),
            state=self.capture_state(),
            event_type="game_event"
        )
        self.event_queue.append(event)

        # Notify callbacks
        for cb in self._on_event_callbacks:
            try:
                cb(event)
            except Exception:
                pass

        return event

    def get_events(self, since: Optional[float] = None) -> List[LENSEvent]:
        """
        Get all recorded events, optionally filtered by time.

        Args:
            since: Optional timestamp to filter events after

        Returns:
            List of LENSEvent objects
        """
        if since is None:
            return list(self.event_queue)
        return [e for e in self.event_queue if e.timestamp >= since]

    def clear_events(self) -> None:
        """Clear all recorded events"""
        self.event_queue.clear()

    # ── JSON Export ───────────────────────────────────────────────

    def get_json(self, pretty: bool = False) -> str:
        """
        Return current game state as a JSON string.

        This is the implementation of FN_LENS_GetJSON.

        Args:
            pretty: If True, pretty-print the JSON

        Returns:
            JSON string of current state
        """
        state = self.capture_all_state()
        indent = 2 if pretty else None
        return json.dumps(state, indent=indent, default=str)

    def get_events_json(self, pretty: bool = False) -> str:
        """
        Return all events as a JSON string.

        Args:
            pretty: If True, pretty-print the JSON

        Returns:
            JSON string of events
        """
        events_data = []
        for event in self.event_queue:
            events_data.append(asdict(event))
        indent = 2 if pretty else None
        return json.dumps(events_data, indent=indent, default=str)

    # ── Snapshots ─────────────────────────────────────────────────

    def snapshot(self, name: str) -> LENSSnapshot:
        """
        Save a named snapshot of the current game state.

        This is the implementation of PROC_LENS_Snapshot.

        Args:
            name: Name for this snapshot (e.g., "before_boss")

        Returns:
            The created LENSSnapshot
        """
        if not self._enabled:
            snapshot = LENSSnapshot(name=name, timestamp=time.time(), state={})
            self.snapshots[name] = snapshot
            return snapshot

        snapshot = LENSSnapshot(
            name=name,
            timestamp=time.time(),
            state=self.capture_all_state(),
            metadata={
                "event_count": len(self.event_queue),
                "line": self.interpreter.state.current_line if self.interpreter else 0,
            }
        )
        self.snapshots[name] = snapshot

        # Notify callbacks
        for cb in self._on_snapshot_callbacks:
            try:
                cb(snapshot)
            except Exception:
                pass

        return snapshot

    def get_snapshot(self, name: str) -> Optional[LENSSnapshot]:
        """Get a saved snapshot by name"""
        return self.snapshots.get(name)

    def list_snapshots(self) -> List[str]:
        """List all saved snapshot names"""
        return list(self.snapshots.keys())

    def get_snapshot_json(self, name: str, pretty: bool = False) -> Optional[str]:
        """Get a snapshot as JSON string"""
        snapshot = self.snapshots.get(name)
        if not snapshot:
            return None
        indent = 2 if pretty else None
        return json.dumps(asdict(snapshot), indent=indent, default=str)

    # ── Integration ───────────────────────────────────────────────

    def attach_to_interpreter(self, interpreter) -> None:
        """
        Attach this LENS engine to a BBC BASIC interpreter.

        This wires up the PROC_LENS_* and FN_LENS_* handlers.

        Args:
            interpreter: BBCBasicInterpreter instance
        """
        self.interpreter = interpreter

        # Register LENS handlers in the interpreter
        interpreter._lens_engine = self

        # Add LENS keywords to interpreter's keyword list
        lens_keywords = [
            "PROC_LENS_FlagEvent",
            "FN_LENS_GetJSON",
            "PROC_LENS_Snapshot",
        ]
        for kw in lens_keywords:
            if kw not in interpreter._keywords:
                interpreter._keywords.append(kw)

    def auto_capture(self) -> Dict[str, Any]:
        """
        Auto-capture: detect changes and flag if any watched vars changed.

        Call this periodically (e.g., after each game loop iteration).

        Returns:
            Dict of changes detected
        """
        changes = self.detect_changes()
        if changes:
            # Auto-flag a state_change event
            var_names = ", ".join(changes.keys())
            self.flag_event(f"state_change: {var_names}")
        return changes


# Convenience functions for BBC BASIC integration

def create_lens_engine(interpreter=None) -> LENSEngine:
    """Create and return a new LENS engine"""
    return LENSEngine(interpreter)
