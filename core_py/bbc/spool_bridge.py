"""
Spool Bridge — Save/Load Game State for uCode1

Spool provides snapshot-based save/load for BBC BASIC programs.
Game state is serialised to JSON and stored in the uDOS spool store.

BBC BASIC extensions:

    PROC_SPOOL_Save("filename")   — Save current game state to Spool file
    FN_SPOOL_Load("filename")     — Load a Spool file and return success flag

The Spool format is cross-snack compatible, allowing state to be
shared between different games (e.g., Eamon -> ACS).
"""

import json
import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class SpoolHeader:
    """Header metadata for a Spool file"""
    version: str = "1.0"
    snack_id: str = "bbc_basic"
    snack_name: str = "BBC BASIC Program"
    timestamp: float = 0.0
    save_slot: str = "auto"
    player_name: str = "Adventurer"
    play_time_seconds: int = 0
    tags: List[str] = field(default_factory=list)


@dataclass
class SpoolEnvelope:
    """Complete Spool save file"""
    header: SpoolHeader = field(default_factory=SpoolHeader)
    variables: Dict[str, Any] = field(default_factory=dict)
    arrays: Dict[str, List[Any]] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    snapshots: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SpoolBridge:
    """
    Spool save/load bridge for BBC BASIC programs.

    Provides save/load functionality that serialises the interpreter's
    full state (variables, arrays, events) to portable JSON files.
    """

    def __init__(self, interpreter=None, spool_dir: Optional[str] = None):
        """
        Initialize Spool bridge.

        Args:
            interpreter: Optional BBCBasicInterpreter to attach to
            spool_dir: Directory for spool files (default: ~/.udos/spools/)
        """
        self.interpreter = interpreter
        self._spool_dir = spool_dir or os.path.expanduser("~/.udos/spools")
        self._current_spool: Optional[SpoolEnvelope] = None
        self._save_count: int = 0
        self._load_count: int = 0

        # Ensure spool directory exists
        os.makedirs(self._spool_dir, exist_ok=True)

        # Auto-attach if interpreter provided
        if interpreter is not None:
            self.attach_to_interpreter(interpreter)

    # ── Properties ────────────────────────────────────────────────

    @property
    def spool_dir(self) -> str:
        """Get the spool directory path"""
        return self._spool_dir

    @spool_dir.setter
    def spool_dir(self, path: str) -> None:
        """Set the spool directory path"""
        self._spool_dir = path
        os.makedirs(self._spool_dir, exist_ok=True)

    @property
    def save_count(self) -> int:
        """Get the number of saves performed"""
        return self._save_count

    @property
    def load_count(self) -> int:
        """Get the number of loads performed"""
        return self._load_count

    # ── Save ──────────────────────────────────────────────────────

    def save(self, filename: str) -> bool:
        """
        Save current game state to a Spool file.

        This is the implementation of PROC_SPOOL_Save.

        Args:
            filename: Name for the save file (without extension)

        Returns:
            True if save was successful
        """
        if not self.interpreter:
            return False

        try:
            # Build spool envelope from interpreter state
            envelope = SpoolEnvelope(
                header=SpoolHeader(
                    version="1.0",
                    snack_id="bbc_basic",
                    snack_name="BBC BASIC Program",
                    timestamp=time.time(),
                    save_slot=filename,
                    tags=["bbc_basic", "ucode1"],
                ),
                variables=dict(self.interpreter.state.variables),
                arrays=dict(self.interpreter.state.arrays),
            )

            # Include LENS events if available
            if hasattr(self.interpreter, '_lens_engine') and self.interpreter._lens_engine:
                lens = self.interpreter._lens_engine
                envelope.events = [asdict(e) for e in lens.event_queue]
                envelope.snapshots = {
                    name: asdict(snap)
                    for name, snap in lens.snapshots.items()
                }

            # Include SKIN state if available
            if hasattr(self.interpreter, '_skin_engine') and self.interpreter._skin_engine:
                skin = self.interpreter._skin_engine
                envelope.metadata['skin'] = skin.active_skin_name
                envelope.metadata['char_mappings'] = {
                    str(k): v for k, v in skin._char_mappings.items()
                }
                envelope.metadata['palette_overrides'] = {
                    str(k): v for k, v in skin._palette_overrides.items()
                }

            # Include MCP state if available
            if hasattr(self.interpreter, '_mcp_bridge') and self.interpreter._mcp_bridge:
                mcp = self.interpreter._mcp_bridge
                envelope.metadata['mcp_responses'] = [
                    {"success": r.success, "result": r.result}
                    for r in mcp._responses
                ]

            # Serialize to JSON
            spool_data = {
                "header": asdict(envelope.header),
                "variables": envelope.variables,
                "arrays": envelope.arrays,
                "events": envelope.events,
                "snapshots": envelope.snapshots,
                "metadata": envelope.metadata,
            }

            # Write to file
            spool_path = self._get_spool_path(filename)
            with open(spool_path, 'w') as f:
                json.dump(spool_data, f, indent=2, default=str)

            self._current_spool = envelope
            self._save_count += 1
            return True

        except Exception as e:
            print(f"Spool save error: {e}")
            return False

    def _get_spool_path(self, filename: str) -> str:
        """Get the full path for a spool file"""
        # Ensure filename has .spool extension
        if not filename.endswith('.spool'):
            filename += '.spool'
        return os.path.join(self._spool_dir, filename)

    # ── Load ──────────────────────────────────────────────────────

    def load(self, filename: str) -> bool:
        """
        Load game state from a Spool file.

        This is the implementation of FN_SPOOL_Load.

        Args:
            filename: Name of the save file to load (without extension)

        Returns:
            True if load was successful
        """
        if not self.interpreter:
            return False

        try:
            spool_path = self._get_spool_path(filename)
            if not os.path.exists(spool_path):
                return False

            # Read from file
            with open(spool_path, 'r') as f:
                spool_data = json.load(f)

            # Restore variables
            variables = spool_data.get('variables', {})
            self.interpreter.state.variables.clear()
            self.interpreter.state.variables.update(variables)

            # Restore arrays
            arrays = spool_data.get('arrays', {})
            self.interpreter.state.arrays.clear()
            self.interpreter.state.arrays.update(arrays)

            # Restore LENS events if available
            if hasattr(self.interpreter, '_lens_engine') and self.interpreter._lens_engine:
                lens = self.interpreter._lens_engine
                events_data = spool_data.get('events', [])
                lens.event_queue.clear()
                for e_data in events_data:
                    from .lens import LENSEvent
                    lens.event_queue.append(LENSEvent(
                        name=e_data.get('name', 'unknown'),
                        timestamp=e_data.get('timestamp', 0),
                        state=e_data.get('state', {}),
                        event_type=e_data.get('event_type', 'game_event'),
                    ))

            # Restore SKIN state if available
            metadata = spool_data.get('metadata', {})
            if hasattr(self.interpreter, '_skin_engine') and self.interpreter._skin_engine:
                skin = self.interpreter._skin_engine
                skin_name = metadata.get('skin', 'teletext_classic')
                skin.apply(skin_name)
                # Restore char mappings
                mappings = metadata.get('char_mappings', {})
                for k, v in mappings.items():
                    skin.map_char(int(k), v)
                # Restore palette
                palette = metadata.get('palette_overrides', {})
                for k, v in palette.items():
                    skin.set_palette(int(k), v)

            self._load_count += 1
            return True

        except Exception as e:
            print(f"Spool load error: {e}")
            return False

    # ── Spool Management ──────────────────────────────────────────

    def list_spools(self) -> List[Dict[str, Any]]:
        """
        List all available spool files.

        Returns:
            List of dicts with 'filename', 'timestamp', 'size' keys
        """
        spools = []
        spool_dir = Path(self._spool_dir)
        for f in sorted(spool_dir.glob("*.spool")):
            try:
                with open(f, 'r') as fh:
                    data = json.load(fh)
                header = data.get('header', {})
                spools.append({
                    'filename': f.stem,
                    'timestamp': header.get('timestamp', 0),
                    'size': f.stat().st_size,
                    'save_slot': header.get('save_slot', ''),
                    'player_name': header.get('player_name', ''),
                })
            except Exception:
                spools.append({
                    'filename': f.stem,
                    'timestamp': 0,
                    'size': f.stat().st_size,
                })
        return spools

    def delete_spool(self, filename: str) -> bool:
        """Delete a spool file"""
        spool_path = self._get_spool_path(filename)
        if os.path.exists(spool_path):
            os.remove(spool_path)
            return True
        return False

    def get_spool_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get information about a spool file"""
        spool_path = self._get_spool_path(filename)
        if not os.path.exists(spool_path):
            return None
        try:
            with open(spool_path, 'r') as f:
                data = json.load(f)
            header = data.get('header', {})
            return {
                'filename': filename,
                'path': spool_path,
                'header': header,
                'variable_count': len(data.get('variables', {})),
                'event_count': len(data.get('events', [])),
                'size': os.path.getsize(spool_path),
            }
        except Exception:
            return None

    # ── Integration ───────────────────────────────────────────────

    def attach_to_interpreter(self, interpreter) -> None:
        """
        Attach this Spool bridge to a BBC BASIC interpreter.

        This wires up the PROC_SPOOL_Save and FN_SPOOL_Load handlers.

        Args:
            interpreter: BBCBasicInterpreter instance
        """
        self.interpreter = interpreter
        interpreter._spool_bridge = self

        # Add Spool keywords to interpreter's keyword list
        spool_keywords = [
            "PROC_SPOOL_Save",
            "FN_SPOOL_Load",
        ]
        for kw in spool_keywords:
            if kw not in interpreter._keywords:
                interpreter._keywords.append(kw)


# Convenience functions

def create_spool_bridge(interpreter=None, spool_dir: Optional[str] = None) -> SpoolBridge:
    """Create and return a new Spool bridge"""
    return SpoolBridge(interpreter, spool_dir)
