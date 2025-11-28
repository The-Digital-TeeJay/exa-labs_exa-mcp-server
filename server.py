#!/usr/bin/env python3
"""
Exa Search MCP Server - FastMCP Implementation
A Model Context Protocol server for web search using Exa AI.
"""

import os
import httpx
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from fastmcp import FastMCP, Context

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("EXA_API_KEY")
if not API_KEY:
    raise ValueError("EXA_API_KEY environment variable is required")

API_BASE_URL = "https://api.exa.ai"
DEFAULT_NUM_RESULTS = 10
MAX_CACHED_SEARCHES = 5


# Pydantic Models for type safety
class ExaSearchResult(BaseModel):
    """Individual search result from Exa API."""
    score: float
    title: str
    id: str
    url: str
    published_date: Optional[str] = Field(None, alias="publishedDate")
    author: Optional[str] = None
    text: Optional[str] = None
    image: Optional[str] = None
    favicon: Optional[str] = None

    class Config:
        populate_by_name = True


class ExaSearchResponse(BaseModel):
    """Response from Exa search API."""
    request_id: str = Field(alias="requestId")
    autoprompt_string: Optional[str] = Field(None, alias="autopromptString")
    resolved_search_type: Optional[str] = Field(None, alias="resolvedSearchType")
    results: list[ExaSearchResult]

    class Config:
        populate_by_name = True


class CachedSearch(BaseModel):
    """Cached search result."""
    query: str
    response: dict
    timestamp: str


# Initialize FastMCP server
mcp = FastMCP(
    name="exa-search-server",
    version="0.1.0",
    description="A Model Context Protocol server for web search using Exa AI"
)

# In-memory cache for recent searches
recent_searches: list[CachedSearch] = []


def get_http_client() -> httpx.AsyncClient:
    """Create an HTTP client with Exa API configuration."""
    return httpx.AsyncClient(
        base_url=API_BASE_URL,
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": API_KEY
        },
        timeout=30.0
    )


# Resources - Expose recent searches
@mcp.resource("exa://searches")
async def list_searches() -> str:
    """List all recent cached searches."""
    if not recent_searches:
        return "No recent searches available."
    
    result = "Recent Searches:\n\n"
    for i, search in enumerate(recent_searches):
        result += f"{i}. Query: {search.query}\n"
        result += f"   Timestamp: {search.timestamp}\n"
        result += f"   Results: {len(search.response.get('results', []))} items\n\n"
    
    return result


@mcp.resource("exa://searches/{index}")
async def get_search(index: int) -> str:
    """Get a specific cached search result by index."""
    if index < 0 or index >= len(recent_searches):
        return f"Search result not found at index {index}. Available indices: 0-{len(recent_searches) - 1}"
    
    search = recent_searches[index]
    import json
    return json.dumps({
        "query": search.query,
        "timestamp": search.timestamp,
        "response": search.response
    }, indent=2)


# Tools
@mcp.tool
async def search(
    query: str,
    num_results: int = DEFAULT_NUM_RESULTS,
    ctx: Context = None
) -> str:
    """
    Search the web using Exa AI.
    
    Args:
        query: The search query to execute.
        num_results: Number of results to return (1-50, default: 10).
    
    Returns:
        JSON string containing search results with titles, URLs, and text content.
    """
    global recent_searches
    
    # Validate num_results
    num_results = max(1, min(50, num_results))
    
    search_request = {
        "query": query,
        "type": "auto",
        "numResults": num_results,
        "contents": {
            "text": True
        }
    }
    
    try:
        async with get_http_client() as client:
            response = await client.post("/search", json=search_request)
            response.raise_for_status()
            data = response.json()
        
        # Cache the search result
        cached = CachedSearch(
            query=query,
            response=data,
            timestamp=datetime.now().isoformat()
        )
        recent_searches.insert(0, cached)
        
        # Keep only recent searches
        if len(recent_searches) > MAX_CACHED_SEARCHES:
            recent_searches = recent_searches[:MAX_CACHED_SEARCHES]
        
        import json
        return json.dumps(data, indent=2)
        
    except httpx.HTTPStatusError as e:
        error_msg = f"Exa API error: {e.response.status_code}"
        try:
            error_data = e.response.json()
            if "message" in error_data:
                error_msg = f"Exa API error: {error_data['message']}"
        except Exception:
            pass
        return error_msg
    
    except httpx.RequestError as e:
        return f"Request error: {str(e)}"


@mcp.tool
async def find_similar(
    url: str,
    num_results: int = DEFAULT_NUM_RESULTS
) -> str:
    """
    Find similar content to a given URL using Exa AI.
    
    Args:
        url: The URL to find similar content for.
        num_results: Number of results to return (1-50, default: 10).
    
    Returns:
        JSON string containing similar content results.
    """
    num_results = max(1, min(50, num_results))
    
    request_data = {
        "url": url,
        "numResults": num_results,
        "contents": {
            "text": True
        }
    }
    
    try:
        async with get_http_client() as client:
            response = await client.post("/findSimilar", json=request_data)
            response.raise_for_status()
            data = response.json()
        
        import json
        return json.dumps(data, indent=2)
        
    except httpx.HTTPStatusError as e:
        error_msg = f"Exa API error: {e.response.status_code}"
        try:
            error_data = e.response.json()
            if "message" in error_data:
                error_msg = f"Exa API error: {error_data['message']}"
        except Exception:
            pass
        return error_msg
    
    except httpx.RequestError as e:
        return f"Request error: {str(e)}"


@mcp.tool
async def get_contents(
    ids: list[str]
) -> str:
    """
    Get the contents of specific documents by their Exa IDs.
    
    Args:
        ids: List of Exa document IDs to retrieve content for.
    
    Returns:
        JSON string containing document contents.
    """
    if not ids:
        return "Error: No document IDs provided."
    
    request_data = {
        "ids": ids,
        "contents": {
            "text": True
        }
    }
    
    try:
        async with get_http_client() as client:
            response = await client.post("/contents", json=request_data)
            response.raise_for_status()
            data = response.json()
        
        import json
        return json.dumps(data, indent=2)
        
    except httpx.HTTPStatusError as e:
        error_msg = f"Exa API error: {e.response.status_code}"
        try:
            error_data = e.response.json()
            if "message" in error_data:
                error_msg = f"Exa API error: {error_data['message']}"
        except Exception:
            pass
        return error_msg
    
    except httpx.RequestError as e:
        return f"Request error: {str(e)}"


# Entry point for different deployment modes
if __name__ == "__main__":
    import sys
    
    # Check for transport mode argument
    transport = "stdio"  # Default to stdio for CLI usage
    
    if "--http" in sys.argv:
        transport = "http"
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        print(f"Starting Exa Search MCP server on http://{host}:{port}/mcp")
        mcp.run(transport=transport, host=host, port=port)
    elif "--sse" in sys.argv:
        transport = "sse"
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        print(f"Starting Exa Search MCP server (SSE) on http://{host}:{port}/sse")
        mcp.run(transport=transport, host=host, port=port)
    else:
        # Default stdio mode for local MCP clients
        mcp.run(transport="stdio")

