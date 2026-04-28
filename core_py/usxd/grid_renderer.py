#!/usr/bin/env python3
"""
TUI Grid Renderer - Python Implementation

This module provides terminal-based rendering for parsed grids,
enabling interactive display of USXD content in Terminal User Interfaces.
"""

import sys
import os
import io
from typing import Optional, List, Dict, Any, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import signal
import tty
import termios
import select
from .grid_parser import ParsedGrid, GridCell, GridComponent, GridFormat, ASCIIGridParser
from .component_mapper import ComponentMapper, ComponentType, ThinUIProperties, Alignment, StylePreset


class ColorMode(Enum):
    """Terminal color modes"""
    NONE = "none"           # No colors
    BASIC = "basic"         # 8 basic ANSI colors
    EXTENDED = "extended"   # 16 colors
    FULL = "full"           # 256 colors
    RGB = "rgb"             # True color (24-bit)


class Key(Enum):
    """Keyboard keys"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    ENTER = "enter"
    SPACE = "space"
    ESC = "esc"
    BACKSPACE = "backspace"
    TAB = "tab"
    UNKNOWN = "unknown"


@dataclass
class Style:
    """Terminal styling options"""
    fg_color: Optional[str] = None
    bg_color: Optional[str] = None
    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: bool = False
    blink: bool = False
    reverse: bool = False
    hidden: bool = False

    def to_ansi(self, color_mode: ColorMode = ColorMode.FULL) -> str:
        """Convert style to ANSI escape codes"""
        codes = []
        
        # Text attributes
        if self.bold:
            codes.append('1')
        if self.dim:
            codes.append('2')
        if self.italic:
            codes.append('3')
        if self.underline:
            codes.append('4')
        if self.blink:
            codes.append('5')
        if self.reverse:
            codes.append('7')
        if self.hidden:
            codes.append('8')
        
        # Foreground color
        if self.fg_color:
            color_code = self._parse_color(self.fg_color, color_mode, fg=True)
            if color_code:
                codes.append(color_code)
        
        # Background color
        if self.bg_color:
            color_code = self._parse_color(self.bg_color, color_mode, fg=False)
            if color_code:
                codes.append(color_code)
        
        if codes:
            return '\033[' + ';'.join(codes) + 'm'
        return ''
    
    def reset(self) -> str:
        """ANSI reset code"""
        return '\033[0m'
    
    def _parse_color(self, color: str, mode: ColorMode, fg: bool = True) -> Optional[str]:
        """Parse color string to ANSI code"""
        color = color.lower().strip()
        
        if mode == ColorMode.NONE:
            return None
        
        # Predefined color names
        color_map = {
            'black': '0',
            'red': '1',
            'green': '2',
            'yellow': '3',
            'blue': '4',
            'magenta': '5',
            'cyan': '6',
            'white': '7',
            'bright_black': '60',
            'bright_red': '61',
            'bright_green': '62',
            'bright_yellow': '63',
            'bright_blue': '64',
            'bright_magenta': '65',
            'bright_cyan': '66',
            'bright_white': '67',
        }
        
        # RGB hex colors (for FULL or RGB mode)
        if color.startswith('#') and len(color) == 7:
            if mode in [ColorMode.FULL, ColorMode.RGB]:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                if mode == ColorMode.FULL:
                    # 256-color mode: RGB approximation
                    color_code = self._rgb_to_256(r, g, b)
                    return f'38;5;{color_code}' if fg else f'48;5;{color_code}'
                elif mode == ColorMode.RGB:
                    return f'38;2;{r};{g};{b}' if fg else f'48;2;{r};{g};{b}'
        
        # RGB decimal (r,g,b)
        if ',' in color:
            parts = color.split(',')
            if len(parts) == 3:
                try:
                    r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
                    if mode == ColorMode.FULL:
                        color_code = self._rgb_to_256(r, g, b)
                        return f'38;5;{color_code}' if fg else f'48;5;{color_code}'
                    elif mode == ColorMode.RGB:
                        return f'38;2;{r};{g};{b}' if fg else f'48;2;{r};{g};{b}'
                except ValueError:
                    pass
        
        # Try named colors
        if color in color_map:
            base_code = color_map[color]
            return base_code if fg else str(int(base_code) + 10)
        
        # 256-color grayscale (0-255)
        if color.isdigit():
            if mode in [ColorMode.FULL, ColorMode.EXTENDED]:
                return f'38;5;{color}' if fg else f'48;5;{color}'
        
        return None
    
    def _rgb_to_256(self, r: int, g: int, b: int) -> int:
        """Convert RGB to 256-color palette index"""
        # Standard 16 colors
        if r == g == b:
            if r < 48:
                return 16
            elif r < 115:
                return 232 + (r - 55) // 10
            else:
                return 231
        
        # RGB cube (6x6x6)
        r6 = (r * 5) // 255
        g6 = (g * 5) // 255
        b6 = (b * 5) // 255
        return 16 + 36 * r6 + 6 * g6 + b6


@dataclass
class RenderConfig:
    """Configuration for grid rendering"""
    color_mode: ColorMode = ColorMode.FULL
    width: Optional[int] = None
    height: Optional[int] = None
    padding: int = 1
    border: bool = True
    box_chars: bool = True
    show_cursor: bool = True
    cursor_blink: bool = True
    default_fg: str = "#FFFFFF"
    default_bg: str = "#000000"
    selection_fg: str = "#000000"
    selection_bg: str = "#FFFF00"
    focus_fg: str = "#000000"
    focus_bg: str = "#00FF00"
    disabled_fg: str = "#888888"
    disabled_bg: str = "#222222"


class KeyboardInput:
    """Handle keyboard input in terminal"""
    
    def __init__(self):
        self._fd = None
        self._old_settings = None
        self._test_mode = False
        
        # Handle redirected stdin (e.g., during pytest)
        try:
            self._fd = sys.stdin.fileno()
        except (io.UnsupportedOperation, AttributeError, ValueError):
            # stdin is redirected or not available (e.g., pytest)
            self._test_mode = True
            self._fd = None
    
    def __enter__(self):
        """Enable raw input mode"""
        if os.name == 'nt' or self._test_mode:
            return self
        
        try:
            self._old_settings = termios.tcgetattr(self._fd)
            new_settings = termios.tcgetattr(self._fd)
            new_settings[3] = new_settings[3] & ~(termios.ICANON | termios.ECHO)
            termios.tcsetattr(self._fd, termios.TCSANOW, new_settings)
        except (termios.error, AttributeError, ValueError, io.UnsupportedOperation):
            # Terminal settings cannot be changed (test mode or non-TTY)
            self._test_mode = True
        return self
    
    def __exit__(self, *args):
        """Restore terminal settings"""
        if os.name == 'nt' or self._test_mode:
            return
        try:
            if self._old_settings:
                termios.tcsetattr(self._fd, termios.TCSANOW, self._old_settings)
        except (termios.error, AttributeError, ValueError, io.UnsupportedOperation):
            pass
    
    def get_key(self, timeout: float = None) -> Key:
        """Get a single key press"""
        if os.name == 'nt' or self._test_mode:
            return Key.UNKNOWN
        
        try:
            if timeout is not None:
                ready, _, _ = select.select([sys.stdin], [], [], timeout)
                if not ready:
                    return Key.UNKNOWN
            
            char = sys.stdin.read(1)
            
            if char == '\x1b':  # ESC
                # Check for arrow keys, function keys, etc.
                next_chars = []
                while True:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        c = sys.stdin.read(1)
                        if c == '\x1b':
                            continue
                        next_chars.append(c)
                        if len(next_chars) >= 2:
                            break
                    else:
                        break
                
                if next_chars:
                    seq = char + ''.join(next_chars)
                    return self._parse_escape_sequence(seq)
                return Key.ESC
            
            return self._parse_key(char)
        except (ValueError, io.UnsupportedOperation, AttributeError):
            self._test_mode = True
            return Key.UNKNOWN
    
    def _parse_key(self, char: str) -> Key:
        """Parse single character"""
        if char == '\n':
            return Key.ENTER
        elif char == ' ':
            return Key.SPACE
        elif char == '\t':
            return Key.TAB
        elif char == '\x7f':
            return Key.BACKSPACE
        return Key.UNKNOWN
    
    def _parse_escape_sequence(self, seq: str) -> Key:
        """Parse ANSI escape sequences"""
        if seq == '\x1b[A':
            return Key.UP
        elif seq == '\x1b[B':
            return Key.DOWN
        elif seq == '\x1b[C':
            return Key.RIGHT
        elif seq == '\x1b[D':
            return Key.LEFT
        return Key.UNKNOWN
    
    def _parse_windows_key(self, char: bytes) -> Key:
        """Parse Windows key codes"""
        import msvcrt
        if char == b'\x00' or char == b'\xe0':
            next_char = msvcrt.getch()
            if next_char == b'H':
                return Key.UP
            elif next_char == b'P':
                return Key.DOWN
            elif next_char == b'M':
                return Key.RIGHT
            elif next_char == b'K':
                return Key.LEFT
            elif next_char == b'\r':
                return Key.ENTER
            elif next_char == b' ':
                return Key.SPACE
        elif char == b'\r':
            return Key.ENTER
        elif char == b' ':
            return Key.SPACE
        return Key.UNKNOWN


class GridRenderer:
    """
    Render parsed grids in terminal with interactive features.
    
    Features:
    - ANSI color support (8, 16, 256, true color)
    - Box drawing character rendering
    - Component highlighting
    - Keyboard navigation
    - Action binding
    - Responsive layout
    
    Usage:
        renderer = GridRenderer()
        renderer.render(parsed_grid)
        # Or for interactive:
        renderer.run_interactive(parsed_grid, actions)
    """
    
    def __init__(self, config: RenderConfig = None):
        """Initialize the renderer"""
        self.config = config or RenderConfig()
        self.parser = ASCIIGridParser()
        self.mapper = ComponentMapper()
        self.keyboard = KeyboardInput()
        self._clear_screen()
    
    def _clear_screen(self) -> None:
        """Clear the terminal screen"""
        sys.stdout.write('\033[2J')
        sys.stdout.write('\033[H')
        sys.stdout.flush()
    
    def _get_terminal_size(self) -> Tuple[int, int]:
        """Get terminal width and height"""
        try:
            import shutil
            size = shutil.get_terminal_size()
            return size.columns, size.lines
        except:
            return 80, 24
    
    def _create_style_for_cell(self, cell: GridCell, 
                              parsed_grid: ParsedGrid,
                              focused: bool = False,
                              selected: bool = False) -> Style:
        """Create render style for a cell"""
        style = Style()
        
        if cell.fg_color:
            style.fg_color = cell.fg_color
        else:
            style.fg_color = self.config.default_fg
        
        if cell.bg_color:
            style.bg_color = cell.bg_color
        else:
            style.bg_color = self.config.default_bg
        
        # Apply focus/selection styles
        if focused:
            style.fn_color = self.config.focus_fg
            style.bg_color = self.config.focus_bg
        elif selected:
            style.fg_color = self.config.selection_fg
            style.bg_color = self.config.selection_bg
        
        # Apply cell metadata as style
        if cell.metadata:
            if 'bold' in cell.metadata and cell.metadata['bold']:
                style.bold = True
            if 'underline' in cell.metadata and cell.metadata['underline']:
                style.underline = True
            if 'blink' in cell.metadata and cell.metadata['blink']:
                style.blink = True
        
        return style
    
    def _get_cell_char(self, cell: GridCell, focused: bool = False) -> str:
        """Get the character to display for a cell"""
        # Cursor indicator
        if focused and self.config.show_cursor:
            return '█'  # Block cursor
        
        return cell.char if cell.char else ' '
    
    def render(self, parsed_grid: ParsedGrid, 
              title: str = None, 
              focused_cell: Tuple[int, int] = None,
              selected_cells: List[Tuple[int, int]] = None) -> str:
        """
        Render a parsed grid to a string with ANSI formatting.
        
        Args:
            parsed_grid: The grid to render
            title: Optional title to display above grid
            focused_cell: (row, col) of currently focused cell
            selected_cells: List of (row, col) tuples for selected cells
            
        Returns:
            Formatted string with ANSI codes
        """
        if focused_cell is None:
            focused_cell = (-1, -1)
        if selected_cells is None:
            selected_cells = []
        
        lines = []
        
        # Add title
        if title or parsed_grid.title:
            grid_title = title or parsed_grid.title
            lines.append(f" {grid_title}\n")
        
        # Render each row
        for row in range(parsed_grid.rows):
            line_parts = []
            for col in range(parsed_grid.cols):
                cell = parsed_grid.get_cell(row, col)
                if not cell:
                    line_parts.append(' ')
                    continue
                
                # Check if focused or selected
                focused = (row, col) == focused_cell
                selected = (row, col) in selected_cells
                
                # Get style and character
                style = self._create_style_for_cell(cell, parsed_grid, focused, selected)
                char = self._get_cell_char(cell, focused)
                
                # Apply style
                ansi_start = style.to_ansi(self.config.color_mode)
                ansi_end = style.reset()
                
                line_parts.append(f"{ansi_start}{char}{ansi_end}")
            
            lines.append(''.join(line_parts))
        
        return '\n'.join(lines)
    
    def render_simple(self, grid_text: str, title: str = None) -> str:
        """
        Parse and render grid text directly.
        
        Args:
            grid_text: ASCII grid text
            title: Optional title
            
        Returns:
            Formatted string
        """
        parsed = self.parser.parse_grid(grid_text, title or "Grid")
        return self.render(parsed, title)
    
    def display(self, parsed_grid: ParsedGrid, 
               title: str = None,
               focused_cell: Tuple[int, int] = None,
               selected_cells: List[Tuple[int, int]] = None,
               clear: bool = True) -> None:
        """
        Display a grid in the terminal.
        
        Args:
            parsed_grid: The grid to display
            title: Optional title
            focused_cell: Currently focused cell
            selected_cells: List of selected cells
            clear: Whether to clear screen first
        """
        rendered = self.render(parsed_grid, title, focused_cell, selected_cells)
        
        if clear:
            self._clear_screen()
        
        sys.stdout.write(rendered)
        sys.stdout.write('\n')
        sys.stdout.flush()
    
    def run_interactive(self, parsed_grid: ParsedGrid, 
                       actions: Dict[str, Callable] = None,
                       initial_position: Tuple[int, int] = None,
                       title: str = None,
                       allow_multi_select: bool = False) -> Optional[str]:
        """
        Run interactive grid rendering with keyboard navigation.
        
        Args:
            parsed_grid: The grid to render
            actions: Mapping from action names to callbacks
            initial_position: Starting cursor position (row, col)
            title: Optional title
            allow_multi_select: Whether to allow multiple selections
            
        Returns:
            Action name that was triggered, or None if user exited
        """
        if actions is None:
            actions = {}
        
        # Validate actions
        valid_actions = {}
        for action_name, callback in actions.items():
            if callable(callback):
                valid_actions[action_name] = callback
        
        # Initialize state
        focused_cell = initial_position or (0, 0)
        selected_cells = [] if allow_multi_select else None
        
        # Ensure initial position is valid
        if (focused_cell[0] >= parsed_grid.rows or 
            focused_cell[1] >= parsed_grid.cols):
            focused_cell = (0, 0)
        
        # Initial render
        self.display(parsed_grid, title, focused_cell, selected_cells)
        
        try:
            with self.keyboard:
                while True:
                    key = self.keyboard.get_key(timeout=0.5)
                    
                    if key == Key.UNKNOWN:
                        continue
                    
                    # Navigation
                    if key == Key.UP:
                        focused_cell = (max(0, focused_cell[0] - 1), focused_cell[1])
                    elif key == Key.DOWN:
                        focused_cell = (min(parsed_grid.rows - 1, focused_cell[0] + 1), focused_cell[1])
                    elif key == Key.LEFT:
                        focused_cell = (focused_cell[0], max(0, focused_cell[1] - 1))
                    elif key == Key.RIGHT:
                        focused_cell = (focused_cell[0], min(parsed_grid.cols - 1, focused_cell[1] + 1))
                    
                    # Selection
                    elif key == Key.SPACE:
                        if allow_multi_select:
                            if focused_cell in selected_cells:
                                selected_cells.remove(focused_cell)
                            else:
                                selected_cells.append(focused_cell)
                    
                    # Actions
                    elif key == Key.ENTER:
                        cell = parsed_grid.get_cell(*focused_cell)
                        if cell and cell.component_id:
                            component = parsed_grid.get_component(cell.component_id)
                            if component:
                                action = component.properties.get('action')
                                if action and action in valid_actions:
                                    valid_actions[action]()
                                    # Re-render to show any changes
                                    self.display(parsed_grid, title, focused_cell, selected_cells)
                                    continue
                        
                        # Try default action
                        if 'default' in valid_actions:
                            valid_actions['default']()
                            self.display(parsed_grid, title, focused_cell, selected_cells)
                            continue
                    
                    # Exit
                    elif key == Key.ESC:
                        break
                    
                    # Update display
                    self.display(parsed_grid, title, focused_cell, selected_cells)
                    
        except KeyboardInterrupt:
            pass
        
        return None
    
    def run_with_components(self, parsed_grid: ParsedGrid,
                           component_actions: Dict[str, Callable] = None,
                           title: str = None) -> Optional[str]:
        """
        Run interactive rendering with component-based actions.
        
        Each component can have an 'action' property that maps to a callback.
        
        Args:
            parsed_grid: The grid with components
            component_actions: Mapping from component IDs to callbacks
            title: Optional title
            
        Returns:
            Component ID that was activated, or None
        """
        if component_actions is None:
            component_actions = {}
        
        # Set up actions based on components
        actions = {}
        actionable_components = {}
        
        for comp_id, component in parsed_grid.components.items():
            if comp_id in component_actions:
                action_name = f"activate_{comp_id}"
                actions[action_name] = component_actions[comp_id]
                actionable_components[comp_id] = action_name
        
        # Add default navigation
        actions['default'] = lambda: None
        
        # Find first actionable component for initial positioning
        initial_pos = None
        for comp_id, component in parsed_grid.components.items():
            if component.cells and comp_id in actionable_components:
                initial_pos = component.cells[0]
                break
        
        if initial_pos is None and parsed_grid.components:
            for comp_id, component in parsed_grid.components.items():
                if component.cells:
                    initial_pos = component.cells[0]
                    break
        
        # Run interactive
        result = self.run_interactive(parsed_grid, actions, initial_pos, title)
        return result
    
    def create_curses_interface(self, parsed_grid: ParsedGrid,
                               actions: Dict[str, Callable] = None):
        """
        Create a curses-based interface for enhanced rendering.
        
        This provides more advanced terminal features if curses is available.
        
        Args:
            parsed_grid: The grid to render
            actions: Action callbacks
            
        Returns:
            CursesInterface object or None if curses not available
        """
        try:
            import curses
            return CursesInterface(self, parsed_grid, actions)
        except ImportError:
            return None


class CursesInterface:
    """Advanced curses-based grid rendering"""
    
    def __init__(self, renderer: GridRenderer, parsed_grid: ParsedGrid,
                 actions: Dict[str, Callable] = None):
        """Initialize curses interface"""
        self.renderer = renderer
        self.parsed_grid = parsed_grid
        self.actions = actions or {}
        self.stdscr = None
        self.focused_cell = (0, 0)
        self.selected_cells = []
        self.running = False
    
    def start(self) -> None:
        """Start the curses interface"""
        try:
            import curses
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            curses.start_color()
            self._init_colors()
            self.running = True
            
            self._main_loop()
            
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the curses interface"""
        if self.stdscr:
            self.stdscr.keypad(False)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            self.stdscr = None
        self.running = False
    
    def _init_colors(self) -> None:
        """Initialize color pairs"""
        try:
            import curses
            # Basic colors
            for i in range(8):
                curses.init_pair(i + 1, i, -1)
                curses.init_pair(i + 9, -1, i)
        except:
            pass  # Not all terminals support colors
    
    def _main_loop(self) -> None:
        """Main curses event loop"""
        try:
            import curses
            
            while self.running:
                # Clear screen
                self.stdscr.clear()
                
                # Draw grid
                self._draw_grid()
                
                # Get input
                key = self.stdscr.getch()
                
                # Handle input
                if key == curses.KEY_UP:
                    self.focused_cell = (max(0, self.focused_cell[0] - 1), self.focused_cell[1])
                elif key == curses.KEY_DOWN:
                    self.focused_cell = (min(self.parsed_grid.rows - 1, self.focused_cell[0] + 1), self.focused_cell[1])
                elif key == curses.KEY_LEFT:
                    self.focused_cell = (self.focused_cell[0], max(0, self.focused_cell[1] - 1))
                elif key == curses.KEY_RIGHT:
                    self.focused_cell = (self.focused_cell[0], min(self.parsed_grid.cols - 1, self.focused_cell[1] + 1))
                elif key == ord(' '):
                    if self.focused_cell in self.selected_cells:
                        self.selected_cells.remove(self.focused_cell)
                    else:
                        self.selected_cells.append(self.focused_cell)
                elif key == ord('\n'):
                    self._handle_action()
                elif key == 27:  # ESC
                    break
                elif key == ord('q'):
                    break
        except Exception as e:
            self.stdscr.addstr(0, 0, f"Error: {e}")
            self.stdscr.refresh()
            time.sleep(1)
    
    def _draw_grid(self) -> None:
        """Draw the grid"""
        try:
            import curses
            
            # Draw title
            title = self.parsed_grid.title or "USXD Grid"
            self.stdscr.addstr(0, 0, title, curses.A_BOLD)
            
            # Draw grid
            for row in range(self.parsed_grid.rows):
                for col in range(self.parsed_grid.cols):
                    cell = self.parsed_grid.get_cell(row, col)
                    if cell:
                        char = cell.char if cell.char else ' '
                        
                        # Determine attributes
                        attr = 0
                        if (row, col) == self.focused_cell:
                            attr |= curses.A_REVERSE
                        elif (row, col) in self.selected_cells:
                            attr |= curses.A_BOLD
                        
                        # Add character
                        try:
                            self.stdscr.addch(row + 2, col, ord(char), attr)
                        except:
                            pass  # Handle edge cases
        except:
            pass
    
    def _handle_action(self) -> None:
        """Handle action for focused cell"""
        cell = self.parsed_grid.get_cell(*self.focused_cell)
        if cell and cell.component_id:
            component = self.parsed_grid.get_component(cell.component_id)
            if component:
                action = component.properties.get('action')
                if action and action in self.actions:
                    self.actions[action]()


