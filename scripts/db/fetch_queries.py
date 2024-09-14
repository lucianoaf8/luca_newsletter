# scripts/db/fetch_queries.py

import os
import sys
import pandas as pd
import json
import random

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.utils.db_connection import get_db_connection, close_connection

# Initialize logger
logger = get_logger('fetch_queries')

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
    Adds additional filters for 'word_of_the_day' table.
    """
    if table == 'word_of_the_day':
        additional_filters = '''
        AND meta_id IS NOT NULL
        AND audio_file_us <> ''
        '''
    elif table == 'historical_events':
        additional_filters = '''
        AND LOWER(month) = LOWER(MONTHNAME(CURDATE()))
        AND day = DAY(CURDATE())
        '''
    else:
        additional_filters = ''
    
    query = f'''
    SELECT DISTINCT id FROM {table} 
    WHERE used_in_newsletter = 0
    {additional_filters};
    '''
    
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
    SELECT DISTINCT id, script_path, custom_params, payload, response, used_in_newsletter, created
    FROM api_calls
    WHERE script_path LIKE '%weather_api.py'
    AND used_in_newsletter = 0
    ORDER BY id DESC
    LIMIT 2;
    '''
    df = execute_query(weather_query)
    return parse_json_columns(df, ['payload', 'response'])

def fetch_exchange_rate_data():
    """
    Fetches exchange rate API calls from the database and parses JSON columns.
    """
    exchange_rate_query = '''
    SELECT id, script_path, custom_params, payload, response, used_in_newsletter, created
    FROM api_calls
    WHERE script_path LIKE '%exchange_rates_api.py'
    AND used_in_newsletter = 0
    ORDER BY id DESC
    LIMIT 1;
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
        SELECT q.id, q.quote_en, q.quote_pt, q.source, q.contextual_notes_en, q.contextual_notes_pt, q.author_name, 
               q.author_overview_en, q.author_overview_pt, q.author_key_works, q.created,
               a.id AS author_id, q.author_name, a.birth_year, a.death_year, a.nationality, a.profession, a.known_for
        FROM quotes q
        INNER JOIN authors a ON a.author = q.author_name
        WHERE q.id = {random_id};
        '''
        return execute_query(quotes_query)
    else:
        logger.warning("No available quotes to fetch")
        return pd.DataFrame()

def fetch_fun_facts_data():
    """
    Fetches a random fun fact.
    """
    random_id = select_random_id('fun_facts')
    if random_id:
        fun_fact=f'''
        SELECT id, category, fun_fact_en, fun_fact_pt, reasoning_en, reasoning_pt, source, practical_implication_en, 
               practical_implication_pt, used_in_newsletter, created, updated
        FROM fun_facts
        WHERE id = {random_id};
        '''
        return execute_query(fun_fact)
    else:
        logger.warning("No available fun facts to fetch")
        return pd.DataFrame()

def fetch_word_of_the_day_data():
    """
    Fetches a random word of the day.
    """
    random_id = select_random_id('word_of_the_day')
    if random_id:
        word_of_the_day=f'''
        SELECT  id, category, word_en, word_pt, sentence_en, sentence_pt, used_in_newsletter, created, updated, meta_id, meta_uuid, 
                part_of_speech_en, part_of_speech_pt, pronunciation_us, audio_file_us, shortdef_1_en, shortdef_1_pt, 
                shortdef_2_en, shortdef_2_pt, shortdef_3_en, shortdef_3_pt, example_1_en, example_1_pt, example_2_en, example_2_pt, 
                etymology, meta_src, meta_section, meta_target_tuuid, meta_target_tsrc, meta_offensive, headword, 
                pronunciation_uk, audio_file_uk, grammatical_notegrammatical_info
        FROM word_of_the_day
        WHERE id = {random_id};
        '''
        return execute_query(word_of_the_day)
    else:
        logger.warning("No available word of the day to fetch")
        return pd.DataFrame()

def fetch_english_tips_data():
    """
    Fetches a random English tip.
    """
    random_id = select_random_id('english_tips')
    if random_id:
        english_tips_query = f'''
        SELECT  id, category_en, category_pt, title_en, title_pt, content_en, content_pt, subcontent1_en, subcontent1_pt, 
                subcontent2_en, subcontent2_pt, quick_tip_en, quick_tip_pt, used_in_newsletter, created, updated
        FROM english_tips
        WHERE id = {random_id};
        '''
        return execute_query(english_tips_query)
    else:
        logger.warning("No available English tips to fetch")
        return pd.DataFrame()

def fetch_historical_event_data():
    random_id = select_random_id('historical_events')
    if random_id:
        historical_event=f'''
        SELECT  id, month, day, year, category, event_description_en, event_description_pt, significance_en, significance_pt, 
                source, used_in_newsletter, created, updated
        FROM historical_events
        WHERE id = {random_id};
        '''
        return execute_query(historical_event)
    else:
        logger.warning("No available historical events to fetch")
        return pd.DataFrame()

def fetch_daily_challenges_data():
    """
    Fetches a random daily challenge.
    """
    random_id = select_random_id('daily_challenges')
    if random_id:
        daily_challenges_query = f'''
        SELECT  id, category, challenge_en, challenge_pt, instructions_en, instructions_pt, motivation_en,
                motivation_pt, used_in_newsletter, created, updated
        FROM daily_challenges
        WHERE id = {random_id};
        '''
        return execute_query(daily_challenges_query)
    else:
        logger.warning("No available daily challenges to fetch")
        return pd.DataFrame()

def fetch_weather_codes():
    """
    Fetch weather codes.
    """
    weather_codes_query = f'''
    SELECT weather_code, description_en, description_pt, icon_file_name, icon_file_url
    FROM tomorrowio_weathercodes;
    '''
    return execute_query(weather_codes_query)

def fetch_all_data():
    """
    Fetches all the required data and returns them as DataFrames.
    """
    weather_data = fetch_weather_data()
    exchange_rate_data = fetch_exchange_rate_data()
    quotes_data = fetch_quotes_data()
    fun_fact = fetch_fun_facts_data()
    word_of_the_day_data = fetch_word_of_the_day_data()
    english_tips_data = fetch_english_tips_data()
    historical_event = fetch_historical_event_data()
    daily_challenges_data = fetch_daily_challenges_data()
    weather_codes = fetch_weather_codes()

    return {
        'weather_data': weather_data,
        'exchange_rate_data': exchange_rate_data,
        'quotes_data': quotes_data,
        'fun_fact_data': fun_fact,
        'word_of_the_day_data': word_of_the_day_data,
        'english_tips_data': english_tips_data,
        'historical_events_data': historical_event,
        'daily_challenges_data': daily_challenges_data,
        'weather_codes': weather_codes
    }

def main():
    data = fetch_all_data()
    for name, df in data.items():
        if not df.empty:
            logger.info(f"Fetched {len(df)} rows for {name}")
            # print(df.head()) 
        else:
            logger.warning(f"No data fetched for {name}")

if __name__ == "__main__":
    main()
