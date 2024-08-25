from newspaper import Article

# Function to scrape article and handle errors
def scrape_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return {
            'title': article.title,
            'text': article.text[:500],  # Extract the first 500 characters of the article
            'authors': article.authors,
            'publish_date': article.publish_date,
            'top_image': article.top_image
        }
    except Exception as e:
        print(f"Error scraping article from {url}: {e}")
        return None

# Example URLs from different sources (replace with actual URLs from NewsAPI)
urls = [
    "https://www.cbsnews.com/news/atm-cash-withdrawal-fee-survey/",  # CBC News
    "https://www.terra.com.br/esportes/jogos-olimpicos/selecao-feminina-de-volei-despacha-japao-e-se-garante-nas-quartas-dos-jogos-de-paris,7ae822c788abb4ec3272a8c190c5f45bcq7eu8wp.html" # Terra
]

# Loop through the URLs and test if Newspaper3k can scrape them
for url in urls:
    article_data = scrape_article(url)
    if article_data:
        print(f"Successfully scraped article from {url}:")
        print(f"Title: {article_data['title']}")
        print(f"First 500 characters: {article_data['text']}")
    else:
        print(f"Failed to scrape article from {url}")
