"""
VDU Driver for BBC BASIC

This module implements VDU (Visual Display Unit) output handling for BBC BASIC.
It captures VDU commands and converts them to various output formats including
ThinUI, teletext, and ASCII.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
import struct


class VDUCommandType(Enum):
    """Types of VDU commands"""
    TEXT = "text"           # Print text
    PLOT = "plot"           # Plot a point
    DRAW = "draw"           # Draw a line
    MOVE = "move"           # Move cursor
    COLOUR = "colour"       # Set color
    GCOL = "gcol"           # Set graphics color
    MODE = "mode"           # Set screen mode
    CLG = "clg"             # Clear graphics
    CLS = "cls"             # Clear screen
    TAB = "tab"             # Tab
    VTAB = "vtab"           # Vertical tab
    CURSOR_ON = "cursor_on" # Show cursor
    CURSOR_OFF = "cursor_off" # Hide cursor
    SOUND = "sound"         # Sound
    ENVELOPE = "envelope"  # Envelope
    ORIGIN = "origin"       # Set graphics origin
    WINDOW = "window"        # Set graphics window
    SCROLL = "scroll"       # Scroll screen
    UNKNOWN = "unknown"     # Unknown command


@dataclass
class VDUCommand:
    """Represents a VDU command"""
    command: int
    type: VDUCommandType
    args: List[int] = field(default_factory=list)
    text: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    color: Optional[int] = None
    raw_data: bytes = b''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'command': self.command,
            'type': self.type.value,
            'args': self.args,
            'text': self.text,
            'x': self.x,
            'y': self.y,
            'color': self.color,
        }


@dataclass
class VDUState:
    """Current VDU state"""
    mode: int = 0              # Current screen mode
    text_col: int = 0         # Current text column
    text_row: int = 0         # Current text row
    g_col: int = 0            # Current graphics column
    g_row: int = 0            # Current graphics row
    fg_color: int = 7         # Foreground color (white)
    bg_color: int = 0         # Background color (black)
    flash: bool = False       # Flash state
    cursor_on: bool = True    # Cursor visibility
    origin_x: int = 0         # Graphics origin X
    origin_y: int = 0         # Graphics origin Y
    window_left: int = 0      # Graphics window left
    window_right: int = 639   # Graphics window right
    window_top: int = 0       # Graphics window top
    window_bottom: int = 767  # Graphics window bottom
    screen_width: int = 80    # Screen width in characters
    screen_height: int = 32   # Screen height in characters
    
    def reset(self):
        """Reset to default state"""
        self.mode = 0
        self.text_col = 0
        self.text_row = 0
        self.g_col = 0
        self.g_row = 0
        self.fg_color = 7
        self.bg_color = 0
        self.flash = False
        self.cursor_on = True
        self.origin_x = 0
        self.origin_y = 0
        self.window_left = 0
        self.window_right = 639
        self.window_top = 0
        self.window_bottom = 767
        self.screen_width = 80
        self.screen_height = 32


class VDUQueue:
    """Queue for VDU commands"""
    
    def __init__(self):
        self._queue: List[VDUCommand] = []
        self._handlers: List[Callable[[VDUCommand], None]] = []
        self._state = VDUState()
        self._output: List[str] = []  # Text output buffer
        self._graphics: List[Dict[str, Any]] = []  # Graphics output buffer
        self._captured: List[VDUCommand] = []  # All captured commands
    
    def enqueue(self, command: VDUCommand) -> None:
        """Add a command to the queue"""
        self._queue.append(command)
        self._captured.append(command)
        
        # Process the command
        self._process_command(command)
        
        # Notify handlers
        for handler in self._handlers:
            handler(command)
    
    def _process_command(self, command: VDUCommand) -> None:
        """Process a VDU command"""
        # Update state based on command
        if command.type == VDUCommandType.MOVE:
            if len(command.args) >= 2:
                self._state.text_col = command.args[0]
                self._state.text_row = command.args[1]
        elif command.type == VDUCommandType.COLOUR:
            if command.args:
                self._state.fg_color = command.args[0] & 7
        elif command.type == VDUCommandType.GCOL:
            if command.args:
                self._state.fg_color = command.args[0]
        elif command.type == VDUCommandType.TEXT:
            # Move cursor after text
            if command.text:
                self._state.text_col += len(command.text)
        elif command.type == VDUCommandType.CLS:
            self._output.clear()
            self._graphics.clear()
            self._captured.clear()
            self._state.reset()
    
    def add_handler(self, handler: Callable[[VDUCommand], None]) -> None:
        """Add a command handler"""
        self._handlers.append(handler)
    
    def remove_handler(self, handler: Callable[[VDUCommand], None]) -> None:
        """Remove a command handler"""
        if handler in self._handlers:
            self._handlers.remove(handler)
    
    def get_state(self) -> VDUState:
        """Get current VDU state"""
        return self._state
    
    def get_output(self) -> str:
        """Get accumulated text output"""
        return ''.join(self._output)
    
    def get_graphics(self) -> List[Dict[str, Any]]:
        """Get accumulated graphics output"""
        return self._graphics
    
    def get_commands(self) -> List[VDUCommand]:
        """Get all captured commands"""
        return self._captured.copy()
    
    def clear(self) -> None:
        """Clear the queue and outputs"""
        self._queue.clear()
        self._output.clear()
        self._graphics.clear()
        self._captured.clear()
        self._state.reset()
    
    def to_ascii_grid(self, width: int = 80, height: int = 25) -> Dict[str, Any]:
        """
        Convert captured VDU output to ASCII grid format.
        
        Returns:
            Dict with 'rows', 'cols', 'cells' for ThinUI
        """
        # Create empty grid
        grid = {
            'rows': height,
            'cols': width,
            'cells': [],
            'title': 'BBC BASIC Output',
            'format': 'simple'
        }
        
        # Initialize cells
        for row in range(height):
            grid['cells'].append([])
            for col in range(width):
                grid['cells'][row].append({
                    'char': ' ',
                    'fgColor': '#000000',
                    'bgColor': '#FFFFFF',
                    'metadata': {}
                })
        
        # Process commands to fill grid
        for command in self._captured:
            self._process_vdu_to_grid(command, grid)
        
        return grid
    
    def _process_vdu_to_grid(self, command: VDUCommand, grid: Dict[str, Any]) -> None:
        """Process a VDU command into the grid"""
        if command.type == VDUCommandType.TEXT and command.text:
            row = self._state.text_row
            col = self._state.text_col
            
            for char in command.text:
                if row < grid['rows'] and col < grid['cols']:
                    grid['cells'][row][col] = {
                        'char': char,
                        'fgColor': ansi_from_bbc(command.color or self._state.fg_color),
                        'bgColor': ansi_from_bbc(self._state.bg_color),
                        'metadata': {'vdu': True}
                    }
                    col += 1
            
            self._state.text_col = col
        
        elif command.type == VDUCommandType.MOVE:
            if len(command.args) >= 2:
                self._state.text_col = command.args[0] % grid['cols']
                self._state.text_row = command.args[1] % grid['rows']
        
        elif command.type == VDUCommandType.COLOUR:
            if command.args:
                self._state.fg_color = command.args[0] & 7
        
        elif command.type == VDUCommandType.GCOL:
            if command.args:
                self._state.fg_color = command.args[0]
        
        elif command.type == VDUCommandType.CLS:
            for row in range(grid['rows']):
                for col in range(grid['cols']):
                    grid['cells'][row][col] = {
                        'char': ' ',
                        'fgColor': ansi_from_bbc(self._state.fg_color),
                        'bgColor': ansi_from_bbc(self._state.bg_color),
                        'metadata': {}
                    }
            self._state.text_col = 0
            self._state.text_row = 0
    
    def to_thinui_format(self) -> Dict[str, Any]:
        """Convert to ThinUI format"""
        grid = self.to_ascii_grid()
        return {
            **grid,
            'components': [],
            'layout': {
                'type': 'bbc-basic-output',
                'mode': self._state.mode
            }
        }


class VDUHandler:
    """Handler for VDU commands with output routing"""
    
    def __init__(self):
        self.queue = VDUQueue()
        self._output_callbacks: List[Callable[[str], None]] = []
        self._graphics_callbacks: List[Callable[[Dict[str, Any]], None]] = []
    
    def write(self, byte: int) -> None:
        """Write a single byte to VDU"""
        self.process_byte(byte)
    
    def write_bytes(self, data: bytes) -> None:
        """Write multiple bytes to VDU"""
        for byte in data:
            self.write(byte)
    
    def process_byte(self, byte: int) -> None:
        """Process a single VDU byte"""
        if byte < 32:
            # Control character
            self._process_control(byte)
        else:
            # Text character
            command = VDUCommand(
                command=byte,
                type=VDUCommandType.TEXT,
                text=chr(byte),
                x=self.queue._state.text_col,
                y=self.queue._state.text_row,
                color=self.queue._state.fg_color
            )
            self.queue.enqueue(command)
            self._notify_text_output(chr(byte))
    
    def _process_control(self, code: int) -> None:
        """Process a VDU control code"""
        # Control codes (0-31)
        if code == 7:  # BEL
            pass  # Bell
        elif code == 8:  # BS (Backspace)
            self.queue._state.text_col = max(0, self.queue._state.text_col - 1)
        elif code == 9:  # TAB
            self.queue._state.text_col = (self.queue._state.text_col + 8) & ~7
        elif code == 10:  # LF (Line Feed)
            self._newline()
        elif code == 11:  # VT (Vertical Tab)
            self.queue._state.text_row += 1
        elif code == 12:  # FF (Form Feed) - Clear screen
            command = VDUCommand(
                command=code,
                type=VDUCommandType.CLS
            )
            self.queue.enqueue(command)
        elif code == 13:  # CR (Carriage Return)
            self.queue._state.text_col = 0
        elif code == 14:  # SO (Shift Out)
            pass
        elif code == 15:  # SI (Shift In)
            pass
        elif code == 16:  # DLE
            pass
        elif code == 17:  # DC1 (often XON)
            pass
        elif code == 18:  # DC2
            pass
        elif code == 19:  # DC3 (often XOFF)
            pass
        elif code == 20:  # DC4
            pass
        elif code == 21:  # NAK
            pass
        elif code == 22:  # SYN
            pass
        elif code == 23:  # ETB
            pass
        elif code == 24:  # CAN
            pass
        elif code == 25:  # EM
            pass
        elif code == 26:  # SUB
            pass
        elif code == 27:  # ESC - Start of VDU sequence
            self._process_escape_sequence()
        elif code == 28:  # FS
            pass
        elif code == 29:  # GS
            pass
        elif code == 30:  # RS
            pass
        elif code == 31:  # US
            pass
    
    def _newline(self) -> None:
        """Process newline"""
        self.queue._state.text_row += 1
        self.queue._state.text_col = 0
        
        # Scroll if needed
        if self.queue._state.text_row >= self.queue._state.screen_height:
            self.queue._state.text_row = self.queue._state.screen_height - 1
            # Should scroll here
    
    def _process_escape_sequence(self) -> None:
        """Process VDU escape sequence (not standard BBC BASIC)"""
        # BBC BASIC doesn't use ESC for VDU, it uses direct VDU codes
        # This is just for ANSI compatibility
        pass
    
    def vdu(self, code: int, *args: int) -> None:
        """
        Execute a VDU command directly.
        
        This is the primary way BBC BASIC sends VDU commands.
        Code 0-31 are control codes, 32-255 are printing characters.
        codes 128-255 with bits 6-7 set are extended commands.
        """
        # Check if it's a multi-byte command
        if code >= 128:
            # Extended command
            self._process_extended_vdu(code, args)
        else:
            # Standard command
            self.process_byte(code)
    
    def _process_extended_vdu(self, code: int, args: List[int]) -> None:
        """Process extended VDU command (code >= 128)"""
        # Extract command number (bits 0-5)
        cmd = code & 63
        
        # Common extended VDU commands
        if cmd == 0:  # PLOT
            if len(args) >= 2:
                x, y = args[0], args[1]
                command = VDUCommand(
                    command=code,
                    type=VDUCommandType.PLOT,
                    args=[x, y],
                    x=x, y=y,
                    color=self.queue._state.fg_color
                )
                self.queue.enqueue(command)
        
        elif cmd == 1:  # Unplot
            pass
        
        elif cmd == 4:  # DRAW
            if len(args) >= 2:
                x, y = args[0], args[1]
                command = VDUCommand(
                    command=code,
                    type=VDUCommandType.DRAW,
                    args=[x, y],
                    x=x, y=y,
                    color=self.queue._state.fg_color
                )
                self.queue.enqueue(command)
        
        elif cmd == 5:  # MOVE
            if len(args) >= 2:
                x, y = args[0], args[1]
                self.queue._state.g_col = x
                self.queue._state.g_row = y
                command = VDUCommand(
                    command=code,
                    type=VDUCommandType.MOVE,
                    args=[x, y],
                    x=x, y=y
                )
                self.queue.enqueue(command)
        
        elif cmd == 17:  # Define graphics color
            if args:
                self.queue._state.fg_color = args[0] & 15
        
        elif cmd == 18:  # Select text color
            if args:
                self.queue._state.fg_color = args[0] & 7
        
        elif cmd == 19:  # Select graphics color
            if args:
                self.queue._state.fg_color = args[0]
        
        elif cmd == 20:  # Reset colors
            self.queue._state.fg_color = 7
            self.queue._state.bg_color = 0
        
        elif cmd == 22:  # Select screen mode
            if args:
                self.queue._state.mode = args[0]
                self._setup_mode()
        
        elif cmd == 23:  # Define text window
            if len(args) >= 4:
                self.queue._state.text_col = args[0]
                self.queue._state.text_row = args[1]
                self.queue._state.screen_width = args[2]
                self.queue._state.screen_height = args[3]
        
        elif cmd == 24:  # Define graphics window
            if len(args) >= 4:
                self.queue._state.window_left = args[0]
                self.queue._state.window_right = args[1]
                self.queue._state.window_top = args[2]
                self.queue._state.window_bottom = args[3]
        
        elif cmd == 25:  # Set origin
            if len(args) >= 2:
                self.queue._state.origin_x = args[0]
                self.queue._state.origin_y = args[1]
        
        elif cmd == 28:  # Set paged mode
            pass
        
        elif cmd == 29:  # Set cursor position
            if len(args) >= 2:
                self.queue._state.text_col = args[1]
                self.queue._state.text_row = args[0]
        
        elif cmd == 30:  # Home cursor
            self.queue._state.text_col = 0
            self.queue._state.text_row = 0
        
        elif cmd == 31:  # Tab
            if args:
                self.queue._state.text_col = args[0]
        
        else:
            # Unknown command
            command = VDUCommand(
                command=code,
                type=VDUCommandType.UNKNOWN,
                args=list(args)
            )
            self.queue.enqueue(command)
    
    def _setup_mode(self) -> None:
        """Setup screen dimensions based on mode"""
        # BBC Micro screen modes
        if self.queue._state.mode == 0:  # Mode 0 - 684x560, 8 colors
            self.queue._state.screen_width = 80
            self.queue._state.screen_height = 32
        elif self.queue._state.mode == 1:  # Mode 1 - 320x256, 4 colors
            self.queue._state.screen_width = 40
            self.queue._state.screen_height = 32
        elif self.queue._state.mode == 2:  # Mode 2 - 640x512, 2 colors
            self.queue._state.screen_width = 80
            self.queue._state.screen_height = 32
        elif self.queue._state.mode == 3:  # Mode 3 - Text only
            self.queue._state.screen_width = 80
            self.queue._state.screen_height = 25
        elif self.queue._state.mode == 4:  # Mode 4 - 320x256, 16 colors
            self.queue._state.screen_width = 40
            self.queue._state.screen_height = 32
        elif self.queue._state.mode == 5:  # Mode 5 - 640x512, 4 colors
            self.queue._state.screen_width = 80
            self.queue._state.screen_height = 32
        elif self.queue._state.mode == 6:  # Mode 6 - Teletext
            self.queue._state.screen_width = 40
            self.queue._state.screen_height = 25
        elif self.queue._state.mode == 7:  # Mode 7 - Teletext with graphics
            self.queue._state.screen_width = 40
            self.queue._state.screen_height = 25
    
    def add_output_callback(self, callback: Callable[[str], None]) -> None:
        """Add callback for text output"""
        self._output_callbacks.append(callback)
    
    def add_graphics_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add callback for graphics output"""
        self._graphics_callbacks.append(callback)
    
    def _notify_text_output(self, text: str) -> None:
        """Notify output callbacks"""
        self.queue._output.append(text)
        for callback in self._output_callbacks:
            callback(text)
    
    def _notify_graphics_output(self, data: Dict[str, Any]) -> None:
        """Notify graphics callbacks"""
        self.queue._graphics.append(data)
        for callback in self._graphics_callbacks:
            callback(data)


