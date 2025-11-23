"""
Oracle MCP Server

Provides MCP tools and resources for interacting with Oracle databases.
"""

import logging
import sys
import asyncio
from typing import Any
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import OracleConfig
from .oracle_client import OracleClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # MCP uses stdout for protocol, so log to stderr
)
logger = logging.getLogger(__name__)

# Initialize server
app = Server("oracle-mcp")

# Global client instance (initialized in main)
oracle_client: OracleClient = None


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """
    List available MCP tools.

    Returns:
        List of tool definitions
    """
    return [
        types.Tool(
            name="execute_query",
            description="Execute a SQL SELECT query and return results. Returns columns and rows as JSON.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute",
                    }
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="list_tables",
            description="List all tables and views in the connected schema or specified schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema": {
                        "type": "string",
                        "description": "Schema name (optional, defaults to connected user)",
                    }
                },
            },
        ),
        types.Tool(
            name="describe_table",
            description="Get detailed column information for a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to describe",
                    },
                    "schema": {
                        "type": "string",
                        "description": "Schema name (optional, defaults to connected user)",
                    },
                },
                "required": ["table_name"],
            },
        ),
        types.Tool(
            name="preview_table",
            description="Get a sample of rows from a table (default: 10 rows)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to preview",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return (default: 10)",
                        "default": 10,
                    },
                    "schema": {
                        "type": "string",
                        "description": "Schema name (optional, defaults to connected user)",
                    },
                },
                "required": ["table_name"],
            },
        ),
        types.Tool(
            name="execute_dml",
            description="Execute INSERT, UPDATE, DELETE, or DDL statements. Only available if read-only mode is disabled.",
            inputSchema={
                "type": "object",
                "properties": {
                    "statement": {
                        "type": "string",
                        "description": "SQL DML or DDL statement to execute",
                    }
                },
                "required": ["statement"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
    """
    Handle tool calls from MCP client.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        List of text content responses
    """
    try:
        if name == "execute_query":
            query = arguments.get("query")
            if not query:
                raise ValueError("query parameter is required")

            result = oracle_client.execute_query(query)

            # Format response
            response = f"Query returned {result['row_count']} rows\n\n"
            response += f"Columns: {', '.join(result['columns'])}\n\n"

            if result['rows']:
                response += "Results:\n"
                for i, row in enumerate(result['rows'][:100], 1):  # Limit display to 100 rows
                    response += f"{i}. {row}\n"

                if result['row_count'] > 100:
                    response += f"\n... ({result['row_count'] - 100} more rows not shown)\n"

            return [types.TextContent(type="text", text=response)]

        elif name == "list_tables":
            schema = arguments.get("schema")
            tables = oracle_client.get_tables(schema)

            response = f"Found {len(tables)} tables/views:\n\n"
            for table in tables:
                response += f"- {table['table_name']} ({table['table_type']})\n"

            return [types.TextContent(type="text", text=response)]

        elif name == "describe_table":
            table_name = arguments.get("table_name")
            schema = arguments.get("schema")

            if not table_name:
                raise ValueError("table_name parameter is required")

            result = oracle_client.describe_table(table_name, schema)

            response = f"Table: {result['schema']}.{result['table_name']}\n\n"
            response += f"Columns ({len(result['columns'])}):\n\n"

            for col in result['columns']:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                type_info = col['data_type']

                if col['precision']:
                    type_info += f"({col['precision']}"
                    if col['scale']:
                        type_info += f",{col['scale']}"
                    type_info += ")"
                elif col['length']:
                    type_info += f"({col['length']})"

                response += f"{col['position']}. {col['column_name']}: {type_info} {nullable}"

                if col['default_value']:
                    response += f" DEFAULT {col['default_value']}"

                response += "\n"

            return [types.TextContent(type="text", text=response)]

        elif name == "preview_table":
            table_name = arguments.get("table_name")
            limit = arguments.get("limit", 10)
            schema = arguments.get("schema")

            if not table_name:
                raise ValueError("table_name parameter is required")

            result = oracle_client.get_table_sample(table_name, limit, schema)

            response = f"Preview of {table_name} (showing {result['row_count']} rows):\n\n"
            response += f"Columns: {', '.join(result['columns'])}\n\n"

            for i, row in enumerate(result['rows'], 1):
                response += f"{i}. {row}\n"

            return [types.TextContent(type="text", text=response)]

        elif name == "execute_dml":
            statement = arguments.get("statement")
            if not statement:
                raise ValueError("statement parameter is required")

            result = oracle_client.execute_dml(statement)

            return [types.TextContent(type="text", text=result['message'])]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        error_msg = f"Error: {str(e)}"
        return [types.TextContent(type="text", text=error_msg)]


@app.list_resources()
async def list_resources() -> list[types.Resource]:
    """
    List available MCP resources.

    Returns:
        List of resource definitions
    """
    return [
        types.Resource(
            uri="oracle://connection",
            name="Database Connection Info",
            mimeType="application/json",
            description="Information about the current database connection",
        ),
        types.Resource(
            uri="oracle://schema",
            name="Schema Information",
            mimeType="application/json",
            description="Information about the connected database schema",
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """
    Read a resource by URI.

    Args:
        uri: Resource URI

    Returns:
        Resource content as string
    """
    try:
        if uri == "oracle://connection":
            conn_info = oracle_client.test_connection()
            import json

            return json.dumps(conn_info, indent=2)

        elif uri == "oracle://schema":
            tables = oracle_client.get_tables()
            import json

            return json.dumps({"table_count": len(tables), "tables": tables}, indent=2)

        else:
            raise ValueError(f"Unknown resource: {uri}")

    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        raise


async def run_server():
    """Run the MCP server."""
    global oracle_client

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = OracleConfig.from_env()
        config.validate()

        logger.info(f"Connecting to Oracle database: {config.get_connection_string()}")
        logger.info(f"Read-only mode: {config.read_only_mode}")

        # Initialize Oracle client
        oracle_client = OracleClient(config)

        # Test connection
        conn_info = oracle_client.test_connection()
        if conn_info["status"] == "connected":
            logger.info(f"Successfully connected to {conn_info['database_name']}")
            logger.info(f"Database version: {conn_info['database_version']}")
        else:
            logger.error(f"Connection test failed: {conn_info.get('error')}")
            raise Exception("Failed to connect to database")

        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Oracle MCP Server is running...")
            await app.run(read_stream, write_stream, app.create_initialization_options())

    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        if oracle_client:
            oracle_client.close()


def main():
    """Main entry point for the server."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
