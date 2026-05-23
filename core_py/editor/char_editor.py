"""
Character Editor — Per-Cell Character Editing with 128-Slot Palette

Provides character-level editing tools for the grid editor:
- Character selection from 128-slot palette
- Per-cell character placement
- Character search and filtering
- Emoji overlay management
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..grid.models import Grid, GridCell
from .palette import CharacterPalette, SlotEntry, SlotCategory


@dataclass
class CharEditState:
    """State for the character editor."""
    selected_slot: int = 22  # Default: full block
    search_query: str = ""
    filter_category: Optional[SlotCategory] = None
    show_emoji: bool = True
    show_hex: bool = False
    recent_slots: List[int] = field(default_factory=list)
    favorites: List[int] = field(default_factory=list)

    def add_recent(self, slot: int) -> None:
        """Add a slot to recent history."""
        if slot in self.recent_slots:
            self.recent_slots.remove(slot)
        self.recent_slots.insert(0, slot)
        # Keep max 20 recent
        self.recent_slots = self.recent_slots[:20]

    def toggle_favorite(self, slot: int) -> None:
        """Toggle a slot as favorite."""
        if slot in self.favorites:
            self.favorites.remove(slot)
        else:
            self.favorites.append(slot)


class CharEditor:
    """
    Character editor for per-cell character manipulation.
    
    Works with the 128-slot palette and provides:
    - Character selection and preview
    - Search/filter across slots
    - Recent and favorite tracking
    - Emoji overlay management
    - Batch character replacement
    """

    def __init__(self, palette: Optional[CharacterPalette] = None):
        self.palette = palette or CharacterPalette()
        self.state = CharEditState()

    # ── Character Selection ──────────────────────────────────

    def select_slot(self, slot: int) -> bool:
        """Select a character slot."""
        entry = self.palette.get(slot)
        if entry is None:
            return False
        self.state.selected_slot = slot
        self.state.add_recent(slot)
        return True

    def select_by_char(self, char: str) -> bool:
        """Select a slot by its character."""
        entry = self.palette.get_by_char(char)
        if entry is None:
            return False
        return self.select_slot(entry.slot)

    def select_by_name(self, name: str) -> bool:
        """Select a slot by its name."""
        entry = self.palette.get_by_name(name)
        if entry is None:
            return False
        return self.select_slot(entry.slot)

    @property
    def current_entry(self) -> Optional[SlotEntry]:
        """Get the currently selected slot entry."""
        return self.palette.get(self.state.selected_slot)

    @property
    def current_char(self) -> str:
        """Get the character of the currently selected slot."""
        entry = self.current_entry
        return entry.display_char if entry else ' '

    # ── Search and Filter ────────────────────────────────────

    def search(self, query: str) -> List[SlotEntry]:
        """Search slots by query string."""
        self.state.search_query = query
        if not query:
            return self.get_filtered_slots()
        return self.palette.search(query)

    def set_filter(self, category: Optional[SlotCategory]) -> None:
        """Set the category filter."""
        self.state.filter_category = category

    def get_filtered_slots(self) -> List[SlotEntry]:
        """Get slots filtered by current category filter."""
        if self.state.filter_category == SlotCategory.TELETEXT_BLOCK:
            return self.palette.get_teletext_blocks()
        elif self.state.filter_category == SlotCategory.PRINTABLE_ASCII:
            return self.palette.get_printable_ascii()
        else:
            return self.palette.get_all_slots()

    def get_recent_slots(self) -> List[SlotEntry]:
        """Get recently used slots."""
        return [
            entry for slot in self.state.recent_slots
            if (entry := self.palette.get(slot)) is not None
        ]

    def get_favorite_slots(self) -> List[SlotEntry]:
        """Get favorite slots."""
        return [
            entry for slot in self.state.favorites
            if (entry := self.palette.get(slot)) is not None
        ]

    # ── Emoji Overlay Management ─────────────────────────────

    def set_emoji_overlay(self, slot: int, emoji: Optional[str]) -> None:
        """Set or clear an emoji overlay for a slot."""
        self.palette.set_emoji_overlay(slot, emoji)

    def clear_emoji_overlay(self, slot: int) -> None:
        """Clear the emoji overlay for a slot."""
        self.palette.set_emoji_overlay(slot, None)

    def toggle_emoji_display(self) -> None:
        """Toggle emoji display on/off."""
        self.state.show_emoji = not self.state.show_emoji

    # ── Batch Operations ─────────────────────────────────────

    def replace_char_in_grid(self, grid: Grid, old_char: str, new_char: str) -> int:
        """
        Replace all occurrences of a character in a grid.
        Returns the number of cells changed.
        """
        count = 0
        for y in range(grid.height):
            for x in range(grid.width):
                cell = grid.get(x, y)
                if cell.char == old_char:
                    cell.char = new_char
                    count += 1
        return count

    def replace_char_in_region(self, grid: Grid, x: int, y: int,
                                width: int, height: int,
                                old_char: str, new_char: str) -> int:
        """
        Replace all occurrences of a character within a region.
        Returns the number of cells changed.
        """
        count = 0
        for ry in range(y, min(y + height, grid.height)):
            for rx in range(x, min(x + width, grid.width)):
                cell = grid.get(rx, ry)
                if cell.char == old_char:
                    cell.char = new_char
                    count += 1
        return count

    def apply_char_to_grid(self, grid: Grid, char: str) -> int:
        """
        Apply the current character to all empty cells in a grid.
        Returns the number of cells changed.
        """
        count = 0
        for y in range(grid.height):
            for x in range(grid.width):
                cell = grid.get(x, y)
                if not cell.char or cell.char == ' ':
                    cell.char = char
                    count += 1
        return count

    # ── Palette Management ───────────────────────────────────

    def export_palette(self) -> Dict[str, Any]:
        """Export the current palette configuration."""
        return self.palette.to_dict()

    def import_palette(self, data: Dict[str, Any]) -> bool:
        """Import a palette configuration."""
        try:
            self.palette = CharacterPalette.from_dict(data)
            return True
        except Exception:
            return False

    def reset_palette(self) -> None:
        """Reset the palette to defaults."""
        self.palette = CharacterPalette()
        self.state = CharEditState()

    # ── Preview ──────────────────────────────────────────────

    def get_preview_grid(self, slots_per_row: int = 16) -> List[List[Optional[SlotEntry]]]:
        """
        Get a preview grid of all slots for display.
        Returns a 2D array of slot entries.
        """
        all_slots = self.get_filtered_slots()
        grid: List[List[Optional[SlotEntry]]] = []
        row: List[Optional[SlotEntry]] = []

        for entry in all_slots:
            row.append(entry)
            if len(row) >= slots_per_row:
                grid.append(row)
                row = []
        if row:
            grid.append(row)

        return grid

    def to_dict(self) -> Dict[str, Any]:
        """Export editor state as a dictionary."""
        return {
            'selected_slot': self.state.selected_slot,
            'current_char': self.current_char,
            'search_query': self.state.search_query,
            'filter_category': self.state.filter_category.value if self.state.filter_category else None,
            'show_emoji': self.state.show_emoji,
            'show_hex': self.state.show_hex,
            'recent_slots': self.state.recent_slots,
            'favorites': self.state.favorites,
            'palette': self.palette.to_dict(),
        }
