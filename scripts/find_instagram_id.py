"""
scripts/find_instagram_id.py
-----------------------------
Finds the correct Instagram Business Account ID linked to your Facebook Page.

Run:
    python scripts/find_instagram_id.py
"""

import os
import sys
import requests

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
BASE_URL = "https://graph.facebook.com/v23.0"

if not ACCESS_TOKEN:
    print("ERROR: INSTAGRAM_ACCESS_TOKEN not set in .env")
    sys.exit(1)

print(f"\nUsing token: {ACCESS_TOKEN[:20]}...\n")

# Step 1: Get all Facebook Pages you manage
print("=" * 60)
print("Step 1 — Fetching your Facebook Pages...")
print("=" * 60)

pages_resp = requests.get(
    f"{BASE_URL}/me/accounts",
    params={"access_token": ACCESS_TOKEN}
).json()

if "error" in pages_resp:
    print(f"ERROR: {pages_resp['error']['message']}")
    sys.exit(1)

pages = pages_resp.get("data", [])
if not pages:
    print("No Facebook Pages found. Make sure your token has 'pages_read_engagement' permission.")
    sys.exit(1)

for page in pages:
    print(f"\n  Page Name : {page.get('name')}")
    print(f"  Page ID   : {page.get('id')}")
    page_token = page.get("access_token")

    # Step 2: Get the Instagram Business Account linked to this page
    ig_resp = requests.get(
        f"{BASE_URL}/{page['id']}",
        params={
            "fields": "instagram_business_account",
            "access_token": page_token or ACCESS_TOKEN
        }
    ).json()

    ig_account = ig_resp.get("instagram_business_account")
    if ig_account:
        ig_id = ig_account["id"]
        print(f"  Instagram Business Account ID: {ig_id}  <-- USE THIS")

        # Step 3: Fetch username to confirm
        ig_detail = requests.get(
            f"{BASE_URL}/{ig_id}",
            params={
                "fields": "username,name,followers_count",
                "access_token": page_token or ACCESS_TOKEN
            }
        ).json()
        print(f"  Instagram Username : @{ig_detail.get('username', 'N/A')}")
        print(f"  Followers          : {ig_detail.get('followers_count', 'N/A')}")
        print(f"\n  --> Add to .env:  INSTAGRAM_ACCOUNT_ID={ig_id}")
    else:
        print("  No Instagram Business Account linked to this page.")
        print("  --> Connect your Instagram account in Facebook Page Settings > Instagram")

print("\n" + "=" * 60)
