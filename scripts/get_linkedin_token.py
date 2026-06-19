import requests
import os 
from dotenv import load_dotenv
load_dotenv()
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"

AUTH_CODE = os.getenv("LINKEDIN_AUTH_TOKEN")

url = "https://www.linkedin.com/oauth/v2/accessToken"

payload = {
    "grant_type": "authorization_code",
    "code": AUTH_CODE,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
}

response = requests.post(url, data=payload)

print(response.status_code)
print(response.text)