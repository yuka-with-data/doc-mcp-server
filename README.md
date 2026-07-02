# Documentation MCP Server
![Status](https://img.shields.io/badge/status-active%20development-blue) ![MCP](https://img.shields.io/badge/MCP-compatible-purple) ![Python](https://img.shields.io/badge/python-3.12.2%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Reference](https://img.shields.io/badge/purpose-reference%20architecture-orange) ![Agents](https://img.shields.io/badge/AI-agents-blueviolet)

## Reference Implementation for MCP Tool Architecture
> A lightweight MCP server for document structure scanning and validation, designed as both a functional tool and a reusable template for building MCP-based systems.

## Overview
This project implements a Model Context Protocol (MCP) server for scanning and validating documentation structure.

It provides practical tools for analyzing markdown files and checking structural consistency across a repository. Beyond its immediate use case, it also serves as a reference implementation for MCP server design.

The goal is to demonstrate a clean, extensible structure for building MCP tools—making it easy to add new capabilities such as code analysis, data processing, or agent workflows with minimal changes to the core system.

## Key Features
- **Markdown Structure Scanning**: Analyze markdown files to extract headings, links, and overall structure.
- **Structural Validation**: Check for consistency in heading levels, link validity, and overall document organization.
- Serves as a reference template for building MCP-based tool servers
- more features to come

## Architecture
This projects follows a modular MCP design where the server exposes independent tools through a standardized protocol interface.

### High-Level Flow
```txt
Codex UI / MCP Client
        ↓
   MCP (stdio transport)
        ↓
   MCP Server (Python)
        ↓
Tools Layer
  - scan_docs_structure_tool
  - validate_structure_tool
```

## Design Structure
- MCP Server Layer: handles communication between the client and tools using MCP protocol over stdio
- Tools Layer: contains indepenedent, composable functions that implement specific capabilities (e.g., scanning, validation)
- Client Layer: Any MCP-compatible interface (Codex UI, agent runtime, etc) that consumes tool outputs

## Key Design Principle
Each tool is:
- Stateless
- Independently callable
- Designed for structured input/output (agent-friendly)

This makes the system easy to extend without modifying the core server logic.

## Runtime Context
This MCP server is designed for **local execusion using stdio transport**. 

In this setup:
- The server runs as a local Python process
- Communication with the client (Codex UI) happens through standard input/output streams (stdio)
- It is typically launched and managed by an MCP-compatible client, such as Codex UI or similar agent runtimes

### Important to Note:
- This example does not cover an HTTP or remote API service
- The server is intended to be executed locally as a subprocess
- MCP clients are responsible for spawning and connecting to the server process
- The architecture is transport-focused on stdio for simplicity and agent integration

## Available Tools
- `scan_docs_structure_tool`: Scans markdown files to extract structural information (headings, links, etc)
- `validate_structure_tool`: Validates the consistency of document structure based on predefined rules (e.g., heading levels, link validity)
- New tools are in development

## Installation
```bash
# 1. Fork the repository on GitHub first
# (Click "Fork" on the repo page)

# 2. Clone your fork
git clone https://github.com/<your-username>/doc-mcp-server.git
cd doc-mcp-server

# 3. (Optional) Add upstream remote for syncing with original repo
git remote add upstream https://github.com/<original>/doc-mcp-server.git

# 4. Install dependencies
pip install -r requirements.txt
```

## Usage (Local/stdio)
This server is designed to run locally and be invoked by an MCP-compatible client via stdio.

Start the server
```py
# At the project root directory, run
python server.py
```

Connect from MCP Client (Example Config)
```json
{
  "mcpServers": {
    "doc-mcp-server": {
      "command": "python",
      "args": ["server.py"]
    }
  }
}
```
## Development
The codebase is structured to facilitate easy development and extension.

### Add a new tool
1. Create a new function in `tools` directory that implements the desired functionality.
2. Register it in the MCP server
3. Ensure input/output follows structured format

## Testing
This project uses `pytest` for validation.

Run tests with:
```py
pytest
```

### What is tested
- Tool functionality
- Input validation
- Structure consistency checks

## Future Work
Planned improvements for this MCP server:

- Add more document analysis tools
- Improve validation with deeper structural rules
- Support multi-repository scanning
- Expand structured outputs for agent workflows
- Explore additional MCP transport options beyond stdio

### Contribution
Contributions are welcome, especially around:
- New MCP tools
- Enhancing output structure
- The use of resource and prompt decorators (`@mcp.resource` and `@mcp.prompt`)

#### How to contribute
1. Fork the repository
2. Create a new branch for your feature or fix
3. Implement your changes
4. Run tests to ensure everything works
5. Submit a pull request with a clear description of your changes
