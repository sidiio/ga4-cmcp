"""FastMCP server factory – wires auth and all tools together."""

import os

from fastmcp import FastMCP

from ga4_mcp.auth import create_auth_provider
from ga4_mcp.tools.analytics import register_analytics_tools


def create_server(base_url: str | None = None) -> FastMCP:
    if base_url is None:
        base_url = os.environ.get("MCP_BASE_URL", "http://localhost:8080")

    auth = create_auth_provider(base_url=base_url)
    mcp = FastMCP(name="google_analytics_4_mcp", auth=auth)

    register_analytics_tools(mcp)

    return mcp
