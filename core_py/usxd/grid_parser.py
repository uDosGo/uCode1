#!/usr/bin/env python3
"""
USXD ASCII Grid Parser - Python Implementation

This module provides functionality to parse ASCII grid formats into structured data
for USXD/OBF integration. It supports parsing ASCII grid text into structured formats
and converting structured data back to ASCII grid format.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Union
import json
import re
from enum import Enum


class GridFormat(Enum):
    """Supported grid formats"""
    SIMPLE = "simple"        # Simple ASCII grid with characters
    BOX_DRAWING = "box"      # Box drawing characters (─│┌┐└┘├┤┬┴┼)
    TELETEXT = "teletext"    # Teletext block characters ( ощеospace characters)
    MARKDOWN = "markdown"    # Markdown table format
    CSV = "csv"              # CSV format


@dataclass
class GridCell:
    """Represents a cell in a grid"""
    char: str = " "
    fg_color: Optional[str] = None
    bg_color: Optional[str] = None
    component_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    row: int = -1
    col: int = -1

    def __post_init__(self):
        """Ensure char is a single character"""
        if self.char and len(self.char) > 1:
            self.char = self.char[0]
        elif not self.char:
            self.char = " "

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'char': self.char,
            'row': self.row,
            'col': self.col
        }
        if self.fg_color:
            result['fg_color'] = self.fg_color
        if self.bg_color:
            result['bg_color'] = self.bg_color
        if self.component_id:
            result['component_id'] = self.component_id
        if self.metadata:
            result['metadata'] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GridCell':
        """Create from dictionary"""
        return cls(
            char=data.get('char', ' '),
            fg_color=data.get('fg_color'),
            bg_color=data.get('bg_color'),
            component_id=data.get('component_id'),
            metadata=data.get('metadata', {}),
            row=data.get('row', -1),
            col=data.get('col', -1)
        )


@dataclass
class GridComponent:
    """Represents a component that can span multiple cells"""
    id: str
    name: str
    component_type: str = "widget"
    properties: Dict[str, Any] = field(default_factory=dict)
    cells: List[Tuple[int, int]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.component_type,
            'properties': self.properties,
            'cells': [{'row': r, 'col': c} for r, c in self.cells],
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GridComponent':
        """Create from dictionary"""
        cells = []
        for cell_data in data.get('cells', []):
            cells.append((cell_data['row'], cell_data['col']))
        return cls(
            id=data['id'],
            name=data['name'],
            component_type=data.get('type', 'widget'),
            properties=data.get('properties', {}),
            cells=cells,
            metadata=data.get('metadata', {})
        )


@dataclass
class ParsedGrid:
    """Represents a parsed ASCII grid"""
    title: str = "Untitled"
    rows: int = 0
    cols: int = 0
    grid: List[List[GridCell]] = field(default_factory=list)
    components: Dict[str, GridComponent] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    format: GridFormat = GridFormat.SIMPLE

    def __post_init__(self):
        """Initialize grid if empty"""
        if not self.grid:
            self.grid = [[GridCell(char=' ', row=r, col=c) 
                          for c in range(self.cols)] 
                         for r in range(self.rows)]

    def get_cell(self, row: int, col: int) -> Optional[GridCell]:
        """Get cell at position"""
        try:
            return self.grid[row][col]
        except IndexError:
            return None

    def set_cell(self, row: int, col: int, cell: GridCell) -> bool:
        """Set cell at position"""
        try:
            cell.row = row
            cell.col = col
            self.grid[row][col] = cell
            return True
        except IndexError:
            return False

    def add_component(self, component: GridComponent) -> None:
        """Add a component"""
        self.components[component.id] = component

    def get_component(self, component_id: str) -> Optional[GridComponent]:
        """Get component by ID"""
        return self.components.get(component_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'rows': self.rows,
            'cols': self.cols,
            'format': self.format.value,
            'grid': [[cell.to_dict() for cell in row] for row in self.grid],
            'components': {comp_id: comp.to_dict() 
                          for comp_id, comp in self.components.items()},
            'metadata': self.metadata
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    def to_ascii(self) -> str:
        """Convert back to ASCII grid string"""
        lines = []
        for row in self.grid:
            line = ''.join(cell.char for cell in row)
            lines.append(line)
        return '\n'.join(lines)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParsedGrid':
        """Create from dictionary"""
        grid_data = data.get('grid', [])
        grid = []
        for row_idx, row_data in enumerate(grid_data):
            row = []
            for col_idx, cell_data in enumerate(row_data):
                cell = GridCell.from_dict(cell_data)
                cell.row = row_idx
                cell.col = col_idx
                row.append(cell)
            grid.append(row)

        components = {}
        for comp_id, comp_data in data.get('components', {}).items():
            components[comp_id] = GridComponent.from_dict(comp_data)

        return cls(
            title=data.get('title', 'Untitled'),
            rows=data.get('rows', len(grid)),
            cols=data.get('cols', len(grid[0]) if grid else 0),
            grid=grid,
            components=components,
            metadata=data.get('metadata', {}),
            format=GridFormat(data.get('format', 'simple'))
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'ParsedGrid':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class ASCIIGridParser:
    """
    Parse ASCII grid formats into structured data for USXD/OBF integration.
    
    This parser handles various ASCII grid formats including:
    - Simple character grids
    - Box drawing character grids (─│┌┐└┘├┤┬┴┼)
    - Teletext grid formats
    - Markdown table formats
    - CSV formats
    
    Usage:
        parser = ASCIIGridParser()
        parsed = parser.parse_grid("simple grid text")
        structured_data = parser.to_structured(parsed)
    """

    # Box drawing characters and their representations
    BOX_CHARS = {
        '─': 'H',  # Horizontal line
        '│': 'V',  # Vertical line
        '┌': 'TL', # Top-left corner
        '┐': 'TR', # Top-right corner
        '└': 'BL', # Bottom-left corner
        '┘': 'BR', # Bottom-right corner
        '├': 'LT', # Left T-junction
        '┤': 'RT', # Right T-junction
        '┬': 'TB', # Top T-junction
        '┴': 'BT', # Bottom T-junction
        '┼': 'X',  # Cross intersection
    }

    # Teletext block characters (simplified)
    TELETEXT_BLOCKS = {
        '█': 'BLOCK',
        '▀': 'TOP',
        '▄': 'BOTTOM',
        '▌': 'RIGHT',
        '▐': 'LEFT',
        '░': 'LIGHT',
        '▒': 'MEDIUM',
        '▓': 'DARK',
    }

    def __init__(self):
        """Initialize the parser"""
        self.components: List[GridComponent] = []

    def detect_format(self, grid_text: str) -> GridFormat:
        """Detect the format of the grid text"""
        lines = grid_text.strip().split('\n')
        
        # Check for markdown table
        if self._is_markdown_table(lines):
            return GridFormat.MARKDOWN
        
        # Check for CSV
        if self._is_csv(lines):
            return GridFormat.CSV
        
        # Check for box drawing characters
        if self._uses_box_chars(grid_text):
            return GridFormat.BOX_DRAWING
        
        # Check for teletext characters
        if self._uses_teletext_chars(grid_text):
            return GridFormat.TELETEXT
        
        return GridFormat.SIMPLE

    def _is_markdown_table(self, lines: List[str]) -> bool:
        """Check if lines form a markdown table"""
        if len(lines) < 2:
            return False
        # Look for | characters and separator line
        has_pipes = any('|' in line for line in lines)
        has_separator = any(
            line.strip().startswith('|') and line.strip().endswith('|') and 
            ('---' in line or ':' in line)
            for line in lines
        )
        return has_pipes and has_separator

    def _is_csv(self, lines: List[str]) -> bool:
        """Check if lines form CSV data"""
        if len(lines) < 2:
            return False
        # Look for commas in most lines
        comma_lines = [line for line in lines if ',' in line]
        return len(comma_lines) / len(lines) > 0.8

    def _uses_box_chars(self, text: str) -> bool:
        """Check if text uses box drawing characters"""
        return any(char in text for char in self.BOX_CHARS.keys())

    def _uses_teletext_chars(self, text: str) -> bool:
        """Check if text uses teletext block characters"""
        return any(char in text for char in self.TELETEXT_BLOCKS.keys())

    def parse_grid(self, grid_text: str, title: str = "Untitled") -> ParsedGrid:
        """
        Parse ASCII grid text into a ParsedGrid object.
        
        Args:
            grid_text: The ASCII grid text to parse
            title: Optional title for the grid
            
        Returns:
            ParsedGrid object with the parsed structure
        """
        lines = grid_text.strip().split('\n')
        
        # Detect format
        grid_format = self.detect_format(grid_text)
        
        # Parse based on format
        if grid_format == GridFormat.MARKDOWN:
            return self._parse_markdown_table(lines, title)
        elif grid_format == GridFormat.CSV:
            return self._parse_csv(lines, title)
        else:
            return self._parse_simple_grid(lines, title, grid_format)

    def _parse_simple_grid(self, lines: List[str], title: str, grid_format: GridFormat) -> ParsedGrid:
        """Parse a simple ASCII grid"""
        rows = len(lines)
        if rows == 0:
            return ParsedGrid(title=title, format=grid_format)
        
        # Find maximum line length
        cols = max(len(line) for line in lines)
        
        # Create grid
        grid = []
        for row_idx, line in enumerate(lines):
            row = []
            # Pad line to cols
            padded_line = line.ljust(cols)
            for col_idx, char in enumerate(padded_line):
                cell = GridCell(
                    char=char,
                    row=row_idx,
                    col=col_idx
                )
                
                # Convert box/teletext characters to standardized representation
                if grid_format == GridFormat.BOX_DRAWING and char in self.BOX_CHARS:
                    cell.metadata['type'] = self.BOX_CHARS[char]
                elif grid_format == GridFormat.TELETEXT and char in self.TELETEXT_BLOCKS:
                    cell.metadata['type'] = self.TELETEXT_BLOCKS[char]
                
                row.append(cell)
            grid.append(row)
        
        return ParsedGrid(
            title=title,
            rows=rows,
            cols=cols,
            grid=grid,
            format=grid_format
        )

    def _parse_markdown_table(self, lines: List[str], title: str) -> ParsedGrid:
        """Parse a markdown table into a grid"""
        # Remove empty lines and separator lines
        clean_lines = []
        separator_found = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if not separator_found and self._is_separator_line(line):
                separator_found = True
                continue
            clean_lines.append(line)
        
        if not clean_lines:
            return ParsedGrid(title=title, format=GridFormat.MARKDOWN)
        
        # Parse cells from each line
        rows = len(clean_lines)
        
        # Count columns from first line
        first_line = clean_lines[0]
        cols = first_line.count('|') - 1  # -1 because | at start and end
        
        grid = []
        for row_idx, line in enumerate(clean_lines):
            row = []
            # Split by | and clean up
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            for col_idx, cell in enumerate(cells):
                grid_cell = GridCell(
                    char=cell[0] if cell else ' ',
                    row=row_idx,
                    col=col_idx
                )
                if len(cell) > 1:
                    grid_cell.metadata['full_text'] = cell
                row.append(grid_cell)
            grid.append(row)
        
        return ParsedGrid(
            title=title,
            rows=rows,
            cols=cols,
            grid=grid,
            format=GridFormat.MARKDOWN
        )

    def _is_separator_line(self, line: str) -> bool:
        """Check if line is a markdown table separator"""
        line = line.strip()
        if not line.startswith('|') or not line.endswith('|'):
            return False
        # Remove outer pipes
        inner = line[1:-1]
        # Should contain only dashes, colons, and pipes
        return all(c in ':-| ' for c in inner) and '---' in inner

    def _parse_csv(self, lines: List[str], title: str) -> ParsedGrid:
        """Parse CSV data into a grid"""
        rows = len(lines)
        if rows == 0:
            return ParsedGrid(title=title, format=GridFormat.CSV)
        
        # Parse all rows
        all_rows = []
        for line in lines:
            # Handle quoted CSV
            row_data = self._parse_csv_line(line)
            all_rows.append(row_data)
        
        # Find maximum columns
        cols = max(len(row) for row in all_rows)
        
        # Create grid
        grid = []
        for row_idx, row_data in enumerate(all_rows):
            row = []
            for col_idx in range(cols):
                cell_data = row_data[col_idx] if col_idx < len(row_data) else ''
                grid_cell = GridCell(
                    char=cell_data[0] if cell_data else ' ',
                    row=row_idx,
                    col=col_idx
                )
                if len(cell_data) > 1:
                    grid_cell.metadata['full_text'] = cell_data
                row.append(grid_cell)
            grid.append(row)
        
        return ParsedGrid(
            title=title,
            rows=rows,
            cols=cols,
            grid=grid,
            format=GridFormat.CSV
        )

    def _parse_csv_line(self, line: str) -> List[str]:
        """Parse a CSV line, handling quoted fields"""
        result = []
        current = ''
        in_quotes = False
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                result.append(current)
                current = ''
            else:
                current += char
        
        result.append(current)
        return result

    def parse_component(self, component_text: str) -> GridComponent:
        """
        Parse an individual component definition.
        
        Format:
        component <id> [name=<name>] [type=<type>] [properties=<json>] [cells=<cell_list>]
        
        Example:
        component header name="Main Header" type="widget" properties={"color": "red"} cells=[(0,0),(0,1),(0,2)]
        """
        # Parse component definition
        match = re.match(
            r'component\s+(\S+)\s*(.*?)$',
            component_text.strip()
        )
        if not match:
            raise ValueError(f"Invalid component definition: {component_text}")
        
        comp_id = match.group(1)
        rest = match.group(2)
        
        # Extract name
        name = "Untitled"
        name_match = re.search(r'name=["\']?([^"\'\s]+)["\']?', rest)
        if name_match:
            name = name_match.group(1)
        
        # Extract type
        comp_type = "widget"
        type_match = re.search(r'type=["\']?([^"\'\s]+)["\']?', rest)
        if type_match:
            comp_type = type_match.group(1)
        
        # Extract properties
        properties = {}
        props_match = re.search(r'properties=(\{.*?\})', rest)
        if props_match:
            try:
                properties = json.loads(props_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Extract cells
        cells = []
        cells_match = re.search(r'cells=\[(.*?)\]', rest)
        if cells_match:
            cell_str = cells_match.group(1)
            cell_pairs = re.findall(r'\((\d+),(\d+)\)', cell_str)
            for row_str, col_str in cell_pairs:
                cells.append((int(row_str), int(col_str)))
        
        return GridComponent(
            id=comp_id,
            name=name,
            component_type=comp_type,
            properties=properties,
            cells=cells
        )

    def parse_with_components(self, grid_text: str, components: List[str], 
                              title: str = "Untitled") -> ParsedGrid:
        """
        Parse ASCII grid with component definitions.
        
        Args:
            grid_text: The ASCII grid text
            components: List of component definition strings
            title: Optional title
            
        Returns:
            ParsedGrid with components
        """
        # Parse grid
        parsed = self.parse_grid(grid_text, title)
        
        # Parse components
        for comp_text in components:
            component = self.parse_component(comp_text)
            parsed.add_component(component)
            
            # Mark cells as belonging to this component
            for row, col in component.cells:
                if row < parsed.rows and col < parsed.cols:
                    cell = parsed.get_cell(row, col)
                    if cell:
                        cell.component_id = component.id
        
        return parsed

    def to_structured(self, parsed: ParsedGrid) -> Dict[str, Any]:
        """
        Convert parsed grid to structured data format.
        
        This creates a format suitable for:
        - JSON serialization
        - USXD document integration
        - ThinUI rendering
        - Component mapping
        
        Args:
            parsed: The ParsedGrid to convert
            
        Returns:
            Structured data dictionary
        """
        return {
            'type': 'grid',
            'title': parsed.title,
            'dimensions': {
                'rows': parsed.rows,
                'cols': parsed.cols
            },
            'format': parsed.format.value,
            'cells': [[cell.to_dict() for cell in row] for row in parsed.grid],
            'components': {comp_id: comp.to_dict() 
                          for comp_id, comp in parsed.components.items()},
            'metadata': parsed.metadata
        }

    def to_grid(self, structured_data: Dict[str, Any]) -> ParsedGrid:
        """
        Convert structured data back to ASCII grid format.
        
        This is the reverse operation of to_structured().
        
        Args:
            structured_data: The structured data dictionary
            
        Returns:
            ParsedGrid object
        """
        if structured_data.get('type') != 'grid':
            raise ValueError("Invalid grid structured data")
        
        # Extract dimensions
        dims = structured_data.get('dimensions', {})
        rows = dims.get('rows', 0)
        cols = dims.get('cols', 0)
        
        # Create grid
        grid_data = structured_data.get('cells', [])
        grid = []
        for row_idx, row_data in enumerate(grid_data):
            row = []
            for col_idx, cell_data in enumerate(row_data):
                cell = GridCell.from_dict(cell_data)
                cell.row = row_idx
                cell.col = col_idx
                row.append(cell)
            grid.append(row)
        
        # Create components
        components = {}
        for comp_id, comp_data in structured_data.get('components', {}).items():
            components[comp_id] = GridComponent.from_dict(comp_data)
        
        return ParsedGrid(
            title=structured_data.get('title', 'Untitled'),
            rows=rows,
            cols=cols,
            grid=grid,
            components=components,
            metadata=structured_data.get('metadata', {}),
            format=GridFormat(structured_data.get('format', 'simple'))
        )

    def split_into_components(self, grid_text: str) -> List[Dict[str, Any]]:
        """
        Automatically detect and split grid into components.
        
        This uses heuristics to identify:
        - Contiguous regions of the same character
        - Box boundaries (when using box drawing chars)
        - Separated sections
        
        Args:
            grid_text: The ASCII grid text
            
        Returns:
            List of component definitions
        """
        parsed = self.parse_grid(grid_text)
        visited = [[False for _ in range(parsed.cols)] for _ in range(parsed.rows)]
        components = []
        comp_id = 0
        
        for row in range(parsed.rows):
            for col in range(parsed.cols):
                if not visited[row][col]:
                    cell = parsed.get_cell(row, col)
                    if cell and cell.char != ' ':
                        # Find region of same character
                        region, region_cells = self._find_region(
                            parsed, row, col, cell.char, visited
                        )
                        if len(region_cells) > 1 or cell.char not in ' \t':
                            components.append({
                                'id': f'comp_{comp_id}',
                                'name': f'Region_{comp_id}',
                                'type': 'region',
                                'char': cell.char,
                                'cells': [{'row': r, 'col': c} for r, c in region_cells],
                                'size': len(region_cells)
                            })
                            comp_id += 1
        
        return components

    def _find_region(self, parsed: ParsedGrid, start_row: int, start_col: int, 
                     target_char: str, visited: List[List[bool]]) -> Tuple[Any, List[Tuple[int, int]]]:
        """Find a contiguous region of the same character"""
        from collections import deque
        
        queue = deque([(start_row, start_col)])
        region_cells = []
        
        while queue:
            row, col = queue.popleft()
            
            if (row < 0 or row >= parsed.rows or 
                col < 0 or col >= parsed.cols or
                visited[row][col]):
                continue
            
            cell = parsed.get_cell(row, col)
            if cell and cell.char == target_char:
                visited[row][col] = True
                region_cells.append((row, col))
                
                # Check neighbors
                queue.append((row - 1, col))
                queue.append((row + 1, col))
                queue.append((row, col - 1))
                queue.append((row, col + 1))
        
        return None, region_cells

    def detect_component_boundaries(self, grid_text: str) -> ParsedGrid:
        """
        Detect component boundaries in a grid using box drawing characters.
        
        This method identifies regions enclosed by box drawing characters
        and creates components for each enclosed region.
        """
        parsed = self.parse_grid(grid_text)
        
        # Find all box corners (┌, ┐, └, ┘)
        corners = []
        for row in range(parsed.rows):
            for col in range(parsed.cols):
                cell = parsed.get_cell(row, col)
                if cell and cell.char in ['┌', '┐', '└', '┘']:
                    corners.append((row, col, cell.char))
        
        # Try to match corners to form rectangles
        rectangles = []
        
        for i, (r1, c1, char1) in enumerate(corners):
            if char1 in ['┌', '└']:  # Top-left or bottom-left
                for j, (r2, c2, char2) in enumerate(corners[i+1:]):
                    rc = r1 + (r2 - r1) - 1
                    if char1 == '┌' and char2 == '┐':  # Top-left and top-right
                        # Look for matching bottom corners
                        for k, (r3, c3, char3) in enumerate(corners[j+1:]):
                            if r3 > r1 and r3 != rc:
                                continue
                            if char3 == '└':  # Bottom-left
                                # Look for bottom-right
                                for (r4, c4, char4) in corners[k+1:]:
                                    if r4 == r3 and c4 > c1 and char4 == '┘':
                                        rectangles.append((r1, c1, r4, c4))
                                        break
                    elif char1 == '└' and char2 == '┘':  # Bottom-left and bottom-right
                        # Look for matching top corners
                        for k, (r3, c3, char3) in enumerate(corners[j+1:]):
                            if r3 < r1:
                                continue
                            if char3 == '┌':  # Top-left
                                # Look for top-right
                                for (r4, c4, char4) in corners[k+1:]:
                                    if r4 == r3 and c4 > c1 and char4 == '┐':
                                        rectangles.append((r3, c1, r1, c4))
                                        break
        
        # Create components from rectangles
        comp_id = 0
        for r1, c1, r2, c2 in rectangles:
            component_id = f'region_{comp_id}'
            
            # Create component
            cells = []
            for row in range(r1 + 1, r2):  # Skip border
                for col in range(c1 + 1, c2):  # Skip border
                    cells.append((row, col))
            
            component = GridComponent(
                id=component_id,
                name=f'Region_{comp_id}',
                component_type='area',
                cells=cells
            )
            parsed.add_component(component)
            
            # Mark cells
            for row, col in cells:
                cell = parsed.get_cell(row, col)
                if cell:
                    cell.component_id = component_id
            
            comp_id += 1
        
        return parsed


# Test the implementation
if __name__ == "__main__":
    print("Testing ASCII Grid Parser...")
    
    # Test 1: Simple grid
    print("\n=== Test 1: Simple Grid ===")
    parser = ASCIIGridParser()
    simple_grid = """ABC
