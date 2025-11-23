#!/usr/bin/env python3
"""
Simple test script to verify Oracle database connection.
"""

import sys
from oracle_mcp.config import OracleConfig
from oracle_mcp.oracle_client import OracleClient


def main():
    print("=" * 60)
    print("Oracle MCP Connection Test")
    print("=" * 60)
    print()

    try:
        # Load configuration
        print("1. Loading configuration from .env file...")
        config = OracleConfig.from_env()
        print("   [OK] Configuration loaded successfully")
        print(f"   - User: {config.user}")
        print(f"   - DSN: {config.dsn}")
        print(f"   - Read-only mode: {config.read_only_mode}")
        print()

        # Validate configuration
        print("2. Validating configuration...")
        config.validate()
        print("   [OK] Configuration is valid")
        print()

        # Initialize Oracle client
        print("3. Initializing Oracle client...")
        client = OracleClient(config)
        print("   [OK] Oracle client initialized")
        print()

        # Test connection
        print("4. Testing database connection...")
        conn_info = client.test_connection()

        if conn_info["status"] == "connected":
            print("   [OK] Connection successful!")
            print()
            print("   Connection Details:")
            print(f"   - Database: {conn_info['database_name']}")
            print(f"   - Version: {conn_info['database_version']}")
            print(f"   - Connected as: {conn_info['connected_user']}")
            print(f"   - DSN: {conn_info['dsn']}")
            print()

            # Try listing tables
            print("5. Listing tables in schema...")
            tables = client.get_tables()
            print(f"   [OK] Found {len(tables)} tables/views")

            if tables:
                print()
                print("   First 10 tables/views:")
                for i, table in enumerate(tables[:10], 1):
                    print(f"   {i}. {table['table_name']} ({table['table_type']})")

                if len(tables) > 10:
                    print(f"   ... and {len(tables) - 10} more")
            print()

            # Try a simple query
            print("6. Testing query execution...")
            result = client.execute_query("SELECT 1 as test_col, 'Hello from Oracle!' as message FROM dual")
            print("   [OK] Query executed successfully")
            print(f"   - Columns: {result['columns']}")
            print(f"   - Row count: {result['row_count']}")
            print(f"   - Result: {result['rows'][0]}")
            print()

            print("=" * 60)
            print("[SUCCESS] ALL TESTS PASSED!")
            print("=" * 60)
            print()
            print("Your Oracle MCP server is ready to use!")
            print()

            # Close connection
            client.close()
            return 0

        else:
            print(f"   [ERROR] Connection failed: {conn_info.get('error')}")
            return 1

    except ValueError as e:
        print(f"   [ERROR] Configuration error: {e}")
        print()
        print("Please check your .env file and ensure all required variables are set.")
        return 1

    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
