import requests
import os 
from dotenv import load_dotenv
load_dotenv()
ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN") 

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

r = requests.get(
    "https://api.linkedin.com/v2/userinfo",
    headers=headers
)

print(r.status_code)
print(r.text)