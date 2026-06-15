import { Storage } from '@google-cloud/storage';
import path from 'path';
import fs from 'fs';

const credentialsPath = process.env.GCP_CREDENTIALS_PATH;
const bucketName = process.env.GCP_BUCKET_NAME || 'databucket_reels_photos';

let storageOptions: any = {};

if (credentialsPath) {
  // Resolve relative path against the application root
  const resolvedPath = path.resolve(process.cwd(), credentialsPath);
  if (fs.existsSync(resolvedPath)) {
    storageOptions.keyFilename = resolvedPath;
  } else {
    console.warn(`GCP credentials file not found at resolved path: ${resolvedPath}. Attempting default configuration.`);
  }
}

const storage = new Storage(storageOptions);
const bucket = storage.bucket(bucketName);

/**
 * Generates a dynamic v4 signed URL for a specific GCS blob.
 * @param blobName The name of the file in the bucket (e.g. "images/gen_123.png")
 * @param expirationSeconds Expiration time in seconds (default: 3600 = 1 hour)
 */
export async function getSignedUrl(blobName: string, expirationSeconds: number = 3600): Promise<string> {
  try {
    // If the path is already a public https URL, return it directly
    if (blobName.startsWith('http://') || blobName.startsWith('https://')) {
      return blobName;
    }
    
    // Clean gs:// prefixes if stored that way
    let cleanBlobName = blobName;
    if (blobName.startsWith('gs://')) {
      // e.g. gs://databucket_reels_photos/images/gen.png -> images/gen.png
      const prefix = `gs://${bucketName}/`;
      if (blobName.startsWith(prefix)) {
        cleanBlobName = blobName.substring(prefix.length);
      } else {
        // Strip off gs://[bucket-name]/
        const parts = blobName.replace('gs://', '').split('/');
        parts.shift(); // remove bucket
        cleanBlobName = parts.join('/');
      }
    }

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

export { storage, bucket, bucketName };
