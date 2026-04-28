"""
Grid Layers and Stacks

Provides layer-based grid organization for multi-layer data.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from .models import Grid, GridCell, GridSize

T = TypeVar('T')


class LayerType(Enum):
    """Types of grid layers."""
    BASE = "base"          # Base terrain/background
    OBJECT = "object"      # Objects/items
    CHARACTER = "character"  # Characters/actors
    OVERLAY = "overlay"    # UI overlays, effects
    FOREGROUND = "foreground"  # Foreground elements
   

@dataclass
class GridLayer(Generic[T]):
    """A single layer in a layered grid.
    
    Layers can be stacked to create complex multi-layer grids.
    """
    name: str
    grid: Grid[T]
    layer_type: LayerType = LayerType.BASE
    visible: bool = True
    opacity: float = 1.0
    z_index: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return f"GridLayer({self.name}, {self.layer_type.value}, z={self.z_index})"
    
    @property
    def width(self) -> int:
        return self.grid.width
    
    @property
    def height(self) -> int:
        return self.grid.height
    
    @property
    def size(self) -> GridSize:
        return self.grid.size()
    
    def get_cell(self, x: int, y: int) -> Optional[GridCell[T]]:
        """Get cell at coordinates."""
        if not self.visible:
            return None
        try:
            return self.grid.get(x, y)
        except:
            return None


@dataclass
class GridStack(Generic[T]):
    """A stack of grid layers.
    
    Manages multiple layers and provides combined views.
    """
    layers: List[GridLayer[T]] = field(default_factory=list)
    default_layer_type: LayerType = LayerType.BASE
    
    def add_layer(self, layer: GridLayer[T]) -> None:
        """Add a layer to the stack."""
        self.layers.append(layer)
        # Sort by z-index
        self.layers.sort(key=lambda l: l.z_index)
    
    def remove_layer(self, name: str) -> bool:
        """Remove a layer by name."""
        initial_count = len(self.layers)
        self.layers = [l for l in self.layers if l.name != name]
        return len(self.layers) < initial_count
    
    def get_layer(self, name: str) -> Optional[GridLayer[T]]:
        """Get a layer by name."""
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None
    
    def get_all_layers(self) -> List[GridLayer[T]]:
        """Get all layers."""
        return list(self.layers)
    
    def get_visible_layers(self) -> List[GridLayer[T]]:
        """Get all visible layers."""
        return [l for l in self.layers if l.visible]
    
    def get_layers_by_type(self, layer_type: LayerType) -> List[GridLayer[T]]:
        """Get layers of a specific type."""
        return [l for l in self.layers if l.layer_type == layer_type]
    
    def hide_layer(self, name: str) -> bool:
        """Hide a layer."""
        layer = self.get_layer(name)
        if layer:
            layer.visible = False
            return True
        return False
    
    def show_layer(self, name: str) -> bool:
        """Show a layer."""
        layer = self.get_layer(name)
        if layer:
            layer.visible = True
            return True
        return False
    
    @property
    def width(self) -> int:
        """Width of the stack (maximum of all layers)."""
        if not self.layers:
            return 0
        return max(l.width for l in self.layers)
    
    @property
    def height(self) -> int:
        """Height of the stack (maximum of all layers)."""
        if not self.layers:
            return 0
        return max(l.height for l in self.layers)
    
    def get_cell_stack(self, x: int, y: int) -> List[Optional[GridCell[T]]]:
        """Get all cells at a coordinate across all visible layers.
        
        Returns cells from bottom layer to top layer.
        """
        cells = []
        for layer in self.layers:
            if layer.visible:
                cell = layer.get_cell(x, y)
                cells.append(cell)
        return cells
    
    def get_top_cell(self, x: int, y: int) -> Optional[GridCell[T]]:
        """Get the top-most non-empty cell at a coordinate."""
        for layer in reversed(self.layers):
            if layer.visible:
                cell = layer.get_cell(x, y)
                if cell and not cell.is_empty():
                    return cell
        return None
    
    def merge_visible(self) -> Grid[Any]:
        """Merge all visible layers into a single grid.
        
        Top layers overwrite bottom layers.
        """
        if not self.layers:
            return Grid(0, 0)
        
        # Use the largest dimensions
        width = self.width
        height = self.height
        result = Grid(width, height)
        
        # Blend layers from bottom to top
        for layer in self.layers:
            if not layer.visible:
                continue
            
            for y in range(min(layer.height, height)):
                for x in range(min(layer.width, width)):
                    cell = layer.get_cell(x, y)
                    if cell and not cell.is_empty():
                        result.set(x, y, cell)
        
        return result
    
    def clear(self) -> None:
        """Remove all layers."""
        self.layers.clear()
    
    def __len__(self) -> int:
        return len(self.layers)
    
    def __repr__(self) -> str:
        return f"GridStack({len(self.layers)} layers, {self.width}x{self.height})"
