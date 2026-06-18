import requests
import os
from dotenv import load_dotenv

load_dotenv()
PAGE_ID = os.getenv("FB_PAGE_ID")
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")


video_path = "Recording 2026-06-11 165341.mp4"

url = f"https://graph.facebook.com/v23.0/{PAGE_ID}/videos"

with open(video_path, "rb") as video_file:

    response = requests.post(
        url,
        files={
            "source": video_file
        },
        data={
            "title": "My Video",
            "description": "Uploaded via Python",
            "access_token": ACCESS_TOKEN
        }
    )

print(response.status_code)
print(response.json())