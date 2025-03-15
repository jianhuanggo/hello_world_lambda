"""
Hello World module with username support.

This module provides functions to generate hello world messages,
optionally including a username.
"""


def hello_world() -> str:
    """
    Generate a simple hello world message.
    
    Returns:
        str: A hello world message
    """
    return "Hello, World!"


def hello_user(username: str) -> str:
    """
    Generate a hello world message with the given username.
    
    Args:
        username (str): The username to include in the message
        
    Returns:
        str: A hello world message including the username
    """
    if not username:
        return hello_world()
    
    return f"Hello, World! I'm {username}."
