import { NextRequest, NextResponse } from 'next/server';
import { getSignedUrl } from '../../../lib/gcs';

export async function GET(req: NextRequest) {
  try {
    const filename = req.nextUrl.searchParams.get('filename');

    if (!filename) {
      return NextResponse.json(
        { error: 'Missing filename query parameter.' },
        { status: 400 }
      );
    }

    const signedUrl = await getSignedUrl(filename);
    return NextResponse.json({
      success: true,
      signedUrl,
    });
  } catch (error: any) {
    console.error('Error generating signed URL for client:', error);
    return NextResponse.json(
      { error: 'Failed to generate signed URL: ' + error.message },
      { status: 500 }
    );
  }
}