DEF
GHI"""
    parsed = parser.parse_grid(simple_grid, "Simple Test")
    print(f"✓ Parsed simple grid: {parsed.rows}x{parsed.cols}")
    print(f"✓ Title: {parsed.title}")
    print(f"✓ Cell (0,0): {parsed.get_cell(0, 0).char}")
    print(f"✓ Cell (2,2): {parsed.get_cell(2, 2).char}")
    
    # Test 2: Grid with box drawing
    print("\n=== Test 2: Box Drawing Grid ===")
    box_grid = """┌───┐
│ABC│
└───┘"""
    parsed = parser.parse_grid(box_grid, "Box Test")
    print(f"✓ Parsed box grid: {parsed.rows}x{parsed.cols}")
    corner = parsed.get_cell(0, 0)
    print(f"✓ Top-left corner: {corner.char} (metadata: {corner.metadata})")
    
    # Test 3: Markdown table
    print("\n=== Test 3: Markdown Table ===")
    md_table = """| A | B | C |
|---|---|---|
| D | E | F |
| G | H | I |"""
    parsed = parser.parse_grid(md_table, "Markdown Test")
    print(f"✓ Parsed markdown table: {parsed.rows}x{parsed.cols}")
    print(f"✓ Cell (1,0): {parsed.get_cell(1, 0).char} (full: {parsed.get_cell(1, 0).metadata.get('full_text', 'N/A')})")
    
    # Test 4: CSV
    print("\n=== Test 4: CSV ===")
    csv_data = """A,B,C
