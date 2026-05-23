"""
Layer Editor — Multi-Layer Grid Editing

Provides layer management for the grid editor:
- Layer stack with z-order management
- Per-layer visibility, opacity, blend modes
- Layer grouping and locking
- Grid merge operations
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..grid.models import Grid, GridCell, Coordinate, GridRegion
from ..grid.layers import GridLayer, GridStack, LayerType


class BlendMode(Enum):
    """Blend modes for layer compositing."""
    NORMAL = "normal"        # Top overwrites bottom
    ADD = "add"              # Additive blending
    MULTIPLY = "multiply"    # Multiplicative blending
    SCREEN = "screen"        # Screen blending
    OVERLAY = "overlay"      # Overlay blending


@dataclass
class LayerEditState:
    """State for the layer editor."""
    active_layer_index: int = 0
    locked_layers: List[str] = field(default_factory=list)
    hidden_layers: List[str] = field(default_factory=list)
    blend_modes: Dict[str, BlendMode] = field(default_factory=dict)
    layer_opacities: Dict[str, float] = field(default_factory=dict)
    layer_groups: Dict[str, str] = field(default_factory=dict)  # layer_name -> group_name
    expanded_groups: List[str] = field(default_factory=list)


class LayerEditor:
    """
    Layer editor for managing multi-layer grid stacks.
    
    Provides:
    - Layer CRUD (add, remove, reorder, rename)
    - Visibility and opacity control
    - Blend modes
    - Layer locking
    - Layer grouping
    - Composite preview
    """

    def __init__(self, stack: Optional[GridStack] = None):
        self.stack = stack or GridStack()
        self.state = LayerEditState()

    # ── Layer CRUD ───────────────────────────────────────────

    @property
    def active_layer(self) -> Optional[GridLayer]:
        """Get the currently active layer."""
        if 0 <= self.state.active_layer_index < len(self.stack.layers):
            return self.stack.layers[self.state.active_layer_index]
        return None

    @property
    def active_grid(self) -> Optional[Grid]:
        """Get the grid of the active layer."""
        layer = self.active_layer
        return layer.grid if layer else None

    @property
    def layer_count(self) -> int:
        """Get the number of layers."""
        return len(self.stack.layers)

    def add_layer(self, name: str, layer_type: LayerType = LayerType.OBJECT,
                  width: int = 40, height: int = 25,
                  z_index: Optional[int] = None) -> GridLayer:
        """Add a new layer to the stack."""
        grid: Grid[Any] = Grid(width, height)
        z = z_index if z_index is not None else len(self.stack.layers)
        layer = GridLayer(name=name, grid=grid, layer_type=layer_type, z_index=z)
        self.stack.add_layer(layer)
        self.state.active_layer_index = len(self.stack.layers) - 1
        return layer

    def remove_layer(self, name: str) -> bool:
        """Remove a layer by name."""
        if len(self.stack.layers) <= 1:
            return False  # Cannot remove the last layer
        if name in self.state.locked_layers:
            return False  # Cannot remove locked layer

        result = self.stack.remove_layer(name)
        if result:
            self.state.active_layer_index = max(0, self.state.active_layer_index - 1)
            self.state.locked_layers = [l for l in self.state.locked_layers if l != name]
            self.state.hidden_layers = [l for l in self.state.hidden_layers if l != name]
            self.state.blend_modes.pop(name, None)
            self.state.layer_opacities.pop(name, None)
            self.state.layer_groups.pop(name, None)
        return result

    def rename_layer(self, old_name: str, new_name: str) -> bool:
        """Rename a layer."""
        layer = self.stack.get_layer(old_name)
        if layer is None:
            return False
        layer.name = new_name
        # Update state references
        if old_name in self.state.locked_layers:
            self.state.locked_layers.remove(old_name)
            self.state.locked_layers.append(new_name)
        if old_name in self.state.hidden_layers:
            self.state.hidden_layers.remove(old_name)
            self.state.hidden_layers.append(new_name)
        if old_name in self.state.blend_modes:
            self.state.blend_modes[new_name] = self.state.blend_modes.pop(old_name)
        if old_name in self.state.layer_opacities:
            self.state.layer_opacities[new_name] = self.state.layer_opacities.pop(old_name)
        if old_name in self.state.layer_groups:
            self.state.layer_groups[new_name] = self.state.layer_groups.pop(old_name)
        return True

    def duplicate_layer(self, name: str, new_name: Optional[str] = None) -> Optional[GridLayer]:
        """Duplicate a layer."""
        layer = self.stack.get_layer(name)
        if layer is None:
            return None

        dup_name = new_name or f"{name}_copy"
        dup_grid = layer.grid.clone()
        dup_layer = GridLayer(
            name=dup_name,
            grid=dup_grid,
            layer_type=layer.layer_type,
            visible=layer.visible,
            opacity=layer.opacity,
            z_index=layer.z_index + 1,
            metadata=dict(layer.metadata),
        )
        self.stack.add_layer(dup_layer)
        return dup_layer

    def move_layer_up(self, name: str) -> bool:
        """Move a layer up in the stack (higher z-order)."""
        layers = self.stack.layers
        for i, layer in enumerate(layers):
            if layer.name == name and i < len(layers) - 1:
                layers[i], layers[i + 1] = layers[i + 1], layers[i]
                layers[i].z_index = i
                layers[i + 1].z_index = i + 1
                if self.state.active_layer_index == i:
                    self.state.active_layer_index = i + 1
                elif self.state.active_layer_index == i + 1:
                    self.state.active_layer_index = i
                return True
        return False

    def move_layer_down(self, name: str) -> bool:
        """Move a layer down in the stack (lower z-order)."""
        layers = self.stack.layers
        for i, layer in enumerate(layers):
            if layer.name == name and i > 0:
                layers[i], layers[i - 1] = layers[i - 1], layers[i]
                layers[i].z_index = i
                layers[i - 1].z_index = i - 1
                if self.state.active_layer_index == i:
                    self.state.active_layer_index = i - 1
                elif self.state.active_layer_index == i - 1:
                    self.state.active_layer_index = i
                return True
        return False

    def set_active_layer(self, index: int) -> bool:
        """Set the active layer by index."""
        if 0 <= index < len(self.stack.layers):
            self.state.active_layer_index = index
            return True
        return False

    def set_active_layer_by_name(self, name: str) -> bool:
        """Set the active layer by name."""
        for i, layer in enumerate(self.stack.layers):
            if layer.name == name:
                self.state.active_layer_index = i
                return True
        return False

    # ── Visibility and Opacity ───────────────────────────────

    def toggle_visibility(self, name: str) -> bool:
        """Toggle layer visibility."""
        layer = self.stack.get_layer(name)
        if layer is None:
            return False
        layer.visible = not layer.visible
        if name in self.state.hidden_layers:
            self.state.hidden_layers.remove(name)
        else:
            self.state.hidden_layers.append(name)
        return True

    def set_visibility(self, name: str, visible: bool) -> bool:
        """Set layer visibility."""
        layer = self.stack.get_layer(name)
        if layer is None:
            return False
        layer.visible = visible
        if visible and name in self.state.hidden_layers:
            self.state.hidden_layers.remove(name)
        elif not visible and name not in self.state.hidden_layers:
            self.state.hidden_layers.append(name)
        return True

    def set_opacity(self, name: str, opacity: float) -> bool:
        """Set layer opacity (0.0 to 1.0)."""
        layer = self.stack.get_layer(name)
        if layer is None:
            return False
        layer.opacity = max(0.0, min(1.0, opacity))
        self.state.layer_opacities[name] = layer.opacity
        return True

    def set_blend_mode(self, name: str, mode: BlendMode) -> bool:
        """Set the blend mode for a layer."""
        layer = self.stack.get_layer(name)
        if layer is None:
            return False
        self.state.blend_modes[name] = mode
        return True

    # ── Layer Locking ────────────────────────────────────────

    def toggle_lock(self, name: str) -> bool:
        """Toggle layer lock."""
        if name in self.state.locked_layers:
            self.state.locked_layers.remove(name)
        else:
            self.state.locked_layers.append(name)
        return True

    def is_locked(self, name: str) -> bool:
        """Check if a layer is locked."""
        return name in self.state.locked_layers

    # ── Layer Groups ─────────────────────────────────────────

    def add_to_group(self, layer_name: str, group_name: str) -> bool:
        """Add a layer to a group."""
        layer = self.stack.get_layer(layer_name)
        if layer is None:
            return False
        self.state.layer_groups[layer_name] = group_name
        if group_name not in self.state.expanded_groups:
            self.state.expanded_groups.append(group_name)
        return True

    def remove_from_group(self, layer_name: str) -> bool:
        """Remove a layer from its group."""
        return self.state.layer_groups.pop(layer_name, None) is not None

    def toggle_group_expanded(self, group_name: str) -> None:
        """Toggle whether a group is expanded in the UI."""
        if group_name in self.state.expanded_groups:
            self.state.expanded_groups.remove(group_name)
        else:
            self.state.expanded_groups.append(group_name)

    def get_layers_in_group(self, group_name: str) -> List[GridLayer]:
        """Get all layers in a group."""
        return [
            layer for layer in self.stack.layers
            if self.state.layer_groups.get(layer.name) == group_name
        ]

    def get_groups(self) -> Dict[str, List[GridLayer]]:
        """Get all layer groups."""
        groups: Dict[str, List[GridLayer]] = {}
        for layer in self.stack.layers:
            group = self.state.layer_groups.get(layer.name)
            if group:
                if group not in groups:
                    groups[group] = []
                groups[group].append(layer)
        return groups

    # ── Composite Operations ─────────────────────────────────

    def get_composite_preview(self) -> Optional[Grid]:
        """Get a composite preview of all visible layers."""
        return self.stack.merge_visible()

    def flatten_layers(self) -> Optional[Grid]:
        """
        Flatten all visible layers into a single grid.
        The stack is replaced with a single layer containing the composite.
        """
        composite = self.stack.merge_visible()
        if composite is None:
            return None

        # Replace stack with single layer
        self.stack.layers.clear()
        self.stack.add_layer(GridLayer(
            name="flattened",
            grid=composite,
            layer_type=LayerType.BASE,
            z_index=0,
        ))
        self.state = LayerEditState()
        return composite

    def merge_layer_down(self, name: str) -> bool:
        """
        Merge a layer into the layer below it.
        The merged layer is removed.
        """
        layers = self.stack.layers
        for i, layer in enumerate(layers):
            if layer.name == name and i > 0:
                target = layers[i - 1]
                # Copy non-empty cells from source to target
                for y in range(min(layer.height, target.height)):
                    for x in range(min(layer.width, target.width)):
                        cell = layer.grid.get(x, y)
                        if cell and not cell.is_empty():
                            target.grid.set(x, y, cell.clone())
                # Remove the source layer
                self.stack.remove_layer(name)
                self.state.active_layer_index = max(0, i - 1)
                return True
        return False

    # ── Layer Data Operations ────────────────────────────────

    def clear_layer(self, name: str) -> bool:
        """Clear all cells in a layer."""
        layer = self.stack.get_layer(name)
        if layer is None:
            return False
        for y in range(layer.height):
            for x in range(layer.width):
                layer.grid.cells[y][x].char = ' '
                layer.grid.cells[y][x].fg_color = '#ffffff'
                layer.grid.cells[y][x].bg_color = '#000000'
        return True

    def resize_layer(self, name: str, new_width: int, new_height: int) -> bool:
        """Resize a layer's grid."""
        layer = self.stack.get_layer(name)
        if layer is None:
            return False

        new_grid: Grid[Any] = Grid(new_width, new_height)
        for y in range(min(layer.height, new_height)):
            for x in range(min(layer.width, new_width)):
                new_grid.cells[y][x] = layer.grid.cells[y][x].clone()

        layer.grid = new_grid
        return True

    # ── Export ───────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Export layer editor state as a dictionary."""
        return {
            'active_layer': self.state.active_layer_index,
            'layer_count': len(self.stack.layers),
            'layers': [
                {
                    'name': l.name,
                    'type': l.layer_type.value,
                    'visible': l.visible,
                    'opacity': l.opacity,
                    'z_index': l.z_index,
                    'locked': l.name in self.state.locked_layers,
                    'blend_mode': self.state.blend_modes.get(l.name, BlendMode.NORMAL).value,
                    'group': self.state.layer_groups.get(l.name),
                    'size': {'width': l.width, 'height': l.height},
                }
                for l in self.stack.layers
            ],
            'groups': {
                group: [l.name for l in layers]
                for group, layers in self.get_groups().items()
            },
            'expanded_groups': self.state.expanded_groups,
        }
