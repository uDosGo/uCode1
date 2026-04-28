"""
ANSI Style Module

Provides ANSI color and styling utilities for terminal output.
"""

import re
from enum import Enum
from typing import List, Optional, Tuple


class ANSIColor(Enum):
    """ANSI color codes."""
    # Standard colors
    BLACK = "30"
    RED = "31"
    GREEN = "32"
    YELLOW = "33"
    BLUE = "34"
    MAGENTA = "35"
    CYAN = "36"
    WHITE = "37"
    
    # Bright colors
    BRIGHT_BLACK = "90"
    BRIGHT_RED = "91"
    BRIGHT_GREEN = "92"
    BRIGHT_YELLOW = "93"
    BRIGHT_BLUE = "94"
    BRIGHT_MAGENTA = "95"
    BRIGHT_CYAN = "96"
    BRIGHT_WHITE = "97"
    
    # Foreground defaults
    DEFAULT = "39"
    
    # Background colors
    BG_BLACK = "40"
    BG_RED = "41"
    BG_GREEN = "42"
    BG_YELLOW = "43"
    BG_BLUE = "44"
    BG_MAGENTA = "45"
    BG_CYAN = "46"
    BG_WHITE = "47"
    
    BG_DEFAULT = "49"


class ANSIStyle(Enum):
    """ANSI style/attribute codes."""
    RESET = "0"
    BOLD = "1"
    DIM = "2"
    ITALIC = "3"
    UNDERLINE = "4"
    BLINK = "5"
    REVERSE = "7"
    HIDDEN = "8"
    STRIKETHROUGH = "9"


# ANSI escape code pattern
ANSI_PATTERN = re.compile(r'\033\[[0-9;]*m')


def colorize(text: str, color: ANSIColor, bg: Optional[ANSIColor] = None,
             styles: Optional[List[ANSIStyle]] = None) -> str:
    """Apply color and styles to text.
    
    Args:
        text: Text to colorize
        color: Foreground color
        bg: Optional background color
        styles: Optional list of styles
    
    Returns:
        ANSI-colored text
    """
    codes = []
    
    if styles:
        codes.extend(s.value for s in styles)
    
    codes.append(color.value)
    
    if bg:
        codes.append(bg.value)
    
    if codes:
        return f"\033[{';'.join(codes)}m{text}\033[0m"
    return text


def style_text(text: str, styles: List[ANSIStyle], 
                color: Optional[ANSIColor] = None,
                bg: Optional[ANSIColor] = None) -> str:
    """Apply multiple styles to text.
    
    Args:
        text: Text to style
        styles: List of style codes
        color: Optional foreground color
        bg: Optional background color
    
    Returns:
        ANSI-styled text
    """
    return colorize(text, color or ANSIColor.DEFAULT, bg, styles)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text.
    
    Args:
        text: Text potentially containing ANSI codes
    
    Returns:
        Clean text without ANSI codes
    """
    return ANSI_PATTERN.sub('', text)


def has_ansi(text: str) -> bool:
    """Check if text contains ANSI escape codes.
    
    Args:
        text: Text to check
    
    Returns:
        True if text contains ANSI codes
    """
    return bool(ANSI_PATTERN.search(text))


def color_name_to_ansi(name: str) -> Optional[ANSIColor]:
    """Convert color name to ANSIColor enum.
    
    Args:
        name: Color name string (case insensitive)
    
    Returns:
        ANSIColor or None if not found
    """
    name_lower = name.lower().replace(" ", "_").replace("bg_", "").replace("_bg", "")
    
    # Try direct match
    if name_lower.upper() in ANSIColor.__members__:
        return ANSIColor[name_lower.upper()]
    
    # Try without BG prefix
    for member_name, member in ANSIColor.__members__.items():
        if "BG_" in member_name:
            clean_name = member_name.replace("BG_", "").lower()
            if clean_name == name_lower:
                return member
        else:
            if member_name.lower() == name_lower:
                return member
    
    # Try with bg suffix
    bg_name = f"BG_{name_lower.upper()}"
    if bg_name in ANSIColor.__members__:
        return ANSIColor[bg_name]
    
    return None


def rgb_to_ansi(r: int, g: int, b: int, bg: bool = False) -> str:
    """Convert RGB to closest ANSI 256-color code.
    
    This is a simplified approximation.
    
    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
        bg: If True, generate background code
    
    Returns:
        ANSI color code string
    """
    # Simple mapping: use grayscale for now
    # A full implementation would map to 256-color palette
    if r == g == b:
        # Grayscale - use color cube index 232-255
        level = int((r / 255.0) * 23) + 232
        return f"38;5;{level}" if not bg else f"48;5;{level}"
    
    # RGB approximation to 6x6x6 color cube
    r6 = int((r * 5) / 255)
    g6 = int((g * 5) / 255)
    b6 = int((b * 5) / 255)
    color_index = 16 + 36 * r6 + 6 * g6 + b6
    
    if bg:
        return f"48;5;{color_index}"
    return f"38;5;{color_index}"


def hex_to_ansi(hex_color: str, bg: bool = False) -> str:
    """Convert hex color string to ANSI escape code.
    
    Args:
        hex_color: Hex color string (e.g., "#FF0000" or "FF0000")
        bg: If True, generate background code
    
    Returns:
        ANSI color code string
    """
    hex_color = hex_color.lstrip('#')
    
    if len(hex_color) == 3:
        # Expand 3-digit hex
        hex_color = ''.join([c * 2 for c in hex_color])
    
    if len(hex_color) != 6:
        return ANSIColor.DEFAULT.value if not bg else ANSIColor.BG_DEFAULT.value
    
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return rgb_to_ansi(r, g, b, bg)


class ANSIColors:
    """Convenience class for ANSI color codes."""
    
    @staticmethod
    def fg(color: ANSIColor) -> str:
        """Get foreground ANSI code."""
        return f"\033[{color.value}m"
    
    @staticmethod
    def bg(color: ANSIColor) -> str:
        """Get background ANSI code."""
        bg_color = getattr(ANSIColor, f"BG_{color.name}", None)
        if bg_color:
            return f"\033[{bg_color.value}m"
        return "\033[49m"  # Default background
    
    @staticmethod
    def style(style: ANSIStyle) -> str:
        """Get style ANSI code."""
        return f"\033[{style.value}m"
    
    @staticmethod
    def reset() -> str:
        """Get ANSI reset code."""
        return "\033[0m"
    
    @staticmethod
    def colored(text: str, fg: ANSIColor, bg: ANSIColor = None, 
                styles: List[ANSIStyle] = None) -> str:
        """Convenience method for colorize."""
        return colorize(text, fg, bg, styles)
