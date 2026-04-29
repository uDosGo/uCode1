"""
MCP Client for uCode1

This module provides a Python client for connecting to the uCode2 MCP server
via Unix domain sockets. The MCP server provides access to vault operations,
notes, intents, and other uCode2 functionality.

The default socket path is ~/.local/mcp.sock, aligned with the uCode2 specification.
"""

import json
import os
import socket
import typing
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class McpRequestType(Enum):
    """Enumeration of MCP request types supported by the uCode2 server."""
    LIST_NOTES = "ListNotes"
    READ_NOTE = "ReadNote"
    SEARCH_NOTES = "SearchNotes"
    CLASSIFY_INTENT = "ClassifyIntent"
    STATUS = "Status"
    PING = "Ping"
    SHUTDOWN = "Shutdown"
    # Vault operations
    VAULT_READ = "VaultRead"
    VAULT_WRITE = "VaultWrite"
    VAULT_LIST = "VaultList"
    VAULT_SEARCH = "VaultSearch"
    VAULT_DELETE = "VaultDelete"
    VAULT_METADATA = "VaultMetadata"
    VAULT_WATCH = "VaultWatch"


@dataclass
class McpRequest:
    """Represents an MCP request to be sent to the server."""
    request_type: McpRequestType
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for JSON serialization.
        
        The Rust server expects the variant name as the key (e.g., {"Ping": null})
        rather than {"type": "Ping"}.
        """
        result = {self.request_type.value: self.data if self.data else None}
        return result
    
    def to_json(self) -> str:
        """Convert request to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class McpResponse:
    """Represents a response from the MCP server."""
    raw_data: Dict[str, Any]
    
    @property
    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return "Error" not in self.raw_data
    
    @property
    def is_error(self) -> bool:
        """Check if the response indicates an error."""
        return not self.is_success
    
    @property
    def error_message(self) -> Optional[str]:
        """Get the error message if this is an error response."""
        if self.is_error:
            error_data = self.raw_data.get("Error", {})
            if isinstance(error_data, dict):
                return error_data.get("message", str(error_data))
            return str(error_data)
        return None
    
    @property
    def data(self) -> Optional[Dict[str, Any]]:
        """Get the data from a Success response."""
        success_data = self.raw_data.get("Success", {})
        if isinstance(success_data, dict):
            return success_data.get("data")
        return success_data if success_data else None
    
    @property
    def notes(self) -> List[str]:
        """Get the list of notes from a Notes response."""
        notes_data = self.raw_data.get("Notes", {})
        if isinstance(notes_data, dict):
            return notes_data.get("list", [])
        return notes_data if isinstance(notes_data, list) else []
    
    @property
    def note_content(self) -> Optional[Dict[str, str]]:
        """Get the note content from a NoteContent response."""
        return self.raw_data.get("NoteContent")
    
    @property
    def intent(self) -> Optional[Dict[str, Any]]:
        """Get the intent from an Intent response."""
        return self.raw_data.get("Intent")
    
    @property
    def status_info(self) -> Optional[Dict[str, str]]:
        """Get the status info from a StatusInfo response."""
        return self.raw_data.get("StatusInfo")
    
    @property
    def vault_content(self) -> Optional[Dict[str, str]]:
        """Get vault content from a VaultContent response."""
        return self.raw_data.get("VaultContent")
    
    @property
    def vault_list(self) -> Optional[Dict[str, List[str]]]:
        """Get vault list from a VaultList response."""
        return self.raw_data.get("VaultList")
    
    @property
    def vault_search_results(self) -> Optional[Dict[str, List[str]]]:
        """Get vault search results from a VaultSearchResults response."""
        return self.raw_data.get("VaultSearchResults")
    
    @property
    def vault_metadata(self) -> Optional[Dict[str, Any]]:
        """Get vault metadata from a VaultMetadata response."""
        return self.raw_data.get("VaultMetadata")


class McpClientError(Exception):
    """Exception raised when an MCP client error occurs."""
    pass


class McpConnectionError(McpClientError):
    """Exception raised when connection to MCP server fails."""
    pass


class McpTimeoutError(McpClientError):
    """Exception raised when MCP request times out."""
    pass


