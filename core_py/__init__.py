# uCode1 Python Core
#
# This package contains the Python implementation of uCode1 core functionality,
# replacing the Rust core implementation as part of the downgrade plan.

__version__ = "0.1.0"
__author__ = "uDos Development Team"
__license__ = "MIT"

# Core modules
from . import snack
from . import relic  # Relic module implemented
# from . import binder  # TODO: Implement binder module
# from . import usxd    # TODO: Implement usxd module

# Export main types for convenience
from .snack.models import Snack, SnackInput, SnackOutput
from .snack.engine import SnackEngine, execute_snack
from .snack.dependency import DependencyResolver, resolve_snack_dependencies, CircularDependencyError
from .snack.validator import validate_snack, validate_snack_file, validate_snack_resources
from .snack.schema import validate_snack_schema
from .snack.exceptions import SnackExecutionError, CircularDependencyError
from .relic.models import Relic, RelicMetadata, RelicResource, RelicBinaryFormat, RelicRegistry
# from .binder.models import Binder  # TODO: Implement
# from .usxd.models import UsxdDocument  # TODO: Implement

__all__ = [
    "snack",
    "relic",  # Relic module implemented
    # "binder",  # TODO: Implement
    # "usxd",    # TODO: Implement
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
    # "Binder",   # TODO: Implement
    # "UsxdDocument"  # TODO: Implement
]