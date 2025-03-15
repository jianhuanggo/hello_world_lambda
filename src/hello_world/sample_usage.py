"""
Sample Usage of the Hello World Module.

This module demonstrates various ways to use the hello world functionality.
"""
import logging
from hello_world.hello import hello_world, hello_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def basic_usage():
    """Demonstrate basic usage of the hello world functions."""
    logger.info("=== Basic Usage ===")
    
    # Simple hello world
    message = hello_world()
    logger.info(f"Simple hello world: {message}")
    
    # Hello world with username
    message = hello_user("John")
    logger.info(f"Hello world with username: {message}")
    
    # Hello world with empty username
    message = hello_user("")
    logger.info(f"Hello world with empty username: {message}")


def multiple_users():
    """Demonstrate usage with multiple users."""
    logger.info("\n=== Multiple Users ===")
    
    users = ["Alice", "Bob", "Charlie", "Dave", "Eve"]
    
    for user in users:
        message = hello_user(user)
        logger.info(f"User {user}: {message}")


def special_characters():
    """Demonstrate usage with special characters in usernames."""
    logger.info("\n=== Special Characters ===")
    
    special_users = [
        "John Doe",  # Space
        "user@example.com",  # Email
        "123456",  # Numbers
        "特殊字符",  # Non-Latin characters
        "O'Reilly",  # Apostrophe
        "Smith-Jones",  # Hyphen
    ]
    
    for user in special_users:
        message = hello_user(user)
        logger.info(f"Special user: {message}")


def programmatic_usage():
    """Demonstrate programmatic usage in a larger application."""
    logger.info("\n=== Programmatic Usage ===")
    
    # Simulate a user database
    user_database = {
        "user1": {"name": "Alice", "active": True},
        "user2": {"name": "Bob", "active": False},
        "user3": {"name": "Charlie", "active": True},
    }
    
    # Process active users
    active_users = [user["name"] for user_id, user in user_database.items() if user["active"]]
    
    logger.info(f"Active users: {', '.join(active_users)}")
    
    for username in active_users:
        message = hello_user(username)
        logger.info(f"Greeting for {username}: {message}")


def main():
    """Main function to run all examples."""
    logger.info("Hello World Module - Sample Usage")
    
    # Run all examples
    basic_usage()
    multiple_users()
    special_characters()
    programmatic_usage()
    
    logger.info("\nAll examples completed!")


if __name__ == "__main__":
    main()
