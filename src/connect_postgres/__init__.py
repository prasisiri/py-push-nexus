"""
Connect PostgreSQL Utility

A PostgreSQL connection utility for AWS RDS with environment-aware credential management.
Supports both local development (property files) and production (Vault) environments.
"""

from .connection import PostgreSQLConnector
from .config import Config
from .exceptions import ConnectionError, ConfigurationError

__version__ = "1.0.0"
__author__ = "Your Organization"

__all__ = [
    "PostgreSQLConnector",
    "Config", 
    "ConnectionError",
    "ConfigurationError"
] 