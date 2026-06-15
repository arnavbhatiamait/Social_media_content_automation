const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

// Manually parse .env.local
const envPath = path.join(__dirname, '.env.local');
const envContent = fs.readFileSync(envPath, 'utf8');
const lines = envContent.split(/\r?\n/);
const envVars = {};

for (const line of lines) {
  const trimmed = line.trim();
  if (trimmed && !trimmed.startsWith('#')) {
    const parts = trimmed.split('=');
    if (parts.length >= 2) {
      const key = parts[0].trim();
      const val = parts.slice(1).join('=').trim();
      envVars[key] = val;
    }
  }
}

const pool = new Pool({
  connectionString: envVars['DATABASE_URL'],
  ssl: { rejectUnauthorized: false }
});

async function run() {
  try {
    const imagesRes = await pool.query('SELECT id, gcp_bucket_url, gcp_filename, url, insta_url FROM images_god LIMIT 3');
    console.log('=== IMAGES RECORDS ===');
    console.log(JSON.stringify(imagesRes.rows, null, 2));

    const videosRes = await pool.query('SELECT id, gcp_bucket_url, gcp_filename, url, insta_url FROM videos_god LIMIT 3');
    console.log('\n=== VIDEOS RECORDS ===');
    console.log(JSON.stringify(videosRes.rows, null, 2));
  } catch (err) {
    console.error('Error running query:', err);
  } finally {
    await pool.end();
  }
}

run();
