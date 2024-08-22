import requests

api_key = 'YOUR_API_KEY'
url = 'https://api.api-ninjas.com/v1/facts?limit=1'  # Limit to one fun fact
headers = {'X-Api-Key': api_key}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    fact = response.json()[0]['fact']
    print(f"Fun Fact: {fact}")
else:
    print(f"Error: {response.status_code}")
