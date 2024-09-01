# scripts\db\fetch_queries.py

import os
import sys
from datetime import datetime
import json

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.utils.db_connection import get_db_connection, close_connection

# Initialize logger
logger = get_logger(__name__)

weather_query = '''
SELECT id, script_path, custom_params, payload, response, used_in_newsletter, timestamp
FROM api_calls
WHERE script_path LIKE '%weather_api.py'
AND used_in_newsletter = 0;
'''

exchange_rate_query = '''
SELECT id, script_path, custom_params, payload, response, used_in_newsletter, timestamp
FROM api_calls
WHERE script_path LIKE '%exchange_rates_api.py'
AND used_in_newsletter = 0;
'''

quotes_query = '''
SELECT q.id, q.quote, q.source, q.contextual_notes, q.author_name, q.author_overview, q.author_key_works, q.timestamp,
    a.id, q.author_name, a.birth_year, a.death_year, a.nationality, a.profession, a.known_for, a.timestamp AS author_timestamp
FROM quotes q
INNER JOIN authors a ON a.author = q.author_name
WHERE q.used_in_newsletter = 0;
'''

english_tips_query = '''
SELECT id, category, title, content, subcontent1, subcontent2, quick_tip, used_in_newsletter, timestamp
FROM english_tips
WHERE used_in_newsletter = 0;
'''

daily_challenges_query = '''
SELECT id, category, challenge, instructions, motivation, used_in_newsletter, timestamp
FROM daily_challenges
WHERE used_in_newsletter = 0;
'''

def process_api_calls(api_calls):
    return [
        {
            'id': int(call['id']),
            'script_path': str(call['script_path']),
            'custom_params': str(call['custom_params']) if call['custom_params'] else None,
            'payload': json.loads(call['payload']) if isinstance(call['payload'], str) else call['payload'],
            'response': json.loads(call['response']) if isinstance(call['response'], str) else call['response'],
            'timestamp': call['timestamp'].isoformat() if isinstance(call['timestamp'], datetime) else str(call['timestamp'])
        }
        for call in api_calls
    ]
    
def process_daily_challenges(challenges):
    return [
        {
            'id': int(challenge['id']),
            'category': str(challenge['category']),
            'challenge': str(challenge['challenge']) if challenge['challenge'] else None,
            'instructions': str(challenge['instructions']) if challenge['instructions'] else None,
            'motivation': str(challenge['motivation']) if challenge['motivation'] else None,
            'used_in_newsletter': bool(challenge['used_in_newsletter']),
            'timestamp': challenge['timestamp'].isoformat() if isinstance(challenge['timestamp'], datetime) else str(challenge['timestamp'])
        }
        for challenge in challenges
    ]

def process_quotes(quotes):
    return [
        {
            'id': int(quote['id']),
            'quote': str(quote['quote']),
            'source': str(quote['source']),
            'contextual_notes': str(quote['contextual_notes']),
            'author_name': str(quote['author_name']),
            'author_overview': str(quote['author_overview']) if quote['author_overview'] else None,
            'author_key_works': str(quote['author_key_works']) if quote['author_key_works'] else None,
            'timestamp': quote['timestamp'].isoformat() if isinstance(quote['timestamp'], datetime) else str(quote['timestamp'])
        }
        for quote in quotes
    ]

def process_english_tips(tips):
    return [
        {
            'id': int(tip['id']),
            'category': str(tip['category']),
            'title': str(tip['title']),
            'content': str(tip['content']),
            'subcontent1': str(tip['subcontent1']),
            'subcontent2': str(tip['subcontent2']),
            'quick_tip': str(tip['quick_tip']),
            'used_in_newsletter': bool(tip['used_in_newsletter']),
            'timestamp': tip['timestamp'].isoformat() if isinstance(tip['timestamp'], datetime) else str(tip['timestamp'])
        }
        for tip in tips
    ]

def fetch_data():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch and process weather API calls
        cursor.execute(weather_query)
        weather_data = process_api_calls(cursor.fetchall())
        logger.info(f"Fetched and processed {len(weather_data)} weather API calls")

        # Fetch and process exchange rate API calls
        cursor.execute(exchange_rate_query)
        exchange_rate_data = process_api_calls(cursor.fetchall())
        logger.info(f"Fetched and processed {len(exchange_rate_data)} exchange rate API calls")
        
        # Fetch and process quotes
        cursor.execute(quotes_query)
        quotes_data = process_quotes(cursor.fetchall())
        logger.info(f"Fetched and processed {len(quotes_data)} quotes")

        # Fetch and process English tips
        cursor.execute(english_tips_query)
        english_tips_data = process_english_tips(cursor.fetchall())
        logger.info(f"Fetched and processed {len(english_tips_data)} English tips")

        # Fetch and process daily challenges
        cursor.execute(daily_challenges_query)
        daily_challenges_data = process_daily_challenges(cursor.fetchall())
        logger.info(f"Fetched and processed {len(daily_challenges_data)} daily challenges")

        return quotes_data, english_tips_data, daily_challenges_data, weather_data, exchange_rate_data

    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None, None, None, None, None, None

    finally:
        if conn:
            close_connection(conn)

def main():
    quotes, english_tips, daily_challenges, weather_data, exchange_rate_data = fetch_data()
    
    if weather_data:
        logger.info(f"Sample weather API call: Script: {weather_data[0]['script_path']}, Timestamp: {weather_data[0]['timestamp']}")
        logger.debug(f"Weather payload: {weather_data[0]['payload']}")
        logger.debug(f"Weather response: {weather_data[0]['response']}")

    if exchange_rate_data:
        logger.info(f"Sample exchange rate API call: Script: {exchange_rate_data[0]['script_path']}, Timestamp: {exchange_rate_data[0]['timestamp']}")
        logger.debug(f"Exchange rate payload: {exchange_rate_data[0]['payload']}")
        logger.debug(f"Exchange rate response: {exchange_rate_data[0]['response']}")
    if quotes:
        logger.info(f"Sample quote: {quotes[0]['quote']} (ID: {quotes[0]['id']})")
    if english_tips:
        logger.info(f"Sample English tip: {english_tips[0]['title']} (Category: {english_tips[0]['category']})")
    if daily_challenges:
        logger.info(f"Sample daily challenge: {daily_challenges[0]['challenge']} (Category: {daily_challenges[0]['category']})")

if __name__ == "__main__":
    main()