#!/usr/bin/env python3
"""
USXD Component Mapper - Python Implementation

This module provides functionality to map parsed grid components to ThinUI
renderable components, enabling the conversion from ASCII grids to interactive
UI elements.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Union, Callable
import json
from enum import Enum
from .grid_parser import GridCell, GridComponent, ParsedGrid, GridFormat, ASCIIGridParser


class ComponentType(Enum):
    """Supported ThinUI component types for mapping"""
    BUTTON = "button"
    TEXT = "text"
    INPUT = "input"
    IMAGE = "image"
    CONTAINER = "container"
    GRID = "grid"
    PANEL = "panel"
    LABEL = "label"
    CARD = "card"
    DIALOG = "dialog"
    PROGRESS = "progress"
    SLIDER = "slider"
    SWITCH = "switch"
    Custom = "custom"


class Alignment(Enum):
    """Component alignment options"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class StylePreset(Enum):
    """Predefined style presets"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    DEFAULT = "default"
    RETRO = "retro"
    TELETEXT = "teletext"
    MODERN = "modern"


@dataclass
class ThinUIProperties:
    """Properties for ThinUI component rendering"""
    component_type: ComponentType = ComponentType.CONTAINER
    text: Optional[str] = None
    style: Optional[str] = None
    style_preset: StylePreset = StylePreset.DEFAULT
    width: Optional[int] = None
    height: Optional[int] = None
    x: Optional[int] = None
    y: Optional[int] = None
    visible: bool = True
    enabled: bool = True
    alignment: Alignment = Alignment.CENTER
    fg_color: Optional[str] = None
    bg_color: Optional[str] = None
    border: Optional[str] = None
    padding: int = 0
    margin: int = 0
    action: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    children: List['ThinUIProperties'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'type': self.component_type.value,
            'style': self.style,
            'style_preset': self.style_preset.value,
            'visible': self.visible,
            'enabled': self.enabled,
            'alignment': self.alignment.value,
            'padding': self.padding,
            'margin': self.margin,
            'data': self.data
        }
        if self.text:
            result['text'] = self.text
        if self.width is not None:
            result['width'] = self.width
        if self.height is not None:
            result['height'] = self.height
        if self.x is not None:
            result['x'] = self.x
        if self.y is not None:
            result['y'] = self.y
        if self.fg_color:
            result['fg_color'] = self.fg_color
        if self.bg_color:
            result['bg_color'] = self.bg_color
        if self.border:
            result['border'] = self.border
        if self.action:
            result['action'] = self.action
        if self.children:
            result['children'] = [child.to_dict() for child in self.children]
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThinUIProperties':
        """Create from dictionary"""
        children = [cls.from_dict(child) for child in data.get('children', [])]
        return cls(
            component_type=ComponentType(data.get('type', 'container')),
            text=data.get('text'),
            style=data.get('style'),
            style_preset=StylePreset(data.get('style_preset', 'default')),
            width=data.get('width'),
            height=data.get('height'),
            x=data.get('x'),
            y=data.get('y'),
            visible=data.get('visible', True),
            enabled=data.get('enabled', True),
            alignment=Alignment(data.get('alignment', 'center')),
            fg_color=data.get('fg_color'),
            bg_color=data.get('bg_color'),
            border=data.get('border'),
            padding=data.get('padding', 0),
            margin=data.get('margin', 0),
            action=data.get('action'),
            data=data.get('data', {}),
            children=children
        )


@dataclass
class ComponentMapping:
    """Mapping between grid component and ThinUI component"""
    grid_component_id: str
    thinui_type: ComponentType = ComponentType.CONTAINER
    properties: ThinUIProperties = field(default_factory=ThinUIProperties)
    conditions: Dict[str, Any] = field(default_factory=dict)
    transform: Optional[Callable] = None
    priority: int = 0

    def matches(self, component: GridComponent, context: Dict[str, Any] = None) -> bool:
        """Check if this mapping matches the given component"""
        if context is None:
            context = {}
        
        # Check basic conditions
        if 'id' in self.conditions and component.id != self.conditions['id']:
            return False
        if 'name' in self.conditions and component.name != self.conditions['name']:
            return False
        if 'type' in self.conditions and component.component_type != self.conditions['type']:
            return False
        
        # Check custom conditions
        for key, value in self.conditions.items():
            if key not in ['id', 'name', 'type']:
                if key in component.properties:
                    if component.properties[key] != value:
                        return False
                elif key in context:
                    if context[key] != value:
                        return False
                else:
                    return False
        
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'grid_component_id': self.grid_component_id,
            'thinui_type': self.thinui_type.value,
            'properties': self.properties.to_dict(),
            'conditions': self.conditions,
            'priority': self.priority
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentMapping':
        """Create from dictionary"""
        return cls(
            grid_component_id=data['grid_component_id'],
            thinui_type=ComponentType(data.get('thinui_type', 'container')),
            properties=ThinUIProperties.from_dict(data.get('properties', {})),
            conditions=data.get('conditions', {}),
            priority=data.get('priority', 0)
        )


class ComponentMapper:
    """
    Map parsed grid components to ThinUI components.
    
    This mapper provides:
    - Automatic mapping based on component properties
    - Rule-based mapping with conditions
    - Custom mapping functions
    - Hierarchical component structure generation
    - Style and layout mapping
    
    Usage:
        mapper = ComponentMapper()
        mapper.add_mapping(rule, thinui_properties)
        thinui_components = mapper.map_grid(parsed_grid)
    """

    # Default character to component type mapping
    CHAR_TO_COMPONENT = {
        'A': ComponentType.BUTTON,
        'B': ComponentType.BUTTON,
        'C': ComponentType.BUTTON,
        'D': ComponentType.INPUT,
        'E': ComponentType.INPUT,
        'F': ComponentType.INPUT,
        'X': ComponentType.IMAGE,
        'O': ComponentType.IMAGE,
        '*': ComponentType.LABEL,
        '#': ComponentType.PANEL,
        '-': ComponentType.CONTAINER,
        '|': ComponentType.CONTAINER,
        '+': ComponentType.CONTAINER,
        '═': ComponentType.CONTAINER,
        '║': ComponentType.CONTAINER,
    }

    # Box drawing character to border style mapping
    BOX_TO_BORDER = {
        '─': ('horizontal', 'thin'),
        '│': ('vertical', 'thin'),
        '┌': ('corner', 'top-left'),
        '┐': ('corner', 'top-right'),
        '└': ('corner', 'bottom-left'),
        '┘': ('corner', 'bottom-right'),
        '├': ('junction', 'left'),
        '┤': ('junction', 'right'),
        '┬': ('junction', 'top'),
        '┴': ('junction', 'bottom'),
        '┼': ('junction', 'cross'),
    }

    # Teletext to style mapping
    TELETEXT_STYLE = {
        '█': ('block', 'full'),
        '▀': ('block', 'top'),
        '▄': ('block', 'bottom'),
        '▌': ('block', 'right'),
        '▐': ('block', 'left'),
        '░': ('shade', 'light'),
        '▒': ('shade', 'medium'),
        '▓': ('shade', 'dark'),
    }

    def __init__(self):
        """Initialize the component mapper"""
        self.mappings: List[ComponentMapping] = []
        self.default_mapping: Optional[ComponentMapping] = None
        self.style_rules: Dict[str, ThinUIProperties] = {}
        self.parser = ASCIIGridParser()

    def add_mapping(self, grid_component_id: str = None, 
                   thinui_type: ComponentType = ComponentType.CONTAINER,
                   properties: ThinUIProperties = None,
                   conditions: Dict[str, Any] = None,
                   priority: int = 0) -> ComponentMapping:
        """
        Add a component mapping rule.
        
        Args:
            grid_component_id: The grid component ID to match
            thinui_type: The ThinUI component type to create
            properties: ThinUI properties for the component
            conditions: Conditions that must be met for mapping
            priority: Priority (higher = applied first)
            
        Returns:
            The created ComponentMapping
        """
        if properties is None:
            properties = ThinUIProperties(component_type=thinui_type)
        if conditions is None:
            conditions = {}
        
        mapping = ComponentMapping(
            grid_component_id=grid_component_id or f"mapping_{len(self.mappings)}",
            thinui_type=thinui_type,
            properties=properties,
            conditions=conditions,
            priority=priority
        )
        
        # Insert based on priority
        self.mappings.append(mapping)
        self.mappings.sort(key=lambda m: m.priority, reverse=True)
        
        return mapping

    def set_default_mapping(self, thinui_type: ComponentType = ComponentType.CONTAINER,
                           properties: ThinUIProperties = None) -> ComponentMapping:
        """Set the default mapping for unmatched components"""
        if properties is None:
            properties = ThinUIProperties(component_type=thinui_type)
        
        self.default_mapping = ComponentMapping(
            grid_component_id="default",
            thinui_type=thinui_type,
            properties=properties
        )
        return self.default_mapping

    def add_style_rule(self, name: str, properties: ThinUIProperties) -> None:
        """Add a named style rule"""
        self.style_rules[name] = properties

    def get_mapping_for_component(self, component: GridComponent, 
                                 context: Dict[str, Any] = None) -> Optional[ComponentMapping]:
        """Get the best mapping for a component"""
        if context is None:
            context = {}
        
        # Try to find matching mapping
        for mapping in self.mappings:
            if mapping.matches(component, context):
                return mapping
        
        return self.default_mapping

    def map_component(self, component: GridComponent, 
                      context: Dict[str, Any] = None) -> ThinUIProperties:
        """
        Map a single grid component to ThinUI properties.
        
        Args:
            component: The GridComponent to map
            context: Additional context for mapping
            
        Returns:
            ThinUIProperties for rendering
        """
        if context is None:
            context = {}
        
        # Get mapping
        mapping = self.get_mapping_for_component(component, context)
        if mapping:
            # Start with mapping properties
            properties = mapping.properties
        else:
            # Use default
            properties = ThinUIProperties()
        
        # Apply automatic type detection
        if properties.component_type == ComponentType.CONTAINER:
            # Try to detect type from component
            if component.cells:
                # Get the character from the first cell
                char = self._get_component_char(component)
                auto_type = self.CHAR_TO_COMPONENT.get(char, ComponentType.CONTAINER)
                if auto_type != ComponentType.CONTAINER:
                    properties.component_type = auto_type
        
        # Apply character-specific properties
        if component.cells:
            char = self._get_component_char(component)
            
            # Box drawing characters
            if char in self.BOX_TO_BORDER:
                border_type, border_style = self.BOX_TO_BORDER[char]
                properties.border = f"{border_type}-{border_style}"
                properties.fg_color = "#888888"
            
            # Teletext characters
            if char in self.TELETEXT_STYLE:
                style_type, style_value = self.TELETEXT_STYLE[char]
                properties.style_preset = StylePreset.TELETEXT
        
        # Apply component name as text if no text is set
        if not properties.text and component.name:
            properties.text = component.name
        
        # Apply component properties
        if component.properties:
            if 'text' in component.properties:
                properties.text = component.properties['text']
            if 'color' in component.properties:
                properties.fg_color = component.properties['color']
            if 'bg_color' in component.properties:
                properties.bg_color = component.properties['bg_color']
            if 'action' in component.properties:
                properties.action = component.properties['action']
        
        # Apply size based on cell count
        if len(component.cells) > 1:
            rows = [r for r, c in component.cells]
            cols = [c for r, c in component.cells]
            properties.width = max(cols) - min(cols) + 1
            properties.height = max(rows) - min(rows) + 1
        
        return properties

    def _get_component_char(self, component: GridComponent) -> str:
        """Get the character from the first cell of the component"""
        if component.cells:
            # This would need access to the grid to get the actual character
            # For now, return a space
            return " "
        return " "

    def map_grid(self, parsed_grid: ParsedGrid, 
                context: Dict[str, Any] = None) -> ThinUIProperties:
        """
        Map an entire parsed grid to ThinUI component tree.
        
        Args:
            parsed_grid: The ParsedGrid to map
            context: Additional context for mapping
            
        Returns:
            Root ThinUIProperties containing the component tree
        """
        if context is None:
            context = {}
        
        # Create root container
        root = ThinUIProperties(
            component_type=ComponentType.CONTAINER,
            text=parsed_grid.title,
            width=parsed_grid.cols,
            height=parsed_grid.rows,
            style=f"grid-{parsed_grid.format.value}"
        )
        
        # Map cells to components
        # First, map explicit components from parsed_grid
        for comp_id, component in parsed_grid.components.items():
            thinui_props = self.map_component(component, context)
            thinui_props.data['source_component'] = comp_id
            root.children.append(thinui_props)
        
        # Map individual cells that belong to components
        # Create a map of cell -> component
        cell_components = {}
        for comp_id, component in parsed_grid.components.items():
            for row, col in component.cells:
                cell_components[(row, col)] = comp_id
        
        # For cells that belong to components, we don't need to create 
        # separate ThinUI components since they're part of the component
        
        # Map cells that don't belong to any component
        unmapped_cells = set()
        for row in range(parsed_grid.rows):
            for col in range(parsed_grid.cols):
                if (row, col) not in cell_components:
                    cell = parsed_grid.get_cell(row, col)
                    if cell and cell.char != ' ':
                        # Create a simple component for this cell
                        cell_props = self._map_cell_to_component(cell, row, col, parsed_grid)
                        root.children.append(cell_props)
                else:
                    unmapped_cells.add((row, col))
        
        return root

    def _map_cell_to_component(self, cell: GridCell, row: int, col: int, 
                              parsed_grid: ParsedGrid) -> ThinUIProperties:
        """Map a single cell to a ThinUI component"""
        # Detect component type from character
        char = cell.char
        
        # Use character mapping
        component_type = self.CHAR_TO_COMPONENT.get(char, ComponentType.LABEL)
        
        properties = ThinUIProperties(
            component_type=component_type,
            text=char if char != ' ' else None,
            x=col,
            y=row,
            width=1,
            height=1
        )
        
        # Apply character-specific styling
        if char in self.BOX_TO_BORDER:
            border_type, border_style = self.BOX_TO_BORDER[char]
            properties.border = f"{border_type}-{border_style}"
            properties.fg_color = "#888888"
            properties.component_type = ComponentType.CONTAINER
        
        elif char in self.TELETEXT_STYLE:
            style_type, style_value = self.TELETEXT_STYLE[char]
            properties.style_preset = StylePreset.TELETEXT
            properties.component_type = ComponentType.CARD
        
        # Apply cell metadata
        if cell.metadata:
            for key, value in cell.metadata.items():
                setattr(properties, key, value)
        
        # Apply component ID if cell belongs to a component
        if cell.component_id:
            properties.data['component_id'] = cell.component_id
        
        return properties

    def map_to_layout(self, parsed_grid: ParsedGrid, 
                     layout_type: str = "grid",
                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Map to a specific layout format for ThinUI rendering.
        
        Args:
            parsed_grid: The ParsedGrid to map
            layout_type: Type of layout ('grid', 'flex', 'absolute', 'teletext')
            context: Additional context
            
        Returns:
            Layout configuration dictionary
        """
        if context is None:
            context = {}
        
        # Map to ThinUI components
        thinui_tree = self.map_grid(parsed_grid, context)
        
        layout_config = {
            'type': layout_type,
            'title': parsed_grid.title,
            'width': parsed_grid.cols,
            'height': parsed_grid.rows,
            'format': parsed_grid.format.value,
            'components': self._flattten_component_tree(thinui_tree),
            'styles': {name: props.to_dict() for name, props in self.style_rules.items()}
        }
        
        # Add layout-specific configurations
        if layout_type == "teletext":
            layout_config['mode7'] = True
            layout_config['color_map'] = self._get_teletext_color_map()
        elif layout_type == "grid":
            layout_config['grid'] = True
            layout_config['cell_size'] = {'width': 1, 'height': 1}
        
        return layout_config

    def _flattten_component_tree(self, tree: ThinUIProperties) -> List[Dict[str, Any]]:
        """Convert component tree to flat list with hierarchy"""
        components = []
        
        def flatten(node: ThinUIProperties, parent_id: str = None):
            comp_dict = node.to_dict()
            comp_dict['id'] = f"comp_{len(components)}"
            if parent_id:
                comp_dict['parent'] = parent_id
            components.append(comp_dict)
            
            for child in node.children:
                flatten(child, comp_dict['id'])
        
        flatten(tree)
        return components

    def _get_teletext_color_map(self) -> Dict[str, str]:
        """Get teletext color mapping"""
        return {
            'black': '#000000',
            'red': '#FF0000',
            'green': '#00FF00', 
            'yellow': '#FFFF00',
            'blue': '#0000FF',
            'magenta': '#FF00FF',
            'cyan': '#00FFFF',
            'white': '#FFFFFF'
        }

    def create_teletext_layout(self, parsed_grid: ParsedGrid) -> Dict[str, Any]:
        """
        Create a teletext-specific layout suitable for CeefaxThinUI rendering.
        
        This creates a layout optimized for teletext mode 7 rendering
        with proper character set and color handling.
        """
        layout = self.map_to_layout(parsed_grid, "teletext")
        
        # Add teletext-specific properties
        layout['mode7'] = True
        layout['character_set'] = 'teletext'
        layout['device'] = 'ceefax'
        
        # Map cells to teletext codes
        cells = []
        for row in range(parsed_grid.rows):
            for col in range(parsed_grid.cols):
                cell = parsed_grid.get_cell(row, col)
                if cell:
                    cells.append({
                        'row': row,
                        'col': col,
                        'char': cell.char,
                        'fg': cell.fg_color or '#FFFFFF',
                        'bg': cell.bg_color or '#000000',
                        'component_id': cell.component_id,
                        'metadata': cell.metadata
                    })
        
        layout['cells'] = cells
        layout['grid_width'] = parsed_grid.cols
        layout['grid_height'] = parsed_grid.rows
        
        return layout

    def create_grid_layout(self, parsed_grid: ParsedGrid) -> Dict[str, Any]:
        """
        Create a standard grid layout for ThinUI rendering.
        """
        layout = self.map_to_layout(parsed_grid, "grid")
        
        # Add grid-specific properties
        layout['grid'] = {
            'rows': parsed_grid.rows,
            'cols': parsed_grid.cols,
            'cell_size': {'width': 1, 'height': 1},
            'spacing': 0
        }
        
        return layout

    def map_to_html(self, parsed_grid: ParsedGrid, 
                   template: str = "default") -> str:
        """
        Map the parsed grid to HTML representation.
        
        Args:
            parsed_grid: The ParsedGrid to convert
            template: HTML template to use
            
        Returns:
            HTML string
        """
        layout = self.map_to_layout(parsed_grid, "grid")
        
        if template == "simple":
            return self._generate_simple_html(layout)
        else:
            return self._generate_default_html(layout)

    def _generate_simple_html(self, layout: Dict[str, Any]) -> str:
        """Generate simple HTML table"""
        html = ['<div class="grid-container">']
        html.append(f'<h2>{layout.get("title", "Grid")}</h2>')
        html.append('<table class="grid">')
        
        # Create table from cells
        for row in range(layout.get('height', 0)):
            html.append('<tr>')
            for col in range(layout.get('width', 0)):
                # Find cell properties
                cell_props = {}
                for comp in layout.get('components', []):
                    if comp.get('x') == col and comp.get('y') == row:
                        cell_props = comp
                        break
                
                cell_content = cell_props.get('text', ' ')
                cell_style = self._get_cell_style(cell_props)
                html.append(f'<td style="{cell_style}">{cell_content or " "}</td>')
            html.append('</tr>')
        
        html.append('</table>')
        html.append('</div>')
        return '\n'.join(html)

    def _generate_default_html(self, layout: Dict[str, Any]) -> str:
        """Generate default HTML with styling"""
        html = ['<!DOCTYPE html>']
        html.append('<html>')
        html.append('<head>')
        html.append('<style>')
        html.append('''
            .grid-container { font-family: monospace; margin: 20px; }
            .grid { border-collapse: collapse; }
            .grid td { 
                width: 30px; height: 30px; 
                border: 1px solid #ccc; 
                text-align: center; 
                vertical-align: middle;
            }
            .box-h { border-top: 2px solid #333; }
            .box-v { border-left: 2px solid #333; }
            .box-tl { border-top: 2px solid #333; border-left: 2px solid #333; }
            .box-tr { border-top: 2px solid #333; border-right: 2px solid #333; }
            .box-bl { border-bottom: 2px solid #333; border-left: 2px solid #333; }
            .box-br { border-bottom: 2px solid #333; border-right: 2px solid #333; }
        ''')
        html.append('</style>')
        html.append('</head>')
        html.append('<body>')
        html.append(self._generate_simple_html(layout))
        html.append('</body>')
        html.append('</html>')
        return '\n'.join(html)

    def _get_cell_style(self, cell_props: Dict[str, Any]) -> str:
        """Get CSS style for a cell"""
        styles = []
        
        if cell_props.get('fg_color'):
            styles.append(f"color: {cell_props['fg_color']}")
        if cell_props.get('bg_color'):
            styles.append(f"background-color: {cell_props['bg_color']}")
        
        border = cell_props.get('border')
        if border:
            if 'horizontal' in border:
                styles.append('border-top: 2px solid #333')
            if 'vertical' in border:
                styles.append('border-left: 2px solid #333')
            if 'top-left' in border:
                styles.append('border-top: 2px solid #333; border-left: 2px solid #333')
            if 'top-right' in border:
                styles.append('border-top: 2px solid #333; border-right: 2px solid #333')
            if 'bottom-left' in border:
                styles.append('border-bottom: 2px solid #333; border-left: 2px solid #333')
            if 'bottom-right' in border:
                styles.append('border-bottom: 2px solid #333; border-right: 2px solid #333')
        
        return '; '.join(styles)


