import { NextRequest, NextResponse } from 'next/server';
import { query } from '../../lib/db';

export async function GET(req: NextRequest) {
  try {
    // Fetch latest 100 images and 100 videos from the database
    const imagesRes = await query('SELECT * FROM images_god ORDER BY created_at DESC LIMIT 100');
    const videosRes = await query('SELECT * FROM videos_god ORDER BY created_at DESC LIMIT 100');

    const images = imagesRes.rows.map((row) => ({
      id: row.id,
      type: 'image',
      url: row.url,
      storage_url: row.gcp_bucket_url,
      filename: row.gcp_filename,
      prompt: row.prompt_used,
      model: row.model_used,
      signed_url: row.insta_url, // GCS signed URL stored during generation
      posted_insta: row.insta_posted || row.posted,
      posted_yt: row.yt_posted,
      alt_text: row.alt_text,
      description: row.description,
      created_at: row.created_at,
      updated_at: row.updated_at,
    }));

    const videos = videosRes.rows.map((row) => ({
      id: row.id,
      type: 'video',
      url: row.url,
      storage_url: row.gcp_bucket_url,
      filename: row.gcp_filename,
      prompt: row.prompt_used,
      model: row.model_used,
      signed_url: row.insta_url, // GCS signed URL stored during generation
      posted_insta: row.insta_posted,
      posted_yt: row.yt_posted,
      yt_url: row.yt_url,
      alt_text: row.alt_text,
      description: row.description,
      created_at: row.created_at,
      updated_at: row.updated_at,
    }));

    // Create a unified stream sorted by created_at descending
    const allMedia = [...images, ...videos].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );

    return NextResponse.json({
      success: true,
      images,
      videos,
      allMedia,
    });
  } catch (error: any) {
    console.error('Error fetching media assets:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve media assets from the database: ' + error.message },
      { status: 500 }
    );
  }
}
