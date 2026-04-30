#!/usr/bin/env python3
"""
USXD System - Python Implementation

This module provides the core functionality for managing USXD documents,
which are portable structured exchange formats in the uDos ecosystem.
"""

# Import cell mapping
from .cell_mapping import (
    add_cell_references_to_doc,
    archive_document_sections,
    cell_to_section,
    link_doc_to_cell_address,
    restore_sections_from_cells,
    section_to_cell,
    section_to_cell_address,
)

# Import component mapper
from .component_mapper import (
    Alignment,
    ComponentMapper,
    ComponentMapping,
    ComponentType,
    StylePreset,
    ThinUIProperties,
)

# Import grid parser components
from .grid_parser import (
    ASCIIGridParser,
    GridCell,
    GridComponent,
    GridFormat,
    ParsedGrid,
)

# Import grid renderer
from .grid_renderer import (
    ColorMode,
    GridRenderer,
    Key,
    KeyboardInput,
    RenderConfig,
    Style,
    TerminalUI,
)
from .models import USXDDocument, USXDFormat, USXDMetadata, USXDRegistry, USXDSection

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