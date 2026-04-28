"""Text Processing Exceptions"""

class TextProcessingError(Exception):
    """Base exception for text processing."""
    pass


class InjectionError(TextProcessingError):
    """Raised when text injection fails."""
    pass


class MarkdownError(TextProcessingError):
    """Raised when markdown processing fails."""
    pass


class FormattingError(TextProcessingError):
    """Raised when text formatting fails."""
    pass


class TemplateError(TextProcessingError):
    """Raised when template processing fails."""
    pass
