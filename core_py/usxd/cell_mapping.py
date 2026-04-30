#!/usr/bin/env python3
"""
Cell Mapping — bridges USXD documents with Cell storage addresses.

Allows USXD document sections to reference and map to Cell addresses
in the UDX format, enabling document sections to be stored, archived,
or linked as atomic storage units.

Workflow:
  USXD doc → section → Cell (archive/store)
  Cell → USXD section (reference/restore)
  USXD doc metadata → Cell addresses (document-level cell linkage)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from .models import USXDDocument, USXDSection, USXDMetadata

from ..cell import (
    Cell,
    CellAddress,
    CellStore,
    layer_name,
    LAYER_GRID,
    LAYER_SPATIAL,
    LAYER_SNACK,
    LAYER_FEED,
    LAYER_META,
    LAYER_CHAR,
    LAYER_BINDER,
    LAYER_USXD,
    LAYER_CUBE,
    LAYER_USER,
)

CELL_SECTION_TYPE = "cell"
CELL_REF_SECTION_TYPE = "cell-reference"
SECTION_CELL_TYPE_MAP = {
    "grid": LAYER_GRID,
    "content": LAYER_USXD,
    "data": LAYER_USXD,
    "metadata": LAYER_META,
    "reference": LAYER_BINDER,
    "snack": LAYER_SNACK,
    "feed": LAYER_FEED,
    "char": LAYER_CHAR,
    "cell": LAYER_USXD,
}


def section_to_cell(section: USXDSection, doc_id: str, store: CellStore) -> Cell:
    """Convert a USXD section into a Cell and write it to the store.

    Derives the Cell address from the section ID and metadata.
    The section's content becomes the Cell's data payload.

    Args:
        section: The USXD section to convert.
        doc_id: The parent document ID used for addressing.
        store: CellStore to write to.

    Returns:
        The created Cell.
    """
    layer = SECTION_CELL_TYPE_MAP.get(section.section_type, LAYER_USXD)
    slot = hash(section.id) % 128
    addr = CellAddress(
        band=100,
        col=hash(doc_id) % 26,
        row=hash(section.name) % 26,
        sub=hash(section.id) % 100,
        layer=layer,
        slot=slot,
        version=0,
    )

    data = {
        "doc_id": doc_id,
        "section_id": section.id,
        "section_name": section.name,
        "section_type": section.section_type,
        "content": section.content,
        "format": section.format,
    }
    if section.metadata:
        data["metadata"] = section.metadata

    cell = Cell(address=addr, data=data)
    store.write(cell)
    return cell


def section_to_cell_address(
    section: USXDSection, doc_id: str, band: int = 100,
) -> CellAddress:
    """Generate a deterministic CellAddress from a USXD section without writing.

    Useful for creating references without actually storing data.

    Args:
        section: The USXD section.
        doc_id: The parent document ID.
        band: Layer band to use.

    Returns:
        A deterministic CellAddress.
    """
    layer = SECTION_CELL_TYPE_MAP.get(section.section_type, LAYER_USXD)
    slot = hash(section.id) % 128
    return CellAddress(
        band=band,
        col=hash(doc_id) % 26,
        row=hash(section.name) % 26,
        sub=hash(section.id) % 100,
        layer=layer,
        slot=slot,
        version=0,
    )


def cell_to_section(cell: Cell) -> USXDSection:
    """Convert a Cell back into a USXD section.

    Args:
        cell: The Cell to convert.

    Returns:
        A reconstructed USXDSection.
    """
    data = cell.data
    return USXDSection(
        id=data.get("section_id", str(cell.address)),
        name=data.get("section_name", data.get("section_type", "restored")),
        section_type=data.get("section_type", "data"),
        content=data.get("content"),
        format=data.get("format"),
        metadata={
            **(data.get("metadata", {})),
            "cell_address": str(cell.address),
            "cell_checksum": cell.checksum,
            "archived_at": cell.created,
        },
    )


def archive_document_sections(
    doc: USXDDocument, store: CellStore, band: int = 100,
) -> Dict[str, str]:
    """Archive all sections of a USXD document as Cells.

    Args:
        doc: The USXD document.
        store: CellStore to write to.
        band: Layer band to use.

    Returns:
        Dict mapping section_id → cell_address strings.
    """
    mapping = {}
    for section in doc.sections:
        cell = section_to_cell(section, doc.metadata.id, store)
        mapping[section.id] = str(cell.address)
    return mapping


def add_cell_references_to_doc(
    doc: USXDDocument, cell_addresses: Dict[str, str],
) -> None:
    """Add cell-reference sections to a USXD document linking to stored Cells.

    Args:
        doc: The USXD document to modify.
        cell_addresses: Dict mapping section_id → cell_address strings.
    """
    ref_data = []
    for section_id, addr_str in cell_addresses.items():
        ref_data.append({"section_id": section_id, "cell_address": addr_str})

    if ref_data:
        ref_section = USXDSection(
            id=f"{doc.metadata.id}-cells",
            name="Cell References",
            section_type=CELL_REF_SECTION_TYPE,
            content=ref_data,
            format="application/json",
            metadata={"count": len(ref_data), "band": "100"},
        )
        doc.add_section(ref_section)


def restore_sections_from_cells(
    cell_refs: List[Dict[str, str]], store: CellStore,
) -> List[USXDSection]:
    """Restore USXD sections from cell references.

    Args:
        cell_refs: List of {"section_id": ..., "cell_address": ...} dicts.
        store: CellStore to read from.

    Returns:
        List of restored USXDSection objects.
    """
    sections = []
    for ref in cell_refs:
        cell = store.read(ref["cell_address"])
        if cell:
            section = cell_to_section(cell)
            sections.append(section)
    return sections


def link_doc_to_cell_address(
    doc: USXDDocument, store: CellStore, band: int = 100,
) -> str:
    """Store the document metadata itself as a Cell and return its address.

    The document-level cell is stored at a deterministic address based on
    the doc ID, so it can be looked up later.

    Args:
        doc: The USXD document.
        store: CellStore to write to.
        band: Layer band.

    Returns:
        The cell address string for the document metadata.
    """
    addr = CellAddress(
        band=band,
        col=hash(doc.metadata.id) % 26,
        row=len(doc.metadata.id) % 26,
        sub=hash(doc.metadata.title) % 100,
        layer=LAYER_USXD,
        slot=0,
        version=0,
    )
    cell = Cell(
        address=addr,
        data={
            "doc_id": doc.metadata.id,
            "title": doc.metadata.title,
            "version": doc.metadata.version,
            "description": doc.metadata.description,
            "author": doc.metadata.author,
            "tags": doc.metadata.tags,
            "section_count": len(doc.sections),
        },
    )
    store.write(cell)
    return str(addr)
