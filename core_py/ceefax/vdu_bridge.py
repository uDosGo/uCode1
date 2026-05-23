"""
Ceefax VDU Bridge — BBC BASIC VDU output to teletext pages

Connects BBC BASIC VDU output to the Ceefax teletext rendering system.
Captures VDU commands (text, colour, cursor movement, screen mode) and
converts them to TeletextGrid pages for display.

Usage:
    bridge = CeefaxVDUBridge()
    bridge.connect(vdu_driver)
    bridge.set_page_number(500)
    bridge.write("Hello from BBC BASIC!")
    grid = bridge.get_grid()
"""

import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

from .bridge import GameToTeletextBridge, TeletextGrid, TeletextColour


@dataclass
class VDUPageState:
    """State tracking for a VDU-to-teletext page"""
    page_number: int
    title: str = ""
    subtitle: str = ""
    last_updated: float = 0.0
    update_count: int = 0
    mode: int = 7  # Default to teletext mode
    auto_flush: bool = True
    flush_interval: float = 0.5  # seconds


class CeefaxVDUBridge:
    """
    Bridges BBC BASIC VDU output to Ceefax teletext pages.

    Captures VDU commands from a BBC BASIC interpreter and renders
    them as teletext pages. Supports Mode 7 (teletext) natively,
    with other modes down-converted to 40x25 teletext format.

    Features:
        - Connect to BBC BASIC VDU driver
        - Capture text output with colour attributes
        - Handle cursor positioning (TAB, VTAB, HOME)
        - Support screen mode changes (especially Mode 7)
        - Auto-flush to teletext grid
        - Multiple page support for different output channels
        - Callback on page updates
    """

    def __init__(self):
        """Initialize the VDU bridge"""
        self._bridge = GameToTeletextBridge()
        self._pages: Dict[int, VDUPageState] = {}
        self._current_page: int = 500  # Default VDU page
        self._vdu_driver = None
        self._on_update_callbacks: List[Callable[[int, TeletextGrid], None]] = []
        self._enabled: bool = True
        self._buffer: List[str] = []
        self._last_flush: float = time.time()

        # Create default page
        self._ensure_page(self._current_page)

    # ── Connection ─────────────────────────────────────────────────

    def connect(self, vdu_driver) -> None:
        """
        Connect to a BBC BASIC VDU driver.

        Args:
            vdu_driver: VDUDriver instance from bbc.vdu
        """
        self._vdu_driver = vdu_driver
        vdu_driver.add_output_callback(self._on_vdu_text)
        vdu_driver.handler.queue.add_handler(self._on_vdu_command)

    def disconnect(self) -> None:
        """Disconnect from the VDU driver"""
        if self._vdu_driver:
            self._vdu_driver.handler.queue.remove_handler(self._on_vdu_command)
        self._vdu_driver = None

    @property
    def connected(self) -> bool:
        """Whether connected to a VDU driver"""
        return self._vdu_driver is not None

    # ── Page Management ────────────────────────────────────────────

    def set_page_number(self, page_number: int) -> None:
        """Set the current VDU output page number"""
        self._current_page = page_number
        self._ensure_page(page_number)

    def get_page_number(self) -> int:
        """Get the current VDU output page number"""
        return self._current_page

    def _ensure_page(self, page_number: int) -> VDUPageState:
        """Ensure a page state exists"""
        if page_number not in self._pages:
            self._pages[page_number] = VDUPageState(
                page_number=page_number,
                title=f"VDU Output {page_number}",
            )
        return self._pages[page_number]

    def get_page_state(self, page_number: int) -> Optional[VDUPageState]:
        """Get the state for a VDU page"""
        return self._pages.get(page_number)

    def list_pages(self) -> List[Dict[str, Any]]:
        """List all VDU pages"""
        return [
            {
                "page_number": p.page_number,
                "title": p.title,
                "subtitle": p.subtitle,
                "last_updated": p.last_updated,
                "update_count": p.update_count,
                "mode": p.mode,
            }
            for p in self._pages.values()
        ]

    # ── VDU Callbacks ──────────────────────────────────────────────

    def _on_vdu_text(self, text: str) -> None:
        """Handle VDU text output"""
        if not self._enabled:
            return

        self._buffer.append(text)
        page = self._ensure_page(self._current_page)

        # Auto-flush if interval has elapsed
        if page.auto_flush and (time.time() - self._last_flush) >= page.flush_interval:
            self.flush()

    def _on_vdu_command(self, command) -> None:
        """Handle VDU commands"""
        if not self._enabled:
            return

        from ..bbc.vdu import VDUCommandType

        page = self._ensure_page(self._current_page)

        if command.type == VDUCommandType.CLS:
            # Clear screen
            self._bridge.clear()
            self._buffer.clear()

        elif command.type == VDUCommandType.MODE:
            # Screen mode change
            page.mode = command.args[0] if command.args else 7
            if page.mode == 7:
                # Teletext mode — native 40x25
                pass

        elif command.type == VDUCommandType.COLOUR:
            # Colour change
            if command.args:
                colour_idx = command.args[0] & 7
                teletext_colour = TeletextColour(colour_idx)
                self._bridge.grid.set_foreground(teletext_colour)

        elif command.type == VDUCommandType.MOVE:
            # Cursor positioning
            if len(command.args) >= 2:
                col = command.args[0] % TeletextGrid.COLS
                row = command.args[1] % TeletextGrid.ROWS
                self._bridge.grid._cursor_col = col
                self._bridge.grid._cursor_row = row

        elif command.type == VDUCommandType.TEXT:
            # Text output (already handled by _on_vdu_text)
            pass

    # ── Rendering ──────────────────────────────────────────────────

    def write(self, text: str, page_number: Optional[int] = None) -> None:
        """
        Write text to the teletext grid.

        Args:
            text: Text to write
            page_number: Optional page number (uses current if omitted)
        """
        if not self._enabled:
            return

        pn = page_number or self._current_page
        self._ensure_page(pn)

        # If this is a different page, flush current first
        if pn != self._current_page:
            self.flush()
            self._current_page = pn

        self._buffer.append(text)

    def flush(self) -> Optional[TeletextGrid]:
        """
        Flush buffered text to the teletext grid.

        Returns:
            The updated TeletextGrid, or None if buffer was empty
        """
        if not self._buffer:
            return None

        text = "".join(self._buffer)
        self._bridge.process_text(text)
        self._buffer.clear()
        self._last_flush = time.time()

        # Update page state
        page = self._ensure_page(self._current_page)
        page.last_updated = time.time()
        page.update_count += 1

        # Notify callbacks
        self._notify_update(self._current_page, self._bridge.grid)

        return self._bridge.grid

    def clear(self, page_number: Optional[int] = None) -> None:
        """
        Clear the teletext grid for a page.

        Args:
            page_number: Optional page number (clears all if omitted)
        """
        if page_number is not None:
            self._bridge.clear()
            self._buffer.clear()
            if page_number in self._pages:
                self._pages[page_number].update_count = 0
        else:
            self._bridge.clear()
            self._buffer.clear()
            for page in self._pages.values():
                page.update_count = 0

    # ── Grid Access ────────────────────────────────────────────────

    def get_grid(self, page_number: Optional[int] = None) -> TeletextGrid:
        """
        Get the current teletext grid.

        Args:
            page_number: Optional page number (uses current if omitted)

        Returns:
            TeletextGrid
        """
        # Flush any pending text first
        self.flush()
        return self._bridge.grid

    def get_grid_data(self, page_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Get grid data as a dictionary.

        Args:
            page_number: Optional page number

        Returns:
            Dict with grid data
        """
        self.flush()
        data = self._bridge.get_grid_data()
        pn = page_number or self._current_page
        page = self._ensure_page(pn)
        data["page_number"] = pn
        data["title"] = page.title
        data["subtitle"] = page.subtitle
        data["mode"] = page.mode
        return data

    def to_html(self, page_number: Optional[int] = None) -> str:
        """Export current grid to HTML"""
        self.flush()
        pn = page_number or self._current_page
        page = self._ensure_page(pn)
        return self._bridge.to_html(title=page.title)

    def to_ansi(self) -> str:
        """Export current grid to ANSI string"""
        self.flush()
        return self._bridge.to_ansi()

    # ── Callbacks ──────────────────────────────────────────────────

    def on_update(self, callback: Callable[[int, TeletextGrid], None]) -> None:
        """
        Register a callback for page updates.

        Args:
            callback: Function(page_number, TeletextGrid)
        """
        self._on_update_callbacks.append(callback)

    def _notify_update(self, page_number: int, grid: TeletextGrid) -> None:
        """Notify all update callbacks"""
        for cb in self._on_update_callbacks:
            try:
                cb(page_number, grid)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"VDU update callback error: {e}")

    # ── Control ────────────────────────────────────────────────────

    def enable(self) -> None:
        """Enable VDU capture"""
        self._enabled = True

    def disable(self) -> None:
        """Disable VDU capture"""
        self._enabled = False

    @property
    def enabled(self) -> bool:
        """Whether VDU capture is enabled"""
        return self._enabled

    def set_title(self, title: str, page_number: Optional[int] = None) -> None:
        """Set the title for a VDU page"""
        pn = page_number or self._current_page
        page = self._ensure_page(pn)
        page.title = title

    def set_subtitle(self, subtitle: str, page_number: Optional[int] = None) -> None:
        """Set the subtitle for a VDU page"""
        pn = page_number or self._current_page
        page = self._ensure_page(pn)
        page.subtitle = subtitle


# Convenience function
def create_vdu_bridge() -> CeefaxVDUBridge:
    """Create and return a CeefaxVDUBridge"""
    return CeefaxVDUBridge()
