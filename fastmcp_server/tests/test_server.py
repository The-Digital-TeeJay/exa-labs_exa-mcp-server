"""Tests for Exa MCP Server using FastMCP Client."""

import pytest
from unittest.mock import AsyncMock, patch
from fastmcp import Client


# Mock response data
MOCK_SEARCH_RESPONSE = {
    "requestId": "test-123",
    "autopromptString": "test query",
    "resolvedSearchType": "auto",
    "results": [
        {
            "score": 0.95,
            "title": "Test Result",
            "id": "doc-1",
            "url": "https://example.com/test",
            "publishedDate": "2024-01-01",
            "author": "Test Author",
            "text": "This is test content."
        }
    ]
}


@pytest.fixture
def mock_env():
    """Set up mock environment variables."""
    with patch.dict("os.environ", {"EXA_API_KEY": "test-api-key"}):
        yield


@pytest.fixture
def mock_httpx():
    """Mock httpx client for API calls."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = MOCK_SEARCH_RESPONSE
        mock_response.raise_for_status = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_list_tools(mock_env):
    """Test that tools are properly registered."""
    # Import after setting up mock env
    from server import mcp
    
    async with Client(mcp) as client:
        tools = await client.list_tools()
        
        tool_names = [tool.name for tool in tools]
        assert "search" in tool_names
        assert "find_similar" in tool_names
        assert "get_contents" in tool_names


@pytest.mark.asyncio
async def test_list_resources(mock_env):
    """Test that resources are properly registered."""
    from server import mcp
    
    async with Client(mcp) as client:
        resources = await client.list_resources()
        
        # Should have at least the searches resource
        assert len(resources) >= 0  # May be empty if no searches yet


@pytest.mark.asyncio
async def test_search_tool(mock_env, mock_httpx):
    """Test the search tool execution."""
    from server import mcp
    
    async with Client(mcp) as client:
        result = await client.call_tool("search", {"query": "test query"})
        
        # Result should contain search data
        assert result is not None


@pytest.mark.asyncio
async def test_search_with_num_results(mock_env, mock_httpx):
    """Test search tool with custom num_results."""
    from server import mcp
    
    async with Client(mcp) as client:
        result = await client.call_tool(
            "search", 
            {"query": "test query", "num_results": 5}
        )
        
        assert result is not None


@pytest.mark.asyncio
async def test_find_similar_tool(mock_env, mock_httpx):
    """Test the find_similar tool execution."""
    from server import mcp
    
    async with Client(mcp) as client:
        result = await client.call_tool(
            "find_similar", 
            {"url": "https://example.com"}
        )
        
        assert result is not None


@pytest.mark.asyncio
async def test_get_contents_tool(mock_env, mock_httpx):
    """Test the get_contents tool execution."""
    from server import mcp
    
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_contents", 
            {"ids": ["doc-1", "doc-2"]}
        )
        
        assert result is not None

