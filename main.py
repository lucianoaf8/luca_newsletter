import os
import sys
import json
from datetime import date
from jinja2 import Environment, FileSystemLoader

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from scripts.db.fetch_subscribers import process_subscribers_data
from scripts.db.fetch_queries import fetch_all_data
from scripts.utils.logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

def main():
    try:
        # Select today's date
        today = date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        logger.info(f"Processing newsletter for date: {formatted_date}")

        # Paths to save the content and ready newsletters
        content_feeder_path = os.path.join(project_root, 'data', 'content_feeder')
        newsletter_ready_path = os.path.join(project_root, 'data', 'newsletter_ready')

        # Fetch and process subscribers
        subscribers_df = process_subscribers_data()

        if subscribers_df is None or subscribers_df.empty:
            logger.error("No subscribers data available.")
            return

        logger.info(f"Processing newsletters for {len(subscribers_df)} subscribers")

        # Fetch all necessary queries data
        queries_data = fetch_all_data()

        # Prepare common section data
        exchange_rate_data = queries_data['exchange_rate_data']
        quotes_data = queries_data['quotes_data']
        english_tips_data = queries_data['english_tips_data']
        daily_challenges_data = queries_data['daily_challenges_data']
        weather_data = queries_data['weather_data']

        # Initialize Jinja2 environment
        env = Environment(loader=FileSystemLoader(os.path.join(project_root, 'templates')))
        template = env.get_template('template.html')

        # Prepare content for each subscriber
        for _, subscriber in subscribers_df.iterrows():
            try:
                subscriber_content = prepare_subscriber_content(subscriber, weather_data, exchange_rate_data, quotes_data, english_tips_data, daily_challenges_data)
                
                # Save subscriber content as JSON
                save_subscriber_content(subscriber, subscriber_content, formatted_date, content_feeder_path)

                # Render and save newsletter HTML
                render_and_save_newsletter(subscriber, subscriber_content, formatted_date, template, newsletter_ready_path)

            except Exception as e:
                logger.error(f"Error processing newsletter for subscriber {subscriber['nickname']}: {e}")

    except Exception as e:
        logger.error(f"An unexpected error occurred in main: {e}")

def prepare_subscriber_content(subscriber, weather_data, exchange_rate_data, quotes_data, english_tips_data, daily_challenges_data):
    subscriber_content = {}

    # Prepare weather data
    subscriber_city = subscriber['city']
    city_weather = weather_data[weather_data['city'] == subscriber_city]
    subscriber_content['weather'] = city_weather.iloc[0].to_dict() if not city_weather.empty else {}

    # Prepare other content sections
    subscriber_content['exchange_rates'] = exchange_rate_data.to_dict(orient='records')
    subscriber_content['quote_of_the_day'] = quotes_data.iloc[0].to_dict() if not quotes_data.empty else {}
    subscriber_content['word_of_the_day'] = english_tips_data.iloc[0].to_dict() if not english_tips_data.empty else {}
    subscriber_content['challenge'] = daily_challenges_data.iloc[0].to_dict() if not daily_challenges_data.empty else {}

    # Placeholder for news and fun fact (to be implemented)
    subscriber_content['news'] = {"message": "News data fetching not implemented yet"}
    subscriber_content['fun_fact'] = {"message": "Fun fact data fetching not implemented yet"}
    subscriber_content['historical_event'] = {"message": "Historical event data fetching not implemented yet"}

    return subscriber_content

def save_subscriber_content(subscriber, content, date, path):
    file_name = f"{subscriber['nickname']}_{date}.json"
    file_path = os.path.join(path, file_name)
    try:
        with open(file_path, 'w') as json_file:
            json.dump(content, json_file, indent=4)
        logger.info(f"Saved content for {subscriber['nickname']} at {file_path}")
    except IOError as e:
        logger.error(f"Error saving content for {subscriber['nickname']}: {e}")

def render_and_save_newsletter(subscriber, content, date, template, path):
    try:
        rendered_html = template.render(content)
        file_name = f"{subscriber['nickname']}_{date}.html"
        file_path = os.path.join(path, file_name)
        with open(file_path, 'w') as html_file:
            html_file.write(rendered_html)
        logger.info(f"Saved newsletter for {subscriber['nickname']} at {file_path}")
    except Exception as e:
        logger.error(f"Error rendering newsletter for {subscriber['nickname']}: {e}")

if __name__ == "__main__":
    main()