# ⚡ Vercel Deployment Guide

This guide details how to deploy the Next.js administration panel and monitoring dashboard (located in the `/website` directory) to **Vercel**.

---

## 🏗️ Pre-deployment Steps

Before deploying, ensure you have the following services configured:

### 1. Database Setup (Neon PostgreSQL)
1. Go to [Neon.tech](https://neon.tech/) and create a free PostgreSQL database.
2. Under the Connection Details, copy your connection string (database URL).
3. Ensure the schema tables are generated (this happens automatically when the Python backend runs for the first time with `USE_DATABASE=TRUE`).

### 2. Google Cloud Service Account JSON
For Vercel, instead of uploading a `gcp_secrets.json` file, we use a single environment variable:
1. Open your GCP service account JSON key file (`gcp_secrets.json`).
2. Copy the entire raw JSON text.
3. You will configure this as the `GCP_CREDENTIALS_JSON` environment variable in Vercel.

---

## 🚀 Deploying to Vercel

### Step 1: Push Your Code to GitHub
Ensure your repository is pushed to a private or public GitHub repository.

### Step 2: Import Project in Vercel
1. Go to the [Vercel Dashboard](https://vercel.com/) and click **Add New** -> **Project**.
2. Select your repository.
3. Under **Root Directory**, click edit and select the `/website` folder.
4. Keep the Framework Preset as **Next.js**.

### Step 3: Configure Environment Variables
Expand the **Environment Variables** section and add the following:

| Key | Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://user:pass@host/dbname?sslmode=require` | Your Neon DB connection string. |
| `GCP_BUCKET_NAME` | `your_gcs_bucket_name` | Name of your GCS bucket. |
| `GCP_CREDENTIALS_JSON` | `{"type": "service_account", ...}` | The raw JSON string of your Google Cloud credentials. |
| `WEBSITE_ADMIN_PASSWORD` | `your_secure_password` | The password required to log in to the admin panel dashboard. |
| `JWT_SECRET` | `your_jwt_secret_signing_key` | A secure random string used to sign admin session tokens. |

### Step 4: Click Deploy!
Vercel will compile the Next.js pages and deploy them. Once done, you will receive a production deployment URL (e.g. `https://your-project.vercel.app`).

---

## 🔄 How the Dashboard Works

- **Visual Dashboard**: Displays recent posts and videos, along with their publishing status across Instagram, YouTube, and Facebook.
- **On-Demand Prompts**: Allows you to queue new prompts via the admin interface. These prompts are stored in `images_on_demand` and `videos_on_demand` tables.
- **Run Orchestrator**: The local Python backend running on your scheduler or cron pulls from this database queue, generates the assets, uploads them to GCS, posts them to platforms, and updates the status to "posted" which reflects instantly on your Vercel site.
