""" 
server.py functions as the bridge between Client(Codex) and tools.
 """

from mcp.server.fastmcp import FastMCP 

# Tools loading

mcp = FastMCP("doc-mcp-server")

# Register tools here

if __name__ == "__main__":
    mcp.run()