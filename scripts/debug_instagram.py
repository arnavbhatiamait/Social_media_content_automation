"""
scripts/debug_instagram.py
---------------------------
Diagnoses exactly why Instagram publishing is failing by running
the same debug calls described in the troubleshooting notes.

Run:
    python scripts/debug_instagram.py
"""

import os
import sys
import requests

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

TOKEN   = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
ACCT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
BASE    = "https://graph.facebook.com/v23.0"

SEP = "=" * 60

print(f"\n{SEP}")
print("Instagram Debug Tool")
print(SEP)
print(f"  Token (first 30 chars) : {TOKEN[:30]}...")
print(f"  INSTAGRAM_ACCOUNT_ID   : {ACCT_ID}")

# ------------------------------------------------------------------ #
# 1. Who does this token belong to?
# ------------------------------------------------------------------ #
print(f"\n{SEP}")
print("1) /me  — token identity check")
print(SEP)
me = requests.get(f"{BASE}/me", params={"access_token": TOKEN}).json()
print(f"  Response: {me}")
me_id = me.get("id", "UNKNOWN")
print(f"  -> Resolved user/page ID: {me_id}")

# ------------------------------------------------------------------ #
# 2. Can we fetch the account ID that's in .env?
# ------------------------------------------------------------------ #
print(f"\n{SEP}")
print(f"2) /{ACCT_ID}  — is this ID accessible?")
print(SEP)
acct = requests.get(
    f"{BASE}/{ACCT_ID}",
    params={"fields": "id,name,username,account_type", "access_token": TOKEN}
).json()
print(f"  Response: {acct}")

# ------------------------------------------------------------------ #
# 3. List all Pages + linked Instagram Business Accounts
# ------------------------------------------------------------------ #
print(f"\n{SEP}")
print("3) /me/accounts  — Facebook Pages + Instagram Business Accounts")
print(SEP)
pages_resp = requests.get(
    f"{BASE}/me/accounts",
    params={"fields": "id,name,instagram_business_account", "access_token": TOKEN}
).json()

pages = pages_resp.get("data", [])
if "error" in pages_resp:
    print(f"  ERROR: {pages_resp['error']}")
elif not pages:
    print("  No pages found. Token may be missing 'pages_show_list' permission.")
else:
    for page in pages:
        print(f"\n  Page: {page.get('name')}  (ID: {page.get('id')})")
        ig = page.get("instagram_business_account")
        if ig:
            ig_id = ig["id"]
            # Fetch username
            ig_detail = requests.get(
                f"{BASE}/{ig_id}",
                params={"fields": "id,username,name,followers_count", "access_token": TOKEN}
            ).json()
            print(f"    Instagram Business ID : {ig_id}  <-- USE THIS")
            print(f"    Username              : @{ig_detail.get('username', 'N/A')}")
            print(f"    Followers             : {ig_detail.get('followers_count', 'N/A')}")
            print(f"\n    --> Set in .env:  INSTAGRAM_ACCOUNT_ID={ig_id}")
        else:
            print("    No Instagram Business Account linked.")

# ------------------------------------------------------------------ #
# 4. Token debug — what scopes are actually granted?
# ------------------------------------------------------------------ #
print(f"\n{SEP}")
print("4) Token introspection — granted scopes")
print(SEP)
debug = requests.get(
    f"{BASE}/debug_token",
    params={"input_token": TOKEN, "access_token": TOKEN}
).json()
data = debug.get("data", {})
print(f"  App ID  : {data.get('app_id')}")
print(f"  Type    : {data.get('type')}")
print(f"  Valid   : {data.get('is_valid')}")
print(f"  Expires : {data.get('expires_at', 'never (long-lived)')}")
print(f"  Scopes  : {data.get('scopes', [])}")

print(f"\n{SEP}")
print("Diagnosis Summary")
print(SEP)
if not me.get("id"):
    print("  PROBLEM: Token is invalid or expired. Regenerate in Graph Explorer.")
elif not pages:
    print("  PROBLEM: No Facebook Pages accessible. Re-generate token with:")
    print("    pages_show_list, pages_read_engagement, instagram_basic,")
    print("    instagram_content_publish, business_management")
else:
    has_ig = any(p.get("instagram_business_account") for p in pages)
    if not has_ig:
        print("  PROBLEM: No Instagram Business/Creator account linked to any Page.")
        print("    Go to Facebook Page Settings -> Instagram -> Connect Account")
    else:
        print("  Token and account look good!")
        print("  Make sure INSTAGRAM_ACCOUNT_ID in .env matches the ID printed above.")
print()
