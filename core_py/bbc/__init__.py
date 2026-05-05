# BBC BASIC Module for uCode1
#
# This module provides BBC BASIC integration for the uDos ecosystem.
# It includes a Python-based BBC BASIC interpreter and integration with
# Matrix Brandy (C-based BBC BASIC interpreter).

__version__ = "0.1.0"
__author__ = "uDos Development Team"
__license__ = "MIT"

# BBC BASIC Core
from .interpreter import BBCBasicInterpreter, BBCBasicState, BBCBasicError
from .vdu import VDUDriver, VDUHandler, VDUQueue
from .memory import BBCMemory, BBCMemoryMap

# uCode1 LENS/SKIN/MCP/Spool Extensions
from .lens import LENSEngine, LENSEvent, LENSSnapshot, create_lens_engine
from .skin import SkinEngine, SkinDefinition, BUILTIN_SKINS, create_skin_engine
from .mcp_bridge import MCPBridge, MCPCommand, MCPCommandType, MCPResponse, create_mcp_bridge
from .spool_bridge import SpoolBridge, SpoolEnvelope, SpoolHeader, create_spool_bridge
from .lens_skin_mcp import LensSkinMCP, create_lens_skin_mcp

# Brandy Integration
try:
    from .brandy import BrandyBridge, BrandyInterpreter
    BRANDY_AVAILABLE = True
except ImportError:
    BRANDY_AVAILABLE = False
    BrandyBridge = None
    BrandyInterpreter = None

# Exports
__all__ = [
    # Core interpreter
    "BBCBasicInterpreter",
    "BBCBasicState",
    "BBCBasicError",
    # VDU
    "VDUDriver",
    "VDUHandler",
    "VDUQueue",
    # Memory
    "BBCMemory",
    "BBCMemoryMap",
    # LENS
    "LENSEngine",
    "LENSEvent",
    "LENSSnapshot",
    "create_lens_engine",
    # SKIN
    "SkinEngine",
    "SkinDefinition",
    "BUILTIN_SKINS",
    "create_skin_engine",
    # MCP
    "MCPBridge",
    "MCPCommand",
    "MCPCommandType",
    "MCPResponse",
    "create_mcp_bridge",
    # Spool
    "SpoolBridge",
    "SpoolEnvelope",
    "SpoolHeader",
    "create_spool_bridge",
    # Unified
    "LensSkinMCP",
    "create_lens_skin_mcp",
    # Brandy
    "BRANDY_AVAILABLE",
    "BrandyBridge",
    "BrandyInterpreter",
]
