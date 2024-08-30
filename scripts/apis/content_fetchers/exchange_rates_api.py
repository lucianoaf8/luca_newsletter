import os
import json
from datetime import datetime, timedelta
import freecurrencyapi
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.logger_config import get_logger

# Initialize logger
logger = get_logger('fetch_exchange_rates')

def get_api_key():
    """Fetch the API key from environment variables."""
    logger.info("Attempting to load API key from environment variables")
    api_key = os.getenv('FREECURRENCYAPI_KEY')
    if not api_key:
        logger.error('API Key not found in environment variables. Please check your .env file.')
        raise ValueError("API Key is missing")
    logger.info("API key loaded successfully")
    return api_key

def fetch_exchange_rates(client, base_currency, currencies, date=None):
    """Fetch the latest or historical exchange rates for specified currencies."""
    if date:
        logger.info(f"Fetching historical exchange rates for {date} for currencies: {currencies}")
        result = client.historical(date=date, base_currency=base_currency, currencies=currencies)
    else:
        logger.info(f"Fetching latest exchange rates for currencies: {currencies}")
        result = client.latest(base_currency=base_currency, currencies=currencies)
    return result

def process_exchange_rates(result, currencies):
    """Process and log the fetched exchange rates."""
    logger.info("Processing fetched exchange rates")
    exchange_rates = {}
    for currency in currencies:
        rate = result['data'].get(currency)
        if rate:
            exchange_rates[currency] = rate
            logger.info(f"{result['meta']['base_currency']} to {currency} = {rate}")
        else:
            logger.warning(f"Exchange rate for {currency} not found in the response")
    return exchange_rates

def calculate_percentage_change(current_rate, previous_rate):
    """Calculate the percentage change between two rates."""
    if previous_rate == 0:
        return 0.0
    return ((current_rate - previous_rate) / previous_rate) * 100

def save_json_response(data, output_dir='data/fetched_results/exchange_rates'):
    """Save the entire JSON response to a file."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"exchange_rates_{timestamp}.json"
    file_path = os.path.join(output_dir, filename)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved JSON response to {file_path}")

def main():
    try:
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")

        # Get API key
        api_key = get_api_key()

        # Initialize the FreeCurrencyAPI client
        client = freecurrencyapi.Client(api_key)
        logger.info("FreeCurrencyAPI client initialized")

        # Define base currency and currencies to fetch
        base_currency = 'USD'
        currencies = ['CAD', 'BRL']

        # Fetch today's exchange rates
        result_today = fetch_exchange_rates(client, base_currency, currencies)

        # Fetch yesterday's exchange rates
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        result_yesterday = fetch_exchange_rates(client, base_currency, currencies, date=yesterday)

        # Process exchange rates
        exchange_rates_today = process_exchange_rates(result_today, currencies)
        exchange_rates_yesterday = process_exchange_rates(result_yesterday, currencies)

        # Calculate percentage changes and prepare final data
        final_data = {
            'base_currency': base_currency,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'exchange_rates': {}
        }

        for currency in currencies:
            if currency in exchange_rates_today and currency in exchange_rates_yesterday:
                rate_today = exchange_rates_today[currency]
                rate_yesterday = exchange_rates_yesterday[currency]
                change = calculate_percentage_change(rate_today, rate_yesterday)
                final_data['exchange_rates'][currency] = {
                    'rate': rate_today,
                    'rate_yesterday': rate_yesterday,
                    'percentage_change': round(change, 4)
                }
        
        # Save the response
        save_json_response(final_data)

        # Print results
        print("Exchange rates and percentage changes:")
        for currency, details in final_data['exchange_rates'].items():
            print(f"{base_currency} to {currency}: Today's rate = {details['rate']}, Yesterday's rate = {details['rate_yesterday']}, Change = {details['percentage_change']}%")

    except ValueError as ve:
        logger.error(f"Value Error: {ve}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Script execution completed")

if __name__ == "__main__":
    main()