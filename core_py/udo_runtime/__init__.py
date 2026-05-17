"""
UDO Runtime — Universal Document Orchestrator

The UDO runtime provides system-layer services for the uDos ecosystem:
- Skills: Event-driven triggers and actions
- Tasks: Background job management
- Variables: Encrypted key-value store
- Agents: Autonomous task runners
- Workflows: Multi-step orchestration
- Publish: Content publishing to targets
- Vault: File system abstraction
- MCP: Model Context Protocol server management
- Checks: System health checks
- Exec: Command execution

This module is the Python reference implementation.
A Rust-native version will be built for Snackbar production deployment.
"""

__version__ = "0.1.0"
__author__ = "uDos Development Team"
__license__ = "MIT"

from .runtime import UDORuntime

__all__ = ["UDORuntime"]
