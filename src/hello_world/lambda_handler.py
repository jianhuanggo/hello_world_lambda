"""
AWS Lambda Handler for Hello World.

This module provides an AWS Lambda handler for generating hello world messages.
"""
import json
import logging
from typing import Dict, Any

from hello_world.hello import hello_world, hello_user

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
        # Extract the username from the event
        username = None
        
        if 'queryStringParameters' in event and event['queryStringParameters'] and 'username' in event['queryStringParameters']:
            username = event['queryStringParameters']['username']
        elif 'body' in event and event['body']:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            username = body.get('username')
        elif 'username' in event:
            username = event['username']
        
        # Generate the appropriate message
        if username:
            message = hello_user(username)
        else:
            message = hello_world()
        
        # Return the response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': message
            })
        }
        
    except Exception as e:
        logger.error("Error: %s", str(e), exc_info=True)
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
