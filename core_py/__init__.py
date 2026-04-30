# uCode1 Python Core
#
# This package contains the Python implementation of uCode1 core functionality,
# replacing the Rust core implementation as part of the downgrade plan.

__version__ = "0.1.0"
__author__ = "uDos Development Team"
__license__ = "MIT"

# Core modules
from . import (
    binder,  # Binder module implemented
    cell,  # Cell System with UDX addressing (NEW)
    feed,  # Feed event archiving to Cells (NEW)
    grid,  # Python grid-core (NEW)
    mcp_client,  # MCP client for uCode2 communication (NEW)
    mdx,  # MDX Runtime with Snack shortcode support (NEW)
    plugin,  # Plugin system (NEW)
    relic,  # Relic module implemented
    seed,  # Seed Pod — default data & location handling (NEW)
    snack,
    text,  # Python text/md tools (NEW)
    thinui,  # ThinUI integration module (NEW)
    usxd,  # USXD module implemented
)
from .binder.models import (
    Binder,
    BinderEntry,
    BinderMetadata,
    BinderRegistry,
    BinderResource,
)

# Grid System
from .grid import (
    Coordinate,
    CoordSystem,
    Grid,
    GridCell,
    GridRegion,
    GridSize,
)

# MCP Client
from .mcp_client import (
    McpClient,
    McpClientError,
    McpConnectionError,
    McpRequest,
    McpRequestType,
    McpResponse,
    McpTimeoutError,
    get_default_socket_path,
    socket_exists,
    test_connection,
)

# Plugin System
from .plugin import (
    PluginDiscovery,
    PluginLoader,
    PluginManifest,
    PluginMetadata,
    PluginRegistry,
    PluginWrapper,
)
from .plugin.exceptions import (
    PluginCompatibilityError,
    PluginDisabledError,
    PluginError,
    PluginLoadError,
    PluginNotFoundError,
)
from .relic.models import (
    Relic,
    RelicBinaryFormat,
    RelicMetadata,
    RelicRegistry,
    RelicResource,
)
from .snack.dependency import (
    DependencyResolver,
    resolve_snack_dependencies,
)
from .snack.engine import SnackEngine, execute_snack
from .snack.exceptions import CircularDependencyError, SnackExecutionError

# Export main types for convenience
from .snack.models import Snack, SnackInput, SnackOutput
from .snack.schema import validate_snack_schema
from .snack.validator import (
    validate_snack,
    validate_snack_file,
    validate_snack_resources,
)

# Text System
from .text import (
    Alignment,
    ANSIColor,
    ANSIStyle,
    TemplateEngine,
    TextFormatter,
    TextInjector,
    WrapMode,
)
from .text.exceptions import (
    FormattingError,
    InjectionError,
    MarkdownError,
    TextProcessingError,
)

# ThinUI Integration
from .thinui import (
    API_AVAILABLE,
    ThinUIComponentType,
    ThinUIGridBridge,
    ThinUIGridData,
    create_api_server,
    run_api_server,
)
from .thinui.formats import ThinUIColor, ThinUIComponent, ThinUIFormat, ThinUILayout
from .usxd.component_mapper import (
    ComponentMapper,
    ComponentMapping,
    ComponentType,
    ThinUIProperties,
)
from .usxd.grid_parser import (
    ASCIIGridParser,
    GridCell,
    GridComponent,
    GridFormat,
    ParsedGrid,
)
from .usxd.grid_renderer import ColorMode, GridRenderer, Style, TerminalUI
from .usxd.models import (
    USXDDocument,
    USXDFormat,
    USXDMetadata,
    USXDRegistry,
    USXDSection,
)

__all__ = [
    "snack",
    "relic",  # Relic module implemented
    "binder",  # Binder module implemented
    "usxd",    # USXD module implemented
    "plugin",  # Plugin system (NEW)
    "grid",    # Python grid-core (NEW)
    "Snack",
    "SnackInput",
    "SnackOutput",
    "SnackEngine",
    "execute_snack",
    "DependencyResolver",
    "resolve_snack_dependencies",
    "CircularDependencyError",
    "validate_snack",
    "validate_snack_file",
    "validate_snack_resources",
    "validate_snack_schema",
    "SnackExecutionError",
    "CircularDependencyError",
    "Relic",
    "RelicMetadata",
    "RelicResource",
    "RelicBinaryFormat",
    "RelicRegistry",
    "Binder",
    "BinderMetadata",
    "BinderEntry",
    "BinderResource",
    "BinderRegistry",
    "USXDDocument",
    "USXDMetadata",
    "USXDSection",
    "USXDRegistry",
    "USXDFormat",
    # Grid Parser
    "ASCIIGridParser",
    "ParsedGrid",
    "GridCell",
    "GridComponent",
    "GridFormat",
    # Component Mapper
    "ComponentMapper",
    "ComponentMapping",
    "ComponentType",
    "ThinUIProperties",
    # Grid Renderer
    "GridRenderer",
    "Style",
    "ColorMode",
    "TerminalUI",
    # ThinUI Integration
    "thinui",
    "ThinUIGridBridge",
    "ThinUIGridData",
    "ThinUILayout",
    "ThinUIComponent",
    "ThinUIComponentType",
    "ThinUIColor",
    "ThinUIFormat",
    "create_api_server",
    "run_api_server",
    "API_AVAILABLE",
    # Plugin System
    "plugin",
    # Grid System
    "grid",
    "Grid",
    "GridCell",
    "GridRegion",
    "GridSize",
    "Coordinate",
    "CoordSystem",
    "text",
    "mcp_client",
    # Text System
    "TextInjector",
    "TemplateEngine",
    "TextFormatter",
    "WrapMode",
    "Alignment",
    "ANSIColor",
    "ANSIStyle",
    "TextProcessingError",
    "InjectionError",
    "MarkdownError",
    "FormattingError",
    # MCP Client
    "McpClient",
    "McpClientError",
    "McpConnectionError",
    "McpTimeoutError",
    "McpRequest",
    "McpRequestType",
    "McpResponse",
    "get_default_socket_path",
    "socket_exists",
    "test_connection",
    # Plugin System
    "PluginDiscovery",
    "PluginRegistry",
    "PluginLoader",
    "PluginWrapper",
    "PluginMetadata",
    "PluginManifest",
    "PluginError",
    "PluginNotFoundError",
    "PluginLoadError",
    "PluginCompatibilityError",
    "PluginDisabledError",
]
