import os
import requests
from dotenv import load_dotenv
from scripts.utils.logger_config import get_logger
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logger = get_logger('motivational_content')

# Fetch the API key from environment variables
api_key = os.getenv('ZYLA_MOTIVATIONAL_API_KEY')

if not api_key:
    logger.error('API Key not found in environment variables. Please check your .env file.')
    raise ValueError("API Key is missing")

# Define the API URL
api_url = "https://zylalabs.com/api/2361/motivational+content+api/2283/get+quotes"

# Set up headers with the API key
headers = {
    'Authorization': f'Bearer {api_key}'
}

try:
    # Make a request to the API
    response = requests.get(api_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        content = response.json()

        # Assume the response has 'quote' or 'challenge' in the data (modify based on API docs)
        motivational_quote = content[0].get("quote", "No quote found")
        daily_challenge = content[0].get("challenge", "No challenge found")

        # Save the content to a .txt file
        file_name = f"daily_motivation_{datetime.now().strftime('%Y-%m-%d')}.txt"
        file_path = os.path.join('motivational_quotes', file_name)

        # Ensure the directory exists
        if not os.path.exists('motivational_quotes'):
            os.makedirs('motivational_quotes')

        with open(file_path, 'w') as file:
            file.write(f"Motivational Quote: {motivational_quote}\n")
            file.write(f"Daily Challenge: {daily_challenge}\n")

        logger.info(f"Successfully saved the daily motivational content to {file_path}")

    else:
        logger.error(f"Failed to fetch data: {response.status_code} - {response.text}")

except Exception as e:
    logger.error(f"Error fetching motivational content: {e}")
    print("Failed to fetch motivational content.")