class McpClient:
    """
    MCP Client for connecting to uCode2's MCP server.
    
    This client communicates with the uCode2 MCP server via Unix domain sockets
    and provides a Python-friendly interface to vault operations, notes,
    intents, and other uCode2 functionality.
    
    Example usage:
    ```python
    client = McpClient(socket_path="~/.local/mcp.sock")
    
    # List all notes
    response = client.list_notes()
    for note in response.notes:
        print(note)
    
    # Read a specific note
    response = client.read_note("my-note")
    print(response.note_content)
    
    # Classify intent
    response = client.classify_intent("What is the weather today?")
    print(response.intent)
    
    client.close()
    ```
    """
    
    DEFAULT_SOCKET_PATH = "~/.local/mcp.sock"
    SOCKET_TIMEOUT = 30.0  # seconds
    
    def __init__(
        self,
        socket_path: Optional[Union[str, Path]] = None,
        timeout: float = SOCKET_TIMEOUT,
        auto_connect: bool = True
    ):
        """
        Initialize the MCP client.
        
        Args:
            socket_path: Path to the Unix domain socket. Defaults to ~/.local/mcp.sock
            timeout: Connection and request timeout in seconds
            auto_connect: Whether to connect immediately on initialization
        """
        if socket_path is None:
            socket_path = self.DEFAULT_SOCKET_PATH
        
        # Expand tilde and convert to Path
        socket_path = Path(str(socket_path)).expanduser()
        self.socket_path = socket_path
        self.timeout = timeout
        self._socket: Optional[socket.socket] = None
        
        if auto_connect:
            self.connect()
    
    def __del__(self):
        """Destructor - ensure connection is closed."""
        self.close()
    
    def connect(self) -> bool:
        """
        Connect to the MCP server.
        
        Returns:
            True if connection succeeded, False otherwise
        
        Raises:
            McpConnectionError: If connection fails
        """
        try:
            # Disconnect if already connected
            self.close()
            
            # Create Unix domain socket
            self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            
            # Connect to the server
            self._socket.connect(str(self.socket_path))
            
            return True
        except socket.error as e:
            self._socket = None
            raise McpConnectionError(
                f"Failed to connect to MCP server at {self.socket_path}: {e}"
            ) from e
    
    def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self._socket:
            try:
                self._socket.close()
            except socket.error:
                pass
            self._socket = None
    
    def close(self) -> None:
        """Alias for disconnect."""
        self.disconnect()
    
    @property
    def is_connected(self) -> bool:
        """Check if the client is currently connected."""
        return self._socket is not None
    
    def _send_request(self, request: McpRequest) -> McpResponse:
        """
        Send a request to the MCP server and return the response.
        
        Args:
            request: The MCP request to send
            
        Returns:
            The MCP response from the server
            
        Raises:
            McpConnectionError: If not connected or send fails
            McpTimeoutError: If request times out
        """
        # Reconnect for each request since server closes connection after each response
        if self.is_connected:
            self.close()
        
        try:
            self.connect()
            # Send request as JSON followed by newline
            request_json = request.to_json() + "\n"
            self._socket.sendall(request_json.encode('utf-8'))
            
            # Read response - MCP server sends one JSON response per request, terminated by newline
            response_lines = []
            buffer = ""
            
            while True:
                data = self._socket.recv(4096)
                if not data:
                    break
                buffer += data.decode('utf-8')
                # Check if we have a complete response (ends with newline)
                if buffer.endswith('\n'):
                    break
            
            # Parse response(s)
            responses = []
            for line in buffer.strip().split('\n'):
                line = line.strip()
                if line:
                    try:
                        responses.append(json.loads(line))
                    except json.JSONDecodeError:
                        # Skip invalid lines
                        pass
            
            # Return the last response (most complete)
            if responses:
                # If there's only one response, return it
                # If multiple, try to find the most complete one
                if len(responses) == 1:
                    return McpResponse(raw_data=responses[0])
                else:
                    # Return the last non-empty response
                    for resp in reversed(responses):
                        if resp:
                            return McpResponse(raw_data=resp)
            
            # If no valid response, return empty
            return McpResponse(raw_data={})
            
        except socket.timeout as e:
            raise McpTimeoutError(f"Request timed out: {e}") from e
        except socket.error as e:
            raise McpConnectionError(f"Socket error: {e}") from e
    
    # High-level API methods
    
    def list_notes(self) -> McpResponse:
        """List all notes in the vault."""
        request = McpRequest(request_type=McpRequestType.LIST_NOTES)
        return self._send_request(request)
    
    def read_note(self, name: str) -> McpResponse:
        """Read a specific note by name."""
        request = McpRequest(
            request_type=McpRequestType.READ_NOTE,
            data={"name": name}
        )
        return self._send_request(request)
    
    def search_notes(self, query: str) -> McpResponse:
        """Search for notes matching the query."""
        request = McpRequest(
            request_type=McpRequestType.SEARCH_NOTES,
            data={"query": query}
        )
        return self._send_request(request)
    
    def classify_intent(self, text: str) -> McpResponse:
        """Classify the intent of the given text."""
        request = McpRequest(
            request_type=McpRequestType.CLASSIFY_INTENT,
            data={"text": text}
        )
        return self._send_request(request)
    
    def status(self) -> McpResponse:
        """Get the status of the MCP server."""
        request = McpRequest(request_type=McpRequestType.STATUS)
        return self._send_request(request)
    
    def ping(self) -> McpResponse:
        """Send a ping request to check server availability."""
        request = McpRequest(request_type=McpRequestType.PING)
        return self._send_request(request)
    
    def shutdown(self) -> McpResponse:
        """Request server shutdown."""
        request = McpRequest(request_type=McpRequestType.SHUTDOWN)
        return self._send_request(request)
    
    # Vault operations
    
    def vault_read(self, path: str) -> McpResponse:
        """Read content from the vault at the specified path."""
        request = McpRequest(
            request_type=McpRequestType.VAULT_READ,
            data={"path": path}
        )
        return self._send_request(request)
    
    def vault_write(self, path: str, content: str) -> McpResponse:
        """Write content to the vault at the specified path."""
        request = McpRequest(
            request_type=McpRequestType.VAULT_WRITE,
            data={"path": path, "content": content}
        )
        return self._send_request(request)
    
    def vault_list(self, path: str) -> McpResponse:
        """List items at the specified vault path."""
        request = McpRequest(
            request_type=McpRequestType.VAULT_LIST,
            data={"path": path}
        )
        return self._send_request(request)
    
    def vault_search(self, query: str) -> McpResponse:
        """Search the vault for items matching the query."""
        request = McpRequest(
            request_type=McpRequestType.VAULT_SEARCH,
            data={"query": query}
        )
        return self._send_request(request)
    
    def vault_delete(self, path: str) -> McpResponse:
        """Delete an item from the vault at the specified path."""
        request = McpRequest(
            request_type=McpRequestType.VAULT_DELETE,
            data={"path": path}
        )
        return self._send_request(request)
    
    def vault_metadata(self, path: str) -> McpResponse:
        """Get metadata for an item in the vault."""
        request = McpRequest(
            request_type=McpRequestType.VAULT_METADATA,
            data={"path": path}
        )
        return self._send_request(request)
    
    def vault_watch(self, path: str) -> McpResponse:
        """Watch for changes at the specified vault path."""
        request = McpRequest(
            request_type=McpRequestType.VAULT_WATCH,
            data={"path": path}
        )
        return self._send_request(request)


def get_default_socket_path() -> Path:
    """Get the default MCP socket path."""
    return Path(McpClient.DEFAULT_SOCKET_PATH).expanduser()


def socket_exists() -> bool:
    """Check if the MCP server socket exists."""
    return get_default_socket_path().exists()


def test_connection() -> bool:
    """
    Test if the MCP server is available and responding.
    
    Returns:
        True if server is available, False otherwise
    """
    try:
        client = McpClient(auto_connect=True)
        response = client.ping()
        return response.is_success
    except (McpConnectionError, McpTimeoutError):
        return False


# Module exports
__all__ = [
    # Client and errors
    'McpClient',
    'McpClientError',
    'McpConnectionError',
    'McpTimeoutError',
    # Request and response types
    'McpRequest',
    'McpRequestType',
    'McpResponse',
    # Utility functions
    'get_default_socket_path',
    'socket_exists',
    'test_connection',
]
