"""
Sample Usage of the Cryptocurrency Information API

This module demonstrates various ways to use the cryptocurrency information API.
"""
import logging
import time
from typing import List, Dict, Any
import concurrent.futures

from crypto_info.api import CryptoAPI, get_crypto_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_single_crypto_info() -> None:
    """
    Demonstrate getting information for a single cryptocurrency.
    """
    logger.info("Getting information for Bitcoin (BTC)...")
    
    try:
        info = get_crypto_info("BTC")
        
        logger.info("Bitcoin Information:")
        logger.info(f"Name: {info['name']}")
        logger.info(f"Symbol: {info['symbol']}")
        logger.info(f"Current Price: ${info['current_price']:,.2f}")
        logger.info(f"Market Cap: ${info['market_cap']:,.0f}")
        logger.info(f"24h Change: {info['price_change_percentage_24h']:.2f}%")
        
    except Exception as e:
        logger.error(f"Error getting Bitcoin information: {e}")


def compare_multiple_cryptos(symbols: List[str]) -> None:
    """
    Demonstrate comparing multiple cryptocurrencies.
    
    Args:
        symbols: List of cryptocurrency symbols to compare
    """
    logger.info(f"Comparing cryptocurrencies: {', '.join(symbols)}")
    
    api = CryptoAPI()
    results = []
    
    try:
        # Get price data for all symbols
        symbols_lower = [s.lower() for s in symbols]
        price_data = api.get_price(symbols_lower, ["usd", "eur"])
        
        # Get detailed information for each symbol
        for symbol in symbols:
            try:
                info = get_crypto_info(symbol)
                results.append({
                    "name": info["name"],
                    "symbol": info["symbol"],
                    "price_usd": info["current_price"],
                    "price_eur": price_data.get(info["id"], {}).get("eur", None),
                    "market_cap": info["market_cap"],
                    "market_cap_rank": info["market_cap_rank"],
                    "24h_change": info["price_change_percentage_24h"]
                })
            except Exception as e:
                logger.error(f"Error getting information for {symbol}: {e}")
        
        # Display comparison
        logger.info("\nCryptocurrency Comparison:")
        logger.info(f"{'Name':<15} {'Symbol':<8} {'Price (USD)':<15} {'Price (EUR)':<15} {'Market Cap':<20} {'Rank':<6} {'24h Change':<10}")
        logger.info("-" * 90)
        
        for crypto in sorted(results, key=lambda x: x["market_cap_rank"] or 9999):
            logger.info(
                f"{crypto['name']:<15} {crypto['symbol']:<8} "
                f"${crypto['price_usd']:,.2f}".ljust(15) + " " +
                f"€{crypto['price_eur']:,.2f}".ljust(15) + " " +
                f"${crypto['market_cap']:,.0f}".ljust(20) + " " +
                f"{crypto['market_cap_rank'] or 'N/A':<6} "
                f"{crypto['24h_change']:+.2f}%".ljust(10)
            )
            
    except Exception as e:
        logger.error(f"Error comparing cryptocurrencies: {e}")


