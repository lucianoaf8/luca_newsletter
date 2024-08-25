import json
import jinja2
import os
import sys
from pprint import pformat

# Add the parent directory of 'scripts' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.logger_config import get_logger

# Initialize logger
logger = get_logger("content_loader")

JSON_FILE_PATH = r"C:\Projects\luca_newsletter_official\data\content_feeder\content.json"
TEMPLATE_FILE_PATH = r"C:\Projects\luca_newsletter_official\templates\index.html"
OUTPUT_FILE_PATH = r"C:\Projects\luca_newsletter_official\data\newsletter_ready\rendered_newsletter.html"

def convert_string_to_int_keys(data):
    if isinstance(data, dict):
        return {int(k) if k.isdigit() else k: convert_string_to_int_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_string_to_int_keys(item) for item in data]
    else:
        return data

def load_json_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        logger.info(f"Successfully loaded JSON data from {file_path}")
        data = convert_string_to_int_keys(data)
        logger.debug(f"JSON data structure after key conversion:\n{pformat(data)}")
        return data
    except FileNotFoundError:
        logger.error(f"JSON file not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in file: {file_path}")
        raise

def load_html_template(file_path):
    try:
        with open(file_path, 'r') as file:
            template = file.read()
        logger.info(f"Successfully loaded HTML template from {file_path}")
        return template
    except FileNotFoundError:
        logger.error(f"HTML template file not found: {file_path}")
        raise

def validate_data(data):
    required_fields = ['newsletter_title', 'newsletter_date', 'coming_soon', 'weather', 'exchange_rates', 'news']
    for field in required_fields:
        if field not in data:
            logger.error(f"Required field '{field}' is missing from the JSON data")
            raise ValueError(f"Required field '{field}' is missing from the JSON data")
    
    # Fix the spelling of 'coming_soon' if necessary
    if 'comming_soon' in data and 'coming_soon' not in data:
        data['coming_soon'] = data.pop('comming_soon')
        logger.warning("Fixed spelling of 'comming_soon' to 'coming_soon'")

    # Ensure 'news' has the correct structure
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
        # Custom Jinja2 environment with better undefined handling
        env = jinja2.Environment(undefined=jinja2.StrictUndefined)
        template = env.from_string(template_string)
        rendered_html = template.render(**data)  # Use **data to unpack the dictionary
        logger.info("Successfully rendered the template with provided data")
        return rendered_html
    except jinja2.exceptions.UndefinedError as e:
        logger.error(f"Template rendering error: {str(e)}")
        logger.error("This usually means the template is trying to access a variable that doesn't exist in the data.")
        logger.error(f"Check if '{str(e).split()[-1]}' exists in your JSON data.")
        raise
    except jinja2.TemplateError as e:
        logger.error(f"Error rendering template: {str(e)}")
        raise

def save_rendered_html(html_content, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        logger.info(f"Successfully saved rendered HTML to {file_path}")
    except IOError:
        logger.error(f"Error writing to file: {file_path}")
        raise

def main():
    logger.info("Starting content loader script")
    try:
        # Load JSON data
        json_data = load_json_data(JSON_FILE_PATH)
        
        # Validate and potentially fix the data
        validate_data(json_data)
        
        # Load HTML template
        template_content = load_html_template(TEMPLATE_FILE_PATH)
        
        # Render the template
        rendered_html = render_template(template_content, json_data)
        
        # Save the rendered HTML
        save_rendered_html(rendered_html, OUTPUT_FILE_PATH)
        
        logger.info(f"Newsletter successfully rendered and saved to {OUTPUT_FILE_PATH}")
    except Exception as e:
        logger.exception(f"An error occurred during script execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()