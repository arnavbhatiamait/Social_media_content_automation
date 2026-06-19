import requests
import os 
from dotenv import load_dotenv
load_dotenv()
ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

# headers = {
#     "Authorization": f"Bearer {ACCESS_TOKEN}",
#     "X-Restli-Protocol-Version": "2.0.0"
# }

# response = requests.get(
#     "https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee",
#     headers=headers
# )

# print(response.status_code)
# print(response.json())


# import requests

# headers = {
#     "Authorization": f"Bearer {ACCESS_TOKEN}"
# }

# r = requests.get(
#     "https://api.linkedin.com/v2/userinfo",
#     headers=headers
# )

# print(r.status_code)
# print(r.text)


import requests

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

r = requests.get(
    "https://api.linkedin.com/v2/me",
    headers=headers
)

print(r.status_code)
print(r.text)