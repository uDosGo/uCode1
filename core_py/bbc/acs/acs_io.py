"""
ACS I/O — Input/Output System for ACS Emulator

Provides keyboard input, display output, and peripheral emulation
for the ACS emulator. Maps Apple II I/O addresses to Python callbacks.

Apple II I/O Addresses:
    0xC000: Keyboard data (read)
    0xC010: Keyboard strobe (read to clear)
    0xC020: Speaker toggle
    0xC030: Cassette output
    0xC050: Graphics mode
    0xC051: Text mode
    0xC052: Full graphics
    0xC053: Mixed graphics/text
    0xC054: Page 1
    0xC055: Page 2
    0xC056: Low-res graphics
    0xC057: High-res graphics
    0xC080-C08F: Slot I/O (disk drives, etc.)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum, auto
import time


class ACS_DisplayMode(Enum):
    """Display mode for ACS output"""
    TEXT = auto()
    LOW_RES = auto()
    HIGH_RES = auto()
    MIXED = auto()


@dataclass
class ACS_DisplayState:
    """Current display state"""
    mode: ACS_DisplayMode = ACS_DisplayMode.TEXT
    page: int = 1
    mixed: bool = False
    text_rows: int = 4
    cols: int = 40
    rows: int = 24


class ACS_IO:
    """
    I/O system for the ACS emulator.

    Provides keyboard input, display output, and disk drive
    emulation. Maps to Apple II I/O addresses at 0xC000-0xCFFF.
    """

    def __init__(self):
        """Initialize the I/O system."""
        # Keyboard state
        self._keyboard_buffer: List[int] = []
        self._keyboard_strobe: bool = False
        self._last_key: int = 0

        # Display state
        self.display = ACS_DisplayState()

        # Display output buffer (for LENS/SKIN pipeline)
        self._display_buffer: List[str] = []
        self._display_changed: bool = False

        # Speaker state
        self._speaker_state: bool = False
        self._last_toggle_time: float = 0.0

        # Disk drive state
        self._drive_motor: bool = False
        self._drive_track: int = 0
        self._drive_sector: int = 0

        # Callbacks
        self._on_display_update: Optional[Callable[[str], None]] = None
        self._on_keypress: Optional[Callable[[int], None]] = None
        self._on_speaker_toggle: Optional[Callable[[], None]] = None

        # Register I/O hooks
        self._io_handlers: Dict[int, Dict[str, Any]] = {}
        self._setup_io_handlers()

    def _setup_io_handlers(self) -> None:
        """Set up Apple II I/O address handlers."""
        # Keyboard data read (0xC000)
        self._io_handlers[0xC000] = {
            "read": self._handle_keyboard_read,
            "write": None,
        }

        # Keyboard strobe (0xC010) - read to clear
        self._io_handlers[0xC010] = {
            "read": self._handle_keyboard_strobe,
            "write": None,
        }

        # Speaker toggle (0xC020)
        self._io_handlers[0xC020] = {
            "read": self._handle_speaker_toggle,
            "write": self._handle_speaker_toggle,
        }

        # Graphics mode (0xC050)
        self._io_handlers[0xC050] = {
            "read": lambda: 0,
            "write": lambda v: setattr(self.display, 'mode', ACS_DisplayMode.LOW_RES),
        }

        # Text mode (0xC051)
        self._io_handlers[0xC051] = {
            "read": lambda: 0,
            "write": lambda v: setattr(self.display, 'mode', ACS_DisplayMode.TEXT),
        }

        # Full graphics (0xC052)
        self._io_handlers[0xC052] = {
            "read": lambda: 0,
            "write": lambda v: setattr(self.display, 'mixed', False),
        }

        # Mixed graphics/text (0xC053)
        self._io_handlers[0xC053] = {
            "read": lambda: 0,
            "write": lambda v: setattr(self.display, 'mixed', True),
        }

        # Page 1 (0xC054)
        self._io_handlers[0xC054] = {
            "read": lambda: 0,
            "write": lambda v: setattr(self.display, 'page', 1),
        }

        # Page 2 (0xC055)
        self._io_handlers[0xC055] = {
            "read": lambda: 0,
            "write": lambda v: setattr(self.display, 'page', 2),
        }

        # Low-res graphics (0xC056)
        self._io_handlers[0xC056] = {
            "read": lambda: 0,
            "write": lambda v: setattr(self.display, 'mode', ACS_DisplayMode.LOW_RES),
        }

        # High-res graphics (0xC057)
        self._io_handlers[0xC057] = {
            "read": lambda: 0,
            "write": lambda v: setattr(self.display, 'mode', ACS_DisplayMode.HIGH_RES),
        }

    # ── Keyboard ───────────────────────────────────────────────────

    def key_press(self, key: int) -> None:
        """Simulate a key press.

        Args:
            key: ASCII key code
        """
        self._keyboard_buffer.append(key)
        self._keyboard_strobe = True
        if self._on_keypress:
            self._on_keypress(key)

    def key_press_char(self, char: str) -> None:
        """Simulate a key press from a character.

        Args:
            char: Single character to press
        """
        self.key_press(ord(char.upper()))

    def type_string(self, text: str) -> None:
        """Type a string of characters.

        Args:
            text: Text to type
        """
        for char in text:
            self.key_press_char(char)

    def clear_keyboard_buffer(self) -> None:
        """Clear the keyboard buffer."""
        self._keyboard_buffer.clear()
        self._keyboard_strobe = False

    def _handle_keyboard_read(self) -> int:
        """Handle read from keyboard data port (0xC000)."""
        if self._keyboard_buffer:
            key = self._keyboard_buffer[0]
            return key | 0x80  # Set high bit to indicate key available
        return 0x00

    def _handle_keyboard_strobe(self) -> int:
        """Handle read from keyboard strobe (0xC010) - clears strobe."""
        if self._keyboard_buffer:
            self._last_key = self._keyboard_buffer.pop(0)
        if not self._keyboard_buffer:
            self._keyboard_strobe = False
        return self._last_key

    # ── Display ────────────────────────────────────────────────────

    def write_text(self, text: str) -> None:
        """Write text to the display buffer.

        Args:
            text: Text to display
        """
        self._display_buffer.append(text)
        self._display_changed = True
        if self._on_display_update:
            self._on_display_update(text)

    def write_char(self, char: str) -> None:
        """Write a single character to the display.

        Args:
            char: Character to display
        """
        self.write_text(char)

    def clear_display(self) -> None:
        """Clear the display buffer."""
        self._display_buffer.clear()
        self._display_changed = True

    def get_display_text(self) -> str:
        """Get the current display text."""
        return "".join(self._display_buffer)

    def get_display_lines(self) -> List[str]:
        """Get the current display as lines."""
        return list(self._display_buffer)

    @property
    def display_changed(self) -> bool:
        """Check if the display has changed since last check."""
        changed = self._display_changed
        self._display_changed = False
        return changed

    # ── Speaker ────────────────────────────────────────────────────

    def _handle_speaker_toggle(self) -> int:
        """Handle speaker toggle (0xC020)."""
        self._speaker_state = not self._speaker_state
        self._last_toggle_time = time.time()
        if self._on_speaker_toggle:
            self._on_speaker_toggle()
        return 0

    # ── Disk Drive ─────────────────────────────────────────────────

    def set_drive_track(self, track: int) -> None:
        """Set the current disk drive track.

        Args:
            track: Track number
        """
        self._drive_track = track

    def set_drive_sector(self, sector: int) -> None:
        """Set the current disk drive sector.

        Args:
            sector: Sector number
        """
        self._drive_sector = sector

    def set_drive_motor(self, on: bool) -> None:
        """Set the disk drive motor state.

        Args:
            on: True to turn motor on
        """
        self._drive_motor = on

    # ── Callbacks ──────────────────────────────────────────────────

    def on_display_update(self, callback: Callable[[str], None]) -> None:
        """Register a callback for display updates.

        Args:
            callback: Function called with display text
        """
        self._on_display_update = callback

    def on_keypress(self, callback: Callable[[int], None]) -> None:
        """Register a callback for key presses.

        Args:
            callback: Function called with key code
        """
        self._on_keypress = callback

    def on_speaker_toggle(self, callback: Callable[[], None]) -> None:
        """Register a callback for speaker toggles.

        Args:
            callback: Function called on speaker toggle
        """
        self._on_speaker_toggle = callback

    # ── I/O Handler Registration ───────────────────────────────────

    def get_io_read_handler(self, address: int) -> Optional[Callable[[], int]]:
        """Get the read handler for an I/O address.

        Args:
            address: I/O address

        Returns:
            Read handler function, or None
        """
        handler = self._io_handlers.get(address)
        if handler and handler["read"]:
            return handler["read"]
        return None

    def get_io_write_handler(self, address: int) -> Optional[Callable[[int], None]]:
        """Get the write handler for an I/O address.

        Args:
            address: I/O address

        Returns:
            Write handler function, or None
        """
        handler = self._io_handlers.get(address)
        if handler and handler["write"]:
            return handler["write"]
        return None

    # ── Reset ──────────────────────────────────────────────────────

    def reset(self) -> None:
        """Reset the I/O system."""
        self._keyboard_buffer.clear()
        self._keyboard_strobe = False
        self._last_key = 0
        self._display_buffer.clear()
        self._display_changed = False
        self._speaker_state = False
        self._drive_motor = False
        self._drive_track = 0
        self._drive_sector = 0
        self.display = ACS_DisplayState()
