#!/usr/bin/env python3
"""
MCP Integration Test Suite

Tests the integration between uCode1 Python MCP client and uCode2 MCP server.
This validates the end-to-end architecture.
"""

import unittest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core_py.mcp_client import (
    McpClient,
    McpConnectionError,
    get_default_socket_path,
    socket_exists,
    test_connection
)


class TestMCPIntegration(unittest.TestCase):
    """Test MCP client integration with uCode2 server."""
    
    def test_default_socket_path(self):
        """Test that default socket path is correct."""
        path = get_default_socket_path()
        self.assertIn(".local", str(path))
        self.assertIn("mcp.sock", str(path))
    
    def test_socket_exists_function(self):
        """Test socket_exists doesn't crash."""
        result = socket_exists()
        self.assertIsInstance(result, bool)
    
    def test_client_no_auto_connect(self):
        """Test creating client without auto-connect."""
        client = McpClient(auto_connect=False)
        self.assertFalse(client.is_connected)
        client.close()
    
    def test_client_manual_connect_fail(self):
        """Test manual connection to non-existent server."""
        client = McpClient(auto_connect=False)
        
        # Try to connect to a non-existent socket
        try:
            client.connect()
            client.close()
        except McpConnectionError:
            # Expected if server is not running
            pass
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")


class TestMCPMethodsAvailability(unittest.TestCase):
    """Test that all MCP client methods are available."""
    
    def test_all_notes_methods_exist(self):
        """Test notes-related methods exist."""
        client = McpClient(auto_connect=False)
        
        self.assertTrue(hasattr(client, 'list_notes'))
        self.assertTrue(hasattr(client, 'read_note'))
        self.assertTrue(hasattr(client, 'search_notes'))
    
    def test_all_vault_methods_exist(self):
        """Test vault-related methods exist."""
        client = McpClient(auto_connect=False)
        
        self.assertTrue(hasattr(client, 'vault_read'))
        self.assertTrue(hasattr(client, 'vault_write'))
        self.assertTrue(hasattr(client, 'vault_list'))
        self.assertTrue(hasattr(client, 'vault_search'))
        self.assertTrue(hasattr(client, 'vault_delete'))
        self.assertTrue(hasattr(client, 'vault_metadata'))
    
    def test_all_utility_methods_exist(self):
        """Test utility methods exist."""
        client = McpClient(auto_connect=False)
        
        self.assertTrue(hasattr(client, 'status'))
        self.assertTrue(hasattr(client, 'ping'))
        self.assertTrue(hasattr(client, 'classify_intent'))
        self.assertTrue(hasattr(client, 'shutdown'))
    
    def test_utilities_exported(self):
        """Test utility functions are exported."""
        from core_py.mcp_client import (
            get_default_socket_path,
            socket_exists,
            test_connection
        )
        self.assertIsNotNone(get_default_socket_path)
        self.assertIsNotNone(socket_exists)
        self.assertIsNotNone(test_connection)


class TestMcpRequest(unittest.TestCase):
    """Test McpRequest creation."""
    
    def test_request_type_enum(self):
        """Test McpRequestType enum values."""
        from core_py.mcp_client import McpRequestType
        
        self.assertEqual(McpRequestType.PING.value, "Ping")
        self.assertEqual(McpRequestType.STATUS.value, "Status")
        self.assertEqual(McpRequestType.LIST_NOTES.value, "ListNotes")
        self.assertEqual(McpRequestType.READ_NOTE.value, "ReadNote")
        self.assertEqual(McpRequestType.VAULT_READ.value, "VaultRead")
    
    def test_request_to_json(self):
        """Test McpRequest serialization."""
        from core_py.mcp_client import McpRequest, McpRequestType
        import json
        
        request = McpRequest(request_type=McpRequestType.PING)
        json_str = request.to_json()
        
        parsed = json.loads(json_str)
        self.assertIn("type", parsed)
        self.assertEqual(parsed["type"], "Ping")
    
    def test_request_with_data(self):
        """Test McpRequest with data."""
        from core_py.mcp_client import McpRequest, McpRequestType
        
        request = McpRequest(
            request_type=McpRequestType.READ_NOTE,
            data={"name": "test-note"}
        )
        json_str = request.to_json()
        
        import json
        parsed = json.loads(json_str)
        self.assertEqual(parsed["type"], "ReadNote")
        self.assertIn("name", parsed)


class TestMcpResponse(unittest.TestCase):
    """Test McpResponse parsing."""
    
    def test_success_response(self):
        """Test parsing success response."""
        from core_py.mcp_client import McpResponse
        
        response = McpResponse(raw_data={"Success": {"data": {"key": "value"}}})
        self.assertTrue(response.is_success)
        self.assertFalse(response.is_error)
    
    def test_error_response(self):
        """Test parsing error response."""
        from core_py.mcp_client import McpResponse
        
        response = McpResponse(raw_data={"Error": {"message": "test error"}})
        self.assertFalse(response.is_success)
        self.assertTrue(response.is_error)
        self.assertEqual(response.error_message, "test error")
    
    def test_notes_response(self):
        """Test parsing notes list response."""
        from core_py.mcp_client import McpResponse
        
        response = McpResponse(raw_data={"Notes": {"list": ["note1", "note2"]}})
        self.assertEqual(response.notes, ["note1", "note2"])


if __name__ == '__main__':
    unittest.main()
