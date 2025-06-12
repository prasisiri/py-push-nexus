"""Tests for the configuration module."""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from connect_postgres.config import Config
from connect_postgres.exceptions import ConfigurationError, VaultError


class TestConfig:
    """Test cases for Config class."""
    
    def test_environment_detection_local(self):
        """Test auto-detection of local environment."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            assert config.environment == 'local'
    
    def test_environment_detection_prod_from_env(self):
        """Test detection of prod environment from ENVIRONMENT variable."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'prod'}, clear=True):
            config = Config()
            assert config.environment == 'prod'
    
    def test_environment_detection_prod_from_vault(self):
        """Test detection of prod environment from VAULT_ADDR."""
        with patch.dict(os.environ, {'VAULT_ADDR': 'https://vault.example.com'}, clear=True):
            config = Config()
            assert config.environment == 'prod'
    
    def test_explicit_environment(self):
        """Test explicit environment setting."""
        config = Config(environment='local')
        assert config.environment == 'local'
        
        config = Config(environment='prod')
        assert config.environment == 'prod'
    
    def test_local_credentials_success(self):
        """Test successful loading of local credentials."""
        # Create temporary config file
        config_content = """
[postgresql]
host = localhost
port = 5432
database = testdb
username = testuser
password = testpass
ssl_mode = require
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.properties', delete=False) as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            with patch.dict(os.environ, {'DB_CONFIG_FILE': config_file}, clear=True):
                config = Config(environment='local')
                credentials = config.get_credentials()
                
                assert credentials['host'] == 'localhost'
                assert credentials['port'] == 5432
                assert credentials['database'] == 'testdb'
                assert credentials['username'] == 'testuser'
                assert credentials['password'] == 'testpass'
                assert credentials['ssl_mode'] == 'require'
        finally:
            os.unlink(config_file)
    
    def test_local_credentials_file_not_found(self):
        """Test error when config file is not found."""
        with patch.dict(os.environ, {'DB_CONFIG_FILE': 'nonexistent.properties'}, clear=True):
            config = Config(environment='local')
            
            with pytest.raises(ConfigurationError) as exc_info:
                config.get_credentials()
            
            assert "Configuration file not found" in str(exc_info.value)
    
    def test_local_credentials_invalid_config(self):
        """Test error with invalid configuration file."""
        config_content = """
[invalid]
host = localhost
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.properties', delete=False) as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            with patch.dict(os.environ, {'DB_CONFIG_FILE': config_file}, clear=True):
                config = Config(environment='local')
                
                with pytest.raises(ConfigurationError) as exc_info:
                    config.get_credentials()
                
                assert "Invalid configuration file" in str(exc_info.value)
        finally:
            os.unlink(config_file)
    
    @patch('hvac.Client')
    def test_vault_credentials_success(self, mock_hvac_client):
        """Test successful loading of Vault credentials."""
        # Mock Vault client
        mock_client = MagicMock()
        mock_client.is_authenticated.return_value = True
        mock_client.secrets.kv.v2.read_secret_version.return_value = {
            'data': {
                'data': {
                    'host': 'vault-host.com',
                    'port': '5432',
                    'database': 'vaultdb',
                    'username': 'vaultuser',
                    'password': 'vaultpass',
                    'ssl_mode': 'require'
                }
            }
        }
        mock_hvac_client.return_value = mock_client
        
        env_vars = {
            'VAULT_ADDR': 'https://vault.example.com',
            'VAULT_TOKEN': 'test-token',
            'DB_VAULT_PATH': 'secret/db/postgres'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config(environment='prod')
            credentials = config.get_credentials()
            
            assert credentials['host'] == 'vault-host.com'
            assert credentials['port'] == 5432
            assert credentials['database'] == 'vaultdb'
            assert credentials['username'] == 'vaultuser'
            assert credentials['password'] == 'vaultpass'
            assert credentials['ssl_mode'] == 'require'
    
    def test_vault_credentials_missing_addr(self):
        """Test error when VAULT_ADDR is missing."""
        with patch.dict(os.environ, {'VAULT_TOKEN': 'test-token'}, clear=True):
            config = Config(environment='prod')
            
            with pytest.raises(ConfigurationError) as exc_info:
                config.get_credentials()
            
            assert "VAULT_ADDR environment variable is required" in str(exc_info.value)
    
    def test_vault_credentials_missing_token(self):
        """Test error when VAULT_TOKEN is missing."""
        with patch.dict(os.environ, {'VAULT_ADDR': 'https://vault.example.com'}, clear=True):
            config = Config(environment='prod')
            
            with pytest.raises(ConfigurationError) as exc_info:
                config.get_credentials()
            
            assert "VAULT_TOKEN environment variable is required" in str(exc_info.value)
    
    @patch('hvac.Client')
    def test_vault_authentication_failed(self, mock_hvac_client):
        """Test error when Vault authentication fails."""
        mock_client = MagicMock()
        mock_client.is_authenticated.return_value = False
        mock_hvac_client.return_value = mock_client
        
        env_vars = {
            'VAULT_ADDR': 'https://vault.example.com',
            'VAULT_TOKEN': 'invalid-token'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config(environment='prod')
            
            with pytest.raises(VaultError) as exc_info:
                config.get_credentials()
            
            assert "Failed to authenticate with Vault" in str(exc_info.value)
    
    def test_validate_credentials_success(self):
        """Test successful credential validation."""
        config = Config()
        credentials = {
            'host': 'localhost',
            'port': 5432,
            'database': 'testdb',
            'username': 'testuser',
            'password': 'testpass'
        }
        
        assert config.validate_credentials(credentials) is True
    
    def test_validate_credentials_missing_key(self):
        """Test credential validation with missing key."""
        config = Config()
        credentials = {
            'host': 'localhost',
            'port': 5432,
            'database': 'testdb',
            'username': 'testuser'
            # Missing password
        }
        
        assert config.validate_credentials(credentials) is False
    
    def test_validate_credentials_empty_value(self):
        """Test credential validation with empty value."""
        config = Config()
        credentials = {
            'host': 'localhost',
            'port': 5432,
            'database': 'testdb',
            'username': 'testuser',
            'password': ''  # Empty password
        }
        
        assert config.validate_credentials(credentials) is False 