import os
import sys
import json
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.utils.db_insert_api_calls import insert_api_response

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Constants
BASE_URL_HISTORICAL = 'https://api.freecurrencyapi.com/v1/historical'
BASE_URL_LATEST = 'https://api.freecurrencyapi.com/v1/latest'
API_KEY = os.getenv('FREECURRENCYAPI_KEY')

def remove_api_key_from_params(params):
    return {k: v for k, v in params.items() if k != 'apikey'}

def fetch_currency_data(url, params):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise

def calculate_rate(from_currency, to_currency, data):
    if from_currency == 'USD':
        return data[to_currency]
    elif to_currency == 'USD':
        return 1 / data[from_currency]
    else:
        return data[to_currency] / data[from_currency]

def calculate_percentage_difference(yesterday_rate, today_rate):
    return ((today_rate - yesterday_rate) / yesterday_rate) * 100

def process_exchange_rates():
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # Fetch yesterday's data
    params_yesterday = {
        'apikey': API_KEY,
        'date': yesterday,
        'base_currency': 'USD',
        'currencies': 'CAD,BRL'
    }
    yesterday_data = fetch_currency_data(BASE_URL_HISTORICAL, params_yesterday)['data'][yesterday]

    # Fetch today's data
    params_today = {
        'apikey': API_KEY,
        'base_currency': 'USD',
        'currencies': 'CAD,BRL'
    }
    today_data = fetch_currency_data(BASE_URL_LATEST, params_today)['data']

    # Calculate rates and differences
    currency_pairs = [('USD', 'BRL'), ('CAD', 'BRL'), ('USD', 'CAD')]
    output = {}

    for from_currency, to_currency in currency_pairs:
        pair_key = f"{from_currency}_to_{to_currency}"
        yesterday_rate = calculate_rate(from_currency, to_currency, yesterday_data)
        today_rate = calculate_rate(from_currency, to_currency, today_data)
        diff = calculate_percentage_difference(yesterday_rate, today_rate)

        output[pair_key] = {
            'yesterday': round(yesterday_rate, 4),
            'today': round(today_rate, 4),
            'percentage_difference': round(diff, 2)
        }

    return output, {'yesterday': params_yesterday, 'today': params_today}

def save_output(output):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'exchange_rates_{timestamp}.json'
    file_path = os.path.join(project_root, 'data', 'fetched_results', 'exchange_rates', filename)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as f:
        json.dump(output, f, indent=4)

    logger.info(f"Output saved to {file_path}")
    return file_path

def main():
    try:
        output, combined_params = process_exchange_rates()
        output_file_path = save_output(output)

        # Remove API key from combined_params
        combined_params['yesterday'] = remove_api_key_from_params(combined_params['yesterday'])
        combined_params['today'] = remove_api_key_from_params(combined_params['today'])

        # Log the combined API call with the final output
        script_path = os.path.abspath(__file__)
        with open(output_file_path, 'r') as f:
            final_output = json.load(f)
        
        insert_api_response(script_path, combined_params, final_output)
        
        logger.info("Exchange rates processed and saved successfully")
    except Exception as e:
        logger.error(f"An error occurred in main: {e}")

if __name__ == "__main__":
    main()