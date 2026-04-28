"""
Text Formatting Module

Provides text wrapping, justification, and formatting utilities.
"""

from enum import Enum
from typing import List, Optional, Callable
import textwrap


class WrapMode(Enum):
    """Text wrapping modes."""
    NO_WRAP = "no_wrap"
    SOFT = "soft"  # Wrap at spaces
    HARD = "hard"  # Break anywhere
    PRESERVE = "preserve"  # Preserve line breaks


class Alignment(Enum):
    """Text alignment modes."""
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    JUSTIFY = "justify"


def wrap_text(text: str, width: int = 80, mode: WrapMode = WrapMode.SOFT) -> str:
    """Wrap text to specified width.
    
    Args:
        text: Text to wrap
        width: Maximum line width
        mode: Wrapping mode
    
    Returns:
        Wrapped text
    """
    if mode == WrapMode.NO_WRAP:
        return text
    elif mode == WrapMode.SOFT:
        return "\n".join(textwrap.wrap(text, width, break_long_words=False))
    elif mode == WrapMode.HARD:
        return "\n".join(textwrap.wrap(text, width, break_long_words=True))
    else:  # PRESERVE
        lines = text.split("\n")
        wrapped_lines = [textwrap.fill(line, width, break_long_words=False) for line in lines]
        return "\n".join(wrapped_lines)


def justify_text(text: str, width: int = 80) -> str:
    """Justify text to specified width.
    
    Args:
        text: Text to justify
        width: Target width
    
    Returns:
        Justified text
    """
    return textwrap.fill(text, width)


def center_text(text: str, width: int = 80, fillchar: str = " ") -> str:
    """Center text in specified width.
    
    Args:
        text: Text to center
        width: Target width
        fillchar: Fill character
    
    Returns:
        Centered text
    """
    if width <= len(text):
        return text
    padding = width - len(text)
    return fillchar * (padding // 2) + text + fillchar * ((padding + 1) // 2)


def pad_text(text: str, width: int = 80, fillchar: str = " ",
              align: Alignment = Alignment.LEFT) -> str:
    """Pad text to specified width with alignment.
    
    Args:
        text: Text to pad
        width: Target width
        fillchar: Fill character
        align: Text alignment
    
    Returns:
        Padded text
    """
    if width <= len(text):
        return text
    
    padding = width - len(text)
    
    if align == Alignment.LEFT:
        return text + fillchar * padding
    elif align == Alignment.RIGHT:
        return fillchar * padding + text
    elif align == Alignment.CENTER:
        return center_text(text, width, fillchar)
    else:  # JUSTIFY - not meaningful for single line
        return text + fillchar * padding


def truncate_text(text: str, length: int, ellipsis: str = "...") -> str:
    """Truncate text to specified length.
    
    Args:
        text: Text to truncate
        length: Maximum length
        ellipsis: Suffix for truncated text
    
    Returns:
        Truncated text
    """
    if len(text) <= length:
        return text
    if length <= len(ellipsis):
        return ellipsis[:length]
    return text[:length - len(ellipsis)] + ellipsis


def indent_text(text: str, indent: int = 4, first_line: bool = True,
                 subsequent: Optional[int] = None) -> str:
    """Indent text lines.
    
    Args:
        text: Text to indent
        indent: Number of spaces to indent
        first_line: Whether to indent first line
        subsequent: Override indent for lines after first (None uses indent)
    
    Returns:
        Indented text
    """
    if not text:
        return text
    
    lines = text.split("\n")
    if not lines:
        return text
    
    result = []
    indent_str = " " * indent
    subsequent_indent = " " * (subsequent if subsequent is not None else indent)
    
    for i, line in enumerate(lines):
        if i == 0 and not first_line:
            result.append(line)
        else:
            result.append(indent_str if i == 0 else subsequent_indent + line)
    
    return "\n".join(result)


class TextFormatter:
    """Comprehensive text formatter."""
    
    def __init__(self, width: int = 80):
        """Initialize formatter."""
        self.width = width
    
    def format_block(self, text: str, align: Alignment = Alignment.LEFT,
                     indent: int = 0, prefix: str = "", suffix: str = "") -> str:
        """Format a text block with alignment and decoration.
        
        Args:
            text: Text content
            align: Text alignment
            indent: Indentation level
            prefix: Prefix for each line
            suffix: Suffix for each line
        
        Returns:
            Formatted text block
        """
        lines = text.split("\n")
        formatted = []
        
        for line in lines:
            if line.strip():  # Non-empty line
                padded = pad_text(line, self.width, align=align)
                full_line = " " * indent + prefix + padded + suffix
                formatted.append(full_line)
            else:
                formatted.append("")
        
        return "\n".join(formatted)
    
    def create_box(self, content: str, char: str = "-", padding: int = 1) -> str:
        """Create a box around content.
        
        Args:
            content: Content to box
            char: Character to use for box border
            padding: Padding inside box
        
        Returns:
            Boxed text
        """
        lines = content.split("\n")
        max_len = max(len(line) for line in lines) + padding * 2
        
        border = char * max_len
        padded_lines = []
        
        for line in lines:
            padded = line.center(max_len - 2)
            padded_lines.append(f"{char} {padded} {char}")
        
        result = [border] + padded_lines + [border]
        return "\n".join(result)
