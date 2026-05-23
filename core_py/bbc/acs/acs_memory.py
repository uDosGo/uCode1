"""
ACS Memory — ACS-Specific Memory Mapping for 6502 Emulation

Provides a custom memory class that maps the 6502's flat 64KB address
space to the ACS game memory layout. Supports bank switching, I/O hooks,
and the read_byte/write_byte interface expected by the LENS layer.

Memory Layout (Apple II ACS):
    0x0000 - 0x00FF: Zero page / system variables
    0x0100 - 0x01FF: Stack
    0x0200 - 0x02FF: Player stats block
    0x0300 - 0x03FF: Current room data
    0x0400 - 0x04FF: Tile grid (15x15 = 225 bytes)
    0x0500 - 0x05FF: Creature data block
    0x0600 - 0x06FF: Inventory data block
    0x0700 - 0x07FF: Story flags
    0x0800 - 0x0FFF: Room descriptions (string data)
    0x1000 - 0x1FFF: Tile definitions
    0x2000 - 0x2FFF: Creature definitions
    0x3000 - 0x3FFF: Item definitions
    0x4000 - 0x4FFF: Room definitions
    0x5000 - 0x5FFF: Message strings
    0x6000 - 0x6FFF: Game logic / scripts
    0x7000 - 0x7FFF: Extended data
    0x8000 - 0xBFFF: ROM (game code)
    0xC000 - 0xCFFF: I/O space (keyboard, display, disk)
    0xD000 - 0xFFFF: ROM (system routines)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
import array


@dataclass
class ACS_MemoryMapping:
    """Describes a region of ACS memory"""
    name: str
    start: int
    end: int
    writable: bool = True
    description: str = ""
    bank_switched: bool = False
    current_bank: int = 0
    num_banks: int = 1


# Standard ACS memory regions
ACS_MEMORY_REGIONS: List[ACS_MemoryMapping] = [
    ACS_MemoryMapping("zero_page",     0x0000, 0x00FF, True,  "Zero page / system variables"),
    ACS_MemoryMapping("stack",         0x0100, 0x01FF, True,  "Stack"),
    ACS_MemoryMapping("player_stats",  0x0200, 0x02FF, True,  "Player stats block"),
    ACS_MemoryMapping("room_data",     0x0300, 0x03FF, True,  "Current room data"),
    ACS_MemoryMapping("tile_grid",     0x0400, 0x04FF, True,  "Tile grid (15x15)"),
    ACS_MemoryMapping("creature_data", 0x0500, 0x05FF, True,  "Creature data block"),
    ACS_MemoryMapping("inventory",     0x0600, 0x06FF, True,  "Inventory data block"),
    ACS_MemoryMapping("story_flags",   0x0700, 0x07FF, True,  "Story flags"),
    ACS_MemoryMapping("room_descs",    0x0800, 0x0FFF, True,  "Room descriptions"),
    ACS_MemoryMapping("tile_defs",     0x1000, 0x1FFF, True,  "Tile definitions"),
    ACS_MemoryMapping("creature_defs", 0x2000, 0x2FFF, True,  "Creature definitions"),
    ACS_MemoryMapping("item_defs",     0x3000, 0x3FFF, True,  "Item definitions"),
    ACS_MemoryMapping("room_defs",     0x4000, 0x4FFF, True,  "Room definitions"),
    ACS_MemoryMapping("messages",      0x5000, 0x5FFF, True,  "Message strings"),
    ACS_MemoryMapping("game_logic",    0x6000, 0x6FFF, True,  "Game logic / scripts"),
    ACS_MemoryMapping("extended",      0x7000, 0x7FFF, True,  "Extended data"),
    ACS_MemoryMapping("rom_code",      0x8000, 0xBFFF, False, "ROM (game code)"),
    ACS_MemoryMapping("io_space",      0xC000, 0xCFFF, True,  "I/O space"),
    ACS_MemoryMapping("rom_system",    0xD000, 0xFFFF, False, "ROM (system routines)"),
]


class ACS_Memory:
    """
    ACS-specific memory for 6502 emulation.

    Provides the full 64KB address space with:
    - RAM for 0x0000-0x7FFF (32KB)
    - ROM for 0x8000-0xBFFF and 0xD000-0xFFFF
    - I/O hooks at 0xC000-0xCFFF
    - read_byte/write_byte interface for LENS layer
    """

    def __init__(self, rom_size: int = 0x8000):
        """
        Initialize ACS memory.

        Args:
            rom_size: Size of ROM space (default 32KB for 0x8000-0xFFFF)
        """
        # 32KB RAM: 0x0000 - 0x7FFF
        self.ram = array.array('B', [0]) * 0x8000

        # 32KB ROM: 0x8000 - 0xFFFF
        self.rom = array.array('B', [0]) * rom_size

        # I/O hooks: address -> callback
        self._io_read_hooks: Dict[int, Callable[[int], int]] = {}
        self._io_write_hooks: Dict[int, Callable[[int, int], None]] = {}

        # Memory access tracking for LENS
        self._read_log: List[Tuple[int, int, float]] = []  # (address, value, timestamp)
        self._write_log: List[Tuple[int, int, float]] = []
        self._logging_enabled: bool = False
        self._max_log_entries: int = 10000

        # Bank switching state
        self._bank_registers: Dict[int, int] = {}
        self._banked_rom: Dict[int, array.array] = {}

        # Region lookup
        self._regions = ACS_MEMORY_REGIONS

    # ── 6502 Memory Interface (for m6502.Memory compatibility) ──────

    def __getitem__(self, address: int) -> int:
        """Read a byte from memory (6502 interface)"""
        return self.read_byte(address)

    def __setitem__(self, address: int, value: int) -> None:
        """Write a byte to memory (6502 interface)"""
        self.write_byte(address, value)

    # ── Read/Write Interface ───────────────────────────────────────

    def read_byte(self, address: int) -> int:
        """Read a byte from the specified address.

        This is the primary interface used by the LENS layer.
        """
        address = address & 0xFFFF

        # Check I/O read hooks first
        if address in self._io_read_hooks:
            value = self._io_read_hooks[address](address)
            if self._logging_enabled:
                self._log_read(address, value)
            return value

        # ROM space
        if address >= 0x8000:
            rom_offset = address - 0x8000
            if rom_offset < len(self.rom):
                value = self.rom[rom_offset]
            else:
                value = 0
        else:
            # RAM space
            value = self.ram[address]

        if self._logging_enabled:
            self._log_read(address, value)
        return value

    def write_byte(self, address: int, value: int) -> None:
        """Write a byte to the specified address."""
        address = address & 0xFFFF
        value = value & 0xFF

        # Check I/O write hooks first
        if address in self._io_write_hooks:
            self._io_write_hooks[address](address, value)
            if self._logging_enabled:
                self._log_write(address, value)
            return

        # ROM is read-only
        if address >= 0x8000:
            return

        # RAM space
        self.ram[address] = value

        if self._logging_enabled:
            self._log_write(address, value)

    # ── Bulk Read/Write ────────────────────────────────────────────

    def read_block(self, start: int, size: int) -> bytes:
        """Read a block of bytes from memory."""
        return bytes(self.read_byte(start + i) for i in range(size))

    def write_block(self, start: int, data: bytes) -> None:
        """Write a block of bytes to memory."""
        for i, b in enumerate(data):
            self.write_byte(start + i, b)

    # ── ROM Loading ────────────────────────────────────────────────

    def load_rom(self, data: bytes, offset: int = 0x8000) -> None:
        """Load ROM data into memory.

        Args:
            data: ROM binary data
            offset: Where to load it (default 0x8000 for game code)
        """
        if offset >= 0x8000:
            rom_offset = offset - 0x8000
            for i, b in enumerate(data):
                if rom_offset + i < len(self.rom):
                    self.rom[rom_offset + i] = b
        else:
            # Load into RAM
            for i, b in enumerate(data):
                if offset + i < 0x8000:
                    self.ram[offset + i] = b

    def load_rom_from_file(self, path: str, offset: int = 0x8000) -> int:
        """Load ROM data from a binary file.

        Args:
            path: Path to ROM file
            offset: Where to load it

        Returns:
            Number of bytes loaded
        """
        with open(path, 'rb') as f:
            data = f.read()
        self.load_rom(data, offset)
        return len(data)

    # ── I/O Hooks ──────────────────────────────────────────────────

    def set_io_read_hook(self, address: int, callback: Callable[[int], int]) -> None:
        """Set a callback for reads from an I/O address."""
        self._io_read_hooks[address] = callback

    def set_io_write_hook(self, address: int, callback: Callable[[int, int], None]) -> None:
        """Set a callback for writes to an I/O address."""
        self._io_write_hooks[address] = callback

    def remove_io_read_hook(self, address: int) -> None:
        """Remove an I/O read hook."""
        self._io_read_hooks.pop(address, None)

    def remove_io_write_hook(self, address: int) -> None:
        """Remove an I/O write hook."""
        self._io_write_hooks.pop(address, None)

    # ── Bank Switching ─────────────────────────────────────────────

    def add_banked_rom(self, bank_id: int, data: bytes) -> None:
        """Add a bank of ROM data for bank switching."""
        self._banked_rom[bank_id] = array.array('B', data)

    def switch_bank(self, bank_id: int, region_start: int = 0x8000) -> None:
        """Switch to a specific ROM bank."""
        if bank_id in self._banked_rom:
            bank_data = self._banked_rom[bank_id]
            rom_offset = region_start - 0x8000
            for i, b in enumerate(bank_data):
                if rom_offset + i < len(self.rom):
                    self.rom[rom_offset + i] = b
            self._bank_registers[region_start] = bank_id

    # ── Memory Access Logging ──────────────────────────────────────

    def enable_logging(self) -> None:
        """Enable memory access logging."""
        self._logging_enabled = True

    def disable_logging(self) -> None:
        """Disable memory access logging."""
        self._logging_enabled = False

    def clear_logs(self) -> None:
        """Clear memory access logs."""
        self._read_log.clear()
        self._write_log.clear()

    def get_read_log(self) -> List[Tuple[int, int, float]]:
        """Get the read access log."""
        return list(self._read_log)

    def get_write_log(self) -> List[Tuple[int, int, float]]:
        """Get the write access log."""
        return list(self._write_log)

    def _log_read(self, address: int, value: int) -> None:
        """Log a memory read."""
        import time
        self._read_log.append((address, value, time.time()))
        if len(self._read_log) > self._max_log_entries:
            self._read_log.pop(0)

    def _log_write(self, address: int, value: int) -> None:
        """Log a memory write."""
        import time
        self._write_log.append((address, value, time.time()))
        if len(self._write_log) > self._max_log_entries:
            self._write_log.pop(0)

    # ── Region Queries ─────────────────────────────────────────────

    def get_region_name(self, address: int) -> str:
        """Get the name of the memory region containing an address."""
        for region in self._regions:
            if region.start <= address <= region.end:
                return region.name
        return "unknown"

    def is_writable(self, address: int) -> bool:
        """Check if an address is writable."""
        for region in self._regions:
            if region.start <= address <= region.end:
                return region.writable
        return False

    def get_region(self, name: str) -> Optional[ACS_MemoryMapping]:
        """Get a memory region by name."""
        for region in self._regions:
            if region.name == name:
                return region
        return None

    # ── Snapshot / Restore ─────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        """Create a snapshot of the current memory state."""
        return {
            "ram": bytes(self.ram),
            "rom": bytes(self.rom),
            "bank_registers": dict(self._bank_registers),
        }

    def restore(self, snapshot: Dict[str, Any]) -> None:
        """Restore memory state from a snapshot."""
        if "ram" in snapshot:
            self.ram = array.array('B', snapshot["ram"])
        if "rom" in snapshot:
            self.rom = array.array('B', snapshot["rom"])
        if "bank_registers" in snapshot:
            self._bank_registers = dict(snapshot["bank_registers"])

    # ── Reset ──────────────────────────────────────────────────────

    def reset(self) -> None:
        """Reset memory to initial state."""
        self.ram = array.array('B', [0]) * 0x8000
        self._read_log.clear()
        self._write_log.clear()
        self._io_read_hooks.clear()
        self._io_write_hooks.clear()
