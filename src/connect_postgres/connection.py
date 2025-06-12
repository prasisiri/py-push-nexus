"""PostgreSQL connection management."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any, Union
from contextlib import contextmanager
import logging

from .config import Config
from .exceptions import ConnectionError, ConfigurationError

logger = logging.getLogger(__name__)


class PostgreSQLConnector:
    """PostgreSQL connection manager with environment-aware credential handling."""
    
    def __init__(self, environment: Optional[str] = None, config: Optional[Config] = None):
        """
        Initialize PostgreSQL connector.
        
        Args:
            environment: Environment type ('local', 'prod'). Auto-detected if None.
            config: Pre-configured Config instance. Creates new one if None.
        """
        self.config = config or Config(environment)
        self._connection: Optional[psycopg2.extensions.connection] = None
        self._credentials: Optional[Dict[str, Any]] = None
        
        # Load and validate credentials
        try:
            self._credentials = self.config.get_credentials()
            if not self.config.validate_credentials(self._credentials):
                raise ConfigurationError("Invalid or incomplete credentials")
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            raise
    
    def connect(self) -> psycopg2.extensions.connection:
        """
        Establish connection to PostgreSQL database.
        
        Returns:
            psycopg2 connection object
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._connection and not self._connection.closed:
            return self._connection
        
        try:
            self._connection = psycopg2.connect(
                host=self._credentials['host'],
                port=self._credentials['port'],
                database=self._credentials['database'],
                user=self._credentials['username'],
                password=self._credentials['password'],
                sslmode=self._credentials.get('ssl_mode', 'require'),
                connect_timeout=30,
                cursor_factory=RealDictCursor
            )
            
            # Test connection
            with self._connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            
            logger.info(f"Successfully connected to PostgreSQL at {self._credentials['host']}:{self._credentials['port']}")
            return self._connection
            
        except psycopg2.Error as e:
            logger.error(f"PostgreSQL connection error: {e}")
            raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            raise ConnectionError(f"Unexpected connection error: {e}")
    
    def disconnect(self) -> None:
        """Close the database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("PostgreSQL connection closed")
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self._connection is not None and not self._connection.closed
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Usage:
            with connector.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM table")
        """
        connection = self.connect()
        try:
            yield connection
        finally:
            # Don't close connection in context manager - let the user manage it
            pass
    
    @contextmanager
    def get_cursor(self, commit: bool = True):
        """
        Context manager for database cursors with automatic transaction handling.
        
        Args:
            commit: Whether to commit the transaction automatically
            
        Usage:
            with connector.get_cursor() as cursor:
                cursor.execute("SELECT * FROM table")
                result = cursor.fetchall()
        """
        connection = self.connect()
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None, fetch: str = 'all') -> Union[list, dict, None]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: 'all', 'one', or 'none'
            
        Returns:
            Query results based on fetch parameter
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            
            if fetch == 'all':
                return cursor.fetchall()
            elif fetch == 'one':
                return cursor.fetchone()
            elif fetch == 'none':
                return None
            else:
                raise ValueError("fetch must be 'all', 'one', or 'none'")
    
    def execute_many(self, query: str, params_list: list) -> None:
        """
        Execute a query multiple times with different parameters.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information (without sensitive data)."""
        if not self._credentials:
            return {}
        
        return {
            'host': self._credentials['host'],
            'port': self._credentials['port'],
            'database': self._credentials['database'],
            'username': self._credentials['username'],
            'ssl_mode': self._credentials.get('ssl_mode', 'require'),
            'environment': self.config.environment,
            'connected': self.is_connected()
        }
    
    def __enter__(self):
        """Support for context manager protocol."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager protocol."""
        self.disconnect()
    
    def __del__(self):
        """Cleanup connection on object destruction."""
        try:
            self.disconnect()
        except Exception:
            pass 