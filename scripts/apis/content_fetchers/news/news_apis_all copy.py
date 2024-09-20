import os
import sys
import json
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import time

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
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
        'key_param': 'apikey',
        'params': ['q', 'country', 'language', 'category', 'from_date', 'to_date']
    },
    'newsapi': {
        'url': "https://newsapi.org/v2/everything",
        'key': os.getenv("NEWSAPI_KEY"),
        'key_param': 'apiKey',
        'params': ['q', 'sources', 'language', 'sortBy', 'pageSize', 'page', 'from', 'to']
    },
    'gnews': {
        'url': "https://gnews.io/api/v4/search",
        'key': os.getenv("GNEWS_API_KEY"),
        'key_param': 'token',
        'params': ['q', 'lang', 'country', 'max', 'from', 'to']
    },
    'mediastack': {
        'url': "http://api.mediastack.com/v1/news",
        'key': os.getenv("MEDIASTACK_API_KEY"),
        'key_param': 'access_key',
        'params': ['keywords', 'countries', 'languages', 'sort', 'limit', 'offset', 'date']
    },
    'currents': {
        'url': "https://api.currentsapi.services/v1/search",
        'key': os.getenv("CURRENTS_API_KEY"),
        'key_param': 'apiKey',
        'params': ['keywords', 'language', 'country', 'start_date', 'end_date']
    }
}

def fetch_api(api_name, params, max_retries=3):
    config = API_CONFIGS[api_name]
    url = config['url']
    params[config['key_param']] = config['key']

    for attempt in range(max_retries):
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
            logger.error(f"Attempt {attempt + 1} failed for {api_name}: {str(e)}")
            logger.error(f"Request URL: {response.url}")
            if attempt == max_retries - 1:
                logger.error(f"Max retries reached for {api_name}. Giving up.")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff

def fetch_newsdata(params):
    params = {k: v for k, v in params.items() if v}  # Remove empty parameters
    return fetch_api('newsdata', params)

def fetch_newsapi(params):
    return fetch_api('newsapi', params)

def fetch_gnews(params):
    return fetch_api('gnews', params)

def fetch_mediastack(params):
    return fetch_api('mediastack', params)

def fetch_currents(params):
    return fetch_api('currents', params)

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
        today = datetime.now()
        week_ago = today - timedelta(days=7)

        for api in apis_to_fetch:
            if api in API_CONFIGS:
                api_params = kwargs.get(api, {}).copy()
                
                # Set default query and language if not provided
                api_params.setdefault('q', api_params.get('keywords', 'technology'))
                api_params.setdefault('language', api_params.get('lang', 'en'))
                
                # Set date parameters
                if api == 'newsdata':
                    api_params.setdefault('from_date', week_ago.strftime('%Y-%m-%d'))
                    api_params.setdefault('to_date', today.strftime('%Y-%m-%d'))
                elif api in ['newsapi', 'gnews']:
                    api_params.setdefault('from', week_ago.strftime('%Y-%m-%d'))
                    api_params.setdefault('to', today.strftime('%Y-%m-%d'))
                elif api == 'mediastack':
                    api_params.setdefault('date', f"{week_ago.strftime('%Y-%m-%d')},{today.strftime('%Y-%m-%d')}")
                elif api == 'currents':
                    api_params.setdefault('start_date', week_ago.strftime('%Y-%m-%d'))
                    api_params.setdefault('end_date', today.strftime('%Y-%m-%d'))

                # Fetch data using the appropriate function
                if api == 'newsdata':
                    news_data[api] = fetch_newsdata(api_params)
                elif api == 'newsapi':
                    news_data[api] = fetch_newsapi(api_params)
                elif api == 'gnews':
                    news_data[api] = fetch_gnews(api_params)
                elif api == 'mediastack':
                    news_data[api] = fetch_mediastack(api_params)
                elif api == 'currents':
                    news_data[api] = fetch_currents(api_params)
            else:
                logger.warning(f"Skipping unknown API: {api}")

        save_news_data(news_data)
        logger.info("News data fetched and saved successfully")
        return news_data
    except Exception as e:
        logger.error(f"An error occurred in main: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    result = main(
        apis_to_fetch=[
            'newsdata', 
            # 'newsapi', 
            # 'gnews', 
            # 'mediastack', 
            # 'currents'
            ],
        newsdata={'q': 'brazilian economy', 'country': 'us'},
        newsapi={'q': 'volleyball', 'sortBy': 'publishedAt', 'pageSize': 10},
        gnews={'q': 'triathlon tips', 'max': 5},
        mediastack={'keywords': 'travel on a budget', 'countries': 'us,gb', 'limit': 5},
        currents={'keywords': 'neuropsychology statistics and breakthroughs'}
    )
    print(json.dumps(result, indent=2))