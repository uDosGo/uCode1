"""
Static HTML Export Engine for uCode1

Generates standalone HTML files from snacks, binders, relics,
and Liquid templates. Supports multiple output formats:

- Full site: Complete HTML page with theme, navigation, and widgets
- Single page: Minimal standalone HTML for a single component
- Widget: Embeddable HTML snippet

Part of the v1.3.0 milestone.
"""

from .engine import ExportEngine, ExportFormat, ExportOptions
from .site import SiteExporter, SiteConfig
from .page import PageExporter, PageConfig

__version__ = "1.0.0"
__all__ = [
    "ExportEngine",
    "ExportFormat",
    "ExportOptions",
    "SiteExporter",
    "SiteConfig",
    "PageExporter",
    "PageConfig",
]
