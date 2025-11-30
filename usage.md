# Oracle MCP Server - Usage Guide

Quick guide to install and configure Oracle MCP server for Claude Desktop and GitHub Copilot.

## Installation

Install the Oracle MCP server using pip:

```bash
pip install git+https://github.com/Akshay-Quorum2145/Oracle-MCP
```

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
      "command": "oracle-mcp",
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
      "command": "oracle-mcp",
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
      "command": "oracle-mcp",
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
      "command": "oracle-mcp",
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

## Setup for GitHub Copilot

### 1. Create Copilot Configuration

GitHub Copilot uses the same MCP configuration format. Create or edit the configuration file:

- **VS Code**: Create `.vscode/mcp.json` in your workspace
- **Global**: `~/.config/github-copilot/mcp.json` (macOS/Linux) or `%APPDATA%\GitHub Copilot\mcp.json` (Windows)

### 2. Add Configuration

```json
{
	"servers": {
	    "oracle": {
        "command": "oracle-mcp",
        "env": {
            "ORACLE_USER": "FCOWNER",
            "ORACLE_PASSWORD": "Fc_0wner",
            "ORACLE_DSN": "FC1070"
            }
        }
	},
	"inputs": []
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
Requires `tnsnames.ora` configuration.

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

### Server Not Found
- Verify `oracle-mcp` is installed: `pip show oracle-mcp`
- Check that Python's Scripts directory is in PATH

### Connection Failed
- Verify database credentials
- Check database is accessible from your network
- Test connection with SQL Developer or similar tool

### TNS Error
- Verify `tnsnames.ora` location
- Check TNS alias exists in `tnsnames.ora`
- Try using direct connection string instead

### Permission Denied
- Ensure database user has SELECT permission
- For DML operations, check write permissions
- Verify user can access required schemas

## Support

For issues and questions, visit the [GitHub repository](https://github.com/yourusername/oracle-mcp).
