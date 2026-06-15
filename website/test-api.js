const { Pool } = require('pg');
const { Storage } = require('@google-cloud/storage');
const path = require('path');
const fs = require('fs');

// Set env vars
process.env.DATABASE_URL = 'postgresql://neondb_owner:local_postgres_password_123@ep-shy-haze-atri6g51-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require';
process.env.GCP_CREDENTIALS_PATH = '../gcp_secrets.json';
process.env.GCP_BUCKET_NAME = 'databucket_reels_photos';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

const credentialsPath = process.env.GCP_CREDENTIALS_PATH;
const bucketName = process.env.GCP_BUCKET_NAME;

let storageOptions = {};
const resolvedPath = path.resolve(process.cwd(), credentialsPath);
if (fs.existsSync(resolvedPath)) {
  storageOptions.keyFilename = resolvedPath;
}

const storage = new Storage(storageOptions);
const bucket = storage.bucket(bucketName);

async function getSignedUrl(blobName, expirationSeconds = 3600) {
  try {
    if (!blobName) return '';
    if (blobName.startsWith('http://') || blobName.startsWith('https://')) {
      return blobName;
    }
    
    let cleanBlobName = blobName;
    if (blobName.startsWith('gs://')) {
      const prefix = `gs://${bucketName}/`;
      if (blobName.startsWith(prefix)) {
        cleanBlobName = blobName.substring(prefix.length);
      } else {
        const parts = blobName.replace('gs://', '').split('/');
        parts.shift();
        cleanBlobName = parts.join('/');
      }
    }

    if (!cleanBlobName.includes('/')) {
      const ext = path.extname(cleanBlobName).toLowerCase();
      if (['.png', '.jpg', '.jpeg', '.webp', '.gif'].includes(ext)) {
        cleanBlobName = `images/${cleanBlobName}`;
      } else if (['.mp4', '.mov', '.webm', '.avi', '.mkv'].includes(ext)) {
        cleanBlobName = `videos/${cleanBlobName}`;
      }
    }

    const [url] = await bucket.file(cleanBlobName).getSignedUrl({
      version: 'v4',
      action: 'read',
      expires: Date.now() + expirationSeconds * 1000,
    });
    return url;
  } catch (error) {
    console.error(`Error signing ${blobName}:`, error.message);
    return '';
  }
}

async function main() {
  try {
    const imagesRes = await pool.query('SELECT * FROM images_god ORDER BY created_at DESC LIMIT 5');
    const videosRes = await pool.query('SELECT * FROM videos_god ORDER BY created_at DESC LIMIT 5');

    console.log('--- SIGNING IMAGES ---');
    for (const row of imagesRes.rows) {
      const targetFilename = row.gcp_bucket_url || row.gcp_filename;
      const signedUrl = await getSignedUrl(targetFilename);
      console.log(`ID: ${row.id}`);
      console.log(`  gcp_bucket_url: ${row.gcp_bucket_url}`);
      console.log(`  gcp_filename: ${row.gcp_filename}`);
      console.log(`  Signed URL: ${signedUrl ? signedUrl.substring(0, 80) + '...' : 'NONE'}`);
    }

    console.log('\n--- SIGNING VIDEOS ---');
    for (const row of videosRes.rows) {
      const targetFilename = row.gcp_bucket_url || row.gcp_filename;
      const signedUrl = await getSignedUrl(targetFilename);
      console.log(`ID: ${row.id}`);
      console.log(`  gcp_bucket_url: ${row.gcp_bucket_url}`);
      console.log(`  gcp_filename: ${row.gcp_filename}`);
      console.log(`  Signed URL: ${signedUrl ? signedUrl.substring(0, 80) + '...' : 'NONE'}`);
    }
  } catch (err) {
    console.error(err);
  } finally {
    await pool.end();
  }
}

main();
