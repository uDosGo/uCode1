"""Ceefax SKIN Themes — visual colour schemes for teletext pages."""

from typing import Dict, Optional


class TeletextTheme:
    """A teletext colour theme."""

    def __init__(
        self,
        name: str,
        foreground: str,
        background: str,
        accent: str,
        header: str,
        font: str = "Teletext50, monospace",
    ):
        self.name = name
        self.foreground = foreground
        self.background = background
        self.accent = accent
        self.header = header
        self.font = font

    def to_css(self) -> str:
        """Generate CSS for this theme."""
        return """
        body {
            background: %(bg)s;
            color: %(fg)s;
            font-family: %(font)s;
        }
        h1, h2, h3 { color: %(header)s; }
        a { color: %(accent)s; }
        .page { max-width: 800px; margin: 2em auto; }
        pre { font-family: %(font)s; margin: 0; }
        """ % {
            "bg": self.background,
            "fg": self.foreground,
            "font": self.font,
            "header": self.header,
            "accent": self.accent,
        }


# Built-in themes
THEMES: Dict[str, TeletextTheme] = {
    "green": TeletextTheme(
        name="Classic Green",
        foreground="#00ff00",
        background="#000000",
        accent="#00ffff",
        header="#ffff00",
    ),
    "amber": TeletextTheme(
        name="Amber",
        foreground="#ffb000",
        background="#000000",
        accent="#ffffff",
        header="#ffff00",
    ),
    "white": TeletextTheme(
        name="White",
        foreground="#ffffff",
        background="#000000",
        accent="#00ffff",
        header="#ffff00",
    ),
    "condensed": TeletextTheme(
        name="Condensed Green",
        foreground="#00ff00",
        background="#000000",
        accent="#00ffff",
        header="#ffff00",
        font="Teletext50 Condensed, monospace",
    ),
}


def get_theme(name: str) -> TeletextTheme:
    """Get a theme by name, falling back to green."""
    return THEMES.get(name, THEMES["green"])
