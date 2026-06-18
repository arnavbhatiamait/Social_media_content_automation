# 📘 Facebook Setup Guide

This guide details how to set up the Meta/Facebook Graph API to authorize and publish posts, Reels, and Carousels automatically using this pipeline.

---

## 🛠️ Step-by-Step Meta API Configuration

### Step 1: Create a Meta Developer Account & App
1. Go to the [Meta Developers Portal](https://developers.facebook.com/).
2. Log in with your Facebook account and click **My Apps** -> **Create App**.
3. Choose **Other** as the use case, click **Next**, and select **Business** or **Consumer** type.
4. Name your App (e.g., `SocialMediaAutomation`) and click **Create App**.

### Step 2: Set Up a Facebook Page & Business Account
1. Create or log in to a **Facebook Page** that you wish to publish content to.
2. Ensure your Meta Developer App is associated with the Facebook Page.

### Step 3: Configure Meta App Permissions
Under **App settings** or **API Tools**, make sure your App has the following permissions enabled:
- `pages_manage_posts` (to upload single image feeds and carousels)
- `pages_read_engagement` (to read analytics and comments)
- `pages_show_list` (to view associated pages)
- `publish_video` (to upload video Reels and long videos)

---

## 🔑 Generate Facebook Tokens

To upload automatically, you need a long-lived Page Access Token:

1. Go to the [Meta Graph API Explorer](https://developers.facebook.com/tools/explorer/).
2. Select your App in the top right.
3. Select **Get User Access Token** from the dropdown. Check the boxes for:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`
   - `publish_video`
4. Click **Generate Access Token**.
5. Copy the generated User Access Token.
6. Open a terminal and run the long-term secret script to convert this into a **Long-Lived Page Access Token** (expires in 60 days):
   ```bash
   python scripts/long_term_secret.py
   ```
   *Note: Ensure you configure your App ID and App Secret in `.env` before running.*

---

## ⚙️ Environment Variables

Add the following variables to your root `.env` file:

```env
# Facebook Page ID
FB_PAGE_ID=your_facebook_page_id

# Long-Lived Page Access Token
FB_ACCESS_TOKEN=your_long_lived_page_access_token
```

---

## 📋 Verifying Setup

You can run a dry-run post to verify that the credentials and permissions are correctly configured:

### 1. Test Text Feed Post
Run:
```bash
python scripts/test_fb.py
```
This sends a test post `"Hello from Python 🚀"` directly to your page feed.

### 2. Test Image Post
Run:
```bash
python scripts/fb_post.py
```
This uploads `person Output.jpg` directly to your page photos.

### 3. Test Video Reel Upload
Run:
```bash
python scripts/fb_upload_video.py
```
This uploads a test video as a Reel on your Facebook Page.
