"""
Configuration management for Oracle MCP Server.
Loads settings from environment variables.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class OracleConfig:
    """Oracle database configuration."""

    user: str
    password: str
    dsn: str
    pool_min: int = 2
    pool_max: int = 10
    query_timeout: int = 30
    read_only_mode: bool = False

    @classmethod
    def from_env(cls) -> "OracleConfig":
        """
        Load configuration from environment variables.

        Required environment variables:
        - ORACLE_USER: Database username
        - ORACLE_PASSWORD: Database password
        - ORACLE_DSN: TNS alias or connection string (host:port/service)

        Optional environment variables:
        - ORACLE_POOL_MIN: Minimum connections in pool (default: 2)
        - ORACLE_POOL_MAX: Maximum connections in pool (default: 10)
        - QUERY_TIMEOUT: Query timeout in seconds (default: 30)
        - READ_ONLY_MODE: Allow only SELECT queries (default: false)

        Returns:
            OracleConfig: Configuration object

        Raises:
            ValueError: If required environment variables are missing
        """
        user = os.getenv("ORACLE_USER")
        password = os.getenv("ORACLE_PASSWORD")
        dsn = os.getenv("ORACLE_DSN")

        if not user:
            raise ValueError("ORACLE_USER environment variable is required")
        if not password:
            raise ValueError("ORACLE_PASSWORD environment variable is required")
        if not dsn:
            raise ValueError("ORACLE_DSN environment variable is required")

        return cls(
            user=user,
            password=password,
            dsn=dsn,
            pool_min=int(os.getenv("ORACLE_POOL_MIN", "2")),
            pool_max=int(os.getenv("ORACLE_POOL_MAX", "10")),
            query_timeout=int(os.getenv("QUERY_TIMEOUT", "30")),
            read_only_mode=os.getenv("READ_ONLY_MODE", "false").lower() == "true",
        )

    def get_connection_string(self) -> str:
        """
        Get a safe connection string for logging (without password).

        Returns:
            str: Connection string with masked password
        """
        return f"{self.user}/***@{self.dsn}"

    def validate(self) -> None:
        """
        Validate configuration values.

        Raises:
            ValueError: If configuration values are invalid
        """
        if self.pool_min < 1:
            raise ValueError("pool_min must be at least 1")
        if self.pool_max < self.pool_min:
            raise ValueError("pool_max must be greater than or equal to pool_min")
        if self.query_timeout < 1:
            raise ValueError("query_timeout must be at least 1 second")
