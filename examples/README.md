# Oracle MCP Configuration Examples

This directory contains example configuration files for using the Oracle MCP server.

Files:
- `mcp_config.json` — Claude Desktop config (uses `mcpServers`)
- `copilot_mcp_config.json` — GitHub Copilot / VS Code config (uses `servers` + `type: stdio`)

## How to Invoke the Server

Two ways:

- **`python -m oracle_mcp`** (recommended) — works anywhere Python is on PATH. Portable and reliable.
- **`oracle-mcp`** — shorter, but requires Python's `Scripts/` directory on PATH *and* the MCP client to inherit it. On some Windows setups this fails with `oracle-mcp required by oracle-mcp is not found`.

The examples below use the recommended `python -m oracle_mcp` form.

## Claude Desktop Configuration

Add the configuration to your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

### Option 1: Direct Configuration (Less Secure)

Copy the contents of `mcp_config.json` into your Claude Desktop config file, replacing the placeholder values:

```json
{
  "mcpServers": {
    "oracle": {
      "command": "python",
      "args": ["-m", "oracle_mcp"],
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
      "command": "python",
      "args": ["-m", "oracle_mcp"],
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

### Option 3: Using the `oracle-mcp` Console Script

If the `oracle-mcp` command is on PATH and your MCP client can find it:

```json
{
  "mcpServers": {
    "oracle": {
      "command": "oracle-mcp",
      "env": {
        "ORACLE_USER": "your_username",
        "ORACLE_PASSWORD": "your_password",
        "ORACLE_DSN": "your_tns_alias"
      }
    }
  }
}
```

### Option 4: Full Path to Python Executable

If you installed the server in a specific virtual environment, you can point directly at its Python:

```json
{
  "mcpServers": {
    "oracle": {
      "command": "C:/path/to/venv/Scripts/python.exe",
      "args": ["-m", "oracle_mcp"],
      "env": {
        "ORACLE_USER": "your_username",
        "ORACLE_PASSWORD": "your_password",
        "ORACLE_DSN": "your_tns_alias"
      }
    }
  }
}
```

## GitHub Copilot (VS Code) Configuration

Copilot uses a different format — `servers` (not `mcpServers`) and a required `type: "stdio"` field.

Create `.vscode/mcp.json` in your workspace, or open the Command Palette and run `MCP: Open User Configuration`.

Copy the contents of `copilot_mcp_config.json`:

```json
{
  "servers": {
    "oracle": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "oracle_mcp"],
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
      "command": "python",
      "args": ["-m", "oracle_mcp"],
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
Requires `tnsnames.ora` to be configured. Make sure `TNS_ADMIN` points to the directory containing it.

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

1. Restart Claude Desktop / VS Code
2. Look for the Oracle MCP server in the available tools
3. Try asking: "What tables are available in the Oracle database?"

## Troubleshooting

- **`oracle-mcp required by oracle-mcp is not found`**: Your MCP client can't find the `oracle-mcp` executable. Switch to `"command": "python", "args": ["-m", "oracle_mcp"]`.
- **Server not appearing**: Verify package is installed (`pip show oracle-mcp`) and that Python is on PATH.
- **`ORACLE_USER environment variable is required` when running manually**: Expected — the MCP client passes env vars from the config; when you run the command manually in a terminal, env vars aren't set.
- **Connection errors**: Verify credentials and network connectivity.
- **TNS errors**: Check that `tnsnames.ora` is accessible, the alias exists, and `TNS_ADMIN` is set correctly.
- **Permission errors**: Ensure database user has necessary privileges.

For more help, see the main README.md file.
