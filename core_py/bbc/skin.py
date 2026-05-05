"""
SKIN — Visual Reskinning Engine for uCode1

SKIN transforms the raw output into a visual style without changing game logic.
Skins are applied live and can be changed at any time.

BBC BASIC extensions:

    PROC_SKIN_Apply("skin_name")       — Change active skin
    PROC_SKIN_MapChar(code, "glyph")   — Map ASCII code to teletext glyph
    PROC_SKIN_SetPalette(index, rgb)   — Set colour palette entry

Built-in skins:
    - teletext_classic: Green on black (original Ceefax)
    - paper_retro:      Parchment background, serif font
    - dark_mode:        High contrast, dark background
    - high_vis:         Yellow on black for accessibility
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import json


@dataclass
class SkinDefinition:
    """Definition of a visual skin"""
    name: str
    description: str
    background_color: str
    foreground_color: str
    font_name: str
    font_size: int
    border_style: str
    glyph_set: str
    palette: Dict[int, str]  # index -> hex color
    char_mappings: Dict[int, str]  # ASCII code -> glyph
    teletext_mode: int = 7  # Default Mode 7 for teletext


# Built-in skin definitions
BUILTIN_SKINS: Dict[str, SkinDefinition] = {
    "teletext_classic": SkinDefinition(
        name="teletext_classic",
        description="Green on black — original Ceefax teletext",
        background_color="#000000",
        foreground_color="#00FF00",
        font_name="CeefaxThinUI",
        font_size=14,
        border_style="none",
        glyph_set="teletext",
        palette={
            0: "#000000",   # Black
            1: "#FF0000",   # Red
            2: "#00FF00",   # Green
            3: "#FFFF00",   # Yellow
            4: "#0000FF",   # Blue
            5: "#FF00FF",   # Magenta
            6: "#00FFFF",   # Cyan
            7: "#FFFFFF",   # White
        },
        char_mappings={},
    ),
    "paper_retro": SkinDefinition(
        name="paper_retro",
        description="Parchment background, serif font — vintage feel",
        background_color="#F5E6C8",
        foreground_color="#4A3728",
        font_name="serif",
        font_size=16,
        border_style="double",
        glyph_set="unicode",
        palette={
            0: "#4A3728",   # Dark brown
            1: "#8B0000",   # Dark red
            2: "#2E7D32",   # Forest green
            3: "#F9A825",   # Gold
            4: "#1565C0",   # Deep blue
            5: "#6A1B9A",   # Purple
            6: "#00838F",   # Teal
            7: "#3E2723",   # Very dark brown
        },
        char_mappings={},
    ),
    "dark_mode": SkinDefinition(
        name="dark_mode",
        description="High contrast, dark background — easy on the eyes",
        background_color="#1E1E1E",
        foreground_color="#E0E0E0",
        font_name="monospace",
        font_size=14,
        border_style="solid",
        glyph_set="teletext",
        palette={
            0: "#1E1E1E",   # Dark grey
            1: "#EF5350",   # Red
            2: "#66BB6A",   # Green
            3: "#FFEE58",   # Yellow
            4: "#42A5F5",   # Blue
            5: "#AB47BC",   # Purple
            6: "#26C6DA",   # Cyan
            7: "#E0E0E0",   # Light grey
        },
        char_mappings={},
    ),
    "high_vis": SkinDefinition(
        name="high_vis",
        description="Yellow on black — maximum readability",
        background_color="#000000",
        foreground_color="#FFFF00",
        font_name="monospace",
        font_size=18,
        border_style="none",
        glyph_set="teletext",
        palette={
            0: "#000000",   # Black
            1: "#FF4444",   # Bright red
            2: "#44FF44",   # Bright green
            3: "#FFFF00",   # Yellow
            4: "#4488FF",   # Bright blue
            5: "#FF44FF",   # Bright magenta
            6: "#44FFFF",   # Bright cyan
            7: "#FFFFFF",   # White
        },
        char_mappings={},
    ),
}


class SkinEngine:
    """
    SKIN visual transformation engine.

    Manages active skin, character mappings, and palette overrides.
    Provides callbacks for when the skin changes so renderers can update.
    """

    def __init__(self, interpreter=None):
        """Initialize SKIN engine with default skin

        Args:
            interpreter: Optional BBCBasicInterpreter to attach to
        """
        self._skins: Dict[str, SkinDefinition] = dict(BUILTIN_SKINS)
        self._active_skin_name: str = "teletext_classic"
        self._active_skin: SkinDefinition = self._skins["teletext_classic"]
        self._char_mappings: Dict[int, str] = {}
        self._palette_overrides: Dict[int, str] = {}
        self._on_change_callbacks: List[Callable[[str, SkinDefinition], None]] = []

        # Auto-attach if interpreter provided
        if interpreter is not None:
            self.attach_to_interpreter(interpreter)

    # ── Properties ────────────────────────────────────────────────

    @property
    def active_skin_name(self) -> str:
        """Get the name of the active skin"""
        return self._active_skin_name

    @property
    def active_skin(self) -> SkinDefinition:
        """Get the active skin definition"""
        return self._active_skin

    @property
    def available_skins(self) -> List[str]:
        """List all available skin names"""
        return list(self._skins.keys())

    # ── Skin Management ───────────────────────────────────────────

    def register_skin(self, skin: SkinDefinition) -> None:
        """Register a custom skin definition"""
        self._skins[skin.name] = skin

    def apply(self, name: str) -> bool:
        """
        Change the active skin.

        This is the implementation of PROC_SKIN_Apply.

        Args:
            name: Name of the skin to apply

        Returns:
            True if skin was applied, False if not found
        """
        if name not in self._skins:
            return False

        self._active_skin_name = name
        self._active_skin = self._skins[name]

        # Reset per-skin mappings and palette
        self._char_mappings = dict(self._active_skin.char_mappings)
        self._palette_overrides = {}

        # Notify callbacks
        for cb in self._on_change_callbacks:
            try:
                cb(name, self._active_skin)
            except Exception:
                pass

        return True

    def get_skin(self, name: str) -> Optional[SkinDefinition]:
        """Get a skin definition by name"""
        return self._skins.get(name)

    # ── Character Mapping ─────────────────────────────────────────

    def map_char(self, code: int, glyph: str) -> None:
        """
        Map an ASCII code to a teletext glyph.

        This is the implementation of PROC_SKIN_MapChar.

        Args:
            code: ASCII code (e.g., 65 for 'A')
            glyph: Glyph to display (e.g., "🗡️" for sword)
        """
        self._char_mappings[code] = glyph

    def get_glyph(self, code: int) -> str:
        """
        Get the glyph for a character code, applying any mapping.

        Args:
            code: ASCII code

        Returns:
            Mapped glyph or the original character
        """
        if code in self._char_mappings:
            return self._char_mappings[code]
        if code < 32 or code > 126:
            return " "
        return chr(code)

    def clear_mappings(self) -> None:
        """Clear all character mappings"""
        self._char_mappings.clear()

    def get_mappings_json(self) -> str:
        """Get all character mappings as JSON"""
        return json.dumps(
            {str(k): v for k, v in self._char_mappings.items()},
            indent=2
        )

    # ── Palette ───────────────────────────────────────────────────

    def set_palette(self, index: int, rgb: str) -> None:
        """
        Set a colour palette entry.

        This is the implementation of PROC_SKIN_SetPalette.

        Args:
            index: Palette index (0-15)
            rgb: Hex colour string (e.g., "#FF0000" for red)
        """
        self._palette_overrides[index] = rgb

    def get_color(self, index: int) -> str:
        """
        Get the colour for a palette index, applying any overrides.

        Args:
            index: Palette index

        Returns:
            Hex colour string
        """
        if index in self._palette_overrides:
            return self._palette_overrides[index]
        return self._active_skin.palette.get(index, "#FFFFFF")

    def reset_palette(self) -> None:
        """Reset palette to skin defaults"""
        self._palette_overrides.clear()

    def get_palette_json(self) -> str:
        """Get current palette as JSON"""
        palette = {}
        for i in range(16):
            palette[i] = self.get_color(i)
        return json.dumps(palette, indent=2)

    # ── Callbacks ─────────────────────────────────────────────────

    def add_change_callback(self, callback: Callable[[str, SkinDefinition], None]) -> None:
        """Register a callback for when the skin changes"""
        self._on_change_callbacks.append(callback)

    def remove_change_callback(self, callback: Callable[[str, SkinDefinition], None]) -> None:
        """Remove a skin change callback"""
        if callback in self._on_change_callbacks:
            self._on_change_callbacks.remove(callback)

    # ── Output Transformation ─────────────────────────────────────

    def transform_text(self, text: str) -> str:
        """
        Transform text through the active skin's character mappings.

        Args:
            text: Input text

        Returns:
            Transformed text with glyphs applied
        """
        result = []
        for char in text:
            code = ord(char)
            if code in self._char_mappings:
                result.append(self._char_mappings[code])
            else:
                result.append(char)
        return "".join(result)

    def get_style_attributes(self) -> Dict[str, Any]:
        """
        Get CSS-style attributes for the active skin.

        Returns:
            Dict with 'background', 'color', 'font-family', 'font-size', 'border'
        """
        return {
            "background": self._active_skin.background_color,
            "color": self._active_skin.foreground_color,
            "font-family": self._active_skin.font_name,
            "font-size": f"{self._active_skin.font_size}px",
            "border": self._active_skin.border_style,
        }

    # ── Integration ───────────────────────────────────────────────

    def attach_to_interpreter(self, interpreter) -> None:
        """
        Attach this SKIN engine to a BBC BASIC interpreter.

        This wires up the PROC_SKIN_* handlers.

        Args:
            interpreter: BBCBasicInterpreter instance
        """
        interpreter._skin_engine = self

        # Add SKIN keywords to interpreter's keyword list
        skin_keywords = [
            "PROC_SKIN_Apply",
            "PROC_SKIN_MapChar",
            "PROC_SKIN_SetPalette",
        ]
        for kw in skin_keywords:
            if kw not in interpreter._keywords:
                interpreter._keywords.append(kw)


# Convenience functions

def create_skin_engine() -> SkinEngine:
    """Create and return a new SKIN engine"""
    return SkinEngine()
