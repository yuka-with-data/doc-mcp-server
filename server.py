""" 
doc-mcp-server

This file initializes and runs a minimal MCP server for Codex.
It registeres documenmentation-related tools and exposes them to AI agents via MCP.

Run this file to start the server and connect it through Codex MCP settings.
 """
# print("🔥 MCP SERVER STARTED", flush=True)

from mcp.server.fastmcp import FastMCP 
import logging
import sys

# Tools loading
from tools.scan import scan_docs_structure
from tools.validate_structure import validate_structure

# Setup basic logging (important for debugging with Codex)
# IMPORTANT: logging must NOT go to stdout
logging.basicConfig(
    level=logging.INFO, 
    stream=sys.stderr
    )

# Create MCP server instance
mcp = FastMCP("doc-mcp-server")

# ---------- Register tools ------------
@mcp.tool()
def scan_docs_structure_tool(repo_path: str) -> list:
    """ Scan repository and return all markdown files. """
    return scan_docs_structure(repo_path)

@mcp.tool()
def validate_structure_tool(file_path: str) -> list:
    """ Check markdown file for missing sections. """
    return validate_structure(file_path)


if __name__ == "__main__":
    mcp.run(transport="stdio")  # Use stdio for communication with Codex