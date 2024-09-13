import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from scripts.utils.send_email import send_html_email
from scripts.utils.logger_config import get_logger
from scripts.utils.logger_config import get_logger

# Initialize logger
logger = get_logger('test_email_sender')

# Load environment variables
load_dotenv()

def send_test_newsletter():
    try:
        # File path
        file_path = r"C:\Projects\luca_newsletter_official\data\newsletter_ready\_debug.html"
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return

        # Read HTML content
        with open(file_path, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()

        # Prepare email details
        long_date = datetime.now().strftime("%B %d, %Y")
        formatted_date = datetime.now().strftime("%A - %B %d, %Y")
        subject = f"{formatted_date} - Your Luca Newsletter Test"

        # List of test email addresses
        test_emails = ["lucianoaf8@gmail.com", "davidknennedy95@hotmail.com"]

        # Send emails
        for email in test_emails:
            try:
                send_html_email(email, subject, html_content)
                logger.info(f"Test newsletter sent successfully to {email}")
            except Exception as e:
                logger.error(f"Failed to send test newsletter to {email}: {e}")

    except Exception as e:
        logger.error(f"An error occurred while sending test newsletters: {e}")

if __name__ == "__main__":
    send_test_newsletter()