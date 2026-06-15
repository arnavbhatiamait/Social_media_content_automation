const { Storage } = require('@google-cloud/storage');
const path = require('path');
const fs = require('fs');

const credentialsPath = '../gcp_secrets.json';
const bucketName = 'databucket_reels_photos';

let storageOptions = {};
const resolvedPath = path.resolve(process.cwd(), credentialsPath);
if (fs.existsSync(resolvedPath)) {
  storageOptions.keyFilename = resolvedPath;
  console.log('Found GCP credentials at:', resolvedPath);
} else {
  console.warn('GCP credentials file not found at:', resolvedPath);
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

    console.log(`Signing blob: "${cleanBlobName}"`);
    const [url] = await bucket.file(cleanBlobName).getSignedUrl({
      version: 'v4',
      action: 'read',
      expires: Date.now() + expirationSeconds * 1000,
    });
    return url;
  } catch (error) {
    console.error(`Error generating signed URL for blob "${blobName}":`, error);
    throw error;
  }
}

async function main() {
  const testBlob = 'gs://databucket_reels_photos/images/gen_07011dc9.png';
  try {
    const url = await getSignedUrl(testBlob);
    console.log('SUCCESS!');
    console.log('Signed URL:', url);
  } catch (err) {
    console.error('FAILED TO GENERATE SIGNED URL:');
    console.error(err);
  }
}

main();
