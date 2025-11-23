"""
Oracle MCP Server

A Model Context Protocol (MCP) server for Oracle 19c databases.
Allows AI agents to execute queries and inspect database schemas.
"""

__version__ = "0.1.0"
__author__ = "Akshay Bachkar"

from .server import app

__all__ = ["app"]
