import requests
import json
import os

# Wordnik API settings
API_KEY = 'mgi41xb0dd1z5ubsnpe34hki2t0hqybtk4fszkc7qb9o2t221'  # Replace with your actual Wordnik API key
BASE_URL = 'https://api.wordnik.com/v4/words.json/randomWords'

# Set the parameters for the request
params = {
    'hasDictionaryDef': 'true',
    'includePartOfSpeech': 'noun',
    'minCorpusCount': '10000',
    'maxCorpusCount': '-1',
    'minDictionaryCount': '1',
    'maxDictionaryCount': '-1',
    'minLength': '5',
    'maxLength': '-1',
    'limit': 1,  # Fetch only one word
    'api_key': API_KEY
}

# Fetch the random noun word
response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    words_data = response.json()
    
    # Create the directory if it doesn't exist
    save_path = r'C:\Projects\luca_newsletter_official\data\fetched_results\word_of_the_day\word_of_the_day'
    os.makedirs(save_path, exist_ok=True)

    # Save the result as a JSON file
    with open(os.path.join(save_path, 'word_of_the_day.json'), 'w') as f:
        json.dump(words_data, f, indent=4)
    
    print(f"Word of the day saved successfully: {words_data[0]['word']}")
else:
    print(f"Failed to fetch word. Status code: {response.status_code}, Message: {response.text}")
