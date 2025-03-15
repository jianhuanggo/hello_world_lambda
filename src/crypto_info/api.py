"""
Cryptocurrency Information API Module

This module provides functionality to fetch cryptocurrency information
from external APIs with rate limiting capabilities.
"""
import time
import logging
from typing import Dict, Any, Optional, List, Union
import requests
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiter to prevent exceeding API rate limits.
    """
    def __init__(self, calls_per_minute: int = 50):
        """
        Initialize the rate limiter.
        
        Args:
            calls_per_minute: Maximum number of calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.interval = 60.0 / calls_per_minute
        self.last_call_time = 0.0
    
    def wait_if_needed(self) -> None:
        """
        Wait if necessary to comply with rate limits.
        """
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.interval:
            wait_time = self.interval - time_since_last_call
            logger.debug(f"Rate limiting: waiting for {wait_time:.2f} seconds")
            time.sleep(wait_time)
        
        self.last_call_time = time.time()


class CryptoAPI:
    """
    API client for fetching cryptocurrency information.
    """
    def __init__(self, base_url: str = "https://api.coingecko.com/api/v3"):
        """
        Initialize the CryptoAPI client.
        
        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url
        self.rate_limiter = RateLimiter()
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a rate-limited API request.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters for the request
            
        Returns:
            API response as a dictionary
            
        Raises:
            RequestException: If the request fails
        """
        self.rate_limiter.wait_if_needed()
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                logger.warning("Rate limit exceeded. Implementing exponential backoff.")
                time.sleep(30)  # Simple backoff strategy
                return self._make_request(endpoint, params)
            raise
    
    def get_coin_info(self, coin_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific cryptocurrency.
        
        Args:
            coin_id: ID of the cryptocurrency (e.g., 'bitcoin', 'ethereum')
            
        Returns:
            Dictionary containing coin information
        """
        endpoint = f"coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false"
        }
        return self._make_request(endpoint, params)
    
    def search_coin(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for cryptocurrencies by name or symbol.
        
        Args:
            query: Search query (e.g., 'BTC', 'Bitcoin')
            
        Returns:
            List of matching cryptocurrencies
        """
        endpoint = "search"
        params = {"query": query}
        response = self._make_request(endpoint, params)
        return response.get("coins", [])
    
    def get_price(self, coin_ids: Union[str, List[str]], vs_currencies: Union[str, List[str]] = "usd") -> Dict[str, Dict[str, float]]:
        """
        Get current prices for cryptocurrencies.
        
        Args:
            coin_ids: Single coin ID or list of coin IDs
            vs_currencies: Single currency or list of currencies to convert to
            
        Returns:
            Dictionary mapping coin IDs to their prices in specified currencies
        """
        endpoint = "simple/price"
        
        if isinstance(coin_ids, list):
            coin_ids = ",".join(coin_ids)
        
        if isinstance(vs_currencies, list):
            vs_currencies = ",".join(vs_currencies)
        
        params = {
            "ids": coin_ids,
            "vs_currencies": vs_currencies
        }
        
        return self._make_request(endpoint, params)


def get_crypto_info(symbol: str) -> Dict[str, Any]:
    """
    Get comprehensive information about a cryptocurrency by its symbol.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        
    Returns:
        Dictionary containing cryptocurrency information
        
    Raises:
        ValueError: If the cryptocurrency cannot be found
    """
    api = CryptoAPI()
    
    # Search for the coin by symbol
    search_results = api.search_coin(symbol)
    
    if not search_results:
        raise ValueError(f"No cryptocurrency found with symbol '{symbol}'")
    
    # Find the best match for the symbol
    best_match = None
    for coin in search_results:
        if coin.get("symbol", "").lower() == symbol.lower():
            best_match = coin
            break
    
    if not best_match:
        best_match = search_results[0]  # Take the first result if no exact match
    
    coin_id = best_match.get("id")
    
    # Get detailed information
    coin_info = api.get_coin_info(coin_id)
    
    # Extract relevant information
    result = {
        "id": coin_info.get("id"),
        "name": coin_info.get("name"),
        "symbol": coin_info.get("symbol", "").upper(),
        "current_price": coin_info.get("market_data", {}).get("current_price", {}).get("usd"),
        "market_cap": coin_info.get("market_data", {}).get("market_cap", {}).get("usd"),
        "market_cap_rank": coin_info.get("market_cap_rank"),
        "total_volume": coin_info.get("market_data", {}).get("total_volume", {}).get("usd"),
        "high_24h": coin_info.get("market_data", {}).get("high_24h", {}).get("usd"),
        "low_24h": coin_info.get("market_data", {}).get("low_24h", {}).get("usd"),
        "price_change_24h": coin_info.get("market_data", {}).get("price_change_24h"),
        "price_change_percentage_24h": coin_info.get("market_data", {}).get("price_change_percentage_24h"),
        "last_updated": coin_info.get("last_updated")
    }
    
    return result
