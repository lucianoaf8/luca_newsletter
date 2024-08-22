import logging
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'path_to_your_credentials.json'  # Your credentials file

def get_service():
    """Sets up the Google Sheets API service."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        logger.info("Successfully authenticated and created Sheets API service.")
        return service
    except FileNotFoundError as fnf_error:
        logger.error(f"Service account file not found: {fnf_error}")
        sys.exit(1)
    except Exception as error:
        logger.error(f"An unexpected error occurred while setting up the service: {error}")
        sys.exit(1)

def load_data(service, spreadsheet_id, range_name):
    """Loads data from the Google Sheet."""
    try:
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        if not values:
            logger.warning("No data found in the spreadsheet.")
        else:
            logger.info(f"Loaded data from {range_name} in spreadsheet {spreadsheet_id}.")
        return values
    except HttpError as http_error:
        logger.error(f"HTTP error occurred: {http_error}")
    except Exception as error:
        logger.error(f"An unexpected error occurred while loading data: {error}")

def save_data(service, spreadsheet_id, range_name, new_values):
    """Saves data to the Google Sheet."""
    try:
        body = {'values': new_values}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        logger.info(f"Data successfully saved to {range_name} in spreadsheet {spreadsheet_id}.")
    except HttpError as http_error:
        logger.error(f"HTTP error occurred while saving data: {http_error}")
    except Exception as error:
        logger.error(f"An unexpected error occurred while saving data: {error}")

def main():
    """Main function to load and save data."""
    try:
        service = get_service()
        SPREADSHEET_ID = 'your_spreadsheet_id'
        RANGE_NAME = 'Sheet1!A1:C10'
        
        # Load existing data
        data = load_data(service, SPREADSHEET_ID, RANGE_NAME)
        if data:
            logger.info("Existing data:")
            for row in data:
                logger.info(row)
        
        # Define new data to be saved
        new_values = [
            ['Name', 'Age', 'Occupation'],
            ['Alice', '24', 'Engineer'],
            ['Bob', '30', 'Designer']
        ]
        
        # Save new data
        save_data(service, SPREADSHEET_ID, RANGE_NAME, new_values)
    except Exception as error:
        logger.error(f"An error occurred in the main function: {error}")

if __name__ == '__main__':
    main()
