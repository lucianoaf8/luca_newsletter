import os
import sys
import json
from datetime import date
from jinja2 import Environment, FileSystemLoader
from scripts.db.fetch_subscribers import process_subscribers_data
from scripts.db.fetch_queries import fetch_all_data
from scripts.utils.logger_config import get_logger
from scripts.utils.send_email import send_html_email 
from scripts.utils.db_connection import get_db_connection, close_connection
import pandas as pd
import re
import html
from datetime import datetime
import pytz

# Initialize logger
logger = get_logger('main')

# HELPER FUNCTIONS

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

# Function to extract hour and minutes from a datetime string
def format_time(time_str, timezone_str):
    if time_str != "N/A" and timezone_str:
        try:
            # Parse the UTC time
            utc_time = datetime.fromisoformat(time_str.rstrip('Z')).replace(tzinfo=pytz.UTC)
            # Convert to subscriber's local time
            local_tz = pytz.timezone(timezone_str)
            local_time = utc_time.astimezone(local_tz)
            return local_time.strftime('%I:%M %p') 
        except (ValueError, pytz.exceptions.UnknownTimeZoneError):
            return "N/A"
    return "N/A"

# Convert pandas Timestamp to ISO format string
def convert_timestamps(data):
    if isinstance(data, dict):
        return {key: value.isoformat() if isinstance(value, pd.Timestamp) else value for key, value in data.items()}
    elif isinstance(data, pd.DataFrame):
        return data.applymap(lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else x)
    else:
        return data

# Remove slashes from quotes
def clean_escape_sequences(text):
    return text.replace("\\", "")  # Removes escape slashes

# Convert numeric values to int and handle N/A values
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return value  # Return the original value if it can't be converted to int


def get_weather_code_description(code):
    weather_code = {
      "0": "Unknown",
      "1000": "Clear, Sunny",
      "1100": "Mostly Clear",
      "1101": "Partly Cloudy",
      "1102": "Mostly Cloudy",
      "1001": "Cloudy",
      "2000": "Fog",
      "2100": "Light Fog",
      "4000": "Drizzle",
      "4001": "Rain",
      "4200": "Light Rain",
      "4201": "Heavy Rain",
      "5000": "Snow",
      "5001": "Flurries",
      "5100": "Light Snow",
      "5101": "Heavy Snow",
      "6000": "Freezing Drizzle",
      "6001": "Freezing Rain",
      "6200": "Light Freezing Rain",
      "6201": "Heavy Freezing Rain",
      "7000": "Ice Pellets",
      "7101": "Heavy Ice Pellets",
      "7102": "Light Ice Pellets",
      "8000": "Thunderstorm"
    }
    return weather_code.get(str(code), "Unknown")

def map_to_weather_code_day(weather_codes_data, description):
    # Ensure weather_codes_data is a dictionary
    if isinstance(weather_codes_data, pd.DataFrame):
        weather_code_day = weather_codes_data.set_index('weather_code')['description'].to_dict()
    elif isinstance(weather_codes_data, pd.Series):
        weather_code_day = weather_codes_data.to_dict()
    else:
        weather_code_day = weather_codes_data
    
    # Create a reverse mapping
    reverse_mapping = {v: k for k, v in weather_code_day.items()}
    
    # Try to find an exact match
    if description in reverse_mapping:
        return weather_code_day[reverse_mapping[description]]
    
    # If no exact match, try to find a partial match
    for key, value in reverse_mapping.items():
        if description in key:
            return weather_code_day[value]
    
    return "Unknown"

