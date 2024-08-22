import mysql.connector
from mysql.connector import Error
import json
from scripts.utils.logger_config import get_logger
import os

# Initialize logger for this script
logger = get_logger(os.path.basename(__file__))

# Database connection function
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name
        )
        logger.info("Connection to MySQL DB successful")
    except Error as e:
        logger.error(f"Error occurred while connecting to the database: {e}")
    return connection

# Query execution function (SELECT)
def execute_read_query(connection, query):
    cursor = connection.cursor(dictionary=True)
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        logger.info(f"Query executed successfully: {query}")
    except Exception as e:
        logger.error(f"Error executing query: {e}")
    finally:
        cursor.close()
    return result

# Data insertion function
def execute_insert_query(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        connection.commit()
        logger.info(f"Insert query executed successfully: {query} with data: {data}")
    except Exception as e:
        connection.rollback()  # Rollback in case of error
        logger.error(f"Error inserting data: {e}")
    finally:
        cursor.close()

# Load JSON data function
def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            logger.info(f"Loaded JSON data from {file_path} successfully")
            return data
    except FileNotFoundError as fnf_error:
        logger.error(f"JSON file not found: {fnf_error}")
    except json.JSONDecodeError as json_error:
        logger.error(f"Error decoding JSON: {json_error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    return None

# Example usage
if __name__ == "__main__":
    try:
        # Create DB connection
        connection = create_connection("localhost", "root", "password", "your_database")
        if connection is None:
            logger.error("Failed to establish database connection")
            raise Exception("Database connection not established")

        # Execute a SELECT query
        query = "SELECT * FROM your_table"
        data = execute_read_query(connection, query)
        logger.info(f"Data retrieved: {data}")

        # Insert data into the database
        insert_query = "INSERT INTO your_table (column1, column2) VALUES (%s, %s)"
        values = ("value1", "value2")
        execute_insert_query(connection, insert_query, values)

        # Load JSON data and insert it into the database
        json_data = load_json("data.json")
        if json_data:
            for item in json_data:
                execute_insert_query(connection, insert_query, (item['column1'], item['column2']))

    except Exception as e:
        logger.error(f"An error occurred in the main script: {e}")
    finally:
        if connection:
            connection.close()
            logger.info("Database connection closed")
