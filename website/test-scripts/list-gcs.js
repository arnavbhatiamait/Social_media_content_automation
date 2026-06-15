const { Storage } = require('@google-cloud/storage');
const path = require('path');
const fs = require('fs');

const credentialsPath = '../gcp_secrets.json';
const bucketName = 'databucket_reels_photos';

let storageOptions = {};
const resolvedPath = path.resolve(process.cwd(), credentialsPath);
if (fs.existsSync(resolvedPath)) {
  storageOptions.keyFilename = resolvedPath;
}

const storage = new Storage(storageOptions);
const bucket = storage.bucket(bucketName);

async function listFiles() {
  try {
    console.log('Listing files in GCS bucket:', bucketName);
    const [files] = await bucket.getFiles({ maxResults: 50 });
    console.log(`Found ${files.length} files:`);
    for (const file of files) {
      console.log(`- ${file.name} (Size: ${file.metadata.size} bytes, Type: ${file.metadata.contentType})`);
    }
  } catch (err) {
    console.error('Failed to list files:', err);
  }
}

listFiles();
