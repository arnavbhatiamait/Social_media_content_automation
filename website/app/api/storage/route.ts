import { NextRequest, NextResponse } from 'next/server';
import { bucket } from '../../lib/gcs';

export async function GET(req: NextRequest) {
  try {
    // Retrieve the first 100 files in the bucket
    const [files] = await bucket.getFiles({ maxResults: 100 });

    const fileList = files.map((file) => ({
      name: file.name,
      id: file.id,
      size: file.metadata.size ? parseInt(file.metadata.size as string, 10) : 0,
      contentType: file.metadata.contentType || 'application/octet-stream',
      updated: file.metadata.updated || file.metadata.timeCreated || new Date().toISOString(),
    }));

    return NextResponse.json({
      success: true,
      files: fileList,
    });
  } catch (error: any) {
    console.error('Error listing GCS bucket files:', error);
    return NextResponse.json(
      { error: 'Failed to list Cloud Storage files: ' + error.message },
      { status: 500 }
    );
  }
}
