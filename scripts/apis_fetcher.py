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
logger = get_logger('apis_fetcher')

# List of API scripts to be called
# For the weather API, provide a tuple with the script and location
api_scripts = [
    ('scripts.apis.content_fetchers.weather_api', 'Calgary'),  # Weather for Calgary
    ('scripts.apis.content_fetchers.weather_api', 'Belo Horizonte'),  # Weather for Belo Horizonte
    ('scripts.apis.content_fetchers.exchange_rates_api', None)  # GTG
    # ('scripts.apis.content_fetchers.news_api', None)  # GTG
]

def run_api_script(script_module, param=None):
    try:
        module = importlib.import_module(script_module)
        if hasattr(module, 'main'):
            if param:
                logger.info(f"Running {script_module} with parameter: {param}")
                module.main(param)
            else:
                logger.info(f"Running {script_module}")
                module.main()
        else:
            logger.warning(f"No main function found in {script_module}")
    except Exception as e:
        logger.error(f"Error running {script_module}: {str(e)}")

def fetch_all_apis():
    logger.info("Starting API fetching process")
    start_time = datetime.now()

    for script, param in api_scripts:
        run_api_script(script, param)

    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"API fetching process completed in {duration}")

if __name__ == "__main__":
    fetch_all_apis()
