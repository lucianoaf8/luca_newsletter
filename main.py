import os
import sys
from datetime import date
from scripts.db.fetch_subscribers import process_subscribers_data
from scripts.db.fetch_queries import fetch_all_data

# Select today's date
today = date.today()
print("Today's date is:", today.strftime("%Y-%m-%d"))

# Call the function to fetch and process subscribers
subscribers_df = process_subscribers_data()

# Print subscribers' data if available
if subscribers_df is not None and not subscribers_df.empty:
    print("Subscribers Data:")
    print(subscribers_df.head())
else:
    print("No subscribers data available.")

# Call the function to fetch all the necessary queries data
queries_data = fetch_all_data()

# Print the fetched queries data
for name, df in queries_data.items():
    if not df.empty:
        print(f"\n{name.capitalize().replace('_', ' ')} Data:")
        print(df.head())
    else:
        print(f"No data fetched for {name.replace('_', ' ').capitalize()}.")

# You can add further processing of the data here if needed

# For each subscriber, do:
    # Get weather data for their city and format as 


# Prepare exchange rates


# Prepare quote of the day


# Prepare fun fact


# Prepare historical event


# Prepare english with luca
# Word of the day

# Tip of the day


# Prepare Challenge

# Prepare News