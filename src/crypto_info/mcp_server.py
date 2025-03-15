"""
Model Context Protocol (MCP) Server for Cryptocurrency Information

This module implements a Model Context Protocol server that integrates
with Cursor AI and Windsurf MCP to provide cryptocurrency information.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from crypto_info.api import get_crypto_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Crypto Info MCP Server",
    description="Model Context Protocol server for cryptocurrency information",
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


class CryptoRequest(BaseModel):
    """Request model for cryptocurrency information"""
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., 'BTC', 'ETH')")


class CryptoResponse(BaseModel):
    """Response model for cryptocurrency information"""
    id: str = Field(..., description="Cryptocurrency ID")
    name: str = Field(..., description="Cryptocurrency name")
    symbol: str = Field(..., description="Cryptocurrency symbol")
    current_price: float = Field(None, description="Current price in USD")
    market_cap: float = Field(None, description="Market capitalization in USD")
    market_cap_rank: int = Field(None, description="Market cap rank")
    total_volume: float = Field(None, description="24h trading volume in USD")
    high_24h: float = Field(None, description="24h high in USD")
    low_24h: float = Field(None, description="24h low in USD")
    price_change_24h: float = Field(None, description="24h price change in USD")
    price_change_percentage_24h: float = Field(None, description="24h price change percentage")
    last_updated: str = Field(None, description="Last updated timestamp")


class MCPRequest(BaseModel):
    """Model Context Protocol request model"""
    query: str = Field(..., description="Query from the client")
    context: Optional[Dict[str, Any]] = Field(None, description="Context information")


class MCPResponse(BaseModel):
    """Model Context Protocol response model"""
    response: str = Field(..., description="Response to the query")
    context: Dict[str, Any] = Field({}, description="Updated context information")
    sources: List[Dict[str, Any]] = Field([], description="Sources of information")


@app.post("/api/crypto", response_model=CryptoResponse)
async def crypto_info(request: CryptoRequest):
    """
    Get information about a cryptocurrency by its symbol.
    """
    try:
        info = get_crypto_info(request.symbol)
        return info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching crypto info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/mcp")
async def mcp_endpoint(request: MCPRequest):
    """
    Model Context Protocol endpoint for integration with AI tools.
    """
    try:
        # Extract cryptocurrency symbol from the query
        query = request.query.lower()
        
        # Simple parsing logic - extract symbols like BTC, ETH, etc.
        # This could be enhanced with NLP for more complex queries
        symbols = []
        words = query.split()
        
        for word in words:
            # Clean up the word
            clean_word = ''.join(c for c in word if c.isalnum())
            if 2 <= len(clean_word) <= 5 and clean_word.upper() == clean_word:
                symbols.append(clean_word)
        
        # If no symbols found in the query, look for keywords
        if not symbols:
            crypto_keywords = ["crypto", "cryptocurrency", "token", "coin"]
            if any(keyword in query for keyword in crypto_keywords):
                # Extract potential symbols - this is a simplified approach
                for word in words:
                    clean_word = ''.join(c for c in word if c.isalnum())
                    if 2 <= len(clean_word) <= 10:
                        symbols.append(clean_word)
        
        # If still no symbols, check if there's a symbol in the context
        if not symbols and request.context and "symbol" in request.context:
            symbols = [request.context["symbol"]]
        
        # If no symbols found, return a helpful message
        if not symbols:
            return MCPResponse(
                response="I couldn't identify a cryptocurrency symbol in your query. Please specify a symbol like BTC, ETH, SOL, etc.",
                context={},
                sources=[]
            )
        
        # Get information for the first symbol
        symbol = symbols[0]
        try:
            crypto_data = get_crypto_info(symbol)
            
            # Format the response
            response = f"Here's information about {crypto_data['name']} ({crypto_data['symbol']}):\n\n"
            response += f"Current Price: ${crypto_data['current_price']:,.2f}\n"
            response += f"Market Cap: ${crypto_data['market_cap']:,.0f} (Rank: {crypto_data['market_cap_rank']})\n"
            response += f"24h Volume: ${crypto_data['total_volume']:,.0f}\n"
            
            if crypto_data['price_change_percentage_24h']:
                change_emoji = "📈" if crypto_data['price_change_percentage_24h'] > 0 else "📉"
                response += f"24h Change: {change_emoji} {crypto_data['price_change_percentage_24h']:.2f}%\n"
            
            response += f"24h Range: ${crypto_data['low_24h']:,.2f} - ${crypto_data['high_24h']:,.2f}\n"
            response += f"\nLast Updated: {crypto_data['last_updated']}"
            
            # Prepare sources
            sources = [{
                "name": f"{crypto_data['name']} Information",
                "url": f"https://www.coingecko.com/en/coins/{crypto_data['id']}",
                "description": f"Data from CoinGecko API for {crypto_data['symbol']}"
            }]
            
            return MCPResponse(
                response=response,
                context={"symbol": crypto_data['symbol'], "last_queried": crypto_data['id']},
                sources=sources
            )
            
        except ValueError:
            return MCPResponse(
                response=f"I couldn't find information for the cryptocurrency symbol '{symbol}'. Please check if the symbol is correct.",
                context={},
                sources=[]
            )
            
    except Exception as e:
        logger.error(f"Error in MCP endpoint: {e}")
        return MCPResponse(
            response="I encountered an error while processing your request. Please try again later.",
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
                "sources": mcp_response.sources,
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
            "metadata": {
                "sources": mcp_response.sources
            }
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
