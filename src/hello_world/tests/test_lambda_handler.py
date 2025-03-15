"""
Tests for the AWS Lambda Handler.
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from hello_world.lambda_handler import lambda_handler


class TestLambdaHandler:
    """Tests for the lambda_handler function."""
    
    def test_lambda_handler_no_username(self):
        """Test lambda handler with no username."""
        event = {}
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == "Hello, World!"
    
    def test_lambda_handler_query_params(self):
        """Test lambda handler with username in query parameters."""
        event = {
            'queryStringParameters': {
                'username': 'John'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == "Hello, World! I'm John."
    
    def test_lambda_handler_json_body(self):
        """Test lambda handler with username in JSON body."""
        event = {
            'body': json.dumps({
                'username': 'Alice'
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == "Hello, World! I'm Alice."
    
    def test_lambda_handler_direct_param(self):
        """Test lambda handler with username as direct parameter."""
        event = {
            'username': 'Bob'
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == "Hello, World! I'm Bob."
    
    def test_lambda_handler_empty_username(self):
        """Test lambda handler with empty username."""
        event = {
            'username': ''
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == "Hello, World!"
    
    @patch('hello_world.lambda_handler.hello_user')
    def test_lambda_handler_exception(self, mock_hello_user):
        """Test lambda handler with an exception."""
        mock_hello_user.side_effect = Exception("Test error")
        
        event = {
            'username': 'ErrorUser'
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body
        assert body['error'] == 'Internal server error'
