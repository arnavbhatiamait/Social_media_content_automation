import requests

# import os 
# from dotenv import load_dotenv 
# load_dotenv()
# r = requests.get(
#     "https://graph.facebook.com/v25.0/me/permissions",
#     params={"access_token": os.getenv("INSTAGRAM_ACCESS_TOKEN") }
# )

# print(r.json())


import requests
import os
from dotenv import load_dotenv
load_dotenv()
# 1. Define your parameters
import requests

# Parameters for Business/Creator accounts
GRAPH_API_VERSION = "v25.0"  # Use the latest version
APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET")
SHORT_LIVED_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/oauth/access_token"
params = {
    "grant_type": "fb_exchange_token",
    "client_id": APP_ID,
    "client_secret": APP_SECRET,
    "fb_exchange_token": SHORT_LIVED_TOKEN
}

response = requests.get(url, params=params)
data = response.json()

if response.status_code == 200:
    long_lived_token = data.get("access_token")
    print(f"Success! Business Long-Lived Token: {long_lived_token}")
else:
    print(f"Error: {data.get('error', {}).get('message')}")