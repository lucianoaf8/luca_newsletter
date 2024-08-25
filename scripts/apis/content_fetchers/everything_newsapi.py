# path: news_fetcher.py
import os
import json
from newsapi import NewsApiClient
from datetime import datetime
from dotenv import load_dotenv

# Load .env file containing the NEWSAPI_KEY
load_dotenv()

# Initialize the NewsAPI client
def initialize_newsapi():
    api_key = os.getenv('NEWSAPI_KEY')  # Ensure your API key is stored as an environment variable
    if not api_key:
        raise ValueError("API Key for NewsAPI not found.")
    return NewsApiClient(api_key=api_key)

# Fetch articles using the /everything endpoint
def fetch_news(query, from_date=None, to_date=None, language='en', sort_by='publishedAt'):
    newsapi = initialize_newsapi()

    try:
        # Log the parameters being used for the request
        print(f"Fetching articles with query: '{query}', language: {language}, from: {from_date}, to: {to_date}, sorted by: {sort_by}")

        # Fetch articles from the /everything endpoint
        news = newsapi.get_everything(
            q=query,
            from_param=from_date,
            to=to_date,
            language=language,
            sort_by=sort_by,
            page_size=100  # Maximum number of results per page
        )
        
        # Check and log the API response status
        if news.get('status') != 'ok':
            print(f"Failed to fetch news: {news.get('message')}")
            return None
        
        # Log total results and some metadata
        print(f"Total results: {news.get('totalResults')}")
        
        return news
    except Exception as e:
        print(f"An error occurred while fetching news: {e}")
        return None

# Save news data to a JSON file with timestamp
def save_news_to_json(data, query):
    # Create the directory if it doesn't exist
    folder_path = r"C:\Projects\luca_newsletter_official\data\fetched_results\everything_news"
    os.makedirs(folder_path, exist_ok=True)

    # Get the current timestamp for the filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create a filename with query and timestamp
    file_name = f"news_{query}_{timestamp}.json"
    file_path = os.path.join(folder_path, file_name)

    # Save the data as a JSON file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"News data saved to {file_path}")

# Main function
def main(query, from_date=None, to_date=None, language='en', sort_by='publishedAt'):
    # Fetch articles using the /everything endpoint
    news_data = fetch_news(query, from_date=from_date, to_date=to_date, language=language, sort_by=sort_by)

    if not news_data or 'articles' not in news_data or len(news_data['articles']) == 0:
        print("No news articles found.")
        return

    # Save the fetched news data to a JSON file
    save_news_to_json(news_data, query)

if __name__ == "__main__":
    # Search for "Olympics" in Canada in English
    main(query="Canadas Drag Race Canada vs The World", language="en", from_date="2024-08-01", to_date="2024-08-22")

    # Search for "Volleyball Buddy" in Brazil in Portuguese
    main(query="Voleibol", language="pt", from_date="2024-08-01", to_date="2024-08-22")