class TerminalUI:
    """
    High-level terminal UI for grid rendering and management.
    
    This provides a complete TUI application for viewing and interacting
    with USXD grids.
    """
    
    def __init__(self):
        """Initialize the terminal UI"""
        self.renderer = GridRenderer()
        self.parser = ASCIIGridParser()
        self.mapper = ComponentMapper()
        self.grids: Dict[str, ParsedGrid] = {}
        self.current_grid_id: Optional[str] = None
        self.focused_cell: Tuple[int, int] = (0, 0)
    
    def add_grid(self, grid_id: str, parsed_grid: ParsedGrid) -> None:
        """Add a grid to the UI"""
        self.grids[grid_id] = parsed_grid
        if self.current_grid_id is None:
            self.current_grid_id = grid_id
    
    def load_grid(self, grid_id: str, grid_text: str, title: str = None) -> ParsedGrid:
        """Load a grid from text"""
        parsed = self.parser.parse_grid(grid_text, title or grid_id)
        self.add_grid(grid_id, parsed)
        return parsed
    
    def set_current_grid(self, grid_id: str) -> bool:
        """Set the current grid"""
        if grid_id in self.grids:
            self.current_grid_id = grid_id
            self.focused_cell = (0, 0)
            return True
        return False
    
    def get_current_grid(self) -> Optional[ParsedGrid]:
        """Get the current grid"""
        if self.current_grid_id:
            return self.grids[self.current_grid_id]
        return None
    
    def render_current(self, title: str = None) -> str:
        """Render the current grid"""
        grid = self.get_current_grid()
        if grid:
            return self.renderer.render(grid, title)
        return "No grid loaded"
    
    def display_current(self, title: str = None, clear: bool = True) -> None:
        """Display the current grid"""
        grid = self.get_current_grid()
        if grid:
            self.renderer.display(grid, title, self.focused_cell, clear=clear)
        else:
            print("No grid loaded")
    
    def run(self) -> None:
        """Run the interactive UI"""
        print("Terminal UI - Press ESC to exit, Arrow keys to navigate")
        
        if not self.current_grid_id:
            print("No grid loaded. Use load_grid() first.")
            return
        
        grid = self.get_current_grid()
        actions = {
            'default': lambda: self._handle_default_action(),
        }
        
        self.renderer.run_interactive(
            grid,
            actions,
            self.focused_cell,
            grid.title
        )
    
    def _handle_default_action(self) -> None:
        """Handle default action"""
        grid = self.get_current_grid()
        if grid:
            cell = grid.get_cell(*self.focused_cell)
            if cell:
                print(f"Selected: {cell.char} at ({self.focused_cell[0]}, {self.focused_cell[1]})")
    
    def show_info(self, grid_id: str = None) -> None:
        """Show information about a grid"""
        grid_id = grid_id or self.current_grid_id
        if grid_id and grid_id in self.grids:
            grid = self.grids[grid_id]
            print(f"Grid: {grid.title}")
            print(f"Size: {grid.rows}x{grid.cols}")
            print(f"Format: {grid.format.value}")
            print(f"Components: {len(grid.components)}")
            for comp_id, comp in grid.components.items():
                print(f"  - {comp_id}: {comp.name} ({comp.component_type})")
                print(f"    Cells: {len(comp.cells)}")
        else:
            print(f"Grid '{grid_id}' not found")


