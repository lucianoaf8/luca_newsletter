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

# Fetch available news sources for the country
def fetch_sources(country):
    newsapi = initialize_newsapi()

    try:
        # Fetch sources for the specified country
        sources = newsapi.get_sources(country=country)

        if sources.get('status') != 'ok':
            print(f"Failed to fetch sources: {sources.get('message')}")
            return []

        # Return the sources list
        return sources.get('sources', [])
    except Exception as e:
        print(f"An error occurred while fetching sources: {e}")
        return []

# Fetch top headlines based on the country (without language filter)
def fetch_news(country, category=None, query=None):
    newsapi = initialize_newsapi()

    try:
        # Log the parameters being used for the request
        print(f"Fetching top headlines for country: {country}, category: {category or 'none'}, query: {query or 'none'}")

        # Fetch articles with the maximum pageSize (100) and optional category or query
        news = newsapi.get_top_headlines(
            country=country, 
            page_size=100, 
            category=category, 
            q=query
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
def save_news_to_json(data, country):
    # Create the directory if it doesn't exist
    folder_path = r"C:\Projects\luca_newsletter_official\data\fetched_results\top_news"
    os.makedirs(folder_path, exist_ok=True)

    # Get the current timestamp for the filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create a filename with country and timestamp
    file_name = f"news_{country}_{timestamp}.json"
    file_path = os.path.join(folder_path, file_name)

    # Save the data as a JSON file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"News data saved to {file_path}")

# Main function
def main(country, category=None, query=None):
    # Fetch sources for the country
    sources = fetch_sources(country)
    if not sources:
        print(f"No sources available for country: {country}")
        return
    
    # List available sources
    print(f"Available sources for {country}: {[source['name'] for source in sources]}")

    # Fetch top headlines without language filter
    news_data = fetch_news(country, category=category, query=query)

    if not news_data or 'articles' not in news_data or len(news_data['articles']) == 0:
        print("No news articles found.")
        return

    # Save the fetched news data to a JSON file
    save_news_to_json(news_data, country)

if __name__ == "__main__":
    # Fetch top headlines from Canada and Brazil with category and query examples
    main(country="ca", category="general")  # General news from Canada
    main(country="br", category="entertainment")  # General news from Brazil
    main(country="ca", query="politics")    # Specific query for politics in Canada
    main(country="br", query="economia")     # Specific query for economy in Brazil
