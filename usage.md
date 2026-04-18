# Oracle MCP Server - Usage Guide

Quick guide to install and configure Oracle MCP server for Claude Desktop and GitHub Copilot.

## Installation

Install the Oracle MCP server using pip:

```bash
pip install git+https://github.com/Akshay-Quorum2145/Oracle-MCP
```

Or if published to PyPI:

```bash
pip install oracle-mcp
```

Verify installation:

```bash
python -m oracle_mcp --help
```

## How to Invoke the Server

Two ways to invoke the MCP server:

| Command | Pros | Cons |
|---|---|---|
| `python -m oracle_mcp` **(recommended)** | Works anywhere Python is on PATH. Portable across Claude Desktop, Claude Code, GitHub Copilot, VS Code. | Slightly longer. |
| `oracle-mcp` | Short. | Only works if Python's `Scripts/` dir (e.g. `%APPDATA%\Python\Python3XX\Scripts` on Windows) is on PATH **and** your MCP client inherits that PATH. Fails with errors like `oracle-mcp required by oracle-mcp is not found` otherwise. |

If in doubt, use `python -m oracle_mcp`.

## Setup for Claude Desktop

### 1. Locate Configuration File

Find your Claude Desktop config file:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Add Oracle MCP Configuration

Edit the config file and add the following:

```json
{
  "mcpServers": {
    "oracle": {
      "command": "python",
      "args": ["-m", "oracle_mcp"],
      "env": {
        "ORACLE_USER": "your_username",
        "ORACLE_PASSWORD": "your_password",
        "ORACLE_DSN": "your_tns_alias_or_connection_string"
      }
    }
  }
}
```

**Example with TNS alias:**
```json
{
  "mcpServers": {
    "oracle": {
      "command": "python",
      "args": ["-m", "oracle_mcp"],
      "env": {
        "ORACLE_USER": "DBUSER",
        "ORACLE_PASSWORD": "mypassword",
        "ORACLE_DSN": "ORCL"
      }
    }
  }
}
```

**Example with direct connection:**
```json
{
  "mcpServers": {
    "oracle": {
      "command": "python",
      "args": ["-m", "oracle_mcp"],
      "env": {
        "ORACLE_USER": "DBUSER",
        "ORACLE_PASSWORD": "mypassword",
        "ORACLE_DSN": "localhost:1521/ORCLPDB"
      }
    }
  }
}
```

### 3. Optional Configuration

Add optional parameters for advanced configuration:

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
        "READ_ONLY_MODE": "true",
        "QUERY_TIMEOUT": "30",
        "ORACLE_POOL_MIN": "2",
        "ORACLE_POOL_MAX": "10"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

Close and restart Claude Desktop to load the new configuration.

### 5. Verify Setup

In Claude Desktop, try asking:
- "What tables are available in the database?"
- "Show me the structure of the EMPLOYEES table"

## Setup for GitHub Copilot (VS Code)

GitHub Copilot's MCP support uses a slightly different config format — note `servers` (not `mcpServers`) and the required `type: "stdio"` field.

### 1. Create Copilot MCP Configuration

Create one of the following files:

- **Workspace**: `.vscode/mcp.json` in your workspace root
- **User-global**: Open the Command Palette (`Ctrl+Shift+P`) → `MCP: Open User Configuration`, or edit `~/.config/github-copilot/mcp.json` (macOS/Linux) / `%APPDATA%\GitHub Copilot\mcp.json` (Windows)

### 2. Add Configuration

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
        "ORACLE_DSN": "your_tns_alias_or_connection_string"
      }
    }
  }
}
```

### 3. Restart VS Code

Reload VS Code to apply the configuration.

### 4. Verify Setup

Use GitHub Copilot chat and ask:
- "List all tables in the Oracle database"
- "Query the EMPLOYEES table"

## Connection String Formats

### TNS Alias (Recommended)
```
ORACLE_DSN=ORCL
```
Requires `tnsnames.ora` configuration. Make sure `TNS_ADMIN` env variable points to the directory containing it, or place it in the default Oracle location.

### Easy Connect
```
ORACLE_DSN=hostname:1521/service_name
```

### Full Connection String
```
ORACLE_DSN=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=hostname)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=service_name)))
```

## Available Tools

Once configured, the following tools are available:

- **execute_query** - Run SELECT queries
- **list_tables** - List all tables and views
- **describe_table** - Show table structure
- **preview_table** - Get sample data from a table
- **execute_dml** - Execute INSERT/UPDATE/DELETE (if read-only mode disabled)

## Example Queries

Ask Claude or Copilot:

- "What tables are in the database?"
- "Describe the CUSTOMERS table"
- "Show me 10 rows from the ORDERS table"
- "Count all records in EMPLOYEES"
- "Find all customers from California"

## Security Best Practices

1. **Use environment variables** instead of hardcoding credentials
2. **Enable READ_ONLY_MODE** when only queries are needed
3. **Create dedicated database users** with minimal permissions
4. **Set QUERY_TIMEOUT** to prevent long-running queries
5. **Never commit credentials** to version control

## Troubleshooting

### Error: `oracle-mcp required by oracle-mcp is not found`

This means the MCP client cannot find the `oracle-mcp` executable. It typically happens on Windows when the Python `Scripts/` directory is not inherited by the MCP client process.

**Fix:** Switch your MCP config from `"command": "oracle-mcp"` to `"command": "python", "args": ["-m", "oracle_mcp"]`. This bypasses the Scripts directory entirely.

### Server Not Found

- Verify package is installed: `pip show oracle-mcp`
- Verify Python can import it: `python -m oracle_mcp --help`
- If you're using `oracle-mcp` as the command, check that Python's `Scripts/` directory is on PATH

### Crashing on Startup with `ORACLE_USER environment variable is required`

Running the server directly from a terminal (e.g. `oracle-mcp` or `python -m oracle_mcp`) without setting env vars gives this error — that's expected. When launched by an MCP client, env vars come from the `"env"` block in the config. Make sure all three (`ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`) are present there.

### Connection Failed

- Verify database credentials
- Check database is accessible from your network
- Test connection with SQL Developer or similar tool

### TNS Error

- Verify `tnsnames.ora` location
- Check TNS alias exists in `tnsnames.ora`
- Set `TNS_ADMIN` env variable to the directory containing `tnsnames.ora`
- Try using direct connection string instead

### Permission Denied

- Ensure database user has SELECT permission
- For DML operations, check write permissions
- Verify user can access required schemas

## Support

For issues and questions, visit the [GitHub repository](https://github.com/Akshay-Quorum2145/Oracle-MCP).
