# Connect PostgreSQL Utility

A robust PostgreSQL connection utility for AWS RDS with environment-aware credential management. This package automatically detects your environment and loads credentials from the appropriate source - local property files for development and HashiCorp Vault for production.

## Features

- **Environment-aware credential management**: Automatically detects local vs production environments
- **Local development**: Uses property files with hardcoded credentials
- **Production ready**: Integrates with HashiCorp Vault for secure credential management
- **AWS RDS optimized**: Built specifically for PostgreSQL on AWS RDS
- **Context managers**: Provides convenient context managers for connections and cursors
- **Connection pooling**: Efficient connection management
- **Error handling**: Comprehensive error handling with custom exceptions
- **Type hints**: Full type annotation support
- **Logging**: Built-in logging for debugging and monitoring

## Installation

### From Nexus Repository

```bash
pip install connect-postgres-utility --extra-index-url https://your-nexus-repo.com/repository/pypi-hosted/simple/
```

### From Source

```bash
git clone <repository-url>
cd connect-postgres-utility
pip install -e .
```

## Quick Start

### Basic Usage

```python
from connect_postgres import PostgreSQLConnector

# Auto-detects environment and loads appropriate credentials
connector = PostgreSQLConnector()

# Using context manager (recommended)
with connector as conn:
    with conn.get_cursor() as cursor:
        cursor.execute("SELECT * FROM your_table LIMIT 10")
        results = cursor.fetchall()
        print(results)
```

### Environment-Specific Initialization

```python
# Explicitly specify environment
local_connector = PostgreSQLConnector(environment='local')
prod_connector = PostgreSQLConnector(environment='prod')
```

### Execute Queries

```python
connector = PostgreSQLConnector()

# Execute a simple query
results = connector.execute_query("SELECT COUNT(*) FROM users")

# Execute with parameters
user = connector.execute_query(
    "SELECT * FROM users WHERE id = %s", 
    (user_id,), 
    fetch='one'
)

# Execute multiple queries
params_list = [(1, 'John'), (2, 'Jane'), (3, 'Bob')]
connector.execute_many(
    "INSERT INTO users (id, name) VALUES (%s, %s)", 
    params_list
)
```

## Configuration

### Local Development

Create a configuration file at `config/database.properties`:

```ini
[postgresql]
host = your-rds-instance.cluster-xxxxxx.us-east-1.rds.amazonaws.com
port = 5432
database = your_database
username = your_username
password = your_password
ssl_mode = require
```

You can also set a custom config file path:

```bash
export DB_CONFIG_FILE=/path/to/your/database.properties
```

### Production (Vault)

Set the following environment variables:

```bash
export ENVIRONMENT=prod
export VAULT_ADDR=https://your-vault-instance.com
export VAULT_TOKEN=your-vault-token
export DB_VAULT_PATH=secret/database/postgresql  # optional, defaults to this path
```

Store credentials in Vault at the specified path with these keys:
- `host`
- `port`
- `database`
- `username`
- `password`
- `ssl_mode` (optional, defaults to 'require')

### Environment Detection

The utility automatically detects the environment based on:

1. `ENVIRONMENT` environment variable (`local`, `dev`, `prod`, `production`)
2. Presence of `VAULT_ADDR` or `AWS_REGION` environment variables
3. Defaults to `local` if unable to determine

## Advanced Usage

### Custom Configuration

```python
from connect_postgres import Config, PostgreSQLConnector

# Create custom configuration
config = Config(environment='prod')
connector = PostgreSQLConnector(config=config)
```

### Connection Information

```python
connector = PostgreSQLConnector()
info = connector.get_connection_info()
print(f"Connected to {info['host']}:{info['port']} as {info['username']}")
```

### Manual Connection Management

```python
connector = PostgreSQLConnector()

# Establish connection
conn = connector.connect()

# Use connection
with conn.cursor() as cursor:
    cursor.execute("SELECT version()")
    version = cursor.fetchone()
    print(version)

# Close when done
connector.disconnect()
```

## Error Handling

The utility provides specific exceptions for different error scenarios:

```python
from connect_postgres import PostgreSQLConnector, ConnectionError, ConfigurationError

try:
    connector = PostgreSQLConnector()
    results = connector.execute_query("SELECT * FROM users")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except ConnectionError as e:
    print(f"Connection error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd connect-postgres-utility

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v --cov=connect_postgres
```

### Code Formatting

```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Publishing to Nexus

### Build the Package

```bash
python -m build
```

### Upload to Nexus

```bash
# Configure repository URL in ~/.pypirc or use twine directly
twine upload --repository-url https://your-nexus-repo.com/repository/pypi-hosted/ dist/*
```

### Using from Nexus

Add your Nexus repository to pip configuration or use the extra-index-url:

```bash
pip install connect-postgres-utility --extra-index-url https://your-nexus-repo.com/repository/pypi-hosted/simple/
```

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ENVIRONMENT` | Environment type (`local`, `dev`, `prod`, `production`) | No | Auto-detected |
| `DB_CONFIG_FILE` | Path to local configuration file | No | `config/database.properties` |
| `VAULT_ADDR` | Vault server URL | Yes (prod) | None |
| `VAULT_TOKEN` | Vault authentication token | Yes (prod) | None |
| `DB_VAULT_PATH` | Path to database secrets in Vault | No | `secret/database/postgresql` |

## Requirements

- Python 3.8+
- PostgreSQL database (tested with AWS RDS)
- HashiCorp Vault (for production environments)

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## Support

For issues and questions, please create an issue in the repository or contact the development team. 