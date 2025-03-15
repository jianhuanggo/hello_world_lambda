# Hello World Lambda

A production-grade Python system for generating hello world messages with username support and Model Context Protocol (MCP) integration.

## Features

- Generate hello world messages with optional username support
- AWS Lambda handler for serverless deployment
- Command Line Interface (CLI) for easy usage
- Model Context Protocol (MCP) server integration with Cursor AI and Windsurf MCP
- Comprehensive test suite with pytest

## Installation

```bash
# Clone the repository
git clone https://github.com/jianhuanggo/hello_world_lambda.git
cd hello_world_lambda

# Install the package
pip install -e .

# For development dependencies
pip install -e ".[dev]"
```

## Usage

### Command Line Interface

```bash
# Simple hello world message
hello-world

# Hello world with username
hello-world --username John

# Enable verbose logging
hello-world --username Alice --verbose
```

### Python API

```python
from hello_world.hello import hello_world, hello_user

# Simple hello world
message = hello_world()
print(message)  # Output: Hello, World!

# Hello world with username
message = hello_user("John")
print(message)  # Output: Hello, World! I'm John.
```

### AWS Lambda

The system includes an AWS Lambda handler for serverless deployment:

```python
from hello_world.lambda_handler import lambda_handler

# The handler function can be configured in AWS Lambda
# It accepts events with the username in various formats
```

### MCP Server

Start the Model Context Protocol server:

```bash
uvicorn hello_world.mcp_server:app --host 0.0.0.0 --port 8000
```

The server provides the following endpoints:
- `/` - Root endpoint returning a simple hello world message
- `/api/hello` - Direct hello world API with username support
- `/api/mcp` - Model Context Protocol endpoint
- `/api/cursor` - Cursor AI integration endpoint
- `/api/windsurf` - Windsurf MCP integration endpoint

## Testing

Run the test suite:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=hello_world
```

## Sample Usage

The package includes a sample script demonstrating various usage patterns:

```bash
python -m hello_world.sample_usage
```

This demonstrates:
- Basic usage of hello world functions
- Usage with multiple users
- Handling special characters in usernames
- Programmatic usage in a larger application

## License

MIT
