# uCode1 Text Processing Tools
#
# Pure Python text and markdown injection/formatting utilities.
# No Rust dependencies.

"""
Text Processing Module

Provides:
- Text template injection (variable substitution)
- Markdown formatting utilities
- HTML generation from markdown
- Text wrapping and formatting
- ANSI color/styling for terminals
- Content injection into templates
"""

from .injection import (
    TextInjector,
    TemplateEngine,
    inject_variables,
    inject_file,
    format_template,
)
from .markdown import (
    MarkdownFormatter,
    MarkdownRenderer,
    format_markdown,
    render_markdown,
    html_to_markdown,
    markdown_to_html,
    strip_markdown,
)
from .formatting import (
    TextFormatter,
    WrapMode,
    Alignment,
    justify_text,
    wrap_text,
    center_text,
    pad_text,
    truncate_text,
    indent_text,
)
from .ansistyle import (
    ANSIColor,
    ANSIStyle,
    colorize,
    style_text,
    strip_ansi,
    has_ansi,
)
from .exceptions import (
    TextProcessingError,
    InjectionError,
    MarkdownError,
    FormattingError,
)

__all__ = [
    # Injection
    'TextInjector',
    'TemplateEngine',
    'inject_variables',
    'inject_file',
    'format_template',
    # Markdown
    'MarkdownFormatter',
    'MarkdownRenderer',
    'format_markdown',
    'render_markdown',
    'html_to_markdown',
    'markdown_to_html',
    'strip_markdown',
    # Formatting
    'TextFormatter',
    'WrapMode',
    'Alignment',
    'justify_text',
    'wrap_text',
    'center_text',
    'pad_text',
    'truncate_text',
    'indent_text',
    # ANSI Style
    'ANSIColor',
    'ANSIStyle',
    'colorize',
    'style_text',
    'strip_ansi',
    'has_ansi',
    # Exceptions
    'TextProcessingError',
    'InjectionError',
    'MarkdownError',
    'FormattingError',
]

__version__ = "0.1.0"
