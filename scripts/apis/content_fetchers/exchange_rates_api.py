import os
import json
from datetime import datetime
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

def fetch_exchange_rates(client, currencies):
    """Fetch the latest exchange rates for specified currencies."""
    logger.info(f"Fetching exchange rates for currencies: {currencies}")
    try:
        result = client.latest(currencies=currencies)
        logger.info("Exchange rates fetched successfully")
        return result
    except Exception as e:
        logger.error(f"Error fetching exchange rates: {e}")
        raise

def process_exchange_rates(result, currencies):
    """Process and log the fetched exchange rates."""
    logger.info("Processing fetched exchange rates")
    exchange_rates = {}
    for currency in currencies:
        rate = result['data'].get(currency)
        if rate:
            exchange_rates[currency] = rate
            logger.info(f"USD to {currency} = {rate}")
        else:
            logger.warning(f"Exchange rate for {currency} not found in the response")
    return exchange_rates

def calculate_cross_rate(exchange_rates, from_currency, to_currency):
    """Calculate the cross-rate between two currencies."""
    if from_currency not in exchange_rates or to_currency not in exchange_rates:
        logger.error(f"Cannot calculate cross-rate: missing data for {from_currency} or {to_currency}")
        return None
    
    # Calculate cross-rate
    if from_currency == 'USD':
        cross_rate = exchange_rates[to_currency]
    elif to_currency == 'USD':
        cross_rate = 1 / exchange_rates[from_currency]
    else:
        cross_rate = exchange_rates[to_currency] / exchange_rates[from_currency]
    
    logger.info(f"Calculated cross-rate: 1 {from_currency} = {cross_rate:.4f} {to_currency}")
    return cross_rate

def save_json_response(data, currency_pairs):
    """Save the entire JSON response along with cross-rates to a file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data', 'exchange_rates')
    os.makedirs(data_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"exchange_rates_{timestamp}.json"
    file_path = os.path.join(data_dir, filename)
    
    # Add cross-rates to the data
    data['cross_rates'] = {
        f"{from_currency}_to_{to_currency}": rate
        for (from_currency, to_currency), rate in currency_pairs.items()
    }
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved JSON response with cross-rates to {file_path}")

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

        # Define currencies to fetch
        currencies = ['USD', 'CAD', 'BRL']

        # Define currency pairs to calculate
        currency_pairs = [
            ('CAD', 'BRL'),
            ('USD', 'BRL'),
            ('USD', 'CAD')
        ]

        # Fetch exchange rates
        result = fetch_exchange_rates(client, currencies)

        # Process exchange rates
        exchange_rates = process_exchange_rates(result, currencies)

        # Calculate cross-rates
        cross_rates = {}
        for from_currency, to_currency in currency_pairs:
            rate = calculate_cross_rate(exchange_rates, from_currency, to_currency)
            if rate:
                cross_rates[(from_currency, to_currency)] = rate

        # Save the response along with cross-rates
        save_json_response(result, cross_rates)

        # Print results
        print("Exchange rates:")
        for (from_currency, to_currency), rate in cross_rates.items():
            print(f"1 {from_currency} = {rate:.4f} {to_currency}")

    except ValueError as ve:
        logger.error(f"Value Error: {ve}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Script execution completed")

if __name__ == "__main__":
    main()