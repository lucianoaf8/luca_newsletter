import os
import sys
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.logger_config import get_logger

logger = get_logger('news_api')

# Load .env file
load_dotenv()

def load_api_key():
    """
    Loads the API key from the .env file.
    Raises an error if the key is missing.
    """
    api_key = os.getenv('MEDIASTACK_API')
    if not api_key:
        raise ValueError("API key not found in .env file.")
    return api_key

def fetch_news_data(api_key, topic, country=None, region=None, language='en', limit=5):
    """
    Fetches the latest news for a given topic, country, and region using the Mediastack API.
    
    Parameters:
    - api_key (str): The API key to authenticate requests.
    - topic (str): The topic to search for.
    - country (str): The country to filter the news (optional).
    - region (str): The region to filter the news (optional).
    - language (str): The language of the news articles (default is 'en').
    - limit (int): The maximum number of news articles to return.
    
    Returns:
    - dict: The JSON response from the API containing the news data.
    """
    url = 'http://api.mediastack.com/v1/news'
    params = {
        'access_key': api_key,
        'keywords': topic,
        'languages': language,
        'countries': country,
        'regions': region,
        'sort': 'published_desc',
        'limit': limit
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError:
        logger.error("Error: Unable to connect to the API.")
    except requests.exceptions.Timeout:
        logger.error("Error: Request timed out.")
    except requests.exceptions.RequestException as err:
        logger.error(f"An error occurred: {err}")
    return None

def save_news_data_as_json(news_data, folder_path):
    """
    Saves the news data to a JSON file.

    Parameters:
    - news_data (dict): The JSON response containing the news articles.
    - folder_path (str): The directory where the news data will be saved.
    """
    # Create the folder if it doesn't exist
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    
    # Define the file path
    file_path = os.path.join(folder_path, 'news_data.json')
    
    if news_data:
        try:
            with open(file_path, 'w') as json_file:
                json.dump(news_data, json_file, indent=4)
            logger.info(f"News data saved to {file_path}")
        except IOError as e:
            logger.error(f"Failed to save news data to {file_path}: {e}")
    else:
        logger.error("No news data available to save.")

def display_news(news_data):
    """
    Displays the news articles from the JSON response.

    Parameters:
    - news_data (dict): The JSON response containing the news articles.
    """
    if news_data and 'data' in news_data:
        for article in news_data['data']:
            logger.info(f"Title: {article['title']}")
            logger.debug(f"Description: {article['description']}")
            logger.debug(f"Source: {article['source']}")
            logger.debug(f"URL: {article['url']}")
            logger.debug(f"Published at: {article['published_at']}")
            logger.debug("-" * 80)
    else:
        logger.debug("No news found for this topic or error in API response.")

def get_latest_news(topic, country=None, region=None, language='en', limit=5, save_as_json=True):
    """
    Fetches and displays the latest news about a given topic, and optionally saves it as a JSON file.

    Parameters:
    - topic (str): The topic to search for.
    - country (str): The country to filter the news (optional).
    - region (str): The region to filter the news (optional).
    - language (str): The language of the news articles (default is 'en').
    - limit (int): The maximum number of news articles to fetch.
    - save_as_json (bool): Whether to save the news data as a JSON file.
    """
    api_key = load_api_key()
    news_data = fetch_news_data(api_key, topic, country, region, language, limit)
    display_news(news_data)
    
    if save_as_json:
        # Define the path where the data will be saved
        folder_path = r"C:\Projects\luca_newsletter_official\data\fetched_results\top_news"
        save_news_data_as_json(news_data, folder_path)

if __name__ == "__main__":
    topic = "neuro psicologia"  # Example topic
    country = "br"  # Example country
    region = None  # Example region (optional)
    language = "pt"  # Example language
    get_latest_news(topic, country, region, language)
