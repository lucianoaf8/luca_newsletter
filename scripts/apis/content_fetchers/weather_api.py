# scripts\apis\content_fetchers\weather_api.py

import sys
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.utils.db_insert_api_calls import insert_api_response

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logger = get_logger('weather_api')

# Initialize Geolocator
geolocator = Nominatim(user_agent="weather_app")  # Replace "weather_app" with your application's name

def get_api_key():
    """Fetch the API key from environment variables."""
    api_key = os.getenv('TOMORROW_API_KEY')
    if not api_key:
        logger.error("API key not found! Please set the TOMORROW_API_KEY environment variable.")
        raise ValueError("API key not found!")
    logger.info("API key loaded successfully.")
    return api_key

def geocode_location(location_name):
    """
    Convert a city name to latitude and longitude using Geopy's Nominatim.

    Args:
        location_name (str): The name of the city.

    Returns:
        tuple: (latitude, longitude)

    Raises:
        ValueError: If the location cannot be geocoded.
    """
    try:
        logger.info(f"Geocoding location: {location_name}...")
        location = geolocator.geocode(location_name, exactly_one=True, timeout=10)
        if location:
            logger.info(f"Geocoded '{location_name}' to (Latitude: {location.latitude}, Longitude: {location.longitude}).")
            return (location.latitude, location.longitude)
        else:
            logger.error(f"Geocoding failed: Could not find coordinates for '{location_name}'.")
            raise ValueError(f"Could not geocode location: {location_name}")
    except GeocoderTimedOut:
        logger.error(f"Geocoding timed out for location: {location_name}.")
        raise
    except GeocoderServiceError as e:
        logger.error(f"Geocoding service error for location: {location_name}: {e}")
        raise

def fetch_weather_data(api_key, latitude, longitude, location_name):
    """Fetch daily weather forecast data from the Tomorrow.io API using coordinates."""
    url = 'https://api.tomorrow.io/v4/weather/forecast'
    params = {
        'apikey': api_key,
        'location': f"{latitude},{longitude}",
        'timesteps': '1d',
        'units': 'metric',
        'fields': 'weatherCode,temperature,humidity,windSpeed'  # Comma-separated string
    }
    
    logger.info(f"Fetching daily weather forecast for coordinates: ({latitude}, {longitude})...")
    response = requests.get(url, params=params)
    logger.debug(f"API Request URL: {response.url}")  # Log the full request URL
    
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred for coordinates ({latitude}, {longitude}): {http_err}")
        try:
            error_response = response.json()
            logger.error(f"Error details: {error_response}")
        except Exception:
            logger.error("Failed to parse error response.")
        raise  # Re-raise the exception after logging
    
    # Modify the response JSON to include the location name
    weather_data = response.json()
    weather_data['location'] = {
        'lat': latitude,
        'lon': longitude,
        'name': location_name
    }
    
    return weather_data

def save_json_response(data, location_name):
    """Save the entire JSON response to a file."""
    data_dir = os.path.join(project_root, 'data', 'fetched_results', 'weather_api')
    os.makedirs(data_dir, exist_ok=True)
    
    sanitized_location = location_name.replace(' ', '_').replace(',', '')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{sanitized_location}_{timestamp}.json"
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

def main(location_name=None):
    if location_name is None:
        raise ValueError("A location name must be provided for weather fetching.")
    
    try:
        api_key = get_api_key()
        latitude, longitude = geocode_location(location_name)
        weather_data = fetch_weather_data(api_key, latitude, longitude, location_name)
        process_weather_data(weather_data, location_name)
        save_json_response(weather_data, location_name)
        
        # Insert into api_calls table
        script_path = os.path.abspath(__file__)
        payload = {'location': location_name, 'units': 'metric'}
        custom_params = f"location={latitude},{longitude}&units=metric"
        insert_api_response(script_path, payload, weather_data, custom_params)
        
    except ValueError as e:
        logger.error(f"Value error for {location_name}: {e}")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred for {location_name}: {http_err}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to connect for {location_name}. Check your internet connection.")
    except requests.exceptions.Timeout:
        logger.error(f"The request timed out for {location_name}.")
    except requests.exceptions.RequestException as err:
        logger.error(f"A request error occurred for {location_name}: {err}")
    except GeocoderTimedOut:
        logger.error(f"Geocoding timed out for {location_name}.")
    except GeocoderServiceError as e:
        logger.error(f"Geocoding service error for {location_name}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred for {location_name}: {e}")
    finally:
        logger.info(f"Script execution finished for {location_name}.")

if __name__ == "__main__":
    # Define the location name here
    location_name = "Calgary"
    main(location_name)
