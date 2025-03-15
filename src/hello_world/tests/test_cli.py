"""
Tests for the Command Line Interface.
"""
import pytest
from unittest.mock import patch, MagicMock

from hello_world.cli import main


class TestMainFunction:
    """Tests for the main function."""
    
    @patch('hello_world.cli.hello_world')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_no_username(self, mock_parse_args, mock_hello_world):
        """Test main function with no username."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.username = None
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        # Mock hello_world function
        mock_hello_world.return_value = "Hello, World!"
        
        # Run the main function
        with patch('builtins.print') as mock_print:
            result = main()
            
            # Verify the results
            assert result == 0
            mock_hello_world.assert_called_once()
            mock_print.assert_called_once_with("Hello, World!")
    
    @patch('hello_world.cli.hello_user')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_with_username(self, mock_parse_args, mock_hello_user):
        """Test main function with a username."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.username = "John"
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        # Mock hello_user function
        mock_hello_user.return_value = "Hello, World! I'm John."
        
        # Run the main function
        with patch('builtins.print') as mock_print:
            result = main()
            
            # Verify the results
            assert result == 0
            mock_hello_user.assert_called_once_with("John")
            mock_print.assert_called_once_with("Hello, World! I'm John.")
    
    @patch('hello_world.cli.hello_world')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_verbose_mode(self, mock_parse_args, mock_hello_world):
        """Test main function with verbose logging."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.username = None
        mock_args.verbose = True
        mock_parse_args.return_value = mock_args
        
        # Mock hello_world function
        mock_hello_world.return_value = "Hello, World!"
        
        # Run the main function
        with patch('logging.getLogger') as mock_logger:
            with patch('builtins.print'):
                result = main()
                
                # Verify the results
                assert result == 0
                mock_logger().setLevel.assert_called_once()
    
    @patch('hello_world.cli.hello_user')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_error(self, mock_parse_args, mock_hello_user):
        """Test main function with an error."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.username = "ErrorUser"
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        # Mock hello_user function to raise an exception
        mock_hello_user.side_effect = Exception("Test error")
        
        # Run the main function
        with patch('logging.getLogger') as mock_logger:
            result = main()
            
            # Verify the results
            assert result == 1
            mock_logger().error.assert_called_once()
