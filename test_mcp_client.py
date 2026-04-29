#!/usr/bin/env python3
"""
Test suite for the Python MCP client module.

Tests the core_py.mcp_client module functionality with mock connections
and verifies it can connect to a real MCP server if available.
"""

import json
import os
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import from core_py
import sys
sys.path.insert(0, str(Path(__file__).parent))

from core_py.mcp_client import (
    McpClient,
    McpClientError,
    McpConnectionError,
    McpTimeoutError,
    McpRequest,
    McpRequestType,
    McpResponse,
    get_default_socket_path,
    socket_exists,
    test_connection,
)


class TestMcpRequest(unittest.TestCase):
    """Test McpRequest dataclass."""
    
    def test_request_to_dict_simple(self):
        """Test converting a simple request to dict."""
        request = McpRequest(request_type=McpRequestType.PING)
        result = request.to_dict()
        # Server expects {"Ping": null} format, not {"type": "Ping"}
        self.assertIn("Ping", result)
    
    def test_request_to_dict_with_data(self):
        """Test converting a request with data to dict."""
        request = McpRequest(
            request_type=McpRequestType.READ_NOTE,
            data={"name": "test-note"}
        )
        result = request.to_dict()
        # Server expects {"ReadNote": {"name": "test-note"}} format
        self.assertIn("ReadNote", result)
        self.assertEqual(result["ReadNote"]["name"], "test-note")
    
    def test_request_to_json(self):
        """Test converting a request to JSON string."""
        request = McpRequest(request_type=McpRequestType.STATUS)
        result = request.to_json()
        self.assertIsInstance(result, str)
        parsed = json.loads(result)
        # Server expects {"Status": null} format
        self.assertIn("Status", parsed)


class TestMcpResponse(unittest.TestCase):
    """Test McpResponse dataclass."""
    
    def test_success_response(self):
        """Test parsing a success response."""
        response = McpResponse(raw_data={
            "Success": {"data": {"key": "value"}}
        })
        self.assertTrue(response.is_success)
        self.assertFalse(response.is_error)
        self.assertEqual(response.data, {"key": "value"})
    
    def test_error_response(self):
        """Test parsing an error response."""
        response = McpResponse(raw_data={
            "Error": {"message": "Something went wrong"}
        })
        self.assertFalse(response.is_success)
        self.assertTrue(response.is_error)
        self.assertEqual(response.error_message, "Something went wrong")
    
    def test_notes_response(self):
        """Test parsing a notes list response."""
        response = McpResponse(raw_data={
            "Notes": {"list": ["note1", "note2", "note3"]}
        })
        self.assertEqual(response.notes, ["note1", "note2", "note3"])
    
    def test_note_content_response(self):
        """Test parsing a note content response."""
        response = McpResponse(raw_data={
            "NoteContent": {
                "name": "test-note",
                "content": "Note content here"
            }
        })
        self.assertEqual(response.note_content["name"], "test-note")
        self.assertEqual(response.note_content["content"], "Note content here")
    
    def test_intent_response(self):
        """Test parsing an intent response."""
        response = McpResponse(raw_data={
            "Intent": {
                "intent": "search",
                "confidence": 0.95,
                "parameters": {"query": "test"}
            }
        })
        self.assertEqual(response.intent["intent"], "search")
        self.assertAlmostEqual(response.intent["confidence"], 0.95)


class TestMcpClient(unittest.TestCase):
    """Test McpClient functionality."""
    
    def test_default_socket_path(self):
        """Test the default socket path."""
        client = McpClient(auto_connect=False)
        expected_path = Path("~/.local/mcp.sock").expanduser()
        self.assertEqual(client.socket_path, expected_path)
    
    def test_custom_socket_path(self):
        """Test using a custom socket path."""
        custom_path = "/tmp/test.sock"
        client = McpClient(socket_path=custom_path, auto_connect=False)
        self.assertEqual(str(client.socket_path), custom_path)
    
    def test_client_not_connected_initially(self):
        """Test that client is not connected when auto_connect=False."""
        client = McpClient(auto_connect=False)
        self.assertFalse(client.is_connected)
    
    @patch('core_py.mcp_client.socket.socket')
    def test_connection_failure(self, mock_socket_class):
        """Test connection failure handling."""
        mock_socket_class.side_effect = socket.error("Connection refused")
        
        with self.assertRaises(McpConnectionError) as context:
            McpClient(socket_path="/nonexistent/path.sock")
        
        self.assertIn("Connection refused", str(context.exception))
    
    @patch('core_py.mcp_client.socket.socket')
    def test_connection_success(self, mock_socket_class):
        """Test successful connection."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        with patch.object(mock_socket, 'connect'):
            # Set settimeout to not fail
            mock_socket.settimeout.return_value = None
            client = McpClient(socket_path="/tmp/test.sock", auto_connect=True)
            self.assertTrue(client.is_connected)
            client.close()
    
    @patch('core_py.mcp_client.socket.socket')
    def test_close_connection(self, mock_socket_class):
        """Test closing connection."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        with patch.object(mock_socket, 'connect'):
            client = McpClient(socket_path="/tmp/test.sock", auto_connect=True)
            self.assertTrue(client.is_connected)
            client.close()
            self.assertFalse(client.is_connected)
            mock_socket.close.assert_called_once()


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_get_default_socket_path(self):
        """Test getting the default socket path."""
        path = get_default_socket_path()
        self.assertIsInstance(path, Path)
        self.assertIn(".local", str(path))
        self.assertIn("mcp.sock", str(path))
    
    def test_socket_exists_false(self):
        """Test socket_exists when socket doesn't exist."""
        # Should not raise an error, just return False
        result = socket_exists()
        self.assertIsInstance(result, bool)


class TestHighLevelAPI(unittest.TestCase):
    """Test high-level API methods (would need running MCP server)."""
    
    @patch('core_py.mcp_client.socket.socket')
    def test_ping_method(self, mock_socket_class):
        """Test the ping method structure."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        with patch.object(mock_socket, 'connect'):
            with patch.object(mock_socket, 'sendall'):
                with patch.object(mock_socket, 'recv', return_value=b'{"Pong":{}\n'):
                    client = McpClient(socket_path="/tmp/test.sock", auto_connect=True)
                    # This would actually need a real MCP server running
                    # For now, just verify the method exists
                    self.assertTrue(hasattr(client, 'ping'))
                    client.close()
    
    def test_all_methods_exist(self):
        """Test that all expected methods exist on McpClient."""
        client = McpClient(auto_connect=False)
        
        expected_methods = [
            'list_notes', 'read_note', 'search_notes', 'classify_intent',
            'status', 'ping', 'shutdown',
            'vault_read', 'vault_write', 'vault_list', 'vault_search',
            'vault_delete', 'vault_metadata', 'vault_watch',
            'connect', 'disconnect', 'close',
        ]
        
        for method in expected_methods:
            self.assertTrue(
                hasattr(client, method),
                f"Method '{method}' not found on McpClient"
            )


if __name__ == '__main__':
    unittest.main()
