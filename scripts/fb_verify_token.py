import requests
import os 
from dotenv import load_dotenv
load_dotenv()

PAGE_ID =os.getenv("FB_PAGE_ID")
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

response = requests.get(
    f"https://graph.facebook.com/v23.0/{PAGE_ID}",
    params={"access_token": ACCESS_TOKEN}
)

print(response.json())