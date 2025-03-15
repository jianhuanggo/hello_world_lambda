"""
Model Context Protocol (MCP) Server for Hello World.

This module implements a Model Context Protocol server that integrates
with Cursor AI and Windsurf MCP to provide hello world functionality.
"""
import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from hello_world.hello import hello_world, hello_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Hello World MCP Server",
    description="Model Context Protocol server for hello world messages",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HelloRequest(BaseModel):
    """Request model for hello world messages"""
    username: Optional[str] = Field(None, description="Username to include in the message")


class HelloResponse(BaseModel):
    """Response model for hello world messages"""
    message: str = Field(..., description="Hello world message")


class MCPRequest(BaseModel):
    """Model Context Protocol request model"""
    query: str = Field(..., description="Query from the client")
    context: Optional[Dict[str, Any]] = Field(None, description="Context information")


class MCPResponse(BaseModel):
    """Model Context Protocol response model"""
    response: str = Field(..., description="Response to the query")
    context: Dict[str, Any] = Field({}, description="Updated context information")
    sources: list = Field([], description="Sources of information")


@app.get("/")
async def root():
    """Root endpoint that returns a simple hello world message."""
    return {"message": hello_world()}


@app.post("/api/hello", response_model=HelloResponse)
async def hello_endpoint(request: HelloRequest):
    """
    Generate a hello world message, optionally with a username.
    """
    try:
        if request.username:
            message = hello_user(request.username)
        else:
            message = hello_world()
        
        return {"message": message}
    except Exception as e:
        logger.error(f"Error generating hello message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/mcp")
async def mcp_endpoint(request: MCPRequest):
    """
    Model Context Protocol endpoint for integration with AI tools.
    """
    try:
        query = request.query.lower()
        context = request.context or {}
        
        # Extract username from the query or context
        username = None
        
        # Check if the query contains a name introduction
        name_indicators = ["i am ", "i'm ", "my name is ", "call me "]
        for indicator in name_indicators:
            if indicator in query:
                username = query.split(indicator, 1)[1].strip().split()[0].rstrip(".,!?")
                break
        
        # If no username in query, check context
        if not username and "username" in context:
            username = context["username"]
        
        # Generate the appropriate message
        if username:
            message = hello_user(username)
            updated_context = {"username": username}
        else:
            message = hello_world()
            updated_context = {}
        
        return MCPResponse(
            response=message,
            context=updated_context,
            sources=[]
        )
        
    except Exception as e:
        logger.error(f"Error in MCP endpoint: {e}")
        return MCPResponse(
            response="I encountered an error while processing your request.",
            context={},
            sources=[]
        )


@app.post("/api/cursor")
async def cursor_ai_endpoint(request: Request):
    """
    Endpoint for integration with Cursor AI.
    """
    try:
        body = await request.json()
        query = body.get("query", "")
        
        if not query:
            return Response(
                content=json.dumps({"error": "No query provided"}),
                media_type="application/json",
                status_code=400
            )
        
        # Process the query similar to MCP endpoint
        mcp_request = MCPRequest(query=query, context=body.get("context"))
        mcp_response = await mcp_endpoint(mcp_request)
        
        # Format response for Cursor AI
        cursor_response = {
            "response": mcp_response.response,
            "metadata": {
                "context": mcp_response.context
            }
        }
        
        return Response(
            content=json.dumps(cursor_response),
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error in Cursor AI endpoint: {e}")
        return Response(
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
            status_code=500
        )


@app.post("/api/windsurf")
async def windsurf_mcp_endpoint(request: Request):
    """
    Endpoint for integration with Windsurf MCP.
    """
    try:
        body = await request.json()
        
        # Windsurf MCP format might be different, adapt as needed
        query = body.get("input", {}).get("text", "")
        context = body.get("context", {})
        
        if not query:
            return Response(
                content=json.dumps({"error": "No query provided"}),
                media_type="application/json",
                status_code=400
            )
        
        # Process the query similar to MCP endpoint
        mcp_request = MCPRequest(query=query, context=context)
        mcp_response = await mcp_endpoint(mcp_request)
        
        # Format response for Windsurf MCP
        windsurf_response = {
            "output": {
                "text": mcp_response.response
            },
            "context": mcp_response.context,
            "metadata": {}
        }
        
        return Response(
            content=json.dumps(windsurf_response),
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error in Windsurf MCP endpoint: {e}")
        return Response(
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
            status_code=500
        )
