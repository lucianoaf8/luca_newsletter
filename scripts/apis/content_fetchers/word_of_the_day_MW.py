import os
import sys
import json
import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException, HTTPError

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# API settings
WORDNIK_API_KEY = os.getenv('WORDNIK_API_KEY')
MW_API_KEY = os.getenv('MW_API_KEY')
WORDNIK_BASE_URL = 'https://api.wordnik.com/v4'
MW_BASE_URL = 'https://www.dictionaryapi.com/api/v3/references/learners/json'


def fetch_random_word(part_of_speech='noun,adjective'):
    """Fetch a random noun or adjective from Wordnik"""
    url = f"{WORDNIK_BASE_URL}/words.json/randomWord"
    params = {
        'api_key': WORDNIK_API_KEY,
        'hasDictionaryDef': 'true',
        'includePartOfSpeech': part_of_speech,
        'minDictionaryCount': 1
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check for HTTP errors
        random_word_data = response.json()
        return random_word_data['word']
    except RequestException as e:
        logger.error(f"Failed to fetch random word: {e}")
        return None


def fetch_word_definition(word):
    """Fetch word details from Merriam-Webster API"""
    url = f"{MW_BASE_URL}/{word}"
    params = {'key': MW_API_KEY}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()
    except HTTPError as e:
        logger.error(f"HTTP error while fetching definition for {word}: {e}")
    except RequestException as e:
        logger.error(f"Failed to fetch definition for {word}: {e}")
    return None


def main():
    # Fetch a random word (noun or adjective)
    random_word = fetch_random_word()
    
    if random_word:
        logger.info(f"Random word fetched: {random_word}")
        
        # Fetch definition of the word from Merriam-Webster API
        word_definition = fetch_word_definition(random_word)
        
        if word_definition:
            logger.info(f"Definition of {random_word}: {json.dumps(word_definition, indent=4)}")
        else:
            logger.error(f"Failed to fetch definition for {random_word}")
    else:
        logger.error("No random word fetched")


if __name__ == "__main__":
    main()
