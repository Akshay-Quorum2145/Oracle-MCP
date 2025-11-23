"""
Oracle database client for MCP server.
Handles connection management and query execution.
"""

import oracledb
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging
from .config import OracleConfig

logger = logging.getLogger(__name__)


class OracleClient:
    """Oracle database client with connection pooling."""

    def __init__(self, config: OracleConfig):
        """
        Initialize Oracle client with configuration.

        Args:
            config: OracleConfig object with connection details
        """
        self.config = config
        self.pool: Optional[oracledb.ConnectionPool] = None
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """
        Initialize connection pool.

        Raises:
            oracledb.DatabaseError: If connection fails
        """
        try:
            logger.info(f"Initializing connection pool for {self.config.get_connection_string()}")

            # Create connection pool using thin mode (no Oracle Client required)
            self.pool = oracledb.create_pool(
                user=self.config.user,
                password=self.config.password,
                dsn=self.config.dsn,
                min=self.config.pool_min,
                max=self.config.pool_max,
                increment=1,
            )

            logger.info("Connection pool initialized successfully")
        except oracledb.DatabaseError as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    def _convert_value(self, value: Any) -> Any:
        """
        Convert Oracle-specific types to JSON-serializable types.

        Args:
            value: Value to convert

        Returns:
            JSON-serializable value
        """
        if value is None:
            return None
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, bytes):
            # Convert BLOB/RAW to hex string
            return value.hex()
        elif isinstance(value, oracledb.LOB):
            # Read LOB content
            return value.read()
        else:
            return value

    def execute_query(self, sql: str) -> Dict[str, Any]:
        """
        Execute a SELECT query and return results.

        Args:
            sql: SQL query to execute

        Returns:
            Dict with 'columns', 'rows', and 'row_count' keys

        Raises:
            ValueError: If query is not a SELECT in read-only mode
            oracledb.DatabaseError: If query execution fails
        """
        sql_upper = sql.strip().upper()

        # Enforce read-only mode if configured
        if self.config.read_only_mode and not sql_upper.startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed in read-only mode")

        connection = None
        cursor = None

        try:
            connection = self.pool.acquire()
            cursor = connection.cursor()

            # Set query timeout
            cursor.callTimeout = self.config.query_timeout * 1000  # Convert to milliseconds

            logger.info(f"Executing query: {sql[:100]}...")
            cursor.execute(sql)

            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch all rows
            rows = cursor.fetchall()

            # Convert rows to list of dicts with proper type conversion
            result_rows = []
            for row in rows:
                result_rows.append({col: self._convert_value(val) for col, val in zip(columns, row)})

            logger.info(f"Query returned {len(result_rows)} rows")

            return {"columns": columns, "rows": result_rows, "row_count": len(result_rows)}

        except oracledb.DatabaseError as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.pool.release(connection)

    def execute_dml(self, sql: str) -> Dict[str, Any]:
        """
        Execute INSERT, UPDATE, DELETE, or DDL statement.

        Args:
            sql: SQL statement to execute

        Returns:
            Dict with 'rows_affected' and 'message' keys

        Raises:
            ValueError: If DML is attempted in read-only mode
            oracledb.DatabaseError: If statement execution fails
        """
        if self.config.read_only_mode:
            raise ValueError("DML/DDL operations are not allowed in read-only mode")

        connection = None
        cursor = None

        try:
            connection = self.pool.acquire()
            cursor = connection.cursor()

            # Set query timeout
            cursor.callTimeout = self.config.query_timeout * 1000

            logger.info(f"Executing DML/DDL: {sql[:100]}...")
            cursor.execute(sql)

            # Get rows affected
            rows_affected = cursor.rowcount

            # Commit the transaction
            connection.commit()

            logger.info(f"Statement executed successfully, {rows_affected} rows affected")

            return {
                "rows_affected": rows_affected,
                "message": f"Statement executed successfully. {rows_affected} rows affected.",
            }

        except oracledb.DatabaseError as e:
            if connection:
                connection.rollback()
            logger.error(f"DML/DDL execution failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.pool.release(connection)

    def get_tables(self, schema: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get list of tables in the schema.

        Args:
            schema: Schema name (defaults to current user)

        Returns:
            List of dicts with 'table_name' and 'table_type' keys
        """
        schema_filter = schema.upper() if schema else self.config.user.upper()

        query = """
        SELECT table_name, 'TABLE' as table_type
        FROM all_tables
        WHERE owner = :schema
        UNION ALL
        SELECT view_name as table_name, 'VIEW' as table_type
        FROM all_views
        WHERE owner = :schema
        ORDER BY table_name
        """

        connection = None
        cursor = None

        try:
            connection = self.pool.acquire()
            cursor = connection.cursor()
            cursor.execute(query, schema=schema_filter)

            tables = []
            for row in cursor:
                tables.append({"table_name": row[0], "table_type": row[1]})

            logger.info(f"Found {len(tables)} tables/views in schema {schema_filter}")
            return tables

        except oracledb.DatabaseError as e:
            logger.error(f"Failed to get tables: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.pool.release(connection)

    def describe_table(self, table_name: str, schema: Optional[str] = None) -> Dict[str, Any]:
        """
        Get column information for a table.

        Args:
            table_name: Name of the table
            schema: Schema name (defaults to current user)

        Returns:
            Dict with 'table_name', 'schema', and 'columns' keys
        """
        schema_filter = schema.upper() if schema else self.config.user.upper()
        table_upper = table_name.upper()

        query = """
        SELECT
            column_name,
            data_type,
            data_length,
            data_precision,
            data_scale,
            nullable,
            column_id,
            data_default
        FROM all_tab_columns
        WHERE owner = :schema
        AND table_name = :table_name
        ORDER BY column_id
        """

        connection = None
        cursor = None

        try:
            connection = self.pool.acquire()
            cursor = connection.cursor()
            cursor.execute(query, schema=schema_filter, table_name=table_upper)

            columns = []
            for row in cursor:
                col_info = {
                    "column_name": row[0],
                    "data_type": row[1],
                    "length": row[2],
                    "precision": row[3],
                    "scale": row[4],
                    "nullable": row[5] == "Y",
                    "position": row[6],
                    "default_value": row[7].strip() if row[7] else None,
                }
                columns.append(col_info)

            if not columns:
                raise ValueError(f"Table {schema_filter}.{table_upper} not found")

            logger.info(f"Described table {schema_filter}.{table_upper} with {len(columns)} columns")

            return {"table_name": table_upper, "schema": schema_filter, "columns": columns}

        except oracledb.DatabaseError as e:
            logger.error(f"Failed to describe table: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.pool.release(connection)

    def get_table_sample(
        self, table_name: str, limit: int = 10, schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get sample rows from a table.

        Args:
            table_name: Name of the table
            limit: Maximum number of rows to return
            schema: Schema name (defaults to current user)

        Returns:
            Dict with query results
        """
        schema_filter = schema.upper() if schema else self.config.user.upper()
        table_upper = table_name.upper()

        # Use FETCH FIRST for Oracle 12c+
        query = f"""
        SELECT * FROM {schema_filter}.{table_upper}
        FETCH FIRST {limit} ROWS ONLY
        """

        return self.execute_query(query)

    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection and return connection info.

        Returns:
            Dict with connection status and database information
        """
        connection = None
        cursor = None

        try:
            connection = self.pool.acquire()
            cursor = connection.cursor()

            # Get database version
            cursor.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
            version = cursor.fetchone()[0]

            # Get current user and database
            cursor.execute("SELECT user, sys_context('USERENV', 'DB_NAME') FROM dual")
            user, db_name = cursor.fetchone()

            logger.info("Connection test successful")

            return {
                "status": "connected",
                "database_version": version,
                "connected_user": user,
                "database_name": db_name,
                "dsn": self.config.dsn,
                "read_only_mode": self.config.read_only_mode,
            }

        except oracledb.DatabaseError as e:
            logger.error(f"Connection test failed: {e}")
            return {"status": "error", "error": str(e)}
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.pool.release(connection)

    def close(self) -> None:
        """Close the connection pool."""
        if self.pool:
            logger.info("Closing connection pool")
            self.pool.close()
            self.pool = None
