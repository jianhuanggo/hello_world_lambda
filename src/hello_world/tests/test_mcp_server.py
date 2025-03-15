"""
Tests for the Model Context Protocol (MCP) Server.
"""
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from hello_world.mcp_server import app, MCPRequest


client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_endpoint(self):
        """Test that the root endpoint returns a hello world message."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Hello, World!"


class TestHelloEndpoint:
    """Tests for the /api/hello endpoint."""
    
    def test_hello_endpoint_no_username(self):
        """Test hello endpoint with no username."""
        response = client.post("/api/hello", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Hello, World!"
    
    def test_hello_endpoint_with_username(self):
        """Test hello endpoint with a username."""
        response = client.post("/api/hello", json={"username": "John"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Hello, World! I'm John."
    
    @patch('hello_world.mcp_server.hello_user')
    def test_hello_endpoint_error(self, mock_hello_user):
        """Test hello endpoint with an error."""
        mock_hello_user.side_effect = Exception("Test error")
        
        response = client.post("/api/hello", json={"username": "ErrorUser"})
        
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]


class TestMCPEndpoint:
    """Tests for the /api/mcp endpoint."""
    
    def test_mcp_endpoint_no_username(self):
        """Test MCP endpoint with no username in query or context."""
        request = MCPRequest(query="Hello there")
        response = client.post("/api/mcp", json=request.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hello, World!"
        assert data["context"] == {}
    
    def test_mcp_endpoint_with_username_in_query(self):
        """Test MCP endpoint with username in query."""
        request = MCPRequest(query="Hello there, I am John")
        response = client.post("/api/mcp", json=request.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hello, World! I'm John."
        assert data["context"]["username"] == "John"
    
    def test_mcp_endpoint_with_username_in_context(self):
        """Test MCP endpoint with username in context."""
        request = MCPRequest(
            query="Hello there",
            context={"username": "Alice"}
        )
        response = client.post("/api/mcp", json=request.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hello, World! I'm Alice."
        assert data["context"]["username"] == "Alice"
    
    @patch('hello_world.mcp_server.hello_user')
    def test_mcp_endpoint_error(self, mock_hello_user):
        """Test MCP endpoint with an error."""
        mock_hello_user.side_effect = Exception("Test error")
        
        request = MCPRequest(query="I am ErrorUser")
        response = client.post("/api/mcp", json=request.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data["response"].lower()
        assert data["context"] == {}


class TestCursorAIEndpoint:
    """Tests for the /api/cursor endpoint."""
    
    @patch('hello_world.mcp_server.mcp_endpoint')
    async def test_cursor_ai_endpoint_success(self, mock_mcp_endpoint):
        """Test successful Cursor AI integration."""
        from hello_world.mcp_server import MCPResponse
        
        # Mock the MCP endpoint response
        mock_response = MCPResponse(
            response="Hello, World! I'm John.",
            context={"username": "John"},
            sources=[]
        )
        mock_mcp_endpoint.return_value = mock_response
        
        response = client.post(
            "/api/cursor",
            json={"query": "I am John"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hello, World! I'm John."
        assert data["metadata"]["context"]["username"] == "John"
    
    def test_cursor_ai_endpoint_no_query(self):
        """Test Cursor AI endpoint with no query."""
        response = client.post("/api/cursor", json={})
        
        assert response.status_code == 400
        assert "No query provided" in response.json()["error"]


class TestWindsurfMCPEndpoint:
    """Tests for the /api/windsurf endpoint."""
    
    @patch('hello_world.mcp_server.mcp_endpoint')
    async def test_windsurf_mcp_endpoint_success(self, mock_mcp_endpoint):
        """Test successful Windsurf MCP integration."""
        from hello_world.mcp_server import MCPResponse
        
        # Mock the MCP endpoint response
        mock_response = MCPResponse(
            response="Hello, World! I'm Alice.",
            context={"username": "Alice"},
            sources=[]
        )
        mock_mcp_endpoint.return_value = mock_response
        
        response = client.post(
            "/api/windsurf",
            json={"input": {"text": "I am Alice"}}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["output"]["text"] == "Hello, World! I'm Alice."
        assert data["context"]["username"] == "Alice"
    
    def test_windsurf_mcp_endpoint_no_query(self):
        """Test Windsurf MCP endpoint with no query."""
        response = client.post("/api/windsurf", json={})
        
        assert response.status_code == 400
        assert "No query provided" in response.json()["error"]
