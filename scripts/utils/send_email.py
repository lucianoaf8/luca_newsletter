import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(filename="email_sending.log", 
                    level=logging.DEBUG, 
                    format="%(asctime)s %(levelname)s %(message)s")

# Function to load SMTP settings from environment variables
def load_smtp_settings():
    try:
        server = os.getenv("SMTP_SERVER")  # Same server for SMTP
        port = int(os.getenv("SMTP_PORT"))  # SMTP port 465 for SSL/TLS
        email = os.getenv("SMTP_EMAIL")
        password = os.getenv("SMTP_PASSWORD")

        if not all([server, port, email, password]):
            raise ValueError("Incomplete SMTP settings.")
        
        return server, port, email, password
    except Exception as e:
        logging.error(f"Error loading SMTP settings: {e}")
        raise

# Function to send the email with HTML content using SMTP
def send_html_email(to_address, subject, html_content):
    try:
        # Load SMTP settings
        server, port, email, password = load_smtp_settings()
        
        # Setup the MIME
        message = MIMEMultipart("alternative")
        message['From'] = email
        message['To'] = to_address
        message['Subject'] = subject

        # Attach the HTML content
        message.attach(MIMEText(html_content, 'html'))
        
        logging.info(f"Starting to send an email to {to_address} via {server}")
        
        # Create an SMTP session with SSL
        with smtplib.SMTP_SSL(server, port) as smtp_session:
            smtp_session.login(email, password)
            logging.info("Authenticated successfully")
            
            # Send the email
            smtp_session.sendmail(email, to_address, message.as_string())
            logging.info(f"HTML email sent successfully to {to_address}")

    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        raise
