"""Configuration management for PostgreSQL connections."""

import os
import configparser
from typing import Dict, Optional
import hvac
from .exceptions import ConfigurationError, VaultError


class Config:
    """Configuration manager for PostgreSQL connections."""
    
    def __init__(self, environment: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            environment: Environment type ('local', 'prod'). 
                        If None, auto-detects from environment variables.
        """
        self.environment = environment or self._detect_environment()
        self._credentials: Optional[Dict[str, str]] = None
    
    def _detect_environment(self) -> str:
        """Auto-detect environment based on environment variables."""
        env = os.getenv('ENVIRONMENT', '').lower()
        if env in ['prod', 'production']:
            return 'prod'
        elif env in ['local', 'dev', 'development']:
            return 'local'
        
        # Check for common production indicators
        if os.getenv('VAULT_ADDR') or os.getenv('AWS_REGION'):
            return 'prod'
        
        # Default to local
        return 'local'
    
    def get_credentials(self) -> Dict[str, str]:
        """Get database credentials based on environment."""
        if self._credentials is None:
            if self.environment == 'local':
                self._credentials = self._load_local_credentials()
            elif self.environment == 'prod':
                self._credentials = self._load_vault_credentials()
            else:
                raise ConfigurationError(f"Unknown environment: {self.environment}")
        
        return self._credentials
    
    def _load_local_credentials(self) -> Dict[str, str]:
        """Load credentials from local property file."""
        config_file = os.getenv('DB_CONFIG_FILE', 'config/database.properties')
        
        if not os.path.exists(config_file):
            raise ConfigurationError(f"Configuration file not found: {config_file}")
        
        config = configparser.ConfigParser()
        config.read(config_file)
        
        try:
            section = 'postgresql'
            return {
                'host': config.get(section, 'host'),
                'port': config.getint(section, 'port'),
                'database': config.get(section, 'database'),
                'username': config.get(section, 'username'),
                'password': config.get(section, 'password'),
                'ssl_mode': config.get(section, 'ssl_mode', fallback='require')
            }
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise ConfigurationError(f"Invalid configuration file: {e}")
    
    def _load_vault_credentials(self) -> Dict[str, str]:
        """Load credentials from HashiCorp Vault."""
        vault_addr = os.getenv('VAULT_ADDR')
        vault_token = os.getenv('VAULT_TOKEN')
        vault_path = os.getenv('DB_VAULT_PATH', 'secret/database/postgresql')
        
        if not vault_addr:
            raise ConfigurationError("VAULT_ADDR environment variable is required for production")
        
        if not vault_token:
            raise ConfigurationError("VAULT_TOKEN environment variable is required for production")
        
        try:
            client = hvac.Client(url=vault_addr, token=vault_token)
            
            if not client.is_authenticated():
                raise VaultError("Failed to authenticate with Vault")
            
            response = client.secrets.kv.v2.read_secret_version(path=vault_path)
            secret_data = response['data']['data']
            
            required_keys = ['host', 'port', 'database', 'username', 'password']
            for key in required_keys:
                if key not in secret_data:
                    raise ConfigurationError(f"Missing required credential: {key}")
            
            return {
                'host': secret_data['host'],
                'port': int(secret_data['port']),
                'database': secret_data['database'],
                'username': secret_data['username'],
                'password': secret_data['password'],
                'ssl_mode': secret_data.get('ssl_mode', 'require')
            }
            
        except hvac.exceptions.VaultError as e:
            raise VaultError(f"Vault error: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load credentials from Vault: {e}")
    
    def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Validate that all required credentials are present."""
        required_keys = ['host', 'port', 'database', 'username', 'password']
        return all(key in credentials and credentials[key] for key in required_keys) 