def prepare_subscriber_content(subscriber, long_date, formatted_date, weather_data, weather_codes_data, exchange_rate_data, quotes_data, fun_facts_data, word_of_the_day_data, english_tips_data, historical_events_data, daily_challenges_data):
    
    subscriber_content = {}
    used_ids = {
        'quotes': [],
        'fun_facts': [],
        'word_of_the_day': [],
        'english_tips': [],
        'historical_events': [],
        'daily_challenges': []
    }
    
    # Helper function to safely get first item from DataFrame or dict
    def get_first_item(data):
        if isinstance(data, pd.DataFrame) and not data.empty:
            return data.iloc[0].to_dict()
        elif isinstance(data, dict):
            return data
        else:
            return {}
    

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
    subscriber_timezone = subscriber['timezone']
    city_weather = weather_data[weather_data['location.name'].str.contains(subscriber_city, case=False, na=False)]

    if not city_weather.empty:
        city_weather_dict = city_weather.iloc[0].to_dict()
        
        # Extract the daily weather data for today (first item in the timelines list)
        today_weather = city_weather_dict['timelines.daily'][0]['values']

        weather_data_nested = {
            "uvIndex": to_int(today_weather.get("uvIndexMax", "N/A")),
            "dewPoint": to_int(today_weather.get("dewPointAvg", "N/A")),
            "humidity": to_int(today_weather.get("humidityAvg", "N/A")),
            "windGust": to_int(today_weather.get("windGustAvg", "N/A")),
            "cloudBase": to_int(today_weather.get("cloudBaseAvg", "N/A")),
            "windSpeed": to_int(today_weather.get("windSpeedAvg", "N/A")),
            "cloudCover": to_int(today_weather.get("cloudCoverAvg", "N/A")),
            "visibility": to_int(today_weather.get("visibilityAvg", "N/A")),
            "temperature": to_int(today_weather.get("temperatureAvg", "N/A")),
            "weatherCode": to_int(today_weather.get("weatherCodeMax", "N/A")),
            "cloudCeiling": to_int(today_weather.get("cloudCeilingAvg", "N/A")),
            "rainIntensity": to_int(today_weather.get("rainIntensityAvg", "N/A")),
            "snowIntensity": to_int(today_weather.get("snowIntensityAvg", "N/A")),
            "windDirection": to_int(today_weather.get("windDirectionAvg", "N/A")),
            "sleetIntensity": to_int(today_weather.get("sleetIntensityAvg", "N/A")),
            "uvHealthConcern": to_int(today_weather.get("uvHealthConcernMax", "N/A")),
            "temperatureApparent": to_int(today_weather.get("temperatureApparentAvg", "N/A")),
            "pressureSurfaceLevel": to_int(today_weather.get("pressureSurfaceLevelAvg", "N/A")),
            "freezingRainIntensity": to_int(today_weather.get("freezingRainIntensityAvg", "N/A")),
            "precipitationProbability": to_int(today_weather.get("precipitationProbabilityAvg", "N/A"))
        }

        # Get weather description
        weather_code_max = today_weather.get("weatherCodeMax", "N/A")
        weather_code_description = get_weather_code_description(weather_code_max)

        # Map to weather_code_day
        weather_code_day_description = map_to_weather_code_day(weather_codes_data, weather_code_description)

        # If no match found by description, find the closest weather_code
        if weather_code_day_description == "Unknown":
            if isinstance(weather_codes_data, pd.DataFrame):
                closest_code = weather_codes_data['weather_code'].astype(int).sub(int(weather_code_max)).abs().idxmin()
                weather_code_day_description = weather_codes_data.loc[closest_code, 'description']
            else:
                closest_code = min(weather_codes_data.keys(), key=lambda x: abs(int(x) - int(weather_code_max)))
                weather_code_day_description = weather_codes_data[closest_code]['description']

        # Find the matching weather code data
        if isinstance(weather_codes_data, pd.DataFrame):
            weather_code_data = weather_codes_data[weather_codes_data['description'] == weather_code_day_description].iloc[0].to_dict()
        else:
            weather_code_data = next((data for data in weather_codes_data.values() if data['description'] == weather_code_day_description), None)

        # Add the nested weather data along with additional fields
        weather_data_nested.update({
            "feels_like_name": "Feels like",
            "description": weather_code_day_description,
            "icon_file_name": weather_code_data['icon_file_name'] if weather_code_data else None,
            "icon_file_url": weather_code_data['icon_file_url'] if weather_code_data else None,
            "sunrise_name": "Sunrise",
            "sunrise": format_time(today_weather.get('sunriseTime', "N/A"), subscriber_timezone),
            "sunset_name": "Sunset",
            "sunset": format_time(today_weather.get('sunsetTime', "N/A"), subscriber_timezone),
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
    
    # Quotes
    quote_data = get_first_item(quotes_data)
    if quote_data:
        quote_of_the_day = quotes_data.iloc[0].to_dict()

        # Clean up the quote field
        if 'quote' in quote_of_the_day:
            quote_of_the_day['quote'] = clean_escape_sequences(quote_of_the_day['quote'])

        quote_of_the_day['author_pic'] = "https://planetsignshop.com/cdn/shop/products/COMING-SOON-10IN-ROUND-RIDER-RED.gif?v=1656448869"

        # Store in subscriber_content
        subscriber_content['quote_of_the_day'] = convert_timestamps(quote_of_the_day)
        used_ids['quotes'].append(quote_of_the_day.get('id'))
    else:
        subscriber_content['quote_of_the_day'] = {}
    
    # Fun Facts
    fun_fact_data = get_first_item(fun_facts_data)
    if fun_fact_data:
        fun_fact = fun_facts_data.iloc[0].to_dict()
        subscriber_content['fun_fact'] = convert_timestamps(fun_fact)
        used_ids['fun_facts'].append(fun_fact.get('id'))
    
    # Word of the Day
    word_data = get_first_item(word_of_the_day_data)
    if word_data:
        word_of_the_day = word_of_the_day_data.iloc[0].to_dict()
        if 'examples' in word_of_the_day:
            # Split the examples into separate examples
            examples = word_of_the_day['examples'].split(';')
            # Clean each example
            cleaned_examples = [clean_and_format_text(example) for example in examples]
            # Join the cleaned examples back together
            word_of_the_day['examples'] = '; '.join(cleaned_examples)
        subscriber_content['word_of_the_day'] = convert_timestamps(word_data)
        used_ids['word_of_the_day'].append(word_data.get('id'))
    else:
        subscriber_content['word_of_the_day'] = {}
    
    # English Tips
    english_tip_data = get_first_item(english_tips_data)
    if english_tip_data:
        english_tip = english_tips_data.iloc[0].to_dict()
        subscriber_content['english_tip'] = convert_timestamps(english_tip)
        used_ids['english_tips'].append(english_tip.get('id'))
    
    
    subscriber_content['news'] = {"message": "News not implemented yet"}


    # Historical Events
    historical_event_data = get_first_item(historical_events_data)
    if historical_event_data:
        historical_event = historical_events_data.iloc[0].to_dict()
        subscriber_content['historical_event'] = convert_timestamps(historical_event)
        used_ids['historical_events'].append(historical_event.get('id'))

    # Daily Challenges
    challenge_data = get_first_item(daily_challenges_data)
    if challenge_data:
        daily_challenge = daily_challenges_data.iloc[0].to_dict()
        challenge_data_nested = convert_timestamps(daily_challenge)
        challenge_data_nested.update({"header": "Today's Challenge"})
        subscriber_content['challenge'] = challenge_data_nested
        used_ids['daily_challenges'].append(daily_challenge.get('id'))
    
    subscriber_content['breathing_technique'] = {"motivation": "Just Breathe!"}
    
    subscriber_content['footer'] = {
        "goodbye": "See you tomorrow. Have a great day!",
        "reply": "Reply ",
        "unsubscribe": " to unsubscribe, report an error, or request a feature"
    }
    
    return subscriber_content, used_ids

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
        # If subscriber's language preference isn't in the content, you might want to add it here
        if 'languages' not in content:
            content['languages'] = [subscriber.get('language', 'en')]
            
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
        # Convert the date string to a datetime object
        date_obj = datetime.strptime(long_date, "%B %d, %Y")
        
        # Get days receiving newsletter and increment by 1
        days_receiving_newsletter = subscriber['days_receiving_newsletter'] + 1
        
        # Format the date with the day of the week
        formatted_date = date_obj.strftime("%A - %B %d, %Y")
        
        with open(file_path, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()
        
        subject = f"{formatted_date} - Daily Digest #{days_receiving_newsletter}"
        to_address = subscriber['email']
        send_html_email(to_address, subject, html_content)
        logger.info(f"Sent newsletter email to {subscriber['nickname']} at {to_address}")
    except Exception as e:
        logger.error(f"Error sending email to {subscriber['nickname']}: {e}")
        raise

def update_used_in_newsletter(used_ids, subscriber_ids):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update used_in_newsletter for content tables
        for table, ids in used_ids.items():
            if ids:
                query = f"UPDATE {table} SET used_in_newsletter = 1 WHERE id IN ({','.join(map(str, ids))})"
                cursor.execute(query)
                logger.info(f"Updated {cursor.rowcount} rows in {table}")

        # Update days_receiving_newsletter for subscribers
        if subscriber_ids:
            query = "UPDATE subscribers SET days_receiving_newsletter = days_receiving_newsletter + 1 WHERE id IN ({})".format(','.join(map(str, subscriber_ids)))
            cursor.execute(query)
            logger.info(f"Updated {cursor.rowcount} subscribers")

        conn.commit()
        logger.info("All updates completed successfully")

    except Exception as e:
        logger.error(f"Error updating used_in_newsletter: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            close_connection(conn)

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
        weather_codes = queries_data['weather_codes']

        # Initialize Jinja2 environment
        env = Environment(loader=FileSystemLoader(os.path.join('templates')))
        template = env.get_template('template.html')

        all_used_ids = {
            'quotes': [],
            'fun_facts': [],
            'word_of_the_day': [],
            'english_tips': [],
            'historical_events': [],
            'daily_challenges': []
        }
        
        updated_subscriber_ids = []
        
         # Prepare content for each subscriber
        for _, subscriber in subscribers_df.iterrows():
            try:
                subscriber_content, used_ids = prepare_subscriber_content(subscriber, long_date, formatted_date, weather_data, weather_codes, exchange_rate_data, quotes_data, fun_fact_data, word_of_the_day_data, english_tips_data, historical_events_data, daily_challenges_data)
                
                # Accumulate used IDs
                for key in all_used_ids:
                    all_used_ids[key].extend(used_ids[key])

                # Save subscriber content as JSON
                save_subscriber_content(subscriber, subscriber_content, formatted_date, content_feeder_path)

                # Render and save newsletter HTML
                newsletter_file_path = render_and_save_newsletter(subscriber, subscriber_content, formatted_date, template, newsletter_ready_path)

                # Send email
                send_newsletter_email(subscriber, long_date, newsletter_file_path)

                # Add subscriber ID to the list of updated subscribers
                updated_subscriber_ids.append(subscriber['id'])

            except Exception as e:
                logger.error(f"Error processing newsletter for subscriber {subscriber['nickname']}: {e}")
                # Continue with the next subscriber if there's an error with the current one
                continue

        # Update used_in_newsletter status and subscriber counts
        update_used_in_newsletter(all_used_ids, updated_subscriber_ids)

    except Exception as e:
        logger.error(f"An unexpected error occurred in main: {e}")

if __name__ == "__main__":
    main()