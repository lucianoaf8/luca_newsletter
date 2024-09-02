import requests
import json
import datetime

# Replace with your Merriam-Webster API key
API_KEY = "your_api_key_here"
URL = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/word_of_the_day?key={API_KEY}"

def fetch_word_of_the_day():
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        word_data = response.json()
        if word_data:
            # Assuming the first item in the response is the word of the day
            word_info = word_data[0]
            word = word_info['meta']['id']
            definition = word_info['shortdef'][0]
            etymology = word_info.get('et', 'No etymology available')
            pronunciation = word_info['hwi']['hw']
            audio_url = f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{word_info['hwi']['prs'][0]['sound']['audio'][0]}.mp3"

            word_details = {
                "word": word,
                "pronunciation": pronunciation,
                "definition": definition,
                "etymology": etymology,
                "audio_pronunciation": audio_url,
                "timestamp": datetime.datetime.now().isoformat()
            }

            with open(f"{word}_word_of_the_day.json", "w") as json_file:
                json.dump(word_details, json_file, indent=4)
                
            print(f"Word of the Day: {word}")
            print(f"Pronunciation: {pronunciation}")
            print(f"Definition: {definition}")
            print(f"Etymology: {etymology}")
            print(f"Audio Pronunciation: {audio_url}")
            print(f"Saved word details to {word}_word_of_the_day.json")
        else:
            print("No word of the day found.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    fetch_word_of_the_day()
