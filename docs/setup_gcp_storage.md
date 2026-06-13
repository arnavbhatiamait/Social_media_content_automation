# ☁️ GCP Storage & Text-to-Speech Setup Guide

This guide walks you through setting up Google Cloud Storage (GCS) and Google Cloud Text-to-Speech (TTS) to manage media hosting and generate audio narrations.

---

## 🛠️ Step 1: Enable Cloud APIs

1.  Open the [Google Cloud Console](https://console.cloud.google.com/).
2.  Ensure your automation project is selected in the top navigation bar.
3.  Navigate to the **API Library** (search for API Library in the top bar).
4.  Search for and **Enable** the following APIs:
    *   **Google Cloud Storage API** (Hosts and shares video/image files).
    *   **Cloud Text-to-Speech API** (Generates voiceovers for videos).
    *   **Vertex AI API** (Optional: Used for the Imagen image generator fallback).

---

## 👥 Step 2: Create a Service Account & Grant IAM Roles

To allow your scripts to authenticate securely without user login screens, you must create a Service Account.

1.  In the left sidebar, navigate to **IAM & Admin** > **Service Accounts**.
2.  Click **Create Service Account** at the top.
3.  Set the service account name (e.g., `content-automation-sa`) and click **Create and Continue**.
4.  **Grant access roles (CRITICAL STEP)**:
    *   Add Role: **Storage Object Admin** (Allows uploading and downloading files in GCS).
    *   Add Role: **Service Account Token Creator** (Allows the SDK to self-sign URLs locally).
    *   Add Role: **Vertex AI User** (Optional: Allows using Imagen fallback).
5.  Click **Continue** and then **Done**.

> [!IMPORTANT]
> The **Service Account Token Creator** role is required. Without it, the client-side code will fail to generate signed URLs, which are essential for Instagram Reels publishing.

---

## 🔑 Step 3: Create and Download the JSON Private Key

1.  In the Service Accounts list, click on the email address of the service account you just created.
2.  Navigate to the **Keys** tab at the top.
3.  Click **Add Key** > **Create New Key**.
4.  Select **JSON** as the key format and click **Create**.
5.  Save the downloaded JSON file to your local computer.
6.  Rename this file to **`gcp_secrets.json`** and place it in the **root directory** of this project.

---

## 🪣 Step 4: Create a Google Cloud Storage Bucket

Instagram requires a public URL to download your video files during posting. The pipeline uploads files to GCS and generates secure, short-lived signed URLs.

1.  In the left navigation bar, search for and select **Buckets** (under Storage).
2.  Click **Create**.
3.  Name your bucket (e.g., `databucket_reels_photos` - must be globally unique).
4.  Choose your location type (e.g., **Region** > `us-central1` or your nearest region).
5.  Select **Standard** storage class.
6.  Under *Control access to objects*, keep **Enforce public access prevention on this bucket** checked (signed URLs bypass this securely).
7.  Click **Create**.
8.  Configure your `.env` file with your bucket details:
    ```env
    GCP_BUCKET_NAME=databucket_reels_photos
    GCP_CREDENTIALS_PATH=gcp_secrets.json
    PROJECT_ID=your_gcp_project_id
    GCP_LOCATION=us-central1
    ```

---

## 🗣️ Step 5: Configure Text-to-Speech (TTS)

The pipeline uses `GoogleTTS` in `tts/gtts.py` to synthesize the video script narration into high-quality WAV audio clips.

### Customizing Voices and Languages
You can customize the TTS configuration by setting environment variables in your `.env` file:

```env
# Configures the narrator voice (default is Hindi)
GOOGLE_TTS_LANGUAGE_CODE=hi-IN
GOOGLE_TTS_VOICE_NAME=hi-IN-Standard-A
GOOGLE_TTS_SAMPLE_RATE=24000
```

*   **`GOOGLE_TTS_LANGUAGE_CODE`**: The language locale (e.g., `en-US` for English, `hi-IN` for Hindi, `es-ES` for Spanish).
*   **`GOOGLE_TTS_VOICE_NAME`**: The specific voice model (e.g., `hi-IN-Standard-A`, `en-US-Journey-F`, `en-IN-Wavenet-B`). You can query the available voices using Google's API documentation or the `list_voices()` function in the class.
*   **`GOOGLE_TTS_SAMPLE_RATE`**: The audio quality frequency (defaults to `24000` Hz).
