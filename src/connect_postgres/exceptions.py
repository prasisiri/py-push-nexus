"""Custom exceptions for the PostgreSQL connection utility."""


class ConnectionError(Exception):
    """Raised when database connection fails."""
    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class VaultError(Exception):
    """Raised when Vault operations fail."""
    pass 