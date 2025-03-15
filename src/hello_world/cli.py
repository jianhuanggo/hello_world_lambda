"""
Command Line Interface for Hello World.

This module provides a CLI for generating hello world messages.
"""
import argparse
import logging
import sys

from hello_world.hello import hello_world, hello_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        description="Generate hello world messages, optionally with a username"
    )
    parser.add_argument(
        "--username", "-u",
        help="Username to include in the message"
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
        # Generate the appropriate message
        if args.username:
            message = hello_user(args.username)
        else:
            message = hello_world()
        
        # Print the message
        print(message)
        
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
