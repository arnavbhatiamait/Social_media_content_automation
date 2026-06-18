import requests

import os 
from dotenv import load_dotenv
load_dotenv()

PAGE_ID = os.getenv("FB_PAGE_ID")
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

image_path = "person Output.jpg"

url = f"https://graph.facebook.com/v23.0/{PAGE_ID}/photos"

with open(image_path, "rb") as img:

    response = requests.post(
        url,
        files={
            "source": img
        },
        data={
            "caption": "Image uploaded via Python",
            "access_token": ACCESS_TOKEN
        }
    )

print(response.status_code)
print(response.json())