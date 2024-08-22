import os
import openai
import json
from dotenv import load_dotenv
from datetime import datetime
from utils import get_logger  # Assuming the logger_config.py is in your utils folder

# Setup logger
logger = get_logger('summarize_news')

# Load the API key from the .env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI with your API key
openai.api_key = api_key

def summarize_text(text):
    try:
        logger.info("Starting text summarization process.")
        
        # API call to summarize text
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize the following text:\n\n{text}",
            max_tokens=150,
            temperature=0.5
        )
        
        summary = response['choices'][0]['text'].strip()
        logger.info("Summarization successful.")
        
        # Save the full response to a JSON file
        save_response_to_json(response)

        return summary
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return f"Error: {e}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Error: {e}"

def save_response_to_json(response):
    """Saves the API response to a JSON file for safe keeping."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summarization_response_{timestamp}.json"
        
        with open(filename, 'w') as json_file:
            json.dump(response, json_file, indent=4)
        
        logger.info(f"Response saved successfully to {filename}.")
    except Exception as e:
        logger.error(f"Failed to save response to JSON: {e}")

# Example usage
if __name__ == "__main__":
    text_to_summarize = "Your text here for summarization"
    summary = summarize_text(text_to_summarize)
    print("Summary:", summary)