def parallel_crypto_fetching(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Demonstrate parallel fetching of cryptocurrency information.
    
    Args:
        symbols: List of cryptocurrency symbols to fetch
        
    Returns:
        List of cryptocurrency information dictionaries
    """
    logger.info(f"Fetching information for {len(symbols)} cryptocurrencies in parallel...")
    start_time = time.time()
    
    results = []
    errors = []
    
    # Use ThreadPoolExecutor for parallel fetching
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        future_to_symbol = {
            executor.submit(get_crypto_info, symbol): symbol
            for symbol in symbols
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                info = future.result()
                results.append(info)
            except Exception as e:
                errors.append((symbol, str(e)))
                logger.error(f"Error fetching {symbol}: {e}")
    
    end_time = time.time()
    logger.info(f"Fetched {len(results)} cryptocurrencies in {end_time - start_time:.2f} seconds")
    
    if errors:
        logger.warning(f"Encountered {len(errors)} errors: {errors}")
    
    return results


def track_price_changes(symbol: str, interval_seconds: int = 60, duration_minutes: int = 5) -> None:
    """
    Demonstrate tracking price changes over time.
    
    Args:
        symbol: Cryptocurrency symbol to track
        interval_seconds: Interval between price checks in seconds
        duration_minutes: Total duration to track in minutes
    """
    logger.info(f"Tracking price changes for {symbol} every {interval_seconds} seconds for {duration_minutes} minutes...")
    
    api = CryptoAPI()
    iterations = (duration_minutes * 60) // interval_seconds
    prices = []
    
    try:
        # Get initial information
        info = get_crypto_info(symbol)
        coin_id = info["id"]
        name = info["name"]
        logger.info(f"Starting to track {name} ({symbol}) prices...")
        
        # Track prices over time
        for i in range(iterations):
            try:
                price_data = api.get_price(coin_id)
                price = price_data.get(coin_id, {}).get("usd")
                
                if price:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    prices.append((timestamp, price))
                    logger.info(f"[{timestamp}] {name} ({symbol}): ${price:,.2f}")
                
                if i < iterations - 1:
                    time.sleep(interval_seconds)
                    
            except Exception as e:
                logger.error(f"Error fetching price: {e}")
        
        # Calculate statistics
        if len(prices) > 1:
            first_price = prices[0][1]
            last_price = prices[-1][1]
            price_change = last_price - first_price
            price_change_pct = (price_change / first_price) * 100
            
            logger.info("\nPrice Tracking Summary:")
            logger.info(f"Start Price: ${first_price:,.2f}")
            logger.info(f"End Price: ${last_price:,.2f}")
            logger.info(f"Change: ${price_change:+,.2f} ({price_change_pct:+.2f}%)")
            
    except Exception as e:
        logger.error(f"Error tracking prices: {e}")


def demonstrate_rate_limiting() -> None:
    """
    Demonstrate the rate limiting functionality.
    """
    logger.info("Demonstrating rate limiting...")
    
    api = CryptoAPI()
    symbols = ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX", "MATIC", "LINK", "UNI", "AAVE"]
    
    try:
        logger.info("Making multiple API requests in quick succession...")
        start_time = time.time()
        
        for symbol in symbols:
            try:
                logger.info(f"Fetching information for {symbol}...")
                info = get_crypto_info(symbol)
                logger.info(f"{info['name']} ({info['symbol']}): ${info['current_price']:,.2f}")
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
        
        end_time = time.time()
        logger.info(f"Completed {len(symbols)} requests in {end_time - start_time:.2f} seconds")
        logger.info("Note: Requests were automatically rate-limited to prevent API throttling")
        
    except Exception as e:
        logger.error(f"Error demonstrating rate limiting: {e}")


def main() -> None:
    """
    Main function to demonstrate various API usage examples.
    """
    logger.info("=== Cryptocurrency Information API Usage Examples ===")
    
    # Example 1: Get information for a single cryptocurrency
    logger.info("\n=== Example 1: Single Cryptocurrency Information ===")
    get_single_crypto_info()
    
    # Example 2: Compare multiple cryptocurrencies
    logger.info("\n=== Example 2: Comparing Multiple Cryptocurrencies ===")
    compare_multiple_cryptos(["BTC", "ETH", "SOL", "ADA", "DOT"])
    
    # Example 3: Parallel fetching
    logger.info("\n=== Example 3: Parallel Fetching ===")
    top_cryptos = ["BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "USDC", "ADA", "AVAX", "DOGE"]
    parallel_crypto_fetching(top_cryptos)
    
    # Example 4: Demonstrate rate limiting
    logger.info("\n=== Example 4: Rate Limiting ===")
    demonstrate_rate_limiting()
    
    # Example 5: Track price changes (commented out as it takes time)
    # logger.info("\n=== Example 5: Tracking Price Changes ===")
    # track_price_changes("BTC", interval_seconds=10, duration_minutes=1)
    
    logger.info("\n=== All examples completed ===")


if __name__ == "__main__":
    main()
