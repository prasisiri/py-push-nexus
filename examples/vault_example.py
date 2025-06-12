#!/usr/bin/env python3
"""
Example for using the connector with HashiCorp Vault in production.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from connect_postgres import PostgreSQLConnector, Config


def setup_vault_environment():
    """Set up environment variables for Vault integration."""
    
    # These would typically be set by your deployment system
    # DO NOT hardcode these in production code!
    
    print("Setting up Vault environment variables...")
    print("(In production, these would be set by your deployment system)")
    
    # Example environment setup
    os.environ['ENVIRONMENT'] = 'prod'
    os.environ['VAULT_ADDR'] = 'https://vault.example.com'
    os.environ['VAULT_TOKEN'] = 'your-vault-token'  # In prod, use proper auth
    os.environ['DB_VAULT_PATH'] = 'secret/database/postgresql'
    
    print(f"VAULT_ADDR: {os.environ.get('VAULT_ADDR')}")
    print(f"DB_VAULT_PATH: {os.environ.get('DB_VAULT_PATH')}")
    print()


def main():
    """Demonstrate Vault integration."""
    
    print("=== Vault Integration Example ===\n")
    
    # In production, these environment variables would be set by your 
    # deployment system (Kubernetes, Docker, etc.)
    setup_vault_environment()
    
    try:
        # Create connector for production environment
        connector = PostgreSQLConnector(environment='prod')
        
        print("Successfully initialized connector with Vault credentials")
        
        # Get connection info (no sensitive data exposed)
        info = connector.get_connection_info()
        print(f"Environment: {info['environment']}")
        print(f"Host: {info['host']}:{info['port']}")
        print(f"Database: {info['database']}")
        print(f"SSL Mode: {info['ssl_mode']}")
        print()
        
        # Test connection
        with connector as conn:
            result = connector.execute_query(
                "SELECT current_database(), current_user, version()", 
                fetch='one'
            )
            
            print("Connection successful!")
            print(f"Database: {result['current_database']}")
            print(f"User: {result['current_user']}")
            print(f"Version: {result['version'][:50]}...")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nFor this example to work, you need:")
        print("1. A running Vault instance")
        print("2. Valid Vault token with read access")
        print("3. Database credentials stored in Vault at the specified path")
        print("\nVault secret should contain:")
        print("  host: your-rds-instance.amazonaws.com")
        print("  port: 5432")
        print("  database: your_database")
        print("  username: your_username")
        print("  password: your_password")
        print("  ssl_mode: require")


if __name__ == "__main__":
    main() 