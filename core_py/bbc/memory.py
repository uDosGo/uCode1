"""
BBC Micro Memory Map

This module implements the memory layout of the BBC Microcomputer
for use with the BBC BASIC interpreter.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import struct
import array


# BBC Micro Memory Map (6502-based)
# 0x0000 - 0x7FFF: RAM (32KB standard, up to 64KB with Sideways RAM)
# 0x8000 - 0xBFFF: ROM (16KB OS ROM)
# 0xC000 - 0xFFFF: ROM (16KB BASIC ROM)

DEFAULT_RAM_SIZE = 32 * 1024  # 32KB
MAX_RAM_SIZE = 64 * 1024  # 64KB
OS_ROM_START = 0x8000
OS_ROM_SIZE = 16 * 1024
BASIC_ROM_START = 0xC000
BASIC_ROM_SIZE = 16 * 1024

# Key BBC Micro addresses
ADDRESS_KEYBOARD = 0xFE40  # Keyboard input (via OS)
ADDRESS_SCREEN_START = 0x3000  # Default screen memory start
ADDRESS_ZERO_PAGE = 0x0000  # Zero page (6502 special)
ADDRESS_STACK = 0x0100  # Stack starts at 0x0100

# OS Workspace
txtptr = 0xF2  # Text pointer
varTop = 0xF4  # Top of variables
progTop = 0xF6  # Top of program
ern = 0xF0  # Error number
err = 0xF2  # Error message pointer


@dataclass
class BBCMemoryMap:
    """
    Memory map for BBC Micro emulation.
    
    This defines the memory layout and key addresses used by BBC BASIC.
    """
    
    # Memory regions
    ram_start: int = 0x0000
    ram_size: int = DEFAULT_RAM_SIZE
    rom_start: int = 0x8000
    rom_size: int = 32 * 1024
    
    # Key addresses
    zero_page: int = ADDRESS_ZERO_PAGE
    stack: int = ADDRESS_STACK
    screen_start: int = ADDRESS_SCREEN_START
    keyboard: int = ADDRESS_KEYBOARD
    
    # OS workspace addresses
    txtptr_addr: int = 0xF2
    var_top_addr: int = 0xF4
    prog_top_addr: int = 0xF6
    ern_addr: int = 0xF0
    err_addr: int = 0xF2
    
    @property
    def ram_end(self) -> int:
        """End of RAM"""
        return self.ram_start + self.ram_size
    
    @property
    def rom_end(self) -> int:
        """End of ROM"""
        return self.rom_start + self.rom_size


class BBCMemory:
    """
    BBC Micro memory implementation.
    
    This class provides read/write access to emulated BBC Micro memory,
    including RAM and ROM regions.
    """
    
    def __init__(self, ram_size: int = DEFAULT_RAM_SIZE):
        """Initialize BBC memory"""
        self.ram_size = ram_size
        self.ram = bytearray(ram_size)
        self.rom = bytearray(OS_ROM_SIZE + BASIC_ROM_SIZE)
        self.memory_map = BBCMemoryMap(ram_size=ram_size)
        
        # Initialize RAM to 0
        self.ram = bytearray(ram_size)
        
        # Initialize OS ROM with basic stubs
        self._init_os_rom()
        
        # Initialize BASIC ROM with basic stubs
        self._init_basic_rom()
    
    def _init_os_rom(self):
        """Initialize OS ROM with basic stubs"""
        # For now, just create empty ROM
        # In a full implementation, this would contain the BBC Micro OS
        self.rom[:OS_ROM_SIZE] = bytearray(OS_ROM_SIZE)
    
    def _init_basic_rom(self):
        """Initialize BASIC ROM with basic stubs"""
        # For now, just create empty ROM
        # In a full implementation, this would contain BBC BASIC ROM
        self.rom[OS_ROM_SIZE:OS_ROM_SIZE + BASIC_ROM_SIZE] = bytearray(BASIC_ROM_SIZE)
    
    def read_byte(self, address: int) -> int:
        """Read a byte from memory"""
        # Check if address is in RAM
        if 0 <= address < self.ram_size:
            return self.ram[address]
        
        # Check if address is in ROM
        if OS_ROM_START <= address < self.memory_map.rom_end:
            offset = address - OS_ROM_START
            if offset < len(self.rom):
                return self.rom[offset]
        
        # Invalid address
        raise MemoryError(f"Address {hex(address)} out of range")
    
    def write_byte(self, address: int, value: int) -> None:
        """Write a byte to memory"""
        value = value & 0xFF  # Ensure 8-bit value
        
        # Only allow writes to RAM
        if 0 <= address < self.ram_size:
            self.ram[address] = value
        else:
            raise MemoryError(f"Cannot write to address {hex(address)}")
    
    def read_word(self, address: int, little_endian: bool = True) -> int:
        """Read a 16-bit word from memory"""
        low = self.read_byte(address)
        high = self.read_byte(address + 1)
        
        if little_endian:
            return (high << 8) | low
        else:
            return (low << 8) | high
    
    def write_word(self, address: int, value: int, little_endian: bool = True) -> None:
        """Write a 16-bit word to memory"""
        value = value & 0xFFFF  # Ensure 16-bit value
        
        low = value & 0xFF
        high = (value >> 8) & 0xFF
        
        if little_endian:
            self.write_byte(address, low)
            self.write_byte(address + 1, high)
        else:
            self.write_byte(address, high)
            self.write_byte(address + 1, low)
    
    def read_string(self, address: int, length: int = 256) -> str:
        """Read a null-terminated string from memory"""
        chars = []
        for i in range(length):
            byte = self.read_byte(address + i)
            if byte == 0:
                break
            chars.append(chr(byte))
        return ''.join(chars)
    
    def write_string(self, address: int, text: str, max_length: int = 256) -> int:
        """Write a string to memory, returns bytes written"""
        bytes_written = 0
        for i, char in enumerate(text):
            if i >= max_length - 1:
                break
            self.write_byte(address + i, ord(char))
            bytes_written += 1
        
        # Null-terminate
        if bytes_written < max_length:
            self.write_byte(address + bytes_written, 0)
        
        return bytes_written
    
    def copy_memory(self, dest: int, src: int, length: int) -> None:
        """Copy memory from one location to another"""
        # Read from source
        data = bytearray(length)
        for i in range(length):
            data[i] = self.read_byte(src + i)
        
        # Write to destination
        for i in range(length):
            self.write_byte(dest + i, data[i])
    
    def fill_memory(self, address: int, value: int, length: int) -> None:
        """Fill memory with a value"""
        value = value & 0xFF
        for i in range(length):
            self.write_byte(address + i, value)
    
    def get_os_workspace(self) -> Dict[str, int]:
        """Get OS workspace values"""
        return {
            'txtptr': self.read_word(self.memory_map.txtptr_addr),
            'varTop': self.read_word(self.memory_map.var_top_addr),
            'progTop': self.read_word(self.memory_map.prog_top_addr),
            'ern': self.read_byte(self.memory_map.ern_addr),
        }
    
    def set_os_workspace(self, values: Dict[str, int]) -> None:
        """Set OS workspace values"""
        if 'txtptr' in values:
            self.write_word(self.memory_map.txtptr_addr, values['txtptr'])
        if 'varTop' in values:
            self.write_word(self.memory_map.var_top_addr, values['varTop'])
        if 'progTop' in values:
            self.write_word(self.memory_map.prog_top_addr, values['progTop'])
        if 'ern' in values:
            self.write_byte(self.memory_map.ern_addr, values['ern'])
    
    def load_rom(self, os_rom: bytes, basic_rom: bytes) -> None:
        """Load ROM images"""
        if len(os_rom) <= OS_ROM_SIZE:
            self.rom[:len(os_rom)] = os_rom
        if len(basic_rom) <= BASIC_ROM_SIZE:
            self.rom[OS_ROM_START - OS_ROM_START:OS_ROM_START - OS_ROM_START + len(basic_rom)] = basic_rom
    
    def save_state(self) -> Dict[str, Any]:
        """Save memory state"""
        return {
            'ram': list(self.ram),
            'rom': list(self.rom),
            'ram_size': self.ram_size,
        }
    
    def restore_state(self, state: Dict[str, Any]) -> None:
        """Restore memory state"""
        self.ram_size = state.get('ram_size', DEFAULT_RAM_SIZE)
        self.ram = bytearray(state.get('ram', [0] * self.ram_size))
        self.rom = bytearray(state.get('rom', [0] * (OS_ROM_SIZE + BASIC_ROM_SIZE)))
    
    def reset(self) -> None:
        """Reset memory to initial state"""
        self.ram = bytearray(self.ram_size)
        self._init_os_rom()
        self._init_basic_rom()


class BBCMemoryView:
    """
    Read-only view of BBC memory for debugging.
    """
    
    def __init__(self, memory: BBCMemory):
        self.memory = memory
    
    def hex_dump(self, start: int, length: int = 256) -> str:
        """Generate hex dump of memory"""
        lines = []
        for offset in range(0, length, 16):
            addr = start + offset
            hex_part = ' '.join(f'{self.memory.read_byte(addr + i):02X}' for i in range(16))
            ascii_part = ''.join(
                chr(self.memory.read_byte(addr + i)) if 32 <= self.memory.read_byte(addr + i) < 127 else '.'
                for i in range(16)
            )
            lines.append(f'{addr:04X}: {hex_part:48s} {ascii_part}')
            if offset + 16 >= length:
                break
        return '\n'.join(lines)
    
    def dump_screen(self, start: int = ADDRESS_SCREEN_START, rows: int = 25, cols: int = 80) -> str:
        """Dump screen memory as text"""
        lines = []
        for row in range(rows):
            line_chars = []
            for col in range(cols):
                addr = start + row * cols + col
                char_code = self.memory.read_byte(addr)
                # BBC Micro screen memory uses character codes withAddr high bit for color/flash
                char = chr(char_code & 0x7F)
                line_chars.append(char)
            lines.append(''.join(line_chars))
        return '\n'.join(lines)


# Predefined BBC Character Set (for Mode 7 Teletext)
BBC_CHARACTER_SET = [
    ' ', '╚', '╝', '╜', '└', '╙', '┖', '┌', '┐', '┘', '┼', '┤', '├', '▚', '▌', '█',
    '▄', '▀', '▜', '▛', '▙', '♂', '♀', '♫', '♬', '♠', '♣', '♥', '♦', '◄', '►',
    '▲', '▼', ' ', '!', '"', '#', '£', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?',
    '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_',
    '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', '␠',
    '␡', '␍', '␌', '␋', '␊', '␉', '␟', '␐', '␎', '␏', '␑', '␓', '␔', '␕', '␖', '␗',
    '␙', '␛', '␜', '␝', '␞', '␟', '␠', '␡', '°', '±', '²', '·', '√', ' advancing', '½',
]


def get_bbc_char(char_code: int) -> str:
    """Get BBC character from code"""
    if 0 <= char_code < len(BBC_CHARACTER_SET):
        return BBC_CHARACTER_SET[char_code]
    return '?'
