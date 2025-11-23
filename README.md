# Oracle MCP Server

A Model Context Protocol (MCP) server for Oracle 19c databases. This server enables AI agents (like Claude) to interact with Oracle databases through MCP, allowing them to execute queries, inspect schemas, and retrieve data directly.

## Features

- **Execute SQL Queries**: Run SELECT queries and get results in JSON format
- **Schema Inspection**: List tables, describe table structures, and preview data
- **TNS Alias Support**: Works with your existing Oracle TNS configuration
- **Connection Pooling**: Efficient database connection management
- **Read-Only Mode**: Optional safety mode that restricts operations to SELECT queries only
- **Secure Configuration**: Environment-based credential management

## Prerequisites

- Python 3.10 or higher
- Oracle 19c database (or compatible version)
- Oracle TNS configuration (tnsnames.ora) or direct connection string

## Installation

### From PyPI (once published)

```bash
pip install oracle-mcp
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/oracle-mcp.git
cd oracle-mcp

# Install in development mode
pip install -e .
```

## Configuration

### 1. Set up Environment Variables

Create a `.env` file in your project directory or set environment variables:

```bash
# Required
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
ORACLE_DSN=your_tns_alias  # e.g., FC1070 or hostname:1521/service_name

# Optional
ORACLE_POOL_MIN=2
ORACLE_POOL_MAX=10
QUERY_TIMEOUT=30
READ_ONLY_MODE=false
```

**For TNS Alias (Recommended):**
If you're using TNS aliases (like in SQL Developer), set `ORACLE_DSN` to your TNS alias name (e.g., `FC1070`). Ensure your `tnsnames.ora` file is properly configured and accessible.

**For Direct Connection:**
Alternatively, use a direct connection string: `hostname:1521/service_name`

### 2. Configure MCP Client

Add the Oracle MCP server to your MCP client configuration. For Claude Desktop, edit the config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "oracle": {
      "command": "oracle-mcp",
      "env": {
        "ORACLE_USER": "your_username",
        "ORACLE_PASSWORD": "your_password",
        "ORACLE_DSN": "FC1070"
      }
    }
  }
}
```

**Security Note:** For better security, use environment variables instead of hardcoding credentials:

```json
{
  "mcpServers": {
    "oracle": {
      "command": "oracle-mcp",
      "env": {
        "ORACLE_USER": "${ORACLE_USER}",
        "ORACLE_PASSWORD": "${ORACLE_PASSWORD}",
        "ORACLE_DSN": "${ORACLE_DSN}"
      }
    }
  }
}
```

Then set these environment variables in your system.

## Usage

Once configured, the Oracle MCP server provides the following tools to AI agents:

### Tools

1. **execute_query** - Execute SELECT queries
   ```
   Execute a SQL query:
   SELECT * FROM employees WHERE department = 'IT'
   ```

2. **list_tables** - List all tables and views
   ```
   Show me all tables in the database
   ```

3. **describe_table** - Get table structure
   ```
   Describe the structure of the employees table
   ```

4. **preview_table** - Get sample data from a table
   ```
   Show me a preview of the employees table
   ```

5. **execute_dml** - Execute INSERT/UPDATE/DELETE (if read-only mode is disabled)
   ```
   Insert a new employee record
   ```

### Resources

- **oracle://connection** - View database connection information
- **oracle://schema** - View schema metadata

## Example Interactions

With the MCP server running, you can ask Claude (or any MCP-compatible AI agent):

- "What tables are available in the database?"
- "Show me the structure of the EMPLOYEES table"
- "Run a query to find all employees in the IT department"
- "Get a sample of data from the ORDERS table"
- "What's the total count of records in CUSTOMERS?"

The AI agent will use the appropriate MCP tools to interact with your Oracle database and provide results.

## Development

### Project Structure

```
oracle-mcp/
├── src/oracle_mcp/
│   ├── __init__.py       # Package initialization
│   ├── server.py         # MCP server implementation
│   ├── oracle_client.py  # Oracle database client
│   └── config.py         # Configuration management
├── tests/                # Test files
├── pyproject.toml        # Package configuration
└── README.md            # This file
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Building for Distribution

```bash
# Install build tools
pip install build

# Build the package
python -m build
```

## Troubleshooting

### TNS Configuration Issues

If you encounter "TNS:could not resolve the connect identifier" errors:

1. Verify your `tnsnames.ora` file location
2. Check that `ORACLE_DSN` matches an entry in your `tnsnames.ora`
3. Ensure `TNS_ADMIN` environment variable points to the directory containing `tnsnames.ora`
4. Try using a direct connection string instead: `hostname:1521/service_name`

### Connection Errors

- Verify database credentials are correct
- Check that the database is accessible from your network
- Ensure Oracle database is running and accepting connections
- Review firewall rules if connecting remotely

### Permission Issues

- Ensure the database user has appropriate SELECT permissions
- For DML operations, ensure write permissions are granted
- Check that the user can access the required schemas

## Security Best Practices

1. **Never commit credentials** - Use environment variables or secure vaults
2. **Use read-only mode** when possible - Set `READ_ONLY_MODE=true`
3. **Limit database permissions** - Grant only necessary privileges to the database user
4. **Use dedicated database users** - Create specific users for AI agent access
5. **Monitor queries** - Review query logs regularly
6. **Set query timeouts** - Prevent long-running queries with `QUERY_TIMEOUT`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with the [Model Context Protocol SDK](https://github.com/modelcontextprotocol/python-sdk)
- Uses [python-oracledb](https://oracle.github.io/python-oracledb/) for Oracle connectivity

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/yourusername/oracle-mcp).
