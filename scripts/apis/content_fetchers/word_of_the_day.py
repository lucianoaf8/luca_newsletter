import os
import sys
import json
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException, HTTPError

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.utils.db_insert_api_calls import insert_api_response

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Wordnik API settings
API_KEY = os.getenv('WORDNIK_KEY')
BASE_URL = 'https://api.wordnik.com/v4'

class RateLimiter:
    def __init__(self):
        self.remaining_minute = None
        self.remaining_hour = None
        self.limit_minute = None
        self.limit_hour = None
        self.last_check_time = 0

    def update_limits(self, headers):
        self.remaining_minute = int(headers.get('x-ratelimit-remaining-minute', 0))
        self.remaining_hour = int(headers.get('x-ratelimit-remaining-hour', 0))
        self.limit_minute = int(headers.get('x-ratelimit-limit-minute', 1))
        self.limit_hour = int(headers.get('x-ratelimit-limit-hour', 1))
        self.last_check_time = time.time()

    def wait_if_needed(self):
        current_time = time.time()
        if current_time - self.last_check_time < 60 and (self.remaining_minute is not None and self.remaining_minute <= 1):
            sleep_time = 60 - (current_time - self.last_check_time)
            logger.info(f"Rate limit approaching. Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        elif self.remaining_hour is not None and self.remaining_hour <= 1:
            sleep_time = 3600 - (current_time - self.last_check_time)
            logger.info(f"Hourly rate limit approaching. Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

rate_limiter = RateLimiter()

def fetch_data_with_rate_limit(endpoint, params=None, max_retries=3):
    url = f"{BASE_URL}{endpoint}"
    params = params or {}
    params['api_key'] = API_KEY
    
    for attempt in range(max_retries):
        try:
            rate_limiter.wait_if_needed()
            response = requests.get(url, params=params)
            rate_limiter.update_limits(response.headers)
            response.raise_for_status()  # Check for HTTP errors
            return response.json()
        except HTTPError as e:
            # Handle 404 Not Found errors gracefully
            if response.status_code == 404:
                logger.warning(f"404 Not Found for {endpoint}. No data available.")
                return None  # Return None so we skip it in the final output
            # Handle other HTTP errors (like 500)
            elif response.status_code == 500:
                logger.error(f"500 Internal Server Error for {endpoint}. Server might be down.")
                if attempt == max_retries - 1:
                    return None
            # Handle rate limiting (429)
            elif response.status_code == 429:
                sleep_time = 60  # Default to 1 minute if header is missing
                if 'Retry-After' in response.headers:
                    sleep_time = int(response.headers['Retry-After'])
                logger.info(f"Rate limited. Waiting for {sleep_time} seconds before retrying.")
                time.sleep(sleep_time)
            else:
                logger.warning(f"Attempt {attempt + 1} failed for {endpoint}: {str(e)}")
            time.sleep(5)  # Wait 5 seconds before retrying for other errors
        except RequestException as e:
            logger.error(f"Request failed for {endpoint}: {str(e)}")
            return None  # Skip this endpoint after retries
    return None

def save_output(output):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'word_of_the_day_{timestamp}.json'
    file_path = os.path.join(project_root, 'data', 'fetched_results', 'word_of_the_day', filename)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as f:
        json.dump(output, f, indent=4)

    logger.info(f"Output saved to {file_path}")
    return file_path

def main():
    # Fetch Word of the Day
    word_of_the_day = fetch_data_with_rate_limit('/words.json/wordOfTheDay')
    
    if not word_of_the_day:
        logger.error("Failed to fetch Word of the Day")
        return

    word = word_of_the_day['word']
    logger.info(f"Word of the day: {word}")

    # Fetch data from multiple endpoints
    endpoints = [
        ('/word.json/{word}/audio', {}),
        ('/word.json/{word}/definitions', {'limit': 5}),
        ('/word.json/{word}/etymologies', {}),
        ('/word.json/{word}/examples', {'limit': 5}),
        ('/word.json/{word}/frequency', {}),
        ('/word.json/{word}/hyphenation', {}),
        ('/word.json/{word}/phrases', {'limit': 5}),
        ('/word.json/{word}/pronunciations', {'limit': 5}),
        ('/word.json/{word}/relatedWords', {'limitPerRelationshipType': 5}),
        ('/word.json/{word}/scrabbleScore', {}),
        ('/word.json/{word}/topExample', {})
    ]

    final_output = {'word_of_the_day': word_of_the_day}
    combined_params = {}

    for endpoint, params in endpoints:
        endpoint_name = endpoint.split('/')[-1]
        formatted_endpoint = endpoint.format(word=word)
        data = fetch_data_with_rate_limit(formatted_endpoint, params)
        
        if data:
            final_output[endpoint_name] = data
            combined_params[endpoint_name] = params
        else:
            logger.warning(f"No data retrieved for {endpoint_name}")

    output_file_path = save_output(final_output)

    # Log the combined API call with the final output
    script_path = os.path.abspath(__file__)
    with open(output_file_path, 'r') as f:
        final_output = json.load(f)

    insert_api_response(script_path, combined_params, final_output)
    
    logger.info(f"Word of the day data saved successfully: {word}")

if __name__ == "__main__":
    main()