class VDUDriver:
    """
    Main VDU driver that handles BBC BASIC VDU commands.
    
    This driver captures VDU output and can route it to various destinations
    including console, ThinUI, teletext, or file.
    """
    
    def __init__(self):
        self.handler = VDUHandler()
        self.output_buffer: List[str] = []
        self.graphics_buffer: List[Dict[str, Any]] = []
        self._thinui_bridge = None
    
    def write(self, data: Union[bytes, int]) -> None:
        """Write data to VDU"""
        if isinstance(data, bytes):
            self.handler.write_bytes(data)
            self.output_buffer.append(data.decode('latin-1'))
        else:
            self.handler.write(data)
            self.output_buffer.append(chr(data))
    
    def write_bytes(self, data: bytes) -> None:
        """Write bytes to VDU"""
        self.handler.write_bytes(data)
        self.output_buffer.append(data.decode('latin-1'))
    
    def vdu(self, code: int, *args: int) -> None:
        """Execute VDU command"""
        self.handler.vdu(code, *args)
    
    def get_output(self) -> str:
        """Get accumulated text output"""
        return ''.join(self.output_buffer)
    
    def get_thinui_grid(self) -> Dict[str, Any]:
        """Get output as ThinUI grid"""
        return self.handler.queue.to_thinui_format()
    
    def clear(self) -> None:
        """Clear all outputs"""
        self.output_buffer.clear()
        self.graphics_buffer.clear()
        self.handler.queue.clear()
    
    def set_thinui_bridge(self, bridge):
        """Set the ThinUIGridBridge for direct conversion"""
        self._thinui_bridge = bridge
    
    def to_parsed_grid(self):
        """Convert output to ParsedGrid using ThinUIGridBridge"""
        if self._thinui_bridge:
            grid_data = self.handler.queue.to_thinui_format()
            return self._thinui_bridge.parse_to_thinui(
                self.handler.get_output(),
                grid_data.get('title', 'BBC BASIC Output')
            )
        return None


