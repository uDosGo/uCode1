# ThinUI Integration Module
# Bridge between Python core (uCode1) and ThinUI frontend

__version__ = "0.1.0"
__author__ = "uDos Development Team"
__license__ = "MIT"

# ThinUI Bridge
from .grid_bridge import ThinUIGridBridge, ThinUIGridData

# ThinUI Formats
from .formats import (
    ThinUIFormat, 
    ThinUIColor, 
    ThinUIComponent, 
    ThinUILayout,
    ThinUIComponentType
)

# ThinUI API Server (optional dependency on Flask)
try:
    from .api import create_api_server, run_api_server
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    create_api_server = None
    run_api_server = None

__all__ = [
    "ThinUIGridBridge",
    "ThinUIGridData",
    "ThinUIFormat",
    "ThinUIColor",
    "ThinUIComponent",
    "ThinUIComponentType",
    "ThinUILayout",
    "create_api_server",
    "run_api_server",
    "API_AVAILABLE",
]
