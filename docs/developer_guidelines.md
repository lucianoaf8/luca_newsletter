# Luca Newsletter Project: Developer Guidelines

## File Structure and Imports

1. Project Root: `C:\Projects\luca_newsletter_official\`
2. Main script locations: `scripts\apis\content_fetchers\`
3. Utility scripts: `scripts\utils\`

### Import Best Practices

1. Always use absolute imports from the project root:

```python
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.utils.db_insert_api_calls import insert_api_response
```

2. Ensure `__init__.py` files exist in all package directories.

## Logging

1. Use the custom logger for all logging operations:

```python
from scripts.utils.logger_config import get_logger

logger = get_logger(__name__)

# Usage
logger.info("Information message")
logger.error("Error message")
logger.debug("Debug message")
```

2. Log all significant events, especially API calls, database operations, and error occurrences.

## Error Handling

1. Use try-except blocks for operations that may raise exceptions:

```python
try:
    # Your code here
except SpecificException as e:
    logger.error(f"Specific error occurred: {e}")
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")
```

2. Always log exceptions with appropriate context.

## Database Operations

1. Use the `db_connection` module for database connections:

```python
from scripts.utils.db_connection import get_db_connection, close_connection

conn = get_db_connection()
try:
    # Your database operations here
finally:
    close_connection(conn)
```

2. Use `insert_api_response` for logging API calls:

```python
from scripts.utils.db_insert_api_calls import insert_api_response

insert_api_response(script_path, payload, response, custom_params)
```

## Creating/Updating API Calls

1. Create new API scripts in `scripts\apis\content_fetchers\`.
2. Follow this template for new API calls:

```python
import sys
import os
import requests
from dotenv import load_dotenv

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.utils.db_insert_api_calls import insert_api_response

load_dotenv()

logger = get_logger(__name__)

def fetch_data_from_api(params):
    try:
        response = requests.get('API_URL', params=params)
        response.raise_for_status()
        data = response.json()
        
        # Log API call
        script_path = os.path.abspath(__file__)
        insert_api_response(script_path, params, data)
        
        return data
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise

def main():
    try:
        params = {'key': 'value'}
        data = fetch_data_from_api(params)
        # Process data here
    except Exception as e:
        logger.error(f"An error occurred in main: {e}")

if __name__ == "__main__":
    main()
```

3. Always use environment variables for sensitive information like API keys.
4. Log all API responses using `insert_api_response`.
5. Handle and log all exceptions appropriately.