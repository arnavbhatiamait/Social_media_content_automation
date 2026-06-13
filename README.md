<p align="center">
  <img src="docs/assets/project_banner.png" alt="Social Media Content Automation Banner" width="100%">
</p>

# 🎬 Social Media Content Automation

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/github%20actions-enabled-brightgreen.svg" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/Google%20Cloud-Storage%20%26%20TTS-orange.svg" alt="GCP Services">
  <img src="https://img.shields.io/badge/Meta%20API-Instagram-purple.svg" alt="Meta API">
</p>

An end-to-end, production-ready AI pipeline that orchestrates LLMs, Image Generators, Text-to-Speech (TTS), and video processors to generate, catalog, and publish viral-ready content to **Instagram** and **YouTube** fully automatically.

---

## 🌟 Features

*   **🤖 Multi-Model Generation**:
    *   **LLM Orchestrator**: Uses Gemini (`gemini-2.5-flash`) via LangChain to generate structured documentary scripts (narration + detailed image prompts).
    *   **Image Generation**: Uses Hugging Face **FLUX.1-schnell** as primary, falling back to **Stable Diffusion XL (SDXL)**, and finally Google Cloud **Vertex AI Imagen** if needed.
    *   **Text-to-Speech (TTS)**: Powered by Google Cloud Text-to-Speech for high-quality audio segments (supporting custom language codes, voices, and speed configurations).
*   **🎥 Automated Video Assembly**:
    *   Slices and animates images (using zoom/pan motion effects).
    *   Generates and burns synchronized subtitles (SRT) into the video using FFmpeg.
    *   Integrates background audio mixing, custom intro title overlays (first 3 seconds), and auto-generates thumbnails.
*   **☁️ Cloud Integration**:
    *   Optionally uploads generated media assets to **Google Cloud Storage (GCS)**.
    *   Auto-generates secure signed URLs required for remote media publishing.
*   **🚀 Automated Posting**:
    *   **Instagram Graph API**: Automatically publishes Images, Reels, Stories, or Carousels.
    *   **YouTube Data API v3**: Automatically uploads YouTube Shorts, custom thumbnails, and schedules full-length videos.
*   **🗄️ Database Tracking**:
    *   Tracks queue execution and media metrics using a PostgreSQL Database (e.g., Neon DB) with SQLAlchemy.
*   **⏰ GitHub Actions Cron**:
    *   Configurable workflows to run pipelines twice a day automatically on a schedule.

---

## 📐 System Architecture & Flow

```mermaid
graph TD
    A[Start Pipeline / Cron] --> B{Choose Type}
    B -- Video Pipeline --> C[Query Gemini for Script & Prompts]
    C --> D[Generate Assets in Parallel]
    D --> E[Image Generation: HF Flux / SDXL / Vertex Imagen]
    D --> F[Audio Generation: Google Cloud TTS]
    E --> G[FFmpeg Video Assembly]
    F --> G
    G --> H[Render Subtitles SRT & Burn]
    H --> I[Add Background Music & Intro Titles]
    I --> J[Save local final_video.mp4]
    
    B -- Image Pipeline --> K[Image Gen: HF Flux / SDXL / Vertex Imagen]
    K --> L[Save local final_image.png]
    
    J & L --> M{Cloud Storage?}
    M -- Yes --> N[Upload to Google Cloud Storage]
    N --> O[Generate GCS Signed URL]
    
    J & L --> P{Publish Platforms}
    O -- Signed URL --> Q[Instagram API: Reels / Posts]
    J -- Local File --> R[YouTube API: Shorts / Videos]
    
    Q & R --> S[Update Database Logs]
    S --> T[End Pipeline]
```

---

## 🖼️ Sample Generated Outputs

### 📸 Image Generation (Flux.1-schnell)
Below is an example of a high-resolution mythological scene generated automatically by the pipeline:

<p align="center">
  <img src="docs/assets/sample_output_shiva.png" alt="Sample Shiva Output" width="60%" style="border-radius: 8px; border: 1px solid #444;">
</p>

### 🎥 Video Generation (YouTube Shorts)
Watch a sample documentary video generated fully automatically (narration, images, background music, subtitles, and intro titles) and published to YouTube Shorts:

<p align="center">
  <a href="https://youtube.com/shorts/vMVLHVE9kus?si=c0W0izpZrPPC4WKy" target="_blank">
    <img src="https://img.youtube.com/vi/vMVLHVE9kus/hqdefault.jpg" alt="Watch the Sample Video on YouTube Shorts" width="300" style="border-radius: 8px; border: 1px solid #444;">
  </a>
  <br>
  <a href="https://youtube.com/shorts/vMVLHVE9kus?si=c0W0izpZrPPC4WKy">▶️ Watch on YouTube Shorts</a>
</p>

---

## 📂 Repository Structure

