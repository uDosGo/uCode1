# uCode1 Python Core
#
# This package contains the Python implementation of uCode1 core functionality,
# replacing the Rust core implementation as part of the downgrade plan.

__version__ = "0.1.0"
__author__ = "uDos Development Team"
__license__ = "MIT"

# Core modules
from . import snack
# from . import relic  # TODO: Implement relic module
# from . import binder  # TODO: Implement binder module
# from . import usxd    # TODO: Implement usxd module

# Export main types for convenience
from .snack.models import Snack, SnackInput, SnackOutput
from .snack.engine import SnackEngine, execute_snack
from .snack.dependency import DependencyResolver, resolve_snack_dependencies, CircularDependencyError
# from .relic.models import Relic  # TODO: Implement
# from .binder.models import Binder  # TODO: Implement
# from .usxd.models import UsxdDocument  # TODO: Implement

__all__ = [
    "snack",
    # "relic",  # TODO: Implement
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
    # "Relic",   # TODO: Implement
    # "Binder",   # TODO: Implement
    # "UsxdDocument"  # TODO: Implement
]