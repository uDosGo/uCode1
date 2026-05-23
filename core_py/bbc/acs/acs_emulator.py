"""
ACS Emulator — Main Emulator for Adventure Construction Set

Wires together the 6502 CPU, ACS memory, disk image handler, I/O system,
and debugger into a complete emulation platform. Provides the execution
loop, LENS integration hooks, and save/load functionality.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
import time
import logging

from m6502 import Processor as M6502_Processor
from .acs_memory import ACS_Memory
from .acs_disk import ACS_DiskImage, ACS_DiskFormat
from .acs_io import ACS_IO, ACS_DisplayMode
from .acs_debugger import ACS_Debugger, Breakpoint

logger = logging.getLogger(__name__)


@dataclass
class ACS_EmulatorConfig:
    """Configuration for the ACS emulator"""
    cpu_frequency: int = 1_000_000  # 1 MHz (Apple II)
    rom_size: int = 0x8000          # 32KB ROM
    ram_size: int = 0x8000          # 32KB RAM
    disk_format: str = "dos33"      # Default disk format
    auto_start: bool = True         # Auto-start after loading
    trace_enabled: bool = False     # Enable execution tracing
    log_memory: bool = False        # Enable memory access logging
    max_instructions: int = 0       # 0 = unlimited


class ACS_Emulator:
    """
    Complete ACS emulator.

    Wires together:
        - 6502 CPU (m6502.Processor)
        - ACS Memory (ACS_Memory)
        - Disk Image Handler (ACS_DiskImage)
        - I/O System (ACS_IO)
        - Debugger (ACS_Debugger)

    Provides the main execution loop and LENS integration hooks.
    """

    def __init__(self, config: Optional[ACS_EmulatorConfig] = None):
        """
        Initialize the ACS emulator.

        Args:
            config: Emulator configuration
        """
        self.config = config or ACS_EmulatorConfig()

        # Initialize subsystems
        self.memory = ACS_Memory(rom_size=self.config.rom_size)
        self.io = ACS_IO()
        self.disk = ACS_DiskImage(self.config.disk_format)
        self.debugger = ACS_Debugger()

        # Initialize 6502 CPU with our custom memory
        self.cpu = M6502_Processor(self.memory)

        # Wire I/O hooks into memory
        self._wire_io_hooks()

        # Wire debugger hooks
        self._wire_debugger_hooks()

        # Execution state
        self._running: bool = False
        self._paused: bool = False
        self._instruction_count: int = 0
        self._start_time: float = 0.0
        self._elapsed_time: float = 0.0

        # LENS integration hooks
        self._on_memory_write: Optional[Callable[[int, int], None]] = None
        self._on_instruction: Optional[Callable[[Dict[str, Any]], None]] = None

        # Memory logging
        if self.config.log_memory:
            self.memory.enable_logging()

        # Tracing
        if self.config.trace_enabled:
            self.debugger.enable_tracing()

    # ── Initialization ─────────────────────────────────────────────

    def _wire_io_hooks(self) -> None:
        """Wire I/O handlers into memory."""
        # Keyboard read (0xC000)
        kb_read = self.io.get_io_read_handler(0xC000)
        if kb_read:
            self.memory.set_io_read_hook(0xC000, lambda addr, r=kb_read: r())

        # Keyboard strobe (0xC010)
        kb_strobe = self.io.get_io_read_handler(0xC010)
        if kb_strobe:
            self.memory.set_io_read_hook(0xC010, lambda addr, r=kb_strobe: r())

        # Speaker toggle (0xC020)
        speaker = self.io.get_io_read_handler(0xC020)
        if speaker:
            self.memory.set_io_read_hook(0xC020, lambda addr, r=speaker: r())

        # Display mode switches (0xC050-0xC057)
        for addr in [0xC050, 0xC051, 0xC052, 0xC053, 0xC054, 0xC055, 0xC056, 0xC057]:
            handler = self.io.get_io_write_handler(addr)
            if handler:
                self.memory.set_io_write_hook(addr, lambda a, v, h=handler: h(v))

    def _wire_debugger_hooks(self) -> None:
        """Wire debugger hooks."""
        self.debugger.on_breakpoint_hit(self._on_breakpoint_hit)

    def _on_breakpoint_hit(self, address: int, bp: Breakpoint) -> None:
        """Handle a breakpoint hit."""
        logger.info(f"Breakpoint hit at 0x{address:04X}: {bp.description}")
        self._paused = True

    # ── ROM/Disk Loading ───────────────────────────────────────────

    def load_rom(self, data: bytes, offset: int = 0x8000) -> None:
        """Load ROM data into memory.

        Args:
            data: ROM binary data
            offset: Memory offset to load at
        """
        self.memory.load_rom(data, offset)

    def load_rom_from_file(self, path: str, offset: int = 0x8000) -> int:
        """Load ROM from a binary file.

        Args:
            path: Path to ROM file
            offset: Memory offset to load at

        Returns:
            Number of bytes loaded
        """
        return self.memory.load_rom_from_file(path, offset)

    def load_disk(self, path: str) -> int:
        """Load a disk image.

        Args:
            path: Path to .dsk file

        Returns:
            Number of bytes loaded
        """
        return self.disk.load(path)

    def load_disk_into_memory(self, start_track: int = 2,
                              start_sector: int = 0,
                              num_sectors: Optional[int] = None,
                              dest_address: int = 0x8000) -> int:
        """Load disk sectors into memory.

        Args:
            start_track: Starting track
            start_sector: Starting sector
            num_sectors: Number of sectors to load
            dest_address: Destination memory address

        Returns:
            Number of bytes loaded
        """
        return self.disk.load_into_memory(
            self.memory, start_track, start_sector,
            num_sectors, dest_address
        )

    # ── CPU State ──────────────────────────────────────────────────

    def get_cpu_state(self) -> Dict[str, Any]:
        """Get the current CPU register state."""
        return {
            "pc": self.cpu.program_counter,
            "sp": self.cpu.stack_pointer,
            "a": self.cpu.reg_a,
            "x": self.cpu.reg_x,
            "y": self.cpu.reg_y,
            "flags": {
                "c": self.cpu.flag_c,
                "z": self.cpu.flag_z,
                "i": self.cpu.flag_i,
                "d": self.cpu.flag_d,
                "b": self.cpu.flag_b,
                "v": self.cpu.flag_v,
                "n": self.cpu.flag_n,
            },
            "cycles": self.cpu.cycles,
        }

    def set_pc(self, address: int) -> None:
        """Set the program counter.

        Args:
            address: New PC value
        """
        self.cpu.program_counter = address & 0xFFFF

    # ── Execution ──────────────────────────────────────────────────

    def reset(self) -> None:
        """Reset the emulator."""
        self.cpu.reset()
        self.memory.reset()
        self.io.reset()
        self.debugger.reset()
        self._instruction_count = 0
        self._running = False
        self._paused = False

    def step(self) -> Dict[str, Any]:
        """Execute a single CPU instruction.

        Returns:
            CPU state after the instruction
        """
        # Check breakpoints
        bp = self.debugger.check_breakpoints(self.cpu.program_counter)
        if bp:
            self._paused = True

        if self._paused:
            return self.get_cpu_state()

        # Execute one instruction
        self.cpu.execute()

        # Record step
        state = self.get_cpu_state()
        self.debugger.record_step(state)
        self._instruction_count += 1

        # Notify LENS hook
        if self._on_instruction:
            self._on_instruction(state)

        return state

    def run(self, max_instructions: int = 0) -> int:
        """Run the emulator.

        Args:
            max_instructions: Maximum instructions to execute (0 = unlimited)

        Returns:
            Number of instructions executed
        """
        self._running = True
        self._paused = False
        self._start_time = time.time()
        limit = max_instructions or self.config.max_instructions
        executed = 0

        try:
            while self._running and not self._paused:
                self.step()
                executed += 1

                if limit and executed >= limit:
                    break

        except KeyboardInterrupt:
            logger.info("Execution interrupted by user")
        except Exception as e:
            logger.error(f"Execution error at PC=0x{self.cpu.program_counter:04X}: {e}")
            raise

        finally:
            self._running = False
            self._elapsed_time = time.time() - self._start_time

        return executed

    def run_until(self, address: int, max_instructions: int = 100000) -> int:
        """Run until PC reaches a specific address.

        Args:
            address: Target address
            max_instructions: Maximum instructions before timeout

        Returns:
            Number of instructions executed
        """
        bp = self.debugger.set_breakpoint(address, f"Run until 0x{address:04X}")
        try:
            return self.run(max_instructions)
        finally:
            self.debugger.remove_breakpoint(address)

    def pause(self) -> None:
        """Pause execution."""
        self._paused = True

    def stop(self) -> None:
        """Stop execution."""
        self._running = False
        self._paused = False

    # ── LENS Integration ───────────────────────────────────────────

    def on_memory_write(self, callback: Callable[[int, int], None]) -> None:
        """Register a callback for memory writes (LENS integration).

        Args:
            callback: Function called with (address, value) on each write
        """
        self._on_memory_write = callback

    def on_instruction(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback for each instruction (LENS integration).

        Args:
            callback: Function called with CPU state dict
        """
        self._on_instruction = callback

    def read_memory(self, address: int) -> int:
        """Read a byte from memory (LENS interface).

        Args:
            address: Memory address

        Returns:
            Byte value
        """
        return self.memory.read_byte(address)

    def read_memory_block(self, start: int, size: int) -> bytes:
        """Read a block of memory (LENS interface).

        Args:
            start: Starting address
            size: Number of bytes

        Returns:
            Block of bytes
        """
        return self.memory.read_block(start, size)

    def write_memory(self, address: int, value: int) -> None:
        """Write a byte to memory.

        Args:
            address: Memory address
            value: Byte value
        """
        self.memory.write_byte(address, value)

    # ── Save/Load State ────────────────────────────────────────────

    def save_state(self) -> Dict[str, Any]:
        """Save the full emulator state.

        Returns:
            Dictionary with complete state
        """
        return {
            "cpu": {
                "pc": self.cpu.program_counter,
                "sp": self.cpu.stack_pointer,
                "a": self.cpu.reg_a,
                "x": self.cpu.reg_x,
                "y": self.cpu.reg_y,
                "cycles": self.cpu.cycles,
            },
            "memory": self.memory.snapshot(),
            "io": {
                "display_text": self.io.get_display_text(),
                "display_mode": self.io.display.mode.name,
            },
            "instruction_count": self._instruction_count,
        }

    def restore_state(self, state: Dict[str, Any]) -> None:
        """Restore the emulator state.

        Args:
            state: State dictionary from save_state()
        """
        if "cpu" in state:
            cpu_state = state["cpu"]
            self.cpu.program_counter = cpu_state.get("pc", 0)
            self.cpu.stack_pointer = cpu_state.get("sp", 0)
            self.cpu.reg_a = cpu_state.get("a", 0)
            self.cpu.reg_x = cpu_state.get("x", 0)
            self.cpu.reg_y = cpu_state.get("y", 0)

        if "memory" in state:
            self.memory.restore(state["memory"])

        if "instruction_count" in state:
            self._instruction_count = state["instruction_count"]

    # ── Properties ─────────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        """Check if the emulator is running."""
        return self._running

    @property
    def is_paused(self) -> bool:
        """Check if the emulator is paused."""
        return self._paused

    @property
    def instruction_count(self) -> int:
        """Get the total instruction count."""
        return self._instruction_count

    @property
    def elapsed_time(self) -> float:
        """Get the elapsed execution time in seconds."""
        if self._running:
            return time.time() - self._start_time
        return self._elapsed_time

    @property
    def ips(self) -> float:
        """Get instructions per second."""
        elapsed = self.elapsed_time
        if elapsed > 0:
            return self._instruction_count / elapsed
        return 0.0

    def get_info(self) -> Dict[str, Any]:
        """Get emulator information."""
        return {
            "running": self._running,
            "paused": self._paused,
            "instructions": self._instruction_count,
            "elapsed": self.elapsed_time,
            "ips": self.ips,
            "cpu": self.get_cpu_state(),
            "disk": self.disk.get_info() if self.disk.is_loaded else None,
            "debugger": self.debugger.get_state(),
        }
