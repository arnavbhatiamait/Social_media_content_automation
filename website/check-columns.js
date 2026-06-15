const { Pool } = require('pg');

const pool = new Pool({
  connectionString: 'postgresql://neondb_owner:local_postgres_password_123@ep-shy-haze-atri6g51-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require',
  ssl: { rejectUnauthorized: false },
});

async function main() {
  try {
    const imagesRes = await pool.query('SELECT * FROM images_god LIMIT 1');
    console.log('--- IMAGES COLUMNS & VALUES ---');
    console.log(imagesRes.rows[0]);

    const videosRes = await pool.query('SELECT * FROM videos_god LIMIT 1');
    console.log('--- VIDEOS COLUMNS & VALUES ---');
    console.log(videosRes.rows[0]);
  } catch (err) {
    console.error(err);
  } finally {
    await pool.end();
  }
}

main();
