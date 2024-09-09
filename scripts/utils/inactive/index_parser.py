import logging
from bs4 import BeautifulSoup
import premailer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(filename="email_sending.log", 
                    level=logging.DEBUG, 
                    format="%(asctime)s %(levelname)s %(message)s")

# Function to read the HTML and inline its existing CSS
def load_html_and_inline_css(html_file_path):
    try:
        # Load HTML content
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Since CSS is now inline, no need to load external CSS files
        # Transform using Premailer to ensure compatibility with email clients
        inlined_html = premailer.transform(str(soup))
        logging.info("HTML has been processed and CSS inlined successfully.")
        return inlined_html

    except Exception as e:
        logging.error(f"Error processing HTML: {e}")
        raise
