# scripts\apis\content_fetchers\weather_api.py

import sys
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.utils.db_insert_api_calls import insert_api_response

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logger = get_logger('weather_api')

def get_api_key():
    """Fetch the API key from environment variables."""
    api_key = os.getenv('TOMORROW_API_KEY')
    if not api_key:
        logger.error("API key not found! Please set the TOMORROW_API_KEY environment variable.")
        raise ValueError("API key not found!")
    logger.info("API key loaded successfully.")
    return api_key

def fetch_weather_data(api_key, location):
    """Fetch daily weather forecast data from the Tomorrow.io API."""
    url = 'https://api.tomorrow.io/v4/weather/forecast'
    params = {
        'apikey': api_key,
        'location': location,
        'timesteps': '1d',  # daily forecast
        'units': 'metric'
    }
    
    logger.info(f"Fetching daily weather forecast for location: {location}...")
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def save_json_response(data, location):
    """Save the entire JSON response to a file."""

    data_dir = os.path.join(project_root, 'data', 'fetched_results', 'weather_api')
    os.makedirs(data_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{location.replace(' ', '_')}_{timestamp}.json"
    file_path = os.path.join(data_dir, filename)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved entire JSON response to {file_path}")
    return timestamp

def process_weather_data(weather_data, location):
    """Process and log the weather data."""
    if 'data' in weather_data and 'values' in weather_data['data']:
        logger.info(f"Weather data retrieved successfully for {location}.")
        values = weather_data['data']['values']
        logger.info(f"Temperature: {values.get('temperature')}°C")
        logger.info(f"Humidity: {values.get('humidity')}%")
        logger.info(f"Wind Speed: {values.get('windSpeed')} m/s")
        logger.info(f"Weather Code: {values.get('weatherCode')}")
    else:
        logger.warning(f"Response received for {location}, but no valid data found.")
    logger.debug(f"Full response: {json.dumps(weather_data, indent=2)}")

def main(location):
    try:
        api_key = get_api_key()
        weather_data = fetch_weather_data(api_key, location)
        process_weather_data(weather_data, location)
        save_json_response(weather_data, location)
        
        # Insert into api_calls table
        script_path = os.path.abspath(__file__)
        payload = {'location': location, 'units': 'metric'}
        custom_params = f"location={location}&units=metric"
        insert_api_response(script_path, payload, weather_data, custom_params)
        
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred for {location}: {http_err}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to connect for {location}. Check your internet connection.")
    except requests.exceptions.Timeout:
        logger.error(f"The request timed out for {location}.")
    except requests.exceptions.RequestException as err:
        logger.error(f"A request error occurred for {location}: {err}")
    except ValueError as e:
        logger.error(f"Value error for {location}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred for {location}: {e}")
    finally:
        logger.info(f"Script execution finished for {location}.")

if __name__ == "__main__":
    location = "Belo Horizonte"
    main(location)