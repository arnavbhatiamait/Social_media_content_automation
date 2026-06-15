import { NextRequest, NextResponse } from 'next/server';
import { query } from '../../lib/db';

// GET: Fetch pending queues
export async function GET(req: NextRequest) {
  try {
    const imagesQueueRes = await query(
      'SELECT * FROM images_on_demand WHERE generated = false ORDER BY created_at DESC'
    );
    const videosQueueRes = await query(
      'SELECT * FROM videos_on_demand WHERE generated = false ORDER BY created_at DESC'
    );

    return NextResponse.json({
      success: true,
      imagesQueue: imagesQueueRes.rows,
      videosQueue: videosQueueRes.rows,
    });
  } catch (error: any) {
    console.error('Error fetching queue:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve queue: ' + error.message },
      { status: 500 }
    );
  }
}

// POST: Enqueue a new generation prompt
export async function POST(req: NextRequest) {
  try {
    const { type, prompt, ytPost = false, instaPost = true } = await req.json();

    if (!prompt || !prompt.trim()) {
      return NextResponse.json(
        { error: 'Prompt is required.' },
        { status: 400 }
      );
    }

    if (type !== 'image' && type !== 'video') {
      return NextResponse.json(
        { error: 'Invalid generation type. Must be "image" or "video".' },
        { status: 400 }
      );
    }

    const tableName = type === 'image' ? 'images_on_demand' : 'videos_on_demand';

    const insertQuery = `
      INSERT INTO ${tableName} (prompt, yt_post, generated, insta_post, created_at, updated_at)
      VALUES ($1, $2, false, $3, NOW(), NOW())
      RETURNING *
    `;

    const result = await query(insertQuery, [prompt.trim(), ytPost, instaPost]);

    return NextResponse.json({
      success: true,
      message: 'Item enqueued successfully.',
      data: result.rows[0],
    });
  } catch (error: any) {
    console.error('Error enqueuing item:', error);
    return NextResponse.json(
      { error: 'Failed to enqueue item: ' + error.message },
      { status: 500 }
    );
  }
}

// DELETE: Remove a queue item
export async function DELETE(req: NextRequest) {
  try {
    const { searchParams } = req.nextUrl;
    const type = searchParams.get('type');
    const id = searchParams.get('id');

    if (!type || !id) {
      return NextResponse.json(
        { error: 'Type (image/video) and ID are required.' },
        { status: 400 }
      );
    }

    if (type !== 'image' && type !== 'video') {
      return NextResponse.json(
        { error: 'Invalid type. Must be "image" or "video".' },
        { status: 400 }
      );
    }

    const tableName = type === 'image' ? 'images_on_demand' : 'videos_on_demand';
    const deleteQuery = `DELETE FROM ${tableName} WHERE id = $1`;

    await query(deleteQuery, [parseInt(id, 10)]);

    return NextResponse.json({
      success: true,
      message: 'Item removed from queue.',
    });
  } catch (error: any) {
    console.error('Error deleting queue item:', error);
    return NextResponse.json(
      { error: 'Failed to delete queue item: ' + error.message },
      { status: 500 }
    );
  }
}
