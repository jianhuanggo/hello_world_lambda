"""
Tests for the Cryptocurrency Information API Module
"""
import pytest
from unittest.mock import patch, MagicMock
import time
import requests
from requests.exceptions import RequestException

from crypto_info.api import RateLimiter, CryptoAPI, get_crypto_info


class TestRateLimiter:
    """Tests for the RateLimiter class"""
    
    def test_init(self):
        """Test RateLimiter initialization"""
        limiter = RateLimiter(calls_per_minute=60)
        assert limiter.calls_per_minute == 60
        assert limiter.interval == 1.0
        assert limiter.last_call_time == 0.0
    
    def test_wait_if_needed_no_wait(self):
        """Test no waiting is needed when sufficient time has passed"""
        limiter = RateLimiter(calls_per_minute=60)
        limiter.last_call_time = time.time() - 2.0  # Last call was 2 seconds ago
        
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        
        assert elapsed < 0.1  # Should return almost immediately
    
    def test_wait_if_needed_with_wait(self):
        """Test waiting occurs when calls are too frequent"""
        limiter = RateLimiter(calls_per_minute=60)  # 1 call per second
        limiter.last_call_time = time.time() - 0.5  # Last call was 0.5 seconds ago
        
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        
        assert 0.4 < elapsed < 0.6  # Should wait about 0.5 seconds


class TestCryptoAPI:
    """Tests for the CryptoAPI class"""
    
    def test_init(self):
        """Test CryptoAPI initialization"""
        api = CryptoAPI(base_url="https://test-api.example.com")
        assert api.base_url == "https://test-api.example.com"
        assert isinstance(api.rate_limiter, RateLimiter)
        assert isinstance(api.session, requests.Session)
    
    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test_data"}
        mock_get.return_value = mock_response
        
        api = CryptoAPI()
        result = api._make_request("test-endpoint", {"param": "value"})
        
        mock_get.assert_called_once_with(
            "https://api.coingecko.com/api/v3/test-endpoint",
            params={"param": "value"},
            timeout=10
        )
        assert result == {"data": "test_data"}
    
    @patch('requests.Session.get')
    def test_make_request_error(self, mock_get):
        """Test API request with error"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = RequestException("API Error")
        mock_get.return_value = mock_response
        
        api = CryptoAPI()
        with pytest.raises(RequestException):
            api._make_request("test-endpoint")
    
    @patch('crypto_info.api.CryptoAPI._make_request')
    def test_get_coin_info(self, mock_make_request):
        """Test getting coin information"""
        mock_make_request.return_value = {"id": "bitcoin", "name": "Bitcoin"}
        
        api = CryptoAPI()
        result = api.get_coin_info("bitcoin")
        
        mock_make_request.assert_called_once_with(
            "coins/bitcoin",
            {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false"
            }
        )
        assert result == {"id": "bitcoin", "name": "Bitcoin"}
    
    @patch('crypto_info.api.CryptoAPI._make_request')
    def test_search_coin(self, mock_make_request):
        """Test searching for coins"""
        mock_make_request.return_value = {"coins": [{"id": "bitcoin", "symbol": "btc"}]}
        
        api = CryptoAPI()
        result = api.search_coin("btc")
        
        mock_make_request.assert_called_once_with("search", {"query": "btc"})
        assert result == [{"id": "bitcoin", "symbol": "btc"}]
    
    @patch('crypto_info.api.CryptoAPI._make_request')
    def test_get_price_single(self, mock_make_request):
        """Test getting price for a single coin"""
        mock_make_request.return_value = {"bitcoin": {"usd": 50000}}
        
        api = CryptoAPI()
        result = api.get_price("bitcoin")
        
        mock_make_request.assert_called_once_with(
            "simple/price",
            {"ids": "bitcoin", "vs_currencies": "usd"}
        )
        assert result == {"bitcoin": {"usd": 50000}}
    
    @patch('crypto_info.api.CryptoAPI._make_request')
    def test_get_price_multiple(self, mock_make_request):
        """Test getting prices for multiple coins"""
        mock_make_request.return_value = {
            "bitcoin": {"usd": 50000, "eur": 42000},
            "ethereum": {"usd": 3000, "eur": 2500}
        }
        
        api = CryptoAPI()
        result = api.get_price(["bitcoin", "ethereum"], ["usd", "eur"])
        
        mock_make_request.assert_called_once_with(
            "simple/price",
            {"ids": "bitcoin,ethereum", "vs_currencies": "usd,eur"}
        )
        assert result == {
            "bitcoin": {"usd": 50000, "eur": 42000},
            "ethereum": {"usd": 3000, "eur": 2500}
        }


class TestGetCryptoInfo:
    """Tests for the get_crypto_info function"""
    
    @patch('crypto_info.api.CryptoAPI.search_coin')
    @patch('crypto_info.api.CryptoAPI.get_coin_info')
    def test_get_crypto_info_exact_match(self, mock_get_coin_info, mock_search_coin):
        """Test getting crypto info with exact symbol match"""
        mock_search_coin.return_value = [
            {"id": "bitcoin", "symbol": "btc"},
            {"id": "bitcoin-cash", "symbol": "bch"}
        ]
        mock_get_coin_info.return_value = {
            "id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "btc",
            "market_data": {
                "current_price": {"usd": 50000},
                "market_cap": {"usd": 1000000000000},
                "total_volume": {"usd": 30000000000},
                "high_24h": {"usd": 51000},
                "low_24h": {"usd": 49000}
            },
            "market_cap_rank": 1,
            "last_updated": "2023-01-01T00:00:00Z"
        }
        
        result = get_crypto_info("btc")
        
        mock_search_coin.assert_called_once_with("btc")
        mock_get_coin_info.assert_called_once_with("bitcoin")
        
        assert result["id"] == "bitcoin"
        assert result["name"] == "Bitcoin"
        assert result["symbol"] == "BTC"
        assert result["current_price"] == 50000
        assert result["market_cap"] == 1000000000000
    
    @patch('crypto_info.api.CryptoAPI.search_coin')
    def test_get_crypto_info_no_results(self, mock_search_coin):
        """Test getting crypto info with no search results"""
        mock_search_coin.return_value = []
        
        with pytest.raises(ValueError, match="No cryptocurrency found with symbol 'xyz'"):
            get_crypto_info("xyz")
