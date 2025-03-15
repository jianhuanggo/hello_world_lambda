"""
AWS Lambda Handler for Cryptocurrency Information

This module provides an AWS Lambda handler for fetching cryptocurrency information.
"""
import json
import logging
from typing import Dict, Any

from crypto_info.api import get_crypto_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        Lambda response object
    """
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        # Extract the cryptocurrency symbol from the event
        if 'queryStringParameters' in event and event['queryStringParameters'] and 'symbol' in event['queryStringParameters']:
            symbol = event['queryStringParameters']['symbol']
        elif 'body' in event and event['body']:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            symbol = body.get('symbol')
        elif 'symbol' in event:
            symbol = event['symbol']
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing cryptocurrency symbol. Please provide a "symbol" parameter.'
                })
            }
        
        # Get cryptocurrency information
        crypto_info = get_crypto_info(symbol)
        
        # Return the response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(crypto_info)
        }
        
    except ValueError as e:
        logger.error("Value error: %s", str(e))
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
        
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }
