# scripts/apis/content_fetchers/news_api.py

import os
import sys
import json
from datetime import datetime
import requests
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.utils.db_insert_api_calls import insert_api_response

# Initialize logger
logger = get_logger('news_api')

# Load environment variables
load_dotenv()

# API configurations
API_CONFIGS = {
    'newsdata': {
        'url': "https://newsdata.io/api/1/news",
        'key': os.getenv("NEWSDATA_API_KEY"),
        'params': ['q', 'country', 'language', 'category', 'page', 'from_date', 'to_date']
    },
    'newsapi': {
        'url': "https://newsapi.org/v2/everything",
        'key': os.getenv("NEWSAPI_KEY"),
        'params': ['q', 'sources', 'language', 'sort_by', 'page_size', 'page', 'from_date', 'to_date']
    },
    'gnews': {
        'url': "https://gnews.io/api/v4/search",
        'key': os.getenv("GNEWS_API_KEY"),
        'params': ['q', 'lang', 'country', 'topic', 'max_results', 'from_date', 'to_date']
    },
    'mediastack': {
        'url': "http://api.mediastack.com/v1/news",
        'key': os.getenv("MEDIASTACK_API_KEY"),
        'params': ['keywords', 'countries', 'categories', 'languages', 'sort', 'limit', 'offset']
    },
    'currents': {
        'url': "https://api.currentsapi.services/v1/latest-news",
        'key': os.getenv("CURRENTS_API_KEY"),
        'params': ['keywords', 'language', 'country', 'category']
    }
}

def fetch_news(api_name, **kwargs):
    if api_name not in API_CONFIGS:
        logger.error(f"Unknown API: {api_name}")
        return None

    config = API_CONFIGS[api_name]
    url = config['url']
    params = {k: v for k, v in kwargs.items() if k in config['params'] and v is not None}
    params[config.get('key_param', 'apikey')] = config['key']

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Log the API call
        script_path = os.path.abspath(__file__)
        insert_api_response(script_path, params, data)

        logger.info(f"Successfully fetched data from {api_name}")
        return data
    except requests.RequestException as e:
        logger.error(f"Error fetching data from {api_name}: {str(e)}")
        return None

def save_news_data(news_data):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'news_data_{timestamp}.json'
    file_path = os.path.join(project_root, 'data', 'fetched_results', 'news', filename)
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(news_data, f, indent=4)
    
    logger.info(f"News data saved to {file_path}")

def main(apis_to_fetch=None, **kwargs):
    try:
        if apis_to_fetch is None:
            apis_to_fetch = API_CONFIGS.keys()
        elif isinstance(apis_to_fetch, str):
            apis_to_fetch = [apis_to_fetch]

        news_data = {}
        for api in apis_to_fetch:
            if api in API_CONFIGS:
                news_data[api] = fetch_news(api, **kwargs.get(api, {}))
            else:
                logger.warning(f"Skipping unknown API: {api}")

        save_news_data(news_data)
        logger.info("News data fetched and saved successfully")
        return news_data
    except Exception as e:
        logger.error(f"An error occurred in main: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usages:
    
    # 1. Fetch from all APIs
    print("Fetching from all APIs:")
    result_all = main()
    print(json.dumps(result_all, indent=2))
    print("\n" + "="*50 + "\n")

    # 2. Fetch from each API individually
    
    # NewsData.io
    print("Fetching from NewsData.io:")
    result_newsdata = main(
        apis_to_fetch='newsdata',
        newsdata={'q': 'technology', 'country': 'us', 'language': 'en'}
    )
    print(json.dumps(result_newsdata, indent=2))
    print("\n" + "="*50 + "\n")

    # NewsAPI.org
    print("Fetching from NewsAPI.org:")
    result_newsapi = main(
        apis_to_fetch='newsapi',
        newsapi={'q': 'artificial intelligence', 'language': 'en', 'sort_by': 'publishedAt', 'page_size': 10}
    )
    print(json.dumps(result_newsapi, indent=2))
    print("\n" + "="*50 + "\n")

    # GNews
    print("Fetching from GNews:")
    result_gnews = main(
        apis_to_fetch='gnews',
        gnews={'q': 'climate change', 'lang': 'en', 'country': 'us', 'max_results': 5}
    )
    print(json.dumps(result_gnews, indent=2))
    print("\n" + "="*50 + "\n")

    # Mediastack
    print("Fetching from Mediastack:")
    result_mediastack = main(
        apis_to_fetch='mediastack',
        mediastack={'keywords': 'space exploration', 'countries': 'us,gb', 'languages': 'en', 'limit': 5}
    )
    print(json.dumps(result_mediastack, indent=2))
    print("\n" + "="*50 + "\n")

    # CurrentsAPI
    print("Fetching from CurrentsAPI:")
    result_currents = main(
        apis_to_fetch='currents',
        currents={'keywords': 'renewable energy', 'language': 'en', 'country': 'us'}
    )
    print(json.dumps(result_currents, indent=2))
    print("\n" + "="*50 + "\n")

    # 3. Fetch from multiple specific APIs
    print("Fetching from multiple specific APIs (NewsAPI and GNews):")
    result_multiple = main(
        apis_to_fetch=['newsapi', 'gnews'],
        newsapi={'q': 'cryptocurrency', 'language': 'en'},
        gnews={'q': 'blockchain', 'lang': 'en', 'country': 'us'}
    )
    print(json.dumps(result_multiple, indent=2))