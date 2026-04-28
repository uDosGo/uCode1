"""
ThinUI Grid Bridge

This module provides the bridge between the Python core's ParsedGrid/ComponentMapper
and the ThinUI frontend. It converts grid data into ThinUI-compatible formats
that can be rendered in the web interface.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json

from .formats import (
    ThinUILayout, ThinUIComponent, ThinUIComponentType, 
    ThinUIColor, ThinUIFormat
)
from ..usxd.grid_parser import ParsedGrid, ASCIIGridParser
from ..usxd.component_mapper import ComponentMapper, ComponentMapping, ComponentType
from ..usxd.grid_renderer import GridRenderer, Style, ColorMode


@dataclass
class ThinUIGridData:
    """
    Grid data structure optimized for ThinUI rendering.
    
    This is the primary data structure passed from Python core to ThinUI frontend.
    """
    
    # Grid dimensions
    rows: int
    cols: int
    
    # Grid cells in a 2D array format for easy access
    cells: List[List[Dict[str, Any]]] = field(default_factory=list)
    
    # Components identified in the grid
    components: List[Dict[str, Any]] = field(default_factory=list)
    
    # Grid metadata
    title: str = "Untitled"
    format: str = "simple"  # simple, box, teletext, markdown, csv
    
    # ThinUI layout tree
    layout: Optional[Dict[str, Any]] = None
    
    # Component mappings
    mappings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Rendering styles
    styles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            'rows': self.rows,
            'cols': self.cols,
            'cells': self.cells,
            'components': self.components,
            'title': self.title,
            'format': self.format,
        }
        if self.layout:
            result['layout'] = self.layout
        if self.mappings:
            result['mappings'] = self.mappings
        if self.styles:
            result['styles'] = self.styles
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)


class ThinUIGridBridge:
    """
    Bridge class that converts between core grid data and ThinUI format.
    
    This class provides methods to:
    - Convert ParsedGrid to ThinUI-compatible format
    - Convert ComponentMapper output to ThinUI components
    - Generate ThinUI layouts from grid data
    - Handle color conversions between ANSI and CSS
    """
    
    def __init__(self):
        self.parser = ASCIIGridParser()
        self.mapper = ComponentMapper()
        self.renderer = GridRenderer()
    
    def parse_to_thinui(
        self, 
        grid_text: str, 
        title: str = "Untitled",
        parse_format: Optional[str] = None
    ) -> ThinUIGridData:
        """
        Parse ASCII grid text and convert to ThinUI format.
        
        Args:
            grid_text: The ASCII grid text to parse
            title: Title for the grid
            parse_format: Optional format hint (simple, box, teletext, markdown, csv)
        
        Returns:
            ThinUIGridData ready for ThinUI rendering
        """
        # Parse the grid
        parsed = self.parser.parse_grid(grid_text, title)
        
        # Convert to ThinUI format
        return self.parsed_grid_to_thinui(parsed)
    
    def parsed_grid_to_thinui(self, parsed: ParsedGrid) -> ThinUIGridData:
        """
        Convert a ParsedGrid to ThinUI format.
        
        Args:
            parsed: The ParsedGrid object from the parser
        
        Returns:
            ThinUIGridData ready for ThinUI rendering
        """
        # Create 2D cell array
        cells_2d = []
        for row in range(parsed.rows):
            row_cells = []
            for col in range(parsed.cols):
                cell = parsed.get_cell(row, col)
                cell_dict = {
                    'char': cell.char,
                    'row': row,
                    'col': col,
                }
                
                # Add colors if present
                if cell.fg_color:
                    cell_dict['fgColor'] = cell.fg_color
                if cell.bg_color:
                    cell_dict['bgColor'] = cell.bg_color
                
                # Add component ID if present
                if cell.component_id:
                    cell_dict['componentId'] = cell.component_id
                
                # Add metadata
                if cell.metadata:
                    cell_dict['metadata'] = cell.metadata
                
                row_cells.append(cell_dict)
            cells_2d.append(row_cells)
        
        # Convert components
        components = []
        for component in parsed.components:
            components.append({
                'id': component.id,
                'name': component.name,
                'type': component.component_type,
                'cells': [(c.row, c.col) for c in component.cells],
                'properties': component.properties,
            })
        
        # Create ThinUI layout
        layout = ThinUILayout.from_parsed_grid(parsed, parsed.title)
        
        return ThinUIGridData(
            rows=parsed.rows,
            cols=parsed.cols,
            cells=cells_2d,
            components=components,
            title=parsed.title or "Untitled",
            format=parsed.format.value if parsed.format else "simple",
            layout=layout.to_dict(),
        )
    
    def map_to_thinui(
        self, 
        parsed: ParsedGrid,
        custom_mappings: Optional[List[ComponentMapping]] = None
    ) -> ThinUIGridData:
        """
        Map a parsed grid to ThinUI components with custom mappings.
        
        Args:
            parsed: The ParsedGrid to map
            custom_mappings: Optional custom component mappings
        
        Returns:
            ThinUIGridData with component mappings applied
        """
        # Apply custom mappings if provided
        if custom_mappings:
            for mapping in custom_mappings:
                self.mapper.add_mapping(
                    grid_component_id=mapping.grid_component_id,
                    thinui_type=mapping.thinui_type,
                    properties=mapping.properties
                )
        
        # Map components
        thinui_tree = self.mapper.map_grid(parsed)
        
        # Convert to ThinUI format
        grid_data = self.parsed_grid_to_thinui(parsed)
        
        # Add mappings to the result
        mappings = []
        for mapping in self.mapper.mappings:
            mappings.append({
                'gridComponentId': mapping.grid_component_id,
                'thinuiType': mapping.thinui_type.value if hasattr(mapping.thinui_type, 'value') else str(mapping.thinui_type),
                'properties': mapping.properties.to_dict() if hasattr(mapping.properties, 'to_dict') else mapping.properties
            })
        
        grid_data.mappings = mappings
        grid_data.layout['mappedComponents'] = thinui_tree.to_dict() if hasattr(thinui_tree, 'to_dict') else str(thinui_tree)
        
        return grid_data
    
    def create_thinui_component_tree(
        self,
        parsed: ParsedGrid,
        include_box_drawing: bool = True
    ) -> ThinUIComponent:
        """
        Create a ThinUI component tree from a parsed grid.
        
        Args:
            parsed: The ParsedGrid to convert
            include_box_drawing: Whether to include box drawing character detection
        
        Returns:
            ThinUIComponent representing the grid as a component tree
        """
        root = ThinUIComponent(
            id="grid-root",
            component_type=ThinUIComponentType.CONTAINER,
            width=parsed.cols,
            height=parsed.rows,
            metadata={'type': 'grid', 'format': parsed.format.value}
        )
        
        # Group cells by components if available
        if parsed.components:
            # Add each component as a group
            for component in parsed.components:
                group = ThinUIComponent(
                    id=component.id,
                    component_type=ComponentTypeToThinUI(component.component_type),
                    x=min(c.col for c in component.cells),
                    y=min(c.row for c in component.cells),
                    width=max(c.col for c in component.cells) - min(c.col for c in component.cells) + 1,
                    height=max(c.row for c in component.cells) - min(c.row for c in component.cells) + 1,
                    metadata={'componentId': component.id, **component.properties}
                )
                
                # Add cells to this component
                for cell_ref in component.cells:
                    cell = parsed.get_cell(cell_ref.row, cell_ref.col)
                    cell_comp = ThinUIComponent(
                        id=f"{component.id}-cell-{cell_ref.row}-{cell_ref.col}",
                        component_type=ThinUIComponentType.CELL,
                        x=cell_ref.col,
                        y=cell_ref.row,
                        text=cell.char,
                        fg_color=ThinUIColor.from_hex(cell.fg_color) if cell.fg_color else None,
                        bg_color=ThinUIColor.from_hex(cell.bg_color) if cell.bg_color else None,
                        metadata=cell.metadata
                    )
                    group.children.append(cell_comp)
                
                root.children.append(group)
        else:
            # Add all cells directly to root
            for row in range(parsed.rows):
                for col in range(parsed.cols):
                    cell = parsed.get_cell(row, col)
                    
                    # Detect box drawing characters for special handling
                    if include_box_drawing and cell.char in self._BOX_DRAWING_CHARS:
                        component_type = self._get_box_drawing_type(cell.char)
                    else:
                        component_type = ThinUIComponentType.CELL
                    
                    cell_comp = ThinUIComponent(
                        id=f"cell-{row}-{col}",
                        component_type=component_type,
                        x=col,
                        y=row,
                        text=cell.char,
                        fg_color=ThinUIColor.from_hex(cell.fg_color) if cell.fg_color else None,
                        bg_color=ThinUIColor.from_hex(cell.bg_color) if cell.bg_color else None,
                        metadata={**cell.metadata, 'originalChar': cell.char}
                    )
                    root.children.append(cell_comp)
        
        return root
    
    def _get_box_drawing_type(self, char: str) -> ThinUIComponentType:
        """Get the appropriate ThinUI component type for a box drawing character"""
        # Corner pieces
        if char in '┌┐└┘':
            return ThinUIComponentType.BOX
        # Line pieces
        elif char in '─━│┃':
            return ThinUIComponentType.LINE
        # T-junctions
        elif char in '├┤┬┴┼':
            return ThinUIComponentType.LINE
        return ThinUIComponentType.CELL
    
    # Box drawing characters
    _BOX_DRAWING_CHARS = {
        '┌', '┐', '└', '┘',  # Corners
        '─', '━', '│', '┃',  # Lines
        '├', '┤', '┬', '┴', '┼',  # Junctions
        '┖', '┗', '┕', '┙', '┚', '┛', '┝', '┞', '┟', '┠',  # Double lines
        '┡', '┢', '┣', '┦', '┧', '┩', '┪', '┫', '┭', '┮', '┯',
        '┱', '┲', '┵', '┶', '┷', '┸', '┹', '┺', '┻', '┽', '┾', '┿',
        '╀', '╁', '╂', '╃', '╄', '╅', '╆', '╇', '╈', '╉', '╊', '╋',
        'anggap', '╍', '╎', '╏', '═', '║', '╒', '╓', '╔', '╕', '╖', '╗',
        '╘', '╙', '╚', '╛', '╝', '╞', '╟', '╠', '╡', '╢', '╣', '╤',
        '╥', '╦', '╧', '╨', '╩', '╪', '╫', '╬',
        '╭', '╮', '╯', '╰', '╱', '╲', '╳', '╴', '╵', '╶', '╷', '╸', '╹', '╺', '╻'
    }


def ComponentTypeToThinUI(comp_type: ComponentType) -> ThinUIComponentType:
    """Convert ComponentType to ThinUIComponentType"""
    type_mapping = {
        ComponentType.CONTAINER: ThinUIComponentType.CONTAINER,
        ComponentType.BUTTON: ThinUIComponentType.BUTTON,
        ComponentType.TEXT: ThinUIComponentType.TEXT,
        ComponentType.INPUT: ThinUIComponentType.INPUT,
        ComponentType.LABEL: ThinUIComponentType.LABEL,
        ComponentType.WIDGET: ThinUIComponentType.GROUP,
        ComponentType.BOX: ThinUIComponentType.BOX,
        ComponentType.LINE: ThinUIComponentType.LINE,
        ComponentType.IMAGE: ThinUIComponentType.IMAGE,
    }
    return type_mapping.get(comp_type, ThinUIComponentType.GROUP)
