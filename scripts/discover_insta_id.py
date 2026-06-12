import os
import sys
import requests
from dotenv import load_dotenv

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Load .env
env_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(env_path)

access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

if not access_token:
    print("Error: INSTAGRAM_ACCESS_TOKEN is not set in .env")
    sys.exit(1)

print("Querying Meta Graph API for your Facebook Pages...")
accounts_url = f"https://graph.facebook.com/v25.0/me/accounts"
params = {
    "access_token": access_token
}

try:
    response = requests.get(accounts_url, params=params)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print(f"Failed to query /me/accounts: {e}")
    sys.exit(1)

pages = data.get("data", [])
if not pages:
    print("No Facebook Pages found linked to this access token. Make sure the token has 'pages_show_list' and 'instagram_basic' permissions.")
    sys.exit(1)

print(f"Found {len(pages)} Facebook Page(s). Searching for linked Instagram Business Accounts...")
instagram_account_id = None

for page in pages:
    page_id = page.get("id")
    page_name = page.get("name")
    print(f"Checking Page: {page_name} (ID: {page_id})...")
    
    # Query linked Instagram accounts
    page_detail_url = f"https://graph.facebook.com/v25.0/{page_id}"
    page_params = {
        "fields": "instagram_business_account,name",
        "access_token": access_token
    }
    
    try:
        page_resp = requests.get(page_detail_url, params=page_params)
        page_resp.raise_for_status()
        page_data = page_resp.json()
        
        insta_biz = page_data.get("instagram_business_account")
        if insta_biz:
            instagram_account_id = insta_biz.get("id")
            print(f"  -> SUCCESS! Found linked Instagram Business Account ID: {instagram_account_id}")
            break
        else:
            print("  -> No linked Instagram Business Account found for this Page.")
    except Exception as e:
        print(f"  -> Error querying details for Page {page_name}: {e}")

if not instagram_account_id:
    print("\nCould not find any linked Instagram Business Accounts. Please verify:")
    print("1. Your Instagram Account is converted to a Professional/Business/Creator account.")
    print("2. Your Instagram Professional Account is linked to a Facebook Page.")
    print("3. Your Access Token was created with the linked Facebook Page and Instagram permissions selected.")
    sys.exit(1)

# Read current .env
with open(env_path, "r", encoding="utf-8") as f:
    env_content = f.read()

# Update INSTAGRAM_ACCOUNT_ID
lines = env_content.splitlines()
updated = False
new_lines = []

for line in lines:
    if line.startswith("INSTAGRAM_ACCOUNT_ID="):
        new_lines.append(f"INSTAGRAM_ACCOUNT_ID={instagram_account_id}")
        updated = True
    else:
        new_lines.append(line)

if not updated:
    new_lines.append(f"INSTAGRAM_ACCOUNT_ID={instagram_account_id}")

with open(env_path, "w", encoding="utf-8") as f:
    f.write("\n".join(new_lines) + "\n")

print(f"\nSuccessfully updated .env file! Set INSTAGRAM_ACCOUNT_ID to: {instagram_account_id}")
