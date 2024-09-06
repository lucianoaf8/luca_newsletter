# scripts\utils\content_loader.py

import json
import jinja2
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

TEMPLATE_FILE_PATH = os.path.join(project_root, 'templates', 'template.html')
OUTPUT_DIR = os.path.join(project_root, 'data', 'newsletter_ready')

def convert_string_to_int_keys(data):
    if isinstance(data, dict):
        return {
            (int(k) if isinstance(k, str) and k.isdigit() else k): convert_string_to_int_keys(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [convert_string_to_int_keys(item) for item in data]
    else:
        return data

def load_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logger.info(f"Successfully loaded JSON data from {file_path}")
        return convert_string_to_int_keys(data)
    except FileNotFoundError:
        logger.error(f"JSON file not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in file: {file_path}")
        raise

def load_html_template(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            template = file.read()
        logger.info(f"Successfully loaded HTML template from {file_path}")
        return template
    except FileNotFoundError:
        logger.error(f"HTML template file not found: {file_path}")
        raise

def validate_data(data):
    required_fields = ['newsletter_title', 'newsletter_date', 'coming_soon', 'weather', 'exchange_rates', 'news', 'newsletter_username', 'todays_date']
    for field in required_fields:
        if field not in data:
            logger.error(f"Required field '{field}' is missing from the JSON data")
            raise ValueError(f"Required field '{field}' is missing from the JSON data")
    
    if 'comming_soon' in data and 'coming_soon' not in data:
        data['coming_soon'] = data.pop('comming_soon')
        logger.warning("Fixed spelling of 'comming_soon' to 'coming_soon'")

    if 'news' in data and 'topic' in data['news']:
        for topic_key, topic_value in data['news']['topic'].items():
            if 'title' not in topic_value or 'news' not in topic_value:
                logger.error(f"Invalid structure in news topic {topic_key}")
                raise ValueError(f"Invalid structure in news topic {topic_key}")
    else:
        logger.error("Invalid 'news' structure in JSON data")
        raise ValueError("Invalid 'news' structure in JSON data")

def render_template(template_string, data):
    try:
        env = jinja2.Environment(undefined=jinja2.StrictUndefined)
        template = env.from_string(template_string)
        rendered_html = template.render(**data)
        logger.info("Successfully rendered the template with provided data")
        return rendered_html
    except jinja2.exceptions.UndefinedError as e:
        logger.error(f"Template rendering error: {str(e)}")
        logger.error(f"Check if '{str(e).split()[-1]}' exists in your JSON data.")
        raise
    except jinja2.TemplateError as e:
        logger.error(f"Error rendering template: {str(e)}")
        raise

def save_rendered_html(html_content, username, date):
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        file_name = f"{username}_{date}.html"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        logger.info(f"Successfully saved rendered HTML to {file_path}")
    except IOError as e:
        logger.error(f"Error writing to file: {file_path}")
        raise

def main(json_data):
    logger.info("Starting content loader script")
    try:
        json_data = convert_string_to_int_keys(json_data)
        validate_data(json_data)
        template_content = load_html_template(TEMPLATE_FILE_PATH)
        rendered_html = render_template(template_content, json_data)
        
        # Extract username and date from the JSON data
        username = json_data.get('newsletter_username')
        date = json_data.get('todays_date')
        
        save_rendered_html(rendered_html, username, date)
        
        logger.info(f"Newsletter successfully rendered and saved for {username}")
    except Exception as e:
        logger.exception(f"An error occurred during script execution: {str(e)}")
        raise

if __name__ == "__main__":
    # This block is only for testing the script standalone
    TEST_JSON_FILE_PATH = r"C:\Projects\luca_newsletter_official\data\content_feeder\content.json"
    logger.info(f"Testing script with JSON file: {TEST_JSON_FILE_PATH}")
    json_data = load_json_data(TEST_JSON_FILE_PATH)
    main(json_data)