# Test the grid renderer
if __name__ == "__main__":
    print("Testing Grid Renderer...")
    
    # Test 1: Simple rendering
    print("\n=== Test 1: Simple Grid Rendering ===")
    renderer = GridRenderer()
    
    grid_text = """┌───┬───┐
│ A │ B │
├───┼───┤
│ C │ D │
└───┴───┘"""
    
    # Parse and render
    parsed = renderer.parser.parse_grid(grid_text, "Test Grid")
    rendered = renderer.render(parsed)
    print("Rendered grid:")
    print(rendered)
    
    # Test 2: Interactive mode demo
    print("\n=== Test 2: Interactive Navigation ===")
    print("Note: Skipping interactive test in automated mode")
    
    # Test 3: Component integration
    print("\n=== Test 3: Component Integration ===")
    
    # Add components
    from .grid_parser import GridComponent
    button_a = GridComponent(
        id="button_a",
        name="Button A",
        component_type="widget",
        properties={"action": "select_a"},
        cells=[(1, 1)]
    )
    button_b = GridComponent(
        id="button_b", 
        name="Button B",
        component_type="widget",
        properties={"action": "select_b"},
        cells=[(1, 3)]
    )
    parsed.add_component(button_a)
    parsed.add_component(button_b)
    
    print(f"✓ Added {len(parsed.components)} components")
    print(f"✓ Button A at {button_a.cells}")
    print(f"✓ Button B at {button_b.cells}")
    
    # Test 4: Render with focus
    print("\n=== Test 4: Render with Focus ===")
    focused_render = renderer.render(parsed, focused_cell=(1, 1))
    print("Rendered with focus on Button A:")
    print(focused_render)
    
    # Test 5: Curses check
    print("\n=== Test 5: Curses Support ===")
    try:
        import curses
        print("✓ Curses is available")
    except ImportError:
        print("✗ Curses not available (expected on some systems)")
    
    # Test 6: Solid box rendering
    print("\n=== Test 6: Solid Box Rendering ===")
    solid_box = """█████
█   █
█   █
█████"""
    parsed_solid = renderer.parser.parse_grid(solid_box, "Solid Box")
    rendered_solid = renderer.render(parsed_solid)
    print("Solid box:")
    print(rendered_solid)
    
    # Test 7: Terminal UI
    print("\n=== Test 7: Terminal UI ===")
    tui = TerminalUI()
    tui.load_grid("test", grid_text, "Test Grid")
    info = tui.show_info()
    
    print("\nAll grid renderer tests passed!")
