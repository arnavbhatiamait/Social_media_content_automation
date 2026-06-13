# 📺 YouTube Data API Setup Guide

This guide details how to configure the YouTube Data API v3 to automate video uploads, schedule posts, customize thumbnails, and post community updates.

---

## 🛠️ Step 1: Create a Google Cloud Project & Enable YouTube API

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Click the project dropdown in the top navigation bar and select **New Project**.
3.  Give your project a name (e.g., `Social Media Automation`) and click **Create**.
4.  Ensure your new project is selected in the dropdown.
5.  Search for **YouTube Data API v3** in the top search bar, click on it, and click **Enable**.

---

## 📝 Step 2: Configure OAuth Consent Screen

Because the app operates on behalf of your channel via user authorization, you must configure the OAuth Consent Screen.

1.  In the left sidebar, navigate to **APIs & Services** > **OAuth Consent Screen**.
2.  Select **External** user type and click **Create**.
3.  Fill in the required App Information:
    *   **App Name**: e.g., `YouTube Automator`
    *   **User Support Email**: Select your email address.
    *   **Developer Contact Information**: Enter your email address.
    *   Click **Save and Continue**.
4.  **Scopes**:
    *   Click **Add or Remove Scopes**.
    *   Add the scope: `https://www.googleapis.com/auth/youtube` (Allows managing YouTube videos, accounts, and uploads).
    *   Click **Update** and then **Save and Continue**.
5.  **Test Users (CRITICAL STEP)**:
    *   Since your app is in "Testing" status, Google restricts authorization access.
    *   Click **Add Users**.
    *   Enter the **exact Gmail address** of the YouTube Channel you intend to upload videos to.
    *   Click **Add** and then **Save and Continue**.

> [!WARNING]
> If you do not add the channel's Gmail address to the "Test Users" list, you will encounter a `Google block / App not verified` error or security block when attempting to authorize.

---

## 🔑 Step 3: Create OAuth Client Credentials

1.  In the left sidebar, navigate to **APIs & Services** > **Credentials**.
2.  Click **Create Credentials** > **OAuth Client ID**.
3.  Set the Application Type to **Desktop App**.
4.  Name the client (e.g., `Desktop Uploader Client`).
5.  Click **Create**.
6.  Click **Download JSON** in the credentials list.
7.  Rename the downloaded file to **`client_secret.json`** and place it in the **root directory** of this project.

---

## 🔑 Step 4: Run Authorization Locally

To generate the active API authorization token (`token.json`), you must run the OAuth flow once in a local browser environment.

1.  Open your terminal in the project root folder.
2.  Verify `client_secret.json` is located in the root.
3.  Run the authentication script:
    ```bash
    python scripts/yt_auth.py
    ```
4.  A browser window will open automatically.
    *   Select the Google Account corresponding to your target YouTube Channel.
    *   If you see a screen saying *"Google hasn't verified this app"*, click **Advanced** > **Go to YouTube Automator (unsafe)**.
    *   Grant the requested YouTube permissions.
5.  Once authorization is complete, the browser will display a success message, and a **`token.json`** file will be generated in your project root.

```
token.json generated
```

> [!TIP]
> The pipeline uses `YoutubeUploader` inside `yt_uploader/Youtube.py`. It reads `token.json` to perform uploads. If the token expires, the client uses the embedded OAuth client parameters to refresh it automatically using Google auth transports, meaning you only need to run this local server setup **once**!

---

## 🎥 Video Formats & Upload Logic

The uploader script supports two methods:

### 1. YouTube Shorts (`upload_short`)
*   Automatically appends `#Shorts` to the video description if not present.
*   Videos should be vertical ($9:16$ ratio, e.g., $1080 \times 1920$).
*   Duration must be $\le 60$ seconds.

### 2. Full-Length Videos (`upload_video`)
*   Allows scheduling posts in advance using UTC timestamp parameters (`publish_at`).
*   Configurable categories (defaults to `"22"` / People & Blogs).
*   Configurable visibility (`public` | `private` | `unlisted`).

### 3. Thumbnails & Community Posts
*   `upload_thumbnail(video_id, image_path)` updates the uploaded video's cover image.
*   `create_community_post(text, video_id=...)` writes updates to your channel's Community Tab (requires $500+$ channel subscribers).
