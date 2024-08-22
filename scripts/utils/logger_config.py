import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def get_logger(script_name, log_level=logging.DEBUG, max_bytes=10485760, backup_count=5):
    try:
        # Create 'logs' directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        # Define log file name based on the script name and current date
        log_file_name = f"{script_name}_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_file_path = os.path.join(logs_dir, log_file_name)

        # Configure the logger
        logger = logging.getLogger(script_name)
        logger.setLevel(log_level)

        # Create a rotating file handler
        file_handler = RotatingFileHandler(log_file_path, maxBytes=max_bytes, backupCount=backup_count)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        # Add handlers if they don't exist
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger

    except Exception as e:
        print(f"Error setting up logger: {e}")
        return logging.getLogger(script_name)