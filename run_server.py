#!/usr/bin/env python
"""Wrapper script to run Oracle MCP server"""
import sys
from oracle_mcp.server import main

if __name__ == "__main__":
    sys.exit(main())
