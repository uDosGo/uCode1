"""
ACS Emulator — Adventure Construction Set Emulator for uCode1

Provides a complete emulation layer for running ACS (Adventure Construction
Set) games on the 6502 CPU. Integrates with the LENS/SKIN pipeline for
data extraction and UI transformation.

Architecture:
    ACS_Emulator
        ├── ACS_CPU (wraps m6502.Processor)
        ├── ACS_Memory (ACS-specific memory mapping)
        ├── ACS_DiskImage (.dsk file handler)
        ├── ACS_IO (keyboard input, display output)
        └── ACS_Debugger (debugging interface)
"""

from .acs_emulator import ACS_Emulator, ACS_EmulatorConfig
from .acs_memory import ACS_Memory, ACS_MemoryMapping
from .acs_disk import ACS_DiskImage, ACS_DiskFormat
from .acs_io import ACS_IO, ACS_DisplayMode
from .acs_debugger import ACS_Debugger

__all__ = [
    "ACS_Emulator", "ACS_EmulatorConfig",
    "ACS_Memory", "ACS_MemoryMapping",
    "ACS_DiskImage", "ACS_DiskFormat",
    "ACS_IO", "ACS_DisplayMode",
    "ACS_Debugger",
]
