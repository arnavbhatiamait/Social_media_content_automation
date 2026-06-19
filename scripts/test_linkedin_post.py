import requests
import os
from dotenv import load_dotenv
load_dotenv()

ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
ORG_ID = os.getenv("LINKEDIN_ORGANIZATIONAL_ID")
MEMBER_ID = "5TFQUpowm0"  # from userinfo sub

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

# 1. Try to post as Person
payload_person = {
    "author": f"urn:li:person:{MEMBER_ID}",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Test post as person"
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

print("--- Testing Post as Person ---")
r = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=payload_person)
print("Status:", r.status_code)
print("Response:", r.text)

# 2. Try to post as Organization
payload_org = {
    "author": f"urn:li:organization:{ORG_ID}",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Test post as organization"
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

print("\n--- Testing Post as Organization ---")
r2 = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=payload_org)
print("Status:", r2.status_code)
print("Response:", r2.text)
