"""
Tests for the Command Line Interface
"""
import json
import pytest
from unittest.mock import patch, MagicMock
import io
import sys

from crypto_info.cli import display_crypto_info, main


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


class TestDisplayCryptoInfo:
    """Tests for the display_crypto_info function"""
    
    def test_display_json_format(self, sample_crypto_data, capsys):
        """Test displaying crypto info in JSON format"""
        display_crypto_info(sample_crypto_data, "json")
        captured = capsys.readouterr()
        
        # Parse the JSON output and verify
        output_data = json.loads(captured.out)
        assert output_data["name"] == "Bitcoin"
        assert output_data["symbol"] == "BTC"
        assert output_data["current_price"] == 50000
    
    def test_display_compact_format(self, sample_crypto_data, capsys):
        """Test displaying crypto info in compact format"""
        display_crypto_info(sample_crypto_data, "compact")
        captured = capsys.readouterr()
        
        assert "Bitcoin (BTC): $50,000.00" in captured.out
    
    def test_display_text_format(self, sample_crypto_data, capsys):
        """Test displaying crypto info in text format"""
        display_crypto_info(sample_crypto_data, "text")
        captured = capsys.readouterr()
        
        assert "Bitcoin (BTC) Information" in captured.out
        assert "Current Price: $50,000.00" in captured.out
        assert "Market Cap: $1,000,000,000,000" in captured.out
        assert "24h Change: 📈 2.00%" in captured.out
    
    def test_display_negative_price_change(self, sample_crypto_data, capsys):
        """Test displaying crypto info with negative price change"""
        sample_crypto_data["price_change_percentage_24h"] = -2.0
        display_crypto_info(sample_crypto_data, "text")
        captured = capsys.readouterr()
        
        assert "24h Change: 📉 -2.00%" in captured.out


class TestMainFunction:
    """Tests for the main function"""
    
    @patch('crypto_info.cli.get_crypto_info')
    @patch('crypto_info.cli.display_crypto_info')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_success(self, mock_parse_args, mock_display, mock_get_crypto_info, sample_crypto_data):
        """Test successful execution of main function"""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.symbol = "BTC"
        mock_args.format = "text"
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        # Mock API response
        mock_get_crypto_info.return_value = sample_crypto_data
        
        # Run the main function
        result = main()
        
        # Verify the results
        assert result == 0
        mock_get_crypto_info.assert_called_once_with("BTC")
        mock_display.assert_called_once_with(sample_crypto_data, "text")
    
    @patch('crypto_info.cli.get_crypto_info')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_value_error(self, mock_parse_args, mock_get_crypto_info):
        """Test main function with ValueError"""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.symbol = "XYZ"
        mock_args.format = "text"
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        # Mock API error
        mock_get_crypto_info.side_effect = ValueError("Crypto not found")
        
        # Run the main function
        result = main()
        
        # Verify the results
        assert result == 1
    
    @patch('crypto_info.cli.get_crypto_info')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_unexpected_error(self, mock_parse_args, mock_get_crypto_info):
        """Test main function with unexpected error"""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.symbol = "BTC"
        mock_args.format = "text"
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        # Mock API error
        mock_get_crypto_info.side_effect = Exception("Unexpected error")
        
        # Run the main function
        result = main()
        
        # Verify the results
        assert result == 2
    
    @patch('crypto_info.cli.get_crypto_info')
    @patch('crypto_info.cli.display_crypto_info')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_verbose_mode(self, mock_parse_args, mock_display, mock_get_crypto_info, sample_crypto_data):
        """Test main function with verbose logging"""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.symbol = "BTC"
        mock_args.format = "text"
        mock_args.verbose = True
        mock_parse_args.return_value = mock_args
        
        # Mock API response
        mock_get_crypto_info.return_value = sample_crypto_data
        
        # Run the main function
        with patch('logging.getLogger') as mock_logger:
            result = main()
            
            # Verify the results
            assert result == 0
            mock_logger().setLevel.assert_called_once()
