"""
MCP Client — Connect to uCode2 MCP Gateway from uCode1.

Allows uCode1 scripts and snacks to call MCP methods on the uCode2 gateway,
accessing vault resources, feed spool, spatial grid, and other services.

Usage:
    from ucode1.mcp_client import McpClient

    client = McpClient()
    result = client.call("vault.list_resources")
    print(result)
"""

import json
import logging
import socket
import struct
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_SOCKET = Path.home() / ".local" / "share" / "udos" / "ucode2.sock"


class McpClientError(Exception):
    """MCP client error."""


class McpClient:
    """Client for the uCode2 MCP Gateway.

    Connects to the gateway's Unix socket and sends JSON-RPC 2.0 requests
    using the length-prefixed protocol.
    """

    def __init__(self, socket_path: Optional[Path] = None):
        self.socket_path = socket_path or DEFAULT_SOCKET
        self._next_id = 1

    def _next_request_id(self) -> int:
        rid = self._next_id
        self._next_id += 1
        return rid

    def call(self, method: str, params: Optional[dict] = None) -> Any:
        """Call an MCP method on the gateway.

        Args:
            method: The method name (e.g. 'vault.list_resources', 'ping')
            params: Optional parameters dict

        Returns:
            The result from the gateway

        Raises:
            McpClientError: If connection fails or the method returns an error
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": method,
        }
        if params is not None:
            request["params"] = params

        payload = json.dumps(request).encode("utf-8")

        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            sock.connect(str(self.socket_path))

            # Send length-prefixed request
            sock.sendall(struct.pack("!I", len(payload)) + payload)

            # Read length-prefixed response (handle partial reads)
            raw_len = sock.recv(4)
            if not raw_len:
                raise McpClientError("Empty response from gateway")
            msg_len = struct.unpack("!I", raw_len)[0]
            raw = b""
            while len(raw) < msg_len:
                chunk = sock.recv(msg_len - len(raw))
                if not chunk:
                    raise McpClientError(f"Connection closed: received {len(raw)} of {msg_len} bytes")
                raw += chunk

            response = json.loads(raw.decode("utf-8"))

            if "error" in response:
                err = response["error"]
                raise McpClientError(
                    f"MCP error [{err.get('code', '?')}]: {err.get('message', 'Unknown')}"
                )

            return response.get("result")

        except socket.timeout:
            raise McpClientError(
                f"Timeout connecting to gateway at {self.socket_path}"
            )
        except FileNotFoundError:
            raise McpClientError(
                f"Gateway socket not found at {self.socket_path}. "
                "Is the uCode2 MCP gateway running?"
            )
        except ConnectionRefusedError:
            raise McpClientError(
                f"Connection refused at {self.socket_path}. "
                "Is the uCode2 MCP gateway running?"
            )
        except json.JSONDecodeError as e:
            raise McpClientError(f"Invalid JSON response: {e}")
        finally:
            sock.close()

    def ping(self) -> dict:
        """Check if the gateway is reachable."""
        return self.call("ping")

    def status(self) -> dict:
        """Get gateway status."""
        return self.call("status")

    def list_methods(self) -> dict:
        """List all available methods on the gateway."""
        return self.call("list_methods")

    def vault_list(self) -> list:
        """List vault resources."""
        return self.call("vault.list_resources")

    def vault_read(self, path: str) -> str:
        """Read a vault resource by path."""
        return self.call("vault.read", {"path": path})

    def feed_write(self, channel: str, content: str) -> dict:
        """Write an entry to the feed spool."""
        return self.call("feed.write", {"channel": channel, "content": content})

    def feed_read(self, channel: str, limit: int = 10) -> list:
        """Read entries from the feed spool."""
        return self.call("feed.read", {"channel": channel, "limit": limit})
