const { Storage } = require('@google-cloud/storage');
const path = require('path');
const fs = require('fs');
const https = require('https');

const credentialsPath = '../gcp_secrets.json';
const bucketName = 'databucket_reels_photos';

let storageOptions = {};
const resolvedPath = path.resolve(process.cwd(), credentialsPath);
if (fs.existsSync(resolvedPath)) {
  storageOptions.keyFilename = resolvedPath;
}

const storage = new Storage(storageOptions);
const bucket = storage.bucket(bucketName);

async function testFetch() {
  const blobName = 'images/gen_07011dc9.png';
  try {
    const [url] = await bucket.file(blobName).getSignedUrl({
      version: 'v4',
      action: 'read',
      expires: Date.now() + 3600 * 1000,
    });
    console.log('Generated signed URL:', url);
    
    console.log('Fetching signed URL...');
    https.get(url, (res) => {
      console.log('STATUS:', res.statusCode);
      console.log('HEADERS:', JSON.stringify(res.headers, null, 2));
      
      let body = '';
      res.on('data', (chunk) => {
        if (body.length < 500) body += chunk;
      });
      res.on('end', () => {
        if (res.statusCode !== 200) {
          console.log('Error Body Snippet:', body);
        } else {
          console.log('Successfully fetched content! Length:', res.headers['content-length']);
        }
      });
    }).on('error', (err) => {
      console.error('Fetch error:', err);
    });
  } catch (err) {
    console.error('Signing failed:', err);
  }
}

testFetch();
