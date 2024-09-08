# scripts/db/fetch_subscribers.py

import os
import sys
import pandas as pd
from datetime import datetime
import logging

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.utils.db_connection import get_db_connection, close_connection

# Initialize logger
logger = get_logger(__name__)

# SQL query to fetch subscribers
subscribers_query = '''
SELECT id, full_name, email, nickname, interests, languages, city, country, timezone, days_receiving_newsletter
FROM subscribers
WHERE is_subscribed = 1
LIMIT 1;
'''

def fetch_subscribers():
    """
    Fetch subscribers data from the database and return as a DataFrame.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Execute the SQL query
        cursor.execute(subscribers_query)
        subscribers = cursor.fetchall()  # Fetch all rows from the query result

        logger.info(f"Fetched and processed {len(subscribers)} subscribers")

        # Convert the result into a pandas DataFrame
        subscribers_df = pd.DataFrame(subscribers)
        return subscribers_df

    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None

    finally:
        if conn:
            close_connection(conn)

def process_subscribers_data():
    """
    Fetches the subscribers' data and prints it as a DataFrame.
    """
    subscribers_df = fetch_subscribers()
    if subscribers_df is not None:
        logger.info("Data fetched successfully")
        print(subscribers_df)
        return subscribers_df
    else:
        logger.error("Failed to fetch subscribers data.")
        return None

if __name__ == "__main__":
    process_subscribers_data()
