import requests
import os   
from dotenv import load_dotenv
load_dotenv()

APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")
SHORT_LIVED_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
GRAPH_API_VERSION = "v23.0"  # Use the latest supported version

url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/oauth/access_token"

params = {
    "grant_type": "fb_exchange_token",
    "client_id": APP_ID,
    "client_secret": APP_SECRET,
    "fb_exchange_token": SHORT_LIVED_TOKEN
}

response = requests.get(url, params=params)

print("Status Code:", response.status_code)
print("Response:", response.json())