# BBC BASIC color to ANSI color mapping
BBC_TO_ANSI = {
    0: 0,   # Black
    1: 4,   # Red
    2: 2,   # Green
    3: 6,   # Yellow
    4: 1,   # Blue
    5: 5,   # Magenta
    6: 3,   # Cyan
    7: 7,   # White
    8: 8,   # Flashing black / Bright black
    9: 12,  # Flashing red / Bright red
    10: 10, # Flashing green / Bright green
    11: 14, # Flashing yellow / Bright yellow
    12: 9,  # Flashing blue / Bright blue
    13: 13, # Flashing magenta / Bright magenta
    14: 11, # Flashing cyan / Bright cyan
    15: 15, # Flashing white / Bright white
}


def ansi_from_bbc(bbc_color: int) -> str:
    """Convert BBC color to ANSI color hex code"""
    # ANSI color codes 0-15
    ansi_colors = [
        '#000000', '#800000', '#008000', '#808000',
        '#000080', '#800080', '#008080', '#C0C0C0',
        '#808080', '#FF0000', '#00FF00', '#FFFF00',
        '#0000FF', '#FF00FF', '#00FFFF', '#FFFFFF'
    ]
    
    mapped = BBC_TO_ANSI.get(bbc_color % 16, 7)
    if mapped < len(ansi_colors):
        return ansi_colors[mapped]
    return '#FFFFFF'
