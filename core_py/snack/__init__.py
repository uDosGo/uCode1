# Snack System - Python Implementation
#
# This module provides the core functionality for managing and executing Snacks,
# which are atomic executable units in the uDos ecosystem.

from .models import Snack, SnackInput, SnackOutput, SnackLexicon, SnackVisuals, SnackChain, SnackResource
from .schema import SnackSchema, VALID_SNACK_KINDS, VALID_SNACK_RUNTIMES, validate_snack_schema
from .validator import validate_snack, validate_snack_file, validate_snack_resources
from .engine import SnackEngine, execute_snack
from .dependency import DependencyResolver, resolve_snack_dependencies
from .exceptions import SnackExecutionError, CircularDependencyError

__all__ = [
    "Snack",
    "SnackInput", 
    "SnackOutput",
    "SnackLexicon",
    "SnackVisuals",
    "SnackChain",
    "SnackResource",
    "SnackSchema",
    "VALID_SNACK_KINDS",
    "VALID_SNACK_RUNTIMES",
    "validate_snack_schema",
    "validate_snack",
    "validate_snack_file",
    "validate_snack_resources",
    "SnackEngine",
    "SnackExecutionError",
    "execute_snack",
    "DependencyResolver",
    "CircularDependencyError",
    "resolve_snack_dependencies"
]