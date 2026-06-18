import requests
import os
from dotenv import load_dotenv
load_dotenv()

page_id = os.getenv("FB_PAGE_ID")
token = os.getenv("FB_ACCESS_TOKEN")

url = f"https://graph.facebook.com/v23.0/{page_id}/feed"

payload = {
    "message": "Hello from Python 🚀",
    "access_token": token
}

response = requests.post(url, data=payload)

print(response.json())