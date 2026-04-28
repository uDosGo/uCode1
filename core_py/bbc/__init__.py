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
    "BBCBasicInterpreter",
    "BBCBasicState",
    "BBCBasicError",
    "VDUDriver",
    "VDUHandler",
    "VDUQueue",
    "BBCMemory",
    "BBCMemoryMap",
    "BRANDY_AVAILABLE",
    "BrandyBridge",
    "BrandyInterpreter",
]
