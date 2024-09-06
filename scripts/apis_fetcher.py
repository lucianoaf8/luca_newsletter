# scripts\apis_fetcher.py

import os
import sys
import importlib
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

# List of API scripts to be called
api_scripts = [
    'scripts.apis.content_fetchers.weather_api', # TODO add location parameter
    'scripts.apis.content_fetchers.exchange_rates_api', # GTG
    'scripts.apis.content_fetchers.news_api', 
    'scripts.apis.content_fetchers.word_of_the_day'
]

def run_api_script(script_module):
    try:
        module = importlib.import_module(script_module)
        if hasattr(module, 'main'):
            logger.info(f"Running {script_module}")
            module.main()
        else:
            logger.warning(f"No main function found in {script_module}")
    except Exception as e:
        logger.error(f"Error running {script_module}: {str(e)}")

def fetch_all_apis():
    logger.info("Starting API fetching process")
    start_time = datetime.now()

    for script in api_scripts:
        run_api_script(script)

    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"API fetching process completed in {duration}")

if __name__ == "__main__":
    fetch_all_apis()