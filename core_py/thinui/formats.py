"""
ThinUI Format Definitions

This module defines the data formats used for communication between
the Python core (uCode1) and the ThinUI frontend (TypeScript/React).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import json


class ThinUIComponentType(Enum):
    """ThinUI component types"""
    CONTAINER = "container"
    GRID = "grid"
    CELL = "cell"
    TEXT = "text"
    BUTTON = "button"
    INPUT = "input"
    LABEL = "label"
    BOX = "box"
    LINE = "line"
    IMAGE = "image"
    GROUP = "group"
    LAYER = "layer"


@dataclass
class ThinUIColor:
    """Color representation for ThinUI"""
    
    # Color can be specified in multiple formats
    hex: Optional[str] = None      # e.g., "#FF0000" 
    rgb: Optional[str] = None      # e.g., "rgb(255,0,0)" or "rgb(100%,0%,0%)"
    hsl: Optional[str] = None      # e.g., "hsl(0,100%,50%)"
    ansi: Optional[int] = None     # ANSI color code (0-255)
    name: Optional[str] = None     # CSS color name e.g., "red"
    
    def to_css(self) -> str:
        """Convert to CSS color string"""
        if self.hex:
            return self.hex
        if self.rgb:
            return self.rgb
        if self.hsl:
            return self.hsl
        if self.ansi is not None:
            return ansi_to_css(self.ansi)
        if self.name:
            return self.name
        return "#000000"  # Default to black
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {}
        if self.hex:
            result['hex'] = self.hex
        if self.rgb:
            result['rgb'] = self.rgb
        if self.hsl:
            result['hsl'] = self.hsl
        if self.ansi is not None:
            result['ansi'] = self.ansi
        if self.name:
            result['name'] = self.name
        return result
    
    @classmethod
    def from_ansi_code(cls, code: int) -> 'ThinUIColor':
        """Create ThinUIColor from ANSI color code"""
        return cls(ansi=code)
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'ThinUIColor':
        """Create ThinUIColor from hex string"""
        return cls(hex=hex_color)


def ansi_to_css(ansi_code: int) -> str:
    """Convert ANSI color code to CSS color string"""
    # Standard colors (0-15)
    standard_colors = {
        0: "#000000", 1: "#800000", 2: "#008000", 3: "#808000",
        4: "#000080", 5: "#800080", 6: "#008080", 7: "#C0C0C0",
        8: "#808080", 9: "#FF0000", 10: "#00FF00", 11: "#FFFF00",
        12: "#0000FF", 13: "#FF00FF", 14: "#00FFFF", 15: "#FFFFFF",
    }
    
    # 256-color mode
    if 0 <= ansi_code <= 15:
        return standard_colors.get(ansi_code, "#000000")
    elif 16 <= ansi_code <= 231:
        # 6x6x6 color cube
        r = (ansi_code - 16) // 36
        g = ((ansi_code - 16) % 36) // 6
        b = (ansi_code - 16) % 6
        r_val = int((r / 5) * 255)
        g_val = int((g / 5) * 255)
        b_val = int((b / 5) * 255)
        return f"#{r_val:02x}{g_val:02x}{b_val:02x}"
    elif 232 <= ansi_code <= 255:
        # Grayscale
        val = int(((ansi_code - 232) / 23) * 255)
        gray = val
        return f"#{gray:02x}{gray:02x}{gray:02x}"
    
    return "#000000"


@dataclass
class ThinUIComponent:
    """Represents a ThinUI component"""
    
    id: str
    component_type: ThinUIComponentType
    text: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fg_color: Optional[ThinUIColor] = None
    bg_color: Optional[ThinUIColor] = None
    border_color: Optional[ThinUIColor] = None
    border_style: Optional[str] = None  # solid, dashed, dotted, double, none
    border_width: Optional[int] = None
    children: List['ThinUIComponent'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    action: Optional[str] = None  # e.g., "click", "submit"
    action_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            'id': self.id,
            'type': self.component_type.value,
        }
        if self.text:
            result['text'] = self.text
        if self.x is not None:
            result['x'] = self.x
        if self.y is not None:
            result['y'] = self.y
        if self.width is not None:
            result['width'] = self.width
        if self.height is not None:
            result['height'] = self.height
        if self.fg_color:
            result['fgColor'] = self.fg_color.to_dict()
        if self.bg_color:
            result['bgColor'] = self.bg_color.to_dict()
        if self.border_color:
            result['borderColor'] = self.border_color.to_dict()
        if self.border_style:
            result['borderStyle'] = self.border_style
        if self.border_width is not None:
            result['borderWidth'] = self.border_width
        if self.children:
            result['children'] = [c.to_dict() for c in self.children]
        if self.metadata:
            result['metadata'] = self.metadata
        if self.action:
            result['action'] = self.action
        if self.action_data:
            result['actionData'] = self.action_data
        return result


@dataclass
class ThinUIFormat:
    """Base format for ThinUI data structures"""
    
    version: str = "1.0.0"
    type: str = "thinui"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'version': self.version,
            'type': self.type,
        }


@dataclass
class ThinUILayout:
    """Complete ThinUI layout with grid and components"""
    
    format: ThinUIFormat = field(default_factory=ThinUIFormat)
    title: str = "Untitled"
    root: ThinUIComponent = field(default_factory=lambda: ThinUIComponent(
        id="root", component_type=ThinUIComponentType.CONTAINER
    ))
    grid: Optional[Dict[str, Any]] = None  # Grid metadata
    styles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'format': self.format.to_dict(),
            'title': self.title,
            'root': self.root.to_dict(),
        }
        if self.grid:
            result['grid'] = self.grid
        if self.styles:
            result['styles'] = self.styles
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_parsed_grid(cls, parsed_grid: 'ParsedGrid', title: Optional[str] = None) -> 'ThinUILayout':
        """Create ThinUILayout from a ParsedGrid object"""
        from ..usxd.grid_parser import ParsedGrid
        
        if title is None:
            title = parsed_grid.title or "Untitled Grid"
        
        # Create root container
        root = ThinUIComponent(
            id="grid-container",
            component_type=ThinUIComponentType.CONTAINER,
            width=parsed_grid.cols,
            height=parsed_grid.rows,
            metadata={'originalFormat': parsed_grid.format.value}
        )
        
        # Add each cell as a component
        for row in range(parsed_grid.rows):
            for col in range(parsed_grid.cols):
                cell = parsed_grid.get_cell(row, col)
                if cell.char != ' ' or cell.fg_color or cell.bg_color:
                    component = ThinUIComponent(
                        id=f"cell-{row}-{col}",
                        component_type=ThinUIComponentType.CELL,
                        x=col,
                        y=row,
                        text=cell.char if cell.char != ' ' else None,
                        fg_color=ThinUIColor.from_hex(cell.fg_color) if cell.fg_color else None,
                        bg_color=ThinUIColor.from_hex(cell.bg_color) if cell.bg_color else None,
                        metadata=cell.metadata
                    )
                    root.children.append(component)
        
        # Store grid metadata
        grid_metadata = {
            'rows': parsed_grid.rows,
            'cols': parsed_grid.cols,
            'format': parsed_grid.format.value,
            'title': parsed_grid.title
        }
        
        return cls(
            format=ThinUIFormat(version="1.0.0", type="grid-layout"),
            title=title,
            root=root,
            grid=grid_metadata
        )
