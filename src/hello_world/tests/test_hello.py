"""
Tests for the Hello World module.
"""
import pytest
from hello_world.hello import hello_world, hello_user


class TestHelloWorld:
    """Tests for the hello_world function."""
    
    def test_hello_world(self):
        """Test that hello_world returns the expected message."""
        result = hello_world()
        assert result == "Hello, World!"


class TestHelloUser:
    """Tests for the hello_user function."""
    
    def test_hello_user_with_name(self):
        """Test that hello_user returns the expected message with a username."""
        result = hello_user("John")
        assert result == "Hello, World! I'm John."
    
    def test_hello_user_with_empty_name(self):
        """Test that hello_user returns the default message with an empty username."""
        result = hello_user("")
        assert result == "Hello, World!"
    
    @pytest.mark.parametrize("username", [
        "Alice",
        "Bob",
        "Charlie",
        "特殊字符",
        "123456",
        "user@example.com",
    ])
    def test_hello_user_with_various_names(self, username):
        """Test that hello_user works with various usernames."""
        result = hello_user(username)
        assert result == f"Hello, World! I'm {username}."
