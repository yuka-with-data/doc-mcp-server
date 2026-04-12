""" 
doc-mcp-server

This file initializes and runs a minimal MCP server for Codex.
It registeres documenmentation-related tools and exposes them to AI agents via MCP.

Run this file to start the server and connect it through Codex MCP settings.
 """

from mcp.server.fastmcp import FastMCP 

# Tools loading

mcp = FastMCP("doc-mcp-server")

# Register tools here

if __name__ == "__main__":
    mcp.run()