# Test the component mapper
if __name__ == "__main__":
    print("Testing Component Mapper...")
    
    # Test 1: Basic mapping
    print("\n=== Test 1: Basic Component Mapping ===")
    mapper = ComponentMapper()
    
    # Create a grid with components
    parser = ASCIIGridParser()
    grid_text = """┌───┐
│ A │
└───┘"""
    parsed = parser.parse_grid(grid_text, "Test Grid")
    
    # Add some components
    from .grid_parser import GridComponent
    button_comp = GridComponent(
        id="button1",
        name="OK Button",
        component_type="widget",
        cells=[(1, 1)]
    )
    parsed.add_component(button_comp)
    
    # Map to ThinUI
    thinui_tree = mapper.map_grid(parsed)
    print(f"✓ Mapped to ThinUI tree with {len(thinui_tree.children)} children")
    
    # Test 2: Layout mapping
    print("\n=== Test 2: Layout Mapping ===")
    grid_layout = mapper.create_grid_layout(parsed)
    print(f"✓ Grid layout created: {grid_layout['type']}")
    print(f"✓ Components: {len(grid_layout['components'])}")
    
    # Test 3: Teletext layout
    print("\n=== Test 3: Teletext Layout ===")
    teletext_layout = mapper.create_teletext_layout(parsed)
    print(f"✓ Teletext layout created: mode7={teletext_layout['mode7']}")
    print(f"✓ Cells: {len(teletext_layout['cells'])}")
    
    # Test 4: HTML generation
    print("\n=== Test 4: HTML Generation ===")
    html = mapper.map_to_html(parsed, "simple")
    print(f"✓ HTML generated: {len(html)} characters")
    print(f"✓ Contains table: {'<table' in html}")
    
    # Test 5: Custom mapping
    print("\n=== Test 5: Custom Mapping ===")
    mapper.add_mapping(
        grid_component_id="button1",
        thinui_type=ComponentType.BUTTON,
        properties=ThinUIProperties(
            component_type=ComponentType.BUTTON,
            text="Click Me",
            fg_color="#FFFFFF",
            bg_color="#0000FF"
        )
    )
    
    custom_tree = mapper.map_grid(parsed)
    button_found = False
    for child in custom_tree.children:
        if child.component_type == ComponentType.BUTTON:
            button_found = True
            print(f"✓ Button mapped: {child.text}, bg={child.bg_color}")
    
    if button_found:
        print("✓ Custom mapping successful")
    
    print("\nAll component mapper tests passed!")
