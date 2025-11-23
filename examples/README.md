# Oracle MCP Configuration Examples

This directory contains example configuration files for using the Oracle MCP server.

## Claude Desktop Configuration

To use Oracle MCP with Claude Desktop, add the configuration to your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

### Option 1: Direct Configuration (Less Secure)

Copy the contents of `mcp_config.json` into your Claude Desktop config file, replacing the placeholder values:

```json
{
  "mcpServers": {
    "oracle": {
      "command": "oracle-mcp",
      "env": {
        "ORACLE_USER": "your_username",
        "ORACLE_PASSWORD": "your_actual_password",
        "ORACLE_DSN": "your_tns_alias"
      }
    }
  }
}
```

### Option 2: Environment Variables (More Secure)

Set environment variables in your system and reference them in the config:

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

Then set these in your system:
- Windows: Use System Properties > Environment Variables
- macOS/Linux: Add to `~/.bashrc`, `~/.zshrc`, or `~/.profile`

### Option 3: Using Python Executable Directly

If `oracle-mcp` command is not in PATH:

```json
{
  "mcpServers": {
    "oracle": {
      "command": "python",
      "args": ["-m", "oracle_mcp.server"],
      "env": {
        "ORACLE_USER": "your_username",
        "ORACLE_PASSWORD": "your_password",
        "ORACLE_DSN": "your_tns_alias"
      }
    }
  }
}
```

## Additional Configuration Options

You can add optional environment variables to customize behavior:

```json
{
  "mcpServers": {
    "oracle": {
      "command": "oracle-mcp",
      "env": {
        "ORACLE_USER": "your_username",
        "ORACLE_PASSWORD": "your_password",
        "ORACLE_DSN": "your_tns_alias",
        "ORACLE_POOL_MIN": "2",
        "ORACLE_POOL_MAX": "10",
        "QUERY_TIMEOUT": "30",
        "READ_ONLY_MODE": "true"
      }
    }
  }
}
```

### Configuration Parameters

- `ORACLE_USER`: Database username (required)
- `ORACLE_PASSWORD`: Database password (required)
- `ORACLE_DSN`: TNS alias or connection string (required)
- `ORACLE_POOL_MIN`: Minimum connections in pool (optional, default: 2)
- `ORACLE_POOL_MAX`: Maximum connections in pool (optional, default: 10)
- `QUERY_TIMEOUT`: Query timeout in seconds (optional, default: 30)
- `READ_ONLY_MODE`: Set to "true" to allow only SELECT queries (optional, default: false)

## Connection String Formats

### TNS Alias (Recommended)
```
ORACLE_DSN=FC1070
```
Requires `tnsnames.ora` to be configured.

### Easy Connect
```
ORACLE_DSN=hostname:1521/service_name
```
Example: `ORACLE_DSN=localhost:1521/ORCLPDB`

### Full Connection String
```
ORACLE_DSN=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=hostname)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=service_name)))
```

## Testing Your Configuration

After setting up the configuration:

1. Restart Claude Desktop
2. Look for the Oracle MCP server in the available tools
3. Try asking Claude: "What tables are available in the Oracle database?"

## Troubleshooting

- **Server not appearing:** Check that `oracle-mcp` is installed and in PATH
- **Connection errors:** Verify credentials and network connectivity
- **TNS errors:** Check that tnsnames.ora is accessible and contains the alias
- **Permission errors:** Ensure database user has necessary privileges

For more help, see the main README.md file.