```directory
├── main.py                     # Entrypoint CLI to run pipelines
├── requirements.txt            # Dependency configuration
├── video_prompts.txt           # File-based prompt/deity queue
├── Piepline/
│   ├── imagePipeline.py        # Image generation, upload & Instagram post pipeline
│   └── VideoPipeline.py        # Full video generation & multi-platform publishing pipeline
├── ImageGeneration/
│   ├── flux.py                 # Hugging Face Flux generation (Schnell/SDXL)
│   └── iamagegen.py            # Vertex AI Imagen image generator fallback
├── tts/
│   └── gtts.py                 # Google Cloud Text-To-Speech implementation
├── video_assembler/
│   ├── video_pipeline.py       # Handles FFmpeg composition, music mixing, and titles
│   ├── scene_creator.py        # Zoompan image animation and audio joining
│   ├── audio_utils.py          # Duration fetching and audio mixing
│   └── subtitle_generator.py   # Dynamic SRT creation and subtitle burning
├── yt_uploader/
│   └── Youtube.py              # YouTube Data API client (Shorts, videos, thumbnails)
├── insta_configuration/
│   └── insta_setup.py          # Meta Graph API client (Reels, images, stories)
├── schemas_n_db/
│   ├── database.py             # Database query helper operations
│   └── schema.py               # SQLAlchemy declarative schemas for Postgres logs
├── prompts/
│   ├── prompts_posts/          # System prompts for single-image posts
│   └── prompts_video/          # System prompts for 5-scene documentary scripts
├── scripts/
│   ├── discover_insta_id.py    # Auto-discovers Instagram Business account ID
│   ├── debug_instagram.py      # Meta API token debug and scope validator
│   └── yt_auth.py              # Local OAuth helper to generate youtube token.json
└── docs/                       # Detailed platform & API setup guides
```

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have the following installed on your machine:
*   Python 3.10 or higher
*   **FFmpeg** (must be available in your system `PATH`)

### 2. Clone & Install
```bash
git clone https://github.com/arnavbhatiamait/Social_media_content_automation.git
cd Social_media_content_automation
pip install -r requirements.txt
```

### 3. Setup Configuration
Create a `.env` file in the root directory. Copy and fill in the following values (see detailed docs below for acquiring keys):

```env
# Database Logs (PostgreSQL / Neon)
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
USE_DATABASE=TRUE

# Google Cloud Storage & Credentials
USE_CLOUD_SAVE=True
GCP_CREDENTIALS_PATH=gcp_secrets.json
GCP_BUCKET_NAME=your_gcs_bucket_name
PROJECT_ID=your_gcp_project_id
GCP_LOCATION=us-central1

# Hugging Face (Flux & SDXL Generation)
HF_TOKEN=your_hugging_face_user_access_token

# Google / Gemini AI
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_API_KEY=your_gemini_api_key

# Instagram API Config
META_APP_ID=your_meta_app_id
INSTAGRAM_APP_SECRET=your_instagram_app_secret
INSTAGRAM_ACCESS_TOKEN=your_long_lived_user_access_token
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id

# Subtitle generation flag for video pipeline (TRUE/FALSE)
ADD_SUBTITLES=FALSE

# Defaults: 100.0s for Vertex AI Imagen, 5.0s for Hugging Face
IMAGE_GEN_SLEEP=100.0
```

### 4. Running the Pipeline

You can run the orchestrator manually using the CLI:

```bash
# Run both image and video pipelines for a specific deity name (e.g. Lord Shiva)
python main.py --type both --prompt "Lord Shiva"

# Run only the image generation and posting pipeline
python main.py --type image --prompt "Lord Krishna" --caption "A beautiful day with Lord Krishna!"

# Run only the video creation and publishing pipeline (pulls from video_prompts.txt queue)
python main.py --type video

# Run with custom generators and options
python main.py --type image --prompt "Lord Ganesha" --generator imagen --no-storage --no-db
```

---

## 🛠️ Setup Guides

To configure all external services, credentials, and cron jobs, follow the step-by-step guides inside the `docs/` directory:

1.  🔑 **[Hugging Face Access Token Setup](docs/setup_huggingface.md)**: Required to query the primary Flux and SDXL image generators.
2.  ☁️ **[Google Cloud Platform & Storage Setup](docs/setup_gcp_storage.md)**: Setup IAM roles, Text-to-Speech API, GCS buckets, and download `gcp_secrets.json`.
3.  📸 **[Instagram API Setup](docs/setup_instagram.md)**: Configure Meta Developers App, link accounts, acquire long-lived tokens, and auto-discover IDs.
4.  📺 **[YouTube Data API Setup](docs/setup_youtube.md)**: Setup OAuth Consent, client secrets, and authorize locally to obtain `token.json`.
5.  ⚙️ **[GitHub Actions & Secrets Setup](docs/setup_github_actions.md)**: Set up cron scheduling and securely pass JSON keys/secrets inside workflows.
6.  ✍️ **[Customizing Prompts & Queue](docs/customizing_prompts.md)**: Learn how the prompt queues are processed and how to add custom deities/visual parameters.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
