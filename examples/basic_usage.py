#!/usr/bin/env python3
"""
Basic usage examples for the connect-postgres utility.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from connect_postgres import PostgreSQLConnector, ConnectionError, ConfigurationError


def main():
    """Demonstrate basic usage of the PostgreSQL connector."""
    
    print("=== PostgreSQL Connector Examples ===\n")
    
    try:
        # Example 1: Auto-detect environment
        print("1. Auto-detecting environment...")
        connector = PostgreSQLConnector()
        
        # Get connection info
        info = connector.get_connection_info()
        print(f"Environment: {info['environment']}")
        print(f"Host: {info['host']}:{info['port']}")
        print(f"Database: {info['database']}")
        print(f"Username: {info['username']}")
        print()
        
        # Example 2: Using context manager (recommended)
        print("2. Using context manager...")
        with connector as conn:
            # Simple query
            result = connector.execute_query("SELECT version()", fetch='one')
            print(f"PostgreSQL Version: {result['version']}")
            
            # Query with parameters
            tables = connector.execute_query("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s
                LIMIT 5
            """, ('public',))
            
            print("Available tables:")
            for table in tables:
                print(f"  - {table['table_name']}")
        
        print()
        
        # Example 3: Manual connection management
        print("3. Manual connection management...")
        conn = connector.connect()
        print(f"Connected: {connector.is_connected()}")
        
        with connector.get_cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user")
            db_info = cursor.fetchone()
            print(f"Current database: {db_info['current_database']}")
            print(f"Current user: {db_info['current_user']}")
        
        connector.disconnect()
        print(f"Connected: {connector.is_connected()}")
        print()
        
        # Example 4: Specify environment explicitly
        print("4. Explicitly setting environment...")
        local_connector = PostgreSQLConnector(environment='local')
        local_info = local_connector.get_connection_info()
        print(f"Local environment configured for: {local_info['host']}")
        
    except ConfigurationError as e:
        print(f"Configuration Error: {e}")
        print("\nMake sure you have:")
        print("- config/database.properties file for local environment")
        print("- Or proper Vault configuration for production environment")
        
    except ConnectionError as e:
        print(f"Connection Error: {e}")
        print("\nMake sure:")
        print("- PostgreSQL server is running and accessible")
        print("- Credentials are correct")
        print("- Network connectivity is available")
        
    except Exception as e:
        print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main() 