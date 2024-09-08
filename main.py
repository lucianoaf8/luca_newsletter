import os
import sys
import json
from datetime import date
from jinja2 import Environment, FileSystemLoader
from scripts.db.fetch_subscribers import process_subscribers_data
from scripts.db.fetch_queries import fetch_all_data
from scripts.utils.logger_config import get_logger
from scripts.utils.send_email import send_html_email 
import pandas as pd
import re
import html

# Initialize logger
logger = get_logger('main')

def clean_and_format_text(text):
    # Remove special formatting markers
    text = re.sub(r'\{phrase\}|\{/phrase\}', '', text)
    
    # Replace square brackets and their content with empty string
    text = re.sub(r'\[.*?\]', '', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Escape HTML special characters
    text = html.escape(text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def prepare_subscriber_content(subscriber, long_date, formatted_date, weather_data, exchange_rate_data, quotes_data, fun_facts_data, word_of_the_day_data, english_tips_data, historical_events_data, daily_challenges_data):
    
    subscriber_content = {}

    # Helper function to convert pandas Timestamp to ISO format string
    def convert_timestamps(data):
        for key, value in data.items():
            if isinstance(value, pd.Timestamp):
                data[key] = value.isoformat()  # Convert Timestamp to string
        return data
    
    # Helper function to remove slashes from quotes
    def clean_escape_sequences(text):
        return text.replace("\\", "")  # Removes escape slashes

    # Helper function to convert numeric values to int and handle N/A values
    def to_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return value  # Return the original value if it can't be converted to int

    subscriber_content['header'] = {
            "newsletter_title": "Good Morning",
            "newsletter_username": subscriber['nickname'],
            "newsletter_date": long_date,
            "todays_date": formatted_date,
            "welcome_message": "Here's your today's Luca Newsletter",
            "presented_by": "Presented by ",
        }
    
    subscriber_content['coming_soon'] = "Coming soon"
    
    # Prepare weather data
    subscriber_city = subscriber['city']
    city_weather = weather_data[weather_data['location'] == subscriber_city]
    if not city_weather.empty:
        city_weather_dict = city_weather.iloc[0].to_dict()
        city_weather_dict = convert_timestamps(city_weather_dict)

        # Create nested structure for `data.values`
        city_weather_dict = weather_data.iloc[0].to_dict() if not weather_data.empty else {}

        weather_data_nested = {
                "uvIndex": to_int(city_weather_dict.get("data.values.uvIndex", "N/A")),
                "dewPoint": to_int(city_weather_dict.get("data.values.dewPoint", "N/A")),
                "humidity": to_int(city_weather_dict.get("data.values.humidity", "N/A")),
                "windGust": to_int(city_weather_dict.get("data.values.windGust", "N/A")),
                "cloudBase": to_int(city_weather_dict.get("data.values.cloudBase", "N/A")),
                "windSpeed": to_int(city_weather_dict.get("data.values.windSpeed", "N/A")),
                "cloudCover": to_int(city_weather_dict.get("data.values.cloudCover", "N/A")),
                "visibility": to_int(city_weather_dict.get("data.values.visibility", "N/A")),
                "temperature": to_int(city_weather_dict.get("data.values.temperature", "N/A")),
                "weatherCode": to_int(city_weather_dict.get("data.values.weatherCode", "N/A")),
                "cloudCeiling": to_int(city_weather_dict.get("data.values.cloudCeiling", "N/A")),
                "rainIntensity": to_int(city_weather_dict.get("data.values.rainIntensity", "N/A")),
                "snowIntensity": to_int(city_weather_dict.get("data.values.snowIntensity", "N/A")),
                "windDirection": to_int(city_weather_dict.get("data.values.windDirection", "N/A")),
                "sleetIntensity": to_int(city_weather_dict.get("data.values.sleetIntensity", "N/A")),
                "uvHealthConcern": to_int(city_weather_dict.get("data.values.uvHealthConcern", "N/A")),
                "temperatureApparent": to_int(city_weather_dict.get("data.values.temperatureApparent", "N/A")),
                "pressureSurfaceLevel": to_int(city_weather_dict.get("data.values.pressureSurfaceLevel", "N/A")),
                "freezingRainIntensity": to_int(city_weather_dict.get("data.values.freezingRainIntensity", "N/A")),
                "precipitationProbability": to_int(city_weather_dict.get("data.values.precipitationProbability", "N/A"))
        }

        subscriber_content['weather'] = weather_data_nested

        # Add the nested weather data along with additional fields
        weather_data_nested.update({
            "feels_like_name": "Feels like",
            "description": city_weather_dict.get('description', "Description not available"),
            "sunrise_name": "Sunrise",
            "sunrise": city_weather_dict.get('sunrise', "N/A"),
            "sunset_name": "Sunset",
            "sunset": city_weather_dict.get('sunset', "N/A"),
            "cloud_cover_name": "Cloud cover",
            "precipitation_name": "Precipitation",
            "humidity_name": "Humidity",
            "wind_name": "Wind",
            "uv_index_name": "UV Index",
            "coming_soon": "Coming soon"
        })
        subscriber_content['weather'] = weather_data_nested
    else:
        subscriber_content['weather'] = {}

    # Prepare simplified exchange rates content
    if not exchange_rate_data.empty:
        record = exchange_rate_data.iloc[0].to_dict()  # Assuming one row of exchange rates
        record = convert_timestamps(record)

        # Simplified exchange rates data structure
        exchange_rates_data = {
            "header": "Today's Exchange Rates",
            "cad_brl": str(record.get("CAD_to_BRL.today", "N/A")),
            "cad_brl_change": str(record.get("CAD_to_BRL.percentage_difference", "N/A")),
            "usd_brl": str(record.get("USD_to_BRL.today", "N/A")),
            "usd_brl_change": str(record.get("USD_to_BRL.percentage_difference", "N/A")),
            "usd_cad": str(record.get("USD_to_CAD.today", "N/A")),
            "usd_cad_change": str(record.get("USD_to_CAD.percentage_difference", "N/A"))
        }

        subscriber_content['exchange_rates'] = exchange_rates_data
    else:
        subscriber_content['exchange_rates'] = {}
    
    # Prepare quote of the day data
    if not quotes_data.empty:
        quote_of_the_day = quotes_data.iloc[0].to_dict()

        # Clean up the quote field
        if 'quote' in quote_of_the_day:
            quote_of_the_day['quote'] = clean_escape_sequences(quote_of_the_day['quote'])

        quote_of_the_day['author_pic'] = "https://planetsignshop.com/cdn/shop/products/COMING-SOON-10IN-ROUND-RIDER-RED.gif?v=1656448869"

        # Store in subscriber_content
        subscriber_content['quote_of_the_day'] = convert_timestamps(quote_of_the_day)
    else:
        subscriber_content['quote_of_the_day'] = {}
    
    subscriber_content['fun_fact'] = convert_timestamps(fun_facts_data.iloc[0].to_dict()) if not fun_facts_data.empty else {}
    
    if not word_of_the_day_data.empty:
        word_of_the_day = word_of_the_day_data.iloc[0].to_dict()
        if 'examples' in word_of_the_day:
            # Split the examples into separate examples
            examples = word_of_the_day['examples'].split(';')
            # Clean each example
            cleaned_examples = [clean_and_format_text(example) for example in examples]
            # Join the cleaned examples back together
            word_of_the_day['examples'] = '; '.join(cleaned_examples)
        subscriber_content['word_of_the_day'] = convert_timestamps(word_of_the_day)
    else:
        subscriber_content['word_of_the_day'] = {}
    
    subscriber_content['english_tip'] = convert_timestamps(english_tips_data.iloc[0].to_dict()) if not english_tips_data.empty else {}

    subscriber_content['news'] = {"message": "News not implemented yet"}

    subscriber_content['historical_event'] = convert_timestamps(historical_events_data.iloc[0].to_dict()) if not historical_events_data.empty else {}

    # Prepare challenge data
    challenge_data_nested = convert_timestamps(daily_challenges_data.iloc[0].to_dict()) if not daily_challenges_data.empty else {}
    
    # Add the nested challenge data along with additional fields
    challenge_data_nested.update({"header": "Today's Challenge"})
    
    subscriber_content['challenge'] = challenge_data_nested         

    subscriber_content['breathing_technique'] = {"motivation": "Just Breathe!"}
    
    subscriber_content['footer'] = {
        "goodbye": "See you tomorrow. Have a great day!",
        "reply": "Reply ",
        "unsubscribe": " to unsubscribe, report an error, or request a feature"
    }
    
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
        # Open the file with utf-8 encoding to handle special characters
        with open(file_path, 'w', encoding='utf-8') as html_file:
            html_file.write(rendered_html)
        logger.info(f"Saved newsletter for {subscriber['nickname']} at {file_path}")
        return file_path  # Return the file path for later use
    except Exception as e:
        logger.error(f"Error rendering newsletter for {subscriber['nickname']}: {e}")
        raise

def send_newsletter_email(subscriber, long_date, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()
        
        subject = f"{long_date} - Luca Newsletter"
        to_address = subscriber['email']
        send_html_email(to_address, subject, html_content)
        logger.info(f"Sent newsletter email to {subscriber['nickname']} at {to_address}")
    except Exception as e:
        logger.error(f"Error sending email to {subscriber['nickname']}: {e}")
        raise

def main():
    try:
        # Select today's date
        today = date.today()
        long_date = today.strftime("%B %d, %Y")
        formatted_date = today.strftime("%Y-%m-%d")
        logger.info(f"Processing newsletter for date: {formatted_date}")

        # Paths to save the content and ready newsletters
        content_feeder_path = os.path.join('data', 'content_feeder')
        newsletter_ready_path = os.path.join('data', 'newsletter_ready')

        # Fetch and process subscribers
        subscribers_df = process_subscribers_data()

        if subscribers_df is None or subscribers_df.empty:
            logger.error("No subscribers data available.")
            return

        logger.info(f"Processing newsletters for {len(subscribers_df)} subscribers")

        # Fetch all necessary queries data
        queries_data = fetch_all_data()

        # Prepare common section data
        weather_data = queries_data['weather_data']
        exchange_rate_data = queries_data['exchange_rate_data']
        quotes_data = queries_data['quotes_data']
        fun_fact_data = queries_data['fun_fact_data']
        word_of_the_day_data = queries_data['word_of_the_day_data']
        english_tips_data = queries_data['english_tips_data']
        historical_events_data = queries_data['historical_events_data']
        daily_challenges_data = queries_data['daily_challenges_data']

        # Initialize Jinja2 environment
        env = Environment(loader=FileSystemLoader(os.path.join('templates')))
        template = env.get_template('template.html')

        # Prepare content for each subscriber
        for _, subscriber in subscribers_df.iterrows():
            try:
                subscriber_content = prepare_subscriber_content(subscriber, long_date, formatted_date, weather_data, exchange_rate_data, quotes_data, fun_fact_data, word_of_the_day_data, english_tips_data, historical_events_data, daily_challenges_data)
                
                # Save subscriber content as JSON
                save_subscriber_content(subscriber, subscriber_content, formatted_date, content_feeder_path)

                # Render and save newsletter HTML
                newsletter_file_path = render_and_save_newsletter(subscriber, subscriber_content, formatted_date, template, newsletter_ready_path)

                # Send email
                send_newsletter_email(subscriber, long_date, newsletter_file_path)

            except Exception as e:
                logger.error(f"Error processing newsletter for subscriber {subscriber['nickname']}: {e}")
                # Continue with the next subscriber if there's an error with the current one
                continue

    except Exception as e:
        logger.error(f"An unexpected error occurred in main: {e}")

if __name__ == "__main__":
    main()