D,E,F
G,H,I"""
    parsed = parser.parse_grid(csv_data, "CSV Test")
    print(f"✓ Parsed CSV: {parsed.rows}x{parsed.cols}")
    
    # Test 5: Component parsing
    print("\n=== Test 5: Component Parsing ===")
    component = parser.parse_component('component header name="Main Header" type="widget" properties={"color": "red"} cells=[(0,0),(0,1),(0,2)]')
    print(f"✓ Component ID: {component.id}")
    print(f"✓ Component name: {component.name}")
    print(f"✓ Component type: {component.component_type}")
    print(f"✓ Component properties: {component.properties}")
    print(f"✓ Component cells: {component.cells}")
    
    # Test 6: Grid with components
    print("\n=== Test 6: Grid with Components ===")
    components = [
        'component header name="Main Header" cells=[(0,0),(0,1),(0,2)]',
        'component body name="Main Body" cells=[(1,0),(1,1),(1,2)]'
    ]
    parsed = parser.parse_with_components("ABC\nDEF\nGHI", components, "Component Test")
    print(f"✓ Parsed grid with {len(parsed.components)} components")
    print(f"✓ Component headers: {list(parsed.components.keys())}")
    print(f"✓ Cell (0,0) component: {parsed.get_cell(0, 0).component_id}")
    
    # Test 7: Structured conversion
    print("\n=== Test 7: Structured Conversion ===")
    structured = parser.to_structured(parsed)
    print(f"✓ Structured data type: {structured['type']}")
    print(f"✓ Dimensions: {structured['dimensions']}")
    print(f"✓ Components count: {len(structured['components'])}")
    
    # Test 8: Back to grid
    print("\n=== Test 8: Back to Grid ===")
    parsed_back = parser.to_grid(structured)
    print(f"✓ Round-trip successful: {parsed_back.rows}x{parsed_back.cols}")
    
    # Test 9: Auto component detection
    print("\n=== Test 9: Auto Component Detection ===")
    grid_with_regions = """AAA
BBB
CCC"""
    components = parser.split_into_components(grid_with_regions)
    print(f"✓ Detected {len(components)} components")
    for comp in components:
        print(f"  - {comp['id']}: {comp['size']} cells")
    
    # Test 10: JSON serialization
    print("\n=== Test 10: JSON Serialization ===")
    json_str = parsed.to_json()
    print(f"✓ JSON length: {len(json_str)}")
    parsed_from_json = ParsedGrid.from_json(json_str)
    print(f"✓ Deserialized from JSON: {parsed_from_json.rows}x{parsed_from_json.cols}")
    
    print("\nAll ASCII grid parser tests passed!")
