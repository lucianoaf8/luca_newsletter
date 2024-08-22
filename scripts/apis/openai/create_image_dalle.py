import os
import openai
from dotenv import load_dotenv
from datetime import datetime
import requests
from utils import get_logger  # Assuming the logger_config.py is in your utils folder

# Setup logger
logger = get_logger('create_image_dalle')

# Load the API key from the .env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI with your API key
openai.api_key = api_key

def generate_image(prompt, folder_path="generated_images"):
    try:
        logger.info("Starting image generation process.")
        
        # API call to create the image with DALL·E
        response = openai.Image.create(
            prompt=prompt,
            n=1,  # Only supports generating one image at a time
            size="1024x1024",  # Standard size
            model="dall-e-3"  # Specify DALL·E 3
        )
        
        image_url = response['data'][0]['url']
        logger.info("Image generation successful.")

        # Download and save the image
        save_image_from_url(image_url, folder_path)

        return image_url
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return f"Error: {e}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Error: {e}"

def save_image_from_url(image_url, folder_path):
    """Downloads the image from the URL and saves it locally."""
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        response = requests.get(image_url)
        if response.status_code == 200:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(folder_path, f"dalle_image_{timestamp}.png")
            
            with open(image_path, 'wb') as img_file:
                img_file.write(response.content)
            
            logger.info(f"Image saved successfully at {image_path}.")
        else:
            logger.error(f"Failed to download the image. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error while saving the image: {e}")

# Example usage
if __name__ == "__main__":
    prompt = "A futuristic city with neon lights, inspired by Tron Legacy."
    image_url = generate_image(prompt)
    print("Image generated and saved. URL:", image_url)
