"""
Tests for the AWS Lambda Handler
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from crypto_info.lambda_handler import lambda_handler


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


class TestLambdaHandler:
    """Tests for the lambda_handler function"""
    
    @patch('crypto_info.lambda_handler.get_crypto_info')
    def test_lambda_handler_query_params(self, mock_get_crypto_info, sample_crypto_data):
        """Test lambda handler with query string parameters"""
        mock_get_crypto_info.return_value = sample_crypto_data
        
        event = {
            'queryStringParameters': {
                'symbol': 'BTC'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        assert 'body' in response
        body = json.loads(response['body'])
        assert body['name'] == 'Bitcoin'
        assert body['symbol'] == 'BTC'
    
    @patch('crypto_info.lambda_handler.get_crypto_info')
    def test_lambda_handler_json_body(self, mock_get_crypto_info, sample_crypto_data):
        """Test lambda handler with JSON body"""
        mock_get_crypto_info.return_value = sample_crypto_data
        
        event = {
            'body': json.dumps({
                'symbol': 'BTC'
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        assert 'body' in response
        body = json.loads(response['body'])
        assert body['name'] == 'Bitcoin'
        assert body['symbol'] == 'BTC'
    
    @patch('crypto_info.lambda_handler.get_crypto_info')
    def test_lambda_handler_direct_param(self, mock_get_crypto_info, sample_crypto_data):
        """Test lambda handler with direct parameter"""
        mock_get_crypto_info.return_value = sample_crypto_data
        
        event = {
            'symbol': 'BTC'
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        assert 'body' in response
        body = json.loads(response['body'])
        assert body['name'] == 'Bitcoin'
        assert body['symbol'] == 'BTC'
    
    def test_lambda_handler_missing_symbol(self):
        """Test lambda handler with missing symbol"""
        event = {}
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        assert 'body' in response
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Missing cryptocurrency symbol' in body['error']
    
    @patch('crypto_info.lambda_handler.get_crypto_info')
    def test_lambda_handler_value_error(self, mock_get_crypto_info):
        """Test lambda handler with value error"""
        mock_get_crypto_info.side_effect = ValueError("Crypto not found")
        
        event = {
            'symbol': 'XYZ'
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 404
        assert 'body' in response
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Crypto not found' in body['error']
    
    @patch('crypto_info.lambda_handler.get_crypto_info')
    def test_lambda_handler_unexpected_error(self, mock_get_crypto_info):
        """Test lambda handler with unexpected error"""
        mock_get_crypto_info.side_effect = Exception("Unexpected error")
        
        event = {
            'symbol': 'BTC'
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 500
        assert 'body' in response
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Internal server error' in body['error']
