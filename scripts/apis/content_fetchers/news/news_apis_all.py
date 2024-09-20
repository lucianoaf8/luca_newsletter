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

def fetch_news(url, params, api_name, max_retries=3):
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
            logger.error(f"Request URL: {response.url}")  # Log the full URL for debugging
            if attempt == max_retries - 1:
                logger.error(f"Max retries reached for {api_name}. Giving up.")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff

def fetch_newsdata(q, country=None, language=None, category=None, from_date=None, to_date=None):
    url = "https://newsdata.io/api/1/archive"
    params = {
        'apikey': os.getenv("NEWSDATA_API_KEY"),
        'q': q,
        'country': country,
        'language': language,
        'category': category,
        'from_date': from_date
    }
    params = {k: v for k, v in params.items() if v is not None}
    return fetch_news(url, params, 'newsdata')

def fetch_newsapi(q, sources=None, language=None, sort_by=None, page_size=None, page=None, from_date=None, to_date=None):
    url = "https://newsapi.org/v2/everything"
    params = {
        'apiKey': os.getenv("NEWSAPI_KEY"),
        'q': q,
        'sources': sources,
        'language': language,
        'sortBy': sort_by,
        'pageSize': page_size,
        'page': page,
        'from': from_date,
        'to': to_date
    }
    params = {k: v for k, v in params.items() if v is not None}
    return fetch_news(url, params, 'newsapi')

def fetch_gnews(q, lang=None, country=None, max=None, from_date=None, to=None):
    url = "https://gnews.io/api/v4/search"
    params = {
        'token': os.getenv("GNEWS_API_KEY"),
        'q': q,
        'lang': lang,
        'country': country,
        'max': max,
        'from': from_date,
        'to': to
    }
    params = {k: v for k, v in params.items() if v is not None}
    return fetch_news(url, params, 'gnews')

def fetch_mediastack(keywords, countries=None, categories=None, languages=None, sort=None, limit=None, offset=None, date=None):
    url = "http://api.mediastack.com/v1/news"
    params = {
        'access_key': os.getenv("MEDIASTACK_API_KEY"),
        'keywords': keywords,
        'countries': countries,
        'categories': categories,
        'languages': languages,
        'sort': sort,
        'limit': limit,
        'offset': offset,
        'date': date
    }
    params = {k: v for k, v in params.items() if v is not None}
    return fetch_news(url, params, 'mediastack')

def fetch_currents(keywords, language=None, country=None, start_date=None, end_date=None):
    url = "https://api.currentsapi.services/v1/search"
    params = {
        'apiKey': os.getenv("CURRENTS_API_KEY"),
        'keywords': keywords,
        'language': language,
        'country': country,
        'start_date': start_date,
        'end_date': end_date
    }
    params = {k: v for k, v in params.items() if v is not None}
    return fetch_news(url, params, 'currents')

def save_news_data(news_data):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder_path = os.path.join(project_root, 'data', 'fetched_results', 'news', timestamp)
    os.makedirs(folder_path, exist_ok=True)
    
    for api_name, api_data in news_data.items():
        filename = f'{api_name}_data.json'
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, 'w') as f:
            json.dump(api_data, f, indent=4)
        
        logger.info(f"{api_name} data saved to {file_path}")

def run_apis(apis_to_fetch, **kwargs):
    news_data = {}
    api_functions = {
        'newsdata': fetch_newsdata,
        'newsapi': fetch_newsapi,
        'gnews': fetch_gnews,
        'mediastack': fetch_mediastack,
        'currents': fetch_currents
    }

    for api in apis_to_fetch:
        if api in api_functions:
            api_params = kwargs.get(api, {})
            news_data[api] = api_functions[api](**api_params)
        else:
            logger.warning(f"Skipping unknown API: {api}")

    return news_data

def main(apis_to_fetch=None, **kwargs):
    try:
        if apis_to_fetch is None:
            apis_to_fetch = ['newsdata', 'newsapi', 'gnews', 'mediastack', 'currents']
        elif isinstance(apis_to_fetch, str):
            apis_to_fetch = [apis_to_fetch]

        news_data = run_apis(apis_to_fetch, **kwargs)
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
            'newsapi', 
            'gnews', 
            'mediastack', 
            'currents'
            ],
        newsdata={
            'q': 'elections',
            'country': 'us',
            'from_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            # 'to_date': datetime.now().strftime('%Y-%m-%d')
        },
        newsapi={
            'q': 'volleyball',
            'sort_by': 'publishedAt',
            'page_size': 10,
            'from_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        },
        gnews={
            'q': 'triathlon tips',
            'max': 5,
            'from_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'to': datetime.now().strftime('%Y-%m-%d')
        },
        mediastack={
            'keywords': 'travel on a budget',
            'countries': 'us,gb',
            'limit': 5,
            'date': f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')},{datetime.now().strftime('%Y-%m-%d')}"
        },
        currents={
            'keywords': 'neuropsychology statistics and breakthroughs',
            'start_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d')
        }
    )
    print(json.dumps(result, indent=2))