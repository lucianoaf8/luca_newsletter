import os
import sys
import requests
from dotenv import load_dotenv
from datetime import datetime

# Append the directory containing your utils to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the custom logger
from utils.logger_config import get_logger

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logger = get_logger('api_ninjas')

# Correct Base URLs for the APIs
QUOTE_URL = 'https://api.api-ninjas.com/v1/quotes'
FACTS_URL = 'https://api.api-ninjas.com/v1/facts'
JOKES_URL = 'https://api.api-ninjas.com/v1/jokes'

# API Key from environment variable
API_KEY = os.getenv('API_NINJAS')

# Headers to pass the API key
headers = {
    'X-Api-Key': API_KEY
}

# Base directory for saving files
BASE_DIR = r'C:\Projects\luca_newsletter_official\scripts\apis\content_fetchers\data\ninjas_apis'

def ensure_directory(directory):
    """Ensure that the specified directory exists."""
    os.makedirs(directory, exist_ok=True)

def save_to_file(content, filename):
    """Save content to a file in the specified directory."""
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)
    logger.info(f"Saved content to {filepath}")

def fetch_quote(category=None):
    try:
        params = {'category': category} if category else {}
        response = requests.get(QUOTE_URL, headers=headers, params=params)
        response.raise_for_status()
        quote = response.json()[0]
        logger.info(f"Successfully fetched quote: {quote['quote']} by {quote['author']}")
        
        # Format and save the quote
        formatted_quote = f"Quote: {quote['quote']}\nAuthor: {quote['author']}\nCategory: {quote['category']}"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"quote_{timestamp}.txt"
        save_to_file(formatted_quote, filename)
        
        return quote
    except Exception as e:
        logger.error(f"Error fetching quote: {str(e)}")
        return None

def fetch_fact():
    try:
        response = requests.get(FACTS_URL, headers=headers)
        response.raise_for_status()
        fact = response.json()[0]['fact']
        logger.info(f"Successfully fetched fact: {fact}")
        
        # Format and save the fact
        formatted_fact = f"Fact: {fact}"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"fact_{timestamp}.txt"
        save_to_file(formatted_fact, filename)
        
        return fact
    except Exception as e:
        logger.error(f"Error fetching fact: {str(e)}")
        return None

def fetch_joke():
    try:
        response = requests.get(JOKES_URL, headers=headers)
        response.raise_for_status()
        joke = response.json()[0]['joke']
        logger.info(f"Successfully fetched joke: {joke}")
        
        # Format and save the joke
        formatted_joke = f"Joke: {joke}"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"joke_{timestamp}.txt"
        save_to_file(formatted_joke, filename)
        
        return joke
    except Exception as e:
        logger.error(f"Error fetching joke: {str(e)}")
        return None

def main():
    # Ensure the base directory exists
    ensure_directory(BASE_DIR)

    # Fetch and save a quote
    quote = fetch_quote(category='inspirational')
    if quote:
        print(f"Quote: {quote['quote']} - {quote['author']}")

    # Fetch and save a fact
    fact = fetch_fact()
    if fact:
        print(f"Fact: {fact}")

    # Fetch and save a joke
    joke = fetch_joke()
    if joke:
        print(f"Joke: {joke}")

if __name__ == "__main__":
    main()