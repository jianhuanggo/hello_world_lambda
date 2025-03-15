"""
Command Line Interface for Cryptocurrency Information

This module provides a CLI for fetching and displaying cryptocurrency information.
"""
import argparse
import json
import logging
import sys
from typing import Dict, Any, Optional

from crypto_info.api import get_crypto_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def display_crypto_info(info: Dict[str, Any], format_type: str = "text") -> None:
    """
    Display cryptocurrency information in the specified format.
    
    Args:
        info: Dictionary containing cryptocurrency information
        format_type: Output format ('text', 'json', or 'compact')
    """
    if format_type == "json":
        print(json.dumps(info, indent=2))
        return
    
    if format_type == "compact":
        print(f"{info['name']} ({info['symbol']}): ${info['current_price']:,.2f}")
        return
    
    # Default text format
    print(f"\n{'=' * 40}")
    print(f"{info['name']} ({info['symbol']}) Information")
    print(f"{'=' * 40}")
    print(f"Current Price: ${info['current_price']:,.2f}")
    print(f"Market Cap: ${info['market_cap']:,.0f} (Rank: {info['market_cap_rank']})")
    print(f"24h Volume: ${info['total_volume']:,.0f}")
    
    if info['price_change_percentage_24h']:
        change_emoji = "📈" if info['price_change_percentage_24h'] > 0 else "📉"
        print(f"24h Change: {change_emoji} {info['price_change_percentage_24h']:.2f}%")
    
    print(f"24h Range: ${info['low_24h']:,.2f} - ${info['high_24h']:,.2f}")
    print(f"\nLast Updated: {info['last_updated']}")
    print(f"{'=' * 40}\n")


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        description="Fetch and display cryptocurrency information"
    )
    parser.add_argument(
        "symbol",
        help="Cryptocurrency symbol (e.g., BTC, ETH)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "compact"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Get cryptocurrency information
        info = get_crypto_info(args.symbol)
        
        # Display the information
        display_crypto_info(info, args.format)
        
        return 0
    except ValueError as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
