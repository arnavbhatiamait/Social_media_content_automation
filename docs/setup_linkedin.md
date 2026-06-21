# 🔗 LinkedIn Setup Guide

This guide details how to set up the LinkedIn API to authorize and publish single and multi-image posts automatically using this pipeline.

---

## 🛠️ Step-by-Step LinkedIn API Configuration

### Step 1: Create a LinkedIn Developer Application
1. Go to the [LinkedIn Developer Portal](https://developer.linkedin.com/).
2. Log in with your LinkedIn account and click **Create app**.
3. Name your app, associate it with a **LinkedIn Page** (you must be an administrator of this page to link it), and upload an app logo.
4. Click **Create app**.

### Step 2: Configure App Products & Permissions
Under the **Products** tab of your app, request access to:
- **Share on LinkedIn** (for personal profile posts)
- **Community Management API** (for posting on LinkedIn Company Pages)

Once approved, your app will have access to the necessary scopes such as `w_member_social` and `w_organization_social`.

---

## 🔑 Generate LinkedIn Access Tokens

LinkedIn uses OAuth 2.0. Follow these steps to generate a long-lived access token:

### Step 1: Get Authorization URL
Create an authorization URL using your **Client ID** and **Client Secret** (found under the **Auth** tab of your App):

```text
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8000/callback&state=foobar&scope=w_member_social,w_organization_social,r_liteprofile
```

Paste this URL into your browser, click **Allow**, and you will be redirected to:
`http://localhost:8000/callback?code=YOUR_AUTHORIZATION_CODE&state=foobar`

Copy the `YOUR_AUTHORIZATION_CODE` parameter.

### Step 2: Exchange Code for Access Token
1. Add your credentials to `.env`:
   ```env
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   LINKEDIN_AUTH_TOKEN=YOUR_AUTHORIZATION_CODE
   ```
2. Run the token retrieval script to generate `LINKEDIN_ACCESS_TOKEN`:
   ```bash
   python scripts/get_linkedin_token.py
   ```
3. Copy the `access_token` from the JSON response and add it to your `.env`.

---

## 🔍 Get User / Organization IDs

To post, you need to identify the author URN (either `urn:li:person:ID` or `urn:li:organization:ID`):

### Get Person ID (MEMBER_ID)
Run the lookup script to retrieve your profile information:
```bash
python scripts/Linkedin_org_id.py
```
This queries the `/me` endpoint and prints your member ID (e.g., `5TFQUpowm0`).

### Get Organization ID (Company Page ID)
If posting to a company page:
1. Go to your LinkedIn Page as an administrator.
2. The URL will look like `https://www.linkedin.com/company/132523913/admin/dashboard/`.
3. The number (`132523913`) is your **Organization ID**.

---

## ⚙️ Environment Variables

Add the following variables to your root `.env` file:

```env
# LinkedIn API Credentials
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ORGANIZATIONAL_ID=your_linkedin_company_page_id
LINKEDIN_ACCESS_TOKEN=your_oauth_access_token
LINKEDIN_POSTING_TYPE=personal # Or organization
```

---

## 📋 Verifying Setup

Run the verification test script to publish a test message:

```bash
python scripts/test_linkedin_post.py
```
This script will attempt to publish a test post as a person or as an organization depending on your configured IDs and scopes.
