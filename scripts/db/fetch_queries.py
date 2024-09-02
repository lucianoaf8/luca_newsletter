# scripts/db/fetch_queries.py

import os
import sys
import pandas as pd
from datetime import datetime
import json
import random
import logging

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.utils.db_connection import get_db_connection, close_connection

# Initialize logger
logger = get_logger(__name__)

def execute_query(query):
    """
    Executes a given SQL query and returns the result as a pandas DataFrame.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        data = cursor.fetchall()
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            close_connection(conn)

def parse_json_columns(df, json_columns):
    """
    Parses the specified JSON columns in a DataFrame and integrates the parsed data into the DataFrame.
    """
    for col in json_columns:
        if col in df.columns:
            df = df.dropna(subset=[col])  # Drop rows where the JSON column is None or NaN
            parsed_data = df[col].apply(lambda x: pd.json_normalize(json.loads(x)) if isinstance(x, str) else pd.DataFrame())
            df = df.drop(columns=[col]).join(pd.concat(parsed_data.to_list(), ignore_index=True))
    return df

def select_random_id(table):
    """
    Selects a random ID from the given table where 'used_in_newsletter' is 0.
    """
    query = f'SELECT DISTINCT id FROM {table} WHERE used_in_newsletter = 0;'
    ids_df = execute_query(query)
    if not ids_df.empty:
        return random.choice(ids_df['id'].tolist())
    else:
        return None

def fetch_weather_data():
    """
    Fetches weather API calls from the database and parses JSON columns.
    """
    weather_query = '''
    SELECT id, script_path, custom_params, payload, response, used_in_newsletter, timestamp
    FROM api_calls
    WHERE script_path LIKE '%weather_api.py'
    AND used_in_newsletter = 0
    AND timestamp >= NOW() - INTERVAL 5 HOUR;
    '''
    df = execute_query(weather_query)
    return parse_json_columns(df, ['payload', 'response'])

def fetch_exchange_rate_data():
    """
    Fetches exchange rate API calls from the database and parses JSON columns.
    """
    exchange_rate_query = '''
    SELECT id, script_path, custom_params, payload, response, used_in_newsletter, timestamp
    FROM api_calls
    WHERE script_path LIKE '%exchange_rates_api.py'
    AND used_in_newsletter = 0
    AND timestamp >= NOW() - INTERVAL 5 HOUR;
    '''
    df = execute_query(exchange_rate_query)
    return parse_json_columns(df, ['payload', 'response'])

def fetch_quotes_data():
    """
    Fetches a random quote and its author details.
    """
    random_id = select_random_id('quotes')
    if random_id:
        quotes_query = f'''
        SELECT q.id, q.quote, q.source, q.contextual_notes, q.author_name, q.author_overview, q.author_key_works, q.timestamp,
            a.id AS author_id, a.birth_year, a.death_year, a.nationality, a.profession, a.known_for, a.timestamp AS author_timestamp
        FROM quotes q
        INNER JOIN authors a ON a.author = q.author_name
        WHERE q.id = {random_id};
        '''
        return execute_query(quotes_query)
    else:
        logger.warning("No available quotes to fetch")
        return pd.DataFrame()

def fetch_english_tips_data():
    """
    Fetches a random English tip.
    """
    random_id = select_random_id('english_tips')
    if random_id:
        english_tips_query = f'''
        SELECT id, category, title, content, subcontent1, subcontent2, quick_tip, used_in_newsletter, timestamp
        FROM english_tips
        WHERE id = {random_id};
        '''
        return execute_query(english_tips_query)
    else:
        logger.warning("No available English tips to fetch")
        return pd.DataFrame()

def fetch_daily_challenges_data():
    """
    Fetches a random daily challenge.
    """
    random_id = select_random_id('daily_challenges')
    if random_id:
        daily_challenges_query = f'''
        SELECT id, category, challenge, instructions, motivation, used_in_newsletter, timestamp
        FROM daily_challenges
        WHERE id = {random_id};
        '''
        return execute_query(daily_challenges_query)
    else:
        logger.warning("No available daily challenges to fetch")
        return pd.DataFrame()

def fetch_all_data():
    """
    Fetches all the required data and returns them as DataFrames.
    """
    weather_data = fetch_weather_data()
    exchange_rate_data = fetch_exchange_rate_data()
    quotes_data = fetch_quotes_data()
    english_tips_data = fetch_english_tips_data()
    daily_challenges_data = fetch_daily_challenges_data()

    return {
        'weather_data': weather_data,
        'exchange_rate_data': exchange_rate_data,
        'quotes_data': quotes_data,
        'english_tips_data': english_tips_data,
        'daily_challenges_data': daily_challenges_data
    }

def main():
    data = fetch_all_data()
    for name, df in data.items():
        if not df.empty:
            logger.info(f"Fetched {len(df)} rows for {name}")
            print(df.head())  # Print the first few rows of each DataFrame
        else:
            logger.warning(f"No data fetched for {name}")

if __name__ == "__main__":
    main()
