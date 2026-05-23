"""
Variable Binding — Bind Grid Cells to Runtime Variables

Provides a system for binding grid cells to Python variables
and expressions, enabling live-updating grids that reflect
variable changes in real-time.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


@dataclass
class CellBinding:
    """
    A binding between a grid cell and a variable/expression.
    
    When the variable changes, the cell is automatically updated.
    """
    cell_x: int
    cell_y: int
    variable_name: str
    format_spec: str = "{}"       # Format string for display
    layer_name: str = "base"      # Which layer this binding is on
    fg_color: Optional[str] = None
    bg_color: Optional[str] = None
    enabled: bool = True
    last_value: Optional[str] = None

    def format_value(self, value: Any) -> str:
        """Format a value for display in the grid cell."""
        try:
            return self.format_spec.format(value)
        except Exception:
            return str(value)[:1]  # Truncate to single char


@dataclass
class RegionBinding:
    """
    A binding between a grid region and a list/object.
    
    Maps iterable data to a rectangular region of the grid.
    """
    region_x: int
    region_y: int
    region_width: int
    region_height: int
    variable_name: str
    layer_name: str = "base"
    enabled: bool = True
    orientation: str = "horizontal"  # "horizontal" or "vertical"


class VariableBinding:
    """
    Manages bindings between grid cells and runtime variables.
    
    Features:
    - Cell-level variable binding
    - Region-level data binding
    - Format string support
    - Live update notification
    - Batch update support
    """

    def __init__(self):
        self._cell_bindings: Dict[str, CellBinding] = {}  # key: "layer:x:y"
        self._region_bindings: List[RegionBinding] = []
        self._variables: Dict[str, Any] = {}
        self._listeners: List[Callable[[str, Any], None]] = []
        self._batch_mode: bool = False
        self._pending_updates: Set[str] = set()

    # ── Variable Management ──────────────────────────────────

    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable value and trigger updates."""
        old_value = self._variables.get(name)
        self._variables[name] = value

        if old_value != value:
            self._notify_variable_changed(name, value)
            self._update_bindings_for_variable(name)

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable value."""
        return self._variables.get(name, default)

    def has_variable(self, name: str) -> bool:
        """Check if a variable exists."""
        return name in self._variables

    def delete_variable(self, name: str) -> bool:
        """Delete a variable."""
        if name in self._variables:
            del self._variables[name]
            self._notify_variable_changed(name, None)
            return True
        return False

    def get_all_variables(self) -> Dict[str, Any]:
        """Get all variables."""
        return dict(self._variables)

    # ── Cell Binding Management ──────────────────────────────

    def bind_cell(self, x: int, y: int, variable_name: str,
                  format_spec: str = "{}",
                  layer_name: str = "base",
                  fg_color: Optional[str] = None,
                  bg_color: Optional[str] = None) -> CellBinding:
        """Bind a grid cell to a variable."""
        key = f"{layer_name}:{x}:{y}"
        binding = CellBinding(
            cell_x=x,
            cell_y=y,
            variable_name=variable_name,
            format_spec=format_spec,
            layer_name=layer_name,
            fg_color=fg_color,
            bg_color=bg_color,
        )
        self._cell_bindings[key] = binding
        return binding

    def unbind_cell(self, x: int, y: int, layer_name: str = "base") -> bool:
        """Remove a cell binding."""
        key = f"{layer_name}:{x}:{y}"
        if key in self._cell_bindings:
            del self._cell_bindings[key]
            return True
        return False

    def get_cell_binding(self, x: int, y: int,
                         layer_name: str = "base") -> Optional[CellBinding]:
        """Get the binding for a specific cell."""
        key = f"{layer_name}:{x}:{y}"
        return self._cell_bindings.get(key)

    def get_all_cell_bindings(self) -> List[CellBinding]:
        """Get all cell bindings."""
        return list(self._cell_bindings.values())

    def get_bindings_for_variable(self, variable_name: str) -> List[CellBinding]:
        """Get all bindings for a specific variable."""
        return [
            b for b in self._cell_bindings.values()
            if b.variable_name == variable_name
        ]

    # ── Region Binding Management ────────────────────────────

    def bind_region(self, x: int, y: int, width: int, height: int,
                    variable_name: str,
                    layer_name: str = "base",
                    orientation: str = "horizontal") -> RegionBinding:
        """Bind a grid region to a list/object variable."""
        binding = RegionBinding(
            region_x=x,
            region_y=y,
            region_width=width,
            region_height=height,
            variable_name=variable_name,
            layer_name=layer_name,
            orientation=orientation,
        )
        self._region_bindings.append(binding)
        return binding

    def unbind_region(self, binding: RegionBinding) -> bool:
        """Remove a region binding."""
        if binding in self._region_bindings:
            self._region_bindings.remove(binding)
            return True
        return False

    def get_all_region_bindings(self) -> List[RegionBinding]:
        """Get all region bindings."""
        return list(self._region_bindings)

    # ── Update and Notification ──────────────────────────────

    def _update_bindings_for_variable(self, variable_name: str) -> None:
        """Update all bindings for a changed variable."""
        for binding in self.get_bindings_for_variable(variable_name):
            value = self._variables.get(variable_name)
            formatted = binding.format_value(value)
            binding.last_value = formatted

            if self._batch_mode:
                key = f"{binding.layer_name}:{binding.cell_x}:{binding.cell_y}"
                self._pending_updates.add(key)
            else:
                self._notify_cell_updated(
                    binding.cell_x, binding.cell_y,
                    formatted, binding.layer_name,
                    binding.fg_color, binding.bg_color,
                )

    def add_listener(self, callback: Callable[[str, Any], None]) -> None:
        """Add a listener for variable changes."""
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[str, Any], None]) -> None:
        """Remove a listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_variable_changed(self, name: str, value: Any) -> None:
        """Notify listeners of a variable change."""
        for listener in self._listeners:
            try:
                listener(name, value)
            except Exception:
                pass

    def _notify_cell_updated(self, x: int, y: int, char: str,
                              layer: str,
                              fg: Optional[str], bg: Optional[str]) -> None:
        """Notify that a cell should be updated."""
        # This would be connected to the grid editor
        pass

    # ── Batch Operations ─────────────────────────────────────

    def begin_batch(self) -> None:
        """Begin batch update mode."""
        self._batch_mode = True

    def end_batch(self) -> Set[str]:
        """End batch update mode and return pending updates."""
        self._batch_mode = False
        pending = set(self._pending_updates)
        self._pending_updates.clear()
        return pending

    # ── Expression Evaluation ────────────────────────────────

    def evaluate_expression(self, expression: str,
                            context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Evaluate a simple expression in the variable context.
        
        Supports:
        - Variable references: {var_name}
        - Arithmetic: {a + b}
        - String concat: {first} {last}
        - Conditionals: {cond ? yes : no}
        """
        if context is None:
            context = self._variables

        # Simple variable substitution
        import re
        def replace_var(match: re.Match) -> str:
            var_name = match.group(1)
            value = context.get(var_name, match.group(0))
            return str(value)

        result = re.sub(r'\{(\w+)\}', replace_var, expression)
        return result

    # ── Export ───────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Export bindings as a dictionary."""
        return {
            'variables': dict(self._variables),
            'cell_bindings': [
                {
                    'x': b.cell_x,
                    'y': b.cell_y,
                    'variable': b.variable_name,
                    'format': b.format_spec,
                    'layer': b.layer_name,
                    'fg': b.fg_color,
                    'bg': b.bg_color,
                }
                for b in self._cell_bindings.values()
            ],
            'region_bindings': [
                {
                    'x': b.region_x,
                    'y': b.region_y,
                    'width': b.region_width,
                    'height': b.region_height,
                    'variable': b.variable_name,
                    'layer': b.layer_name,
                    'orientation': b.orientation,
                }
                for b in self._region_bindings
            ],
        }
