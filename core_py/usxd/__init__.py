#!/usr/bin/env python3
"""
USXD System - Python Implementation

This module provides the core functionality for managing USXD documents,
which are portable structured exchange formats in the uDos ecosystem.
"""

from .models import (
    USXDDocument, USXDMetadata, USXDSection, USXDRegistry, USXDFormat
)

# Import grid parser components
from .grid_parser import (
    ASCIIGridParser,
    ParsedGrid,
    GridCell,
    GridComponent,
    GridFormat,
)

# Import component mapper
from .component_mapper import (
    ComponentMapper,
    ComponentMapping,
    ComponentType,
    ThinUIProperties,
    Alignment,
    StylePreset,
)

# Import grid renderer
from .grid_renderer import (
    GridRenderer,
    Style,
    ColorMode,
    Key,
    KeyboardInput,
    RenderConfig,
    TerminalUI,
)

# Import cell mapping
from .cell_mapping import (
    section_to_cell,
    section_to_cell_address,
    cell_to_section,
    archive_document_sections,
    add_cell_references_to_doc,
    restore_sections_from_cells,
    link_doc_to_cell_address,
)

__all__ = [
    # USXD Models
    "USXDDocument",
    "USXDMetadata",
    "USXDSection",
    "USXDRegistry",
    "USXDFormat",
    # Grid Parser
    "ASCIIGridParser",
    "ParsedGrid",
    "GridCell",
    "GridComponent",
    "GridFormat",
    # Component Mapper
    "ComponentMapper",
    "ComponentMapping",
    "ComponentType",
    "ThinUIProperties",
    "Alignment",
    "StylePreset",
    # Grid Renderer
    "GridRenderer",
    "Style",
    "ColorMode",
    "Key",
    "KeyboardInput",
    "RenderConfig",
    "TerminalUI",
    # Cell Mapping
    "section_to_cell",
    "section_to_cell_address",
    "cell_to_section",
    "archive_document_sections",
    "add_cell_references_to_doc",
    "restore_sections_from_cells",
    "link_doc_to_cell_address",
]