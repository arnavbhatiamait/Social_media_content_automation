# ⚙️ GitHub Actions & Secrets Setup Guide

This guide details how to configure GitHub Actions to run your automation pipelines twice a day using a schedule, and how to configure repository secrets securely.

---

## ⏰ Cron Schedule & Workflow Configuration

The workflow is configured in **`.github/workflows/cron_insta.yml`**. It triggers in two ways:
1.  **Manual Trigger (`workflow_dispatch`)**: Allows you to run the pipeline manually from the GitHub Actions dashboard.
2.  **Scheduled Cron (`schedule`)**: Runs automatically at specified times:
    *   `30 6 * * *` (06:30 AM UTC / **12:00 PM IST**)
    *   `30 12 * * *` (12:30 PM UTC / **06:00 PM IST**)

---

## 🗝️ Repository Secrets Configuration

To run the pipeline securely without committing raw credentials, API keys, or private files to public repositories, you must register them as **GitHub Repository Secrets**.

### Step 1: Open Secrets Settings
1.  Go to your repository on GitHub.
2.  Navigate to **Settings** > **Secrets and variables** > **Actions**.
3.  Click **New repository secret**.

### Step 2: Add all Required Secrets
Add the following key-value pairs (match the names exactly):

| Secret Name | Value Description |
| :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string (e.g. Neon DB URL). |
| `GCP_BUCKET_NAME` | The name of your GCS bucket. |
| `PROJECT_ID` | Your GCP Project ID. |
| `GCP_LOCATION` | Your GCS bucket region (e.g., `us-central1`). |
| `HF_TOKEN` | Hugging Face user access token (Read access). |
| `GOOGLE_API_KEY` | Your Gemini API Key. |
| `GEMINI_API_KEY` | Same as `GOOGLE_API_KEY`. |
| `META_APP_ID` | Your Meta Developer App ID. |
| `INSTAGRAM_APP_SECRET` | Your Meta Developer App Secret. |
| `INSTAGRAM_USER_ID` | Your Instagram User ID. |
| `INSTAGRAM_ACCOUNT_ID` | Your Instagram Business Account ID. |
| `INSTAGRAM_ACCESS_TOKEN` | Long-lived Instagram Access Token. |
| `GCP_SECRETS_JSON` | **Raw file contents** of your local `gcp_secrets.json` service account key file. |
| `YT_CLIENT_SECRET_JSON` | **Raw file contents** of your local `client_secret.json` client secret file. |
| `YT_TOKEN_JSON` | **Raw file contents** of your generated `token.json` OAuth token file. |

---

## 🏗️ How the Runner Handles Credentials

During runtime, the GitHub runner requires physical files on disk for Google OAuth client parameters, Google Cloud authentication, and local token refreshes.

The GitHub Actions workflow automates this in the **Write Secrets Files** step before running the pipeline:

```yaml
- name: Write Secrets Files
  run: |
    echo '${{ secrets.GCP_SECRETS_JSON }}' > gcp_secrets.json
    echo '${{ secrets.YT_TOKEN_JSON }}' > token.json
    echo '${{ secrets.YT_CLIENT_SECRET_JSON }}' > client_secret.json
```

These files are ignored by `.gitignore` and are destroyed as soon as the ephemeral GitHub Actions runner terminates, ensuring no sensitive data is leaked or stored persistently.

---

## 📁 Repository Permissions & Queue Synchronization

If you use the file-based prompt queue (`video_prompts.txt`), the GitHub runner must mark prompts as `# [PROCESSED]` on execution and push the updated queue back to your repository.

1.  The workflow specifies the permission:
    ```yaml
    permissions:
      contents: write
    ```
2.  Enable the Git commit section at the end of the `.yml` file by uncommenting the step:
    ```yaml
    - name: Commit and push changes to video_prompts.txt
      run: |
        git config --global user.name "github-actions[bot]"
        git config --global user.email "github-actions[bot]@users.noreply.github.com"
        git add video_prompts.txt
        git diff --quiet && git diff --staged --quiet || (git commit -m "chore: update video prompts queue [skip ci]" && git push)
    ```

This checks if the pipeline marked any items as processed, commits the changes back to your repository, and avoids triggering secondary workflow loops using the `[skip ci]` commit flag.
