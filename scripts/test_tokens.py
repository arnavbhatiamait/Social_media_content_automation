import requests
import os
from dotenv import load_dotenv

# Ensure project root is in path to load correct .env
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

GRAPH_API_VERSION = "v25.0"
APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET")
SHORT_LIVED_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

print("--- Token Introspection ---")
debug_url = "https://graph.facebook.com/debug_token"
debug_params = {
    "input_token": SHORT_LIVED_TOKEN,
    "access_token": SHORT_LIVED_TOKEN
}
try:
    debug_response = requests.get(debug_url, params=debug_params)
    debug_data = debug_response.json()
    if "data" in debug_data:
        token_app_id = debug_data["data"].get("app_id")
        print(f"Token was generated for App ID: {token_app_id}")
        print(f"Current META_APP_ID in .env    : {APP_ID}")
        if token_app_id != APP_ID:
            print("⚠️ WARNING: Mismatch detected! The token belongs to a different App ID than the one in your .env file.")
        print(f"Is Token Valid?                : {debug_data['data'].get('is_valid')}")
        print(f"Token Scopes                   : {debug_data['data'].get('scopes')}")
    else:
        print(f"Could not introspect token: {debug_data}")
except Exception as e:
    print(f"Failed to query token introspection: {e}")
print("---------------------------\n")

print("--- Exchanging Token ---")
url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/oauth/access_token"
params = {
    "grant_type": "fb_exchange_token",
    "client_id": APP_ID,
    "client_secret": APP_SECRET,
    "fb_exchange_token": SHORT_LIVED_TOKEN
}

print(f"Using META_APP_ID      : {APP_ID}")
print(f"Using APP_SECRET (mask): {APP_SECRET[:4]}... (length: {len(APP_SECRET) if APP_SECRET else 0})")

try:
    response = requests.get(url, params=params)
    data = response.json()
    if response.status_code == 200:
        long_lived_token = data.get("access_token")
        print(f"Success! Business Long-Lived Token: {long_lived_token}")
    else:
        print(f"Error status code: {response.status_code}")
        print(f"Error message    : {data.get('error', {}).get('message')}")
        print(f"Full Error details: {data}")
except Exception as e:
    print(f"Failed to perform exchange request: {e}")