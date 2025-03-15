"""
Tests for the Model Context Protocol (MCP) Server
"""
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from crypto_info.mcp_server import app, MCPRequest


client = TestClient(app)


@pytest.fixture
def sample_crypto_data():
    """Sample cryptocurrency data for testing"""
    return {
        "id": "bitcoin",
        "name": "Bitcoin",
        "symbol": "BTC",
        "current_price": 50000,
        "market_cap": 1000000000000,
        "market_cap_rank": 1,
        "total_volume": 30000000000,
        "high_24h": 51000,
        "low_24h": 49000,
        "price_change_24h": 1000,
        "price_change_percentage_24h": 2.0,
        "last_updated": "2023-01-01T00:00:00Z"
    }


class TestCryptoInfoEndpoint:
    """Tests for the /api/crypto endpoint"""
    
    @patch('crypto_info.mcp_server.get_crypto_info')
    def test_crypto_info_success(self, mock_get_crypto_info, sample_crypto_data):
        """Test successful crypto info retrieval"""
        mock_get_crypto_info.return_value = sample_crypto_data
        
        response = client.post("/api/crypto", json={"symbol": "BTC"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "bitcoin"
        assert data["name"] == "Bitcoin"
        assert data["symbol"] == "BTC"
        assert data["current_price"] == 50000
    
    @patch('crypto_info.mcp_server.get_crypto_info')
    def test_crypto_info_not_found(self, mock_get_crypto_info):
        """Test crypto info not found"""
        mock_get_crypto_info.side_effect = ValueError("Crypto not found")
        
        response = client.post("/api/crypto", json={"symbol": "XYZ"})
        
        assert response.status_code == 404
        assert "Crypto not found" in response.json()["detail"]
    
    @patch('crypto_info.mcp_server.get_crypto_info')
    def test_crypto_info_server_error(self, mock_get_crypto_info):
        """Test server error handling"""
        mock_get_crypto_info.side_effect = Exception("Server error")
        
        response = client.post("/api/crypto", json={"symbol": "BTC"})
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


class TestMCPEndpoint:
    """Tests for the /api/mcp endpoint"""
    
    @patch('crypto_info.mcp_server.get_crypto_info')
    def test_mcp_endpoint_with_symbol(self, mock_get_crypto_info, sample_crypto_data):
        """Test MCP endpoint with symbol in query"""
        mock_get_crypto_info.return_value = sample_crypto_data
        
        request = MCPRequest(query="What is the price of BTC?")
        response = client.post("/api/mcp", json=request.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert "Bitcoin (BTC)" in data["response"]
        assert "$50,000.00" in data["response"]
        assert data["context"]["symbol"] == "BTC"
        assert len(data["sources"]) == 1
    
    @patch('crypto_info.mcp_server.get_crypto_info')
    def test_mcp_endpoint_with_context(self, mock_get_crypto_info, sample_crypto_data):
        """Test MCP endpoint with symbol in context"""
        mock_get_crypto_info.return_value = sample_crypto_data
        
        request = MCPRequest(
            query="What is the current price?",
            context={"symbol": "BTC"}
        )
        response = client.post("/api/mcp", json=request.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert "Bitcoin (BTC)" in data["response"]
    
    def test_mcp_endpoint_no_symbol(self):
        """Test MCP endpoint with no symbol in query or context"""
        request = MCPRequest(query="Tell me about cryptocurrency")
        response = client.post("/api/mcp", json=request.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert "couldn't identify a cryptocurrency symbol" in data["response"]
    
    @patch('crypto_info.mcp_server.get_crypto_info')
    def test_mcp_endpoint_symbol_not_found(self, mock_get_crypto_info):
        """Test MCP endpoint with symbol not found"""
        mock_get_crypto_info.side_effect = ValueError("Crypto not found")
        
        request = MCPRequest(query="What is the price of XYZ?")
        response = client.post("/api/mcp", json=request.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert "couldn't find information" in data["response"]


class TestCursorAIEndpoint:
    """Tests for the /api/cursor endpoint"""
    
    @patch('crypto_info.mcp_server.mcp_endpoint')
    async def test_cursor_ai_endpoint_success(self, mock_mcp_endpoint, sample_crypto_data):
        """Test successful Cursor AI integration"""
        from crypto_info.mcp_server import MCPResponse
        
        # Mock the MCP endpoint response
        mock_response = MCPResponse(
            response="Bitcoin (BTC) price is $50,000.00",
            context={"symbol": "BTC"},
            sources=[{"name": "Bitcoin Information", "url": "https://example.com"}]
        )
        mock_mcp_endpoint.return_value = mock_response
        
        response = client.post(
            "/api/cursor",
            json={"query": "What is the price of BTC?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Bitcoin (BTC) price is $50,000.00"
        assert "sources" in data["metadata"]
    
    def test_cursor_ai_endpoint_no_query(self):
        """Test Cursor AI endpoint with no query"""
        response = client.post("/api/cursor", json={})
        
        assert response.status_code == 400
        assert "No query provided" in response.json()["error"]


class TestWindsurfMCPEndpoint:
    """Tests for the /api/windsurf endpoint"""
    
    @patch('crypto_info.mcp_server.mcp_endpoint')
    async def test_windsurf_mcp_endpoint_success(self, mock_mcp_endpoint, sample_crypto_data):
        """Test successful Windsurf MCP integration"""
        from crypto_info.mcp_server import MCPResponse
        
        # Mock the MCP endpoint response
        mock_response = MCPResponse(
            response="Bitcoin (BTC) price is $50,000.00",
            context={"symbol": "BTC"},
            sources=[{"name": "Bitcoin Information", "url": "https://example.com"}]
        )
        mock_mcp_endpoint.return_value = mock_response
        
        response = client.post(
            "/api/windsurf",
            json={"input": {"text": "What is the price of BTC?"}}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["output"]["text"] == "Bitcoin (BTC) price is $50,000.00"
        assert "sources" in data["metadata"]
    
    def test_windsurf_mcp_endpoint_no_query(self):
        """Test Windsurf MCP endpoint with no query"""
        response = client.post("/api/windsurf", json={})
        
        assert response.status_code == 400
        assert "No query provided" in response.json()["error"]
