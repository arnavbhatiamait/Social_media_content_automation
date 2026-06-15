import { NextRequest, NextResponse } from 'next/server';
import { query } from '../../lib/db';

export async function GET(req: NextRequest) {
  try {
    // 1. Fetch total generated asset counts
    const imagesCountRes = await query('SELECT COUNT(*) FROM images_god');
    const videosCountRes = await query('SELECT COUNT(*) FROM videos_god');
    
    // 2. Fetch pending queue counts
    const imagesQueueCountRes = await query('SELECT COUNT(*) FROM images_on_demand WHERE generated = false');
    const videosQueueCountRes = await query('SELECT COUNT(*) FROM videos_on_demand WHERE generated = false');

    // 3. Fetch social media posted counts
    const instaImagesCountRes = await query('SELECT COUNT(*) FROM images_god WHERE insta_posted = true');
    const instaVideosCountRes = await query('SELECT COUNT(*) FROM videos_god WHERE insta_posted = true');
    const ytVideosCountRes = await query('SELECT COUNT(*) FROM videos_god WHERE yt_posted = true');

    // 4. Sum up total analytics metrics
    const analyticsSumRes = await query(
      'SELECT SUM(impressions) as impressions, SUM(reach) as reach, SUM(likes) as likes, SUM(comments) as comments, SUM(shares) as shares, SUM(saves) as saves FROM analytics'
    );

    // 5. Fetch recent social media platform interactions log
    let recentLogs = [];
    try {
      const recentAnalyticsRes = await query(
        'SELECT a.*, c.title as content_title, c.content_type FROM analytics a JOIN contents c ON a.content_id = c.id ORDER BY a.collected_at DESC LIMIT 10'
      );
      recentLogs = recentAnalyticsRes.rows;
    } catch (tblErr) {
      console.warn('Analytics or contents tables may not be initialized yet:', tblErr);
    }

    const counts = {
      images: parseInt(imagesCountRes.rows[0]?.count || '0', 10),
      videos: parseInt(videosCountRes.rows[0]?.count || '0', 10),
      imagesQueue: parseInt(imagesQueueCountRes.rows[0]?.count || '0', 10),
      videosQueue: parseInt(videosQueueCountRes.rows[0]?.count || '0', 10),
      postedInstaImages: parseInt(instaImagesCountRes.rows[0]?.count || '0', 10),
      postedInstaVideos: parseInt(instaVideosCountRes.rows[0]?.count || '0', 10),
      postedYtVideos: parseInt(ytVideosCountRes.rows[0]?.count || '0', 10),
    };

    const sums = {
      impressions: parseInt(analyticsSumRes.rows[0]?.impressions || '0', 10),
      reach: parseInt(analyticsSumRes.rows[0]?.reach || '0', 10),
      likes: parseInt(analyticsSumRes.rows[0]?.likes || '0', 10),
      comments: parseInt(analyticsSumRes.rows[0]?.comments || '0', 10),
      shares: parseInt(analyticsSumRes.rows[0]?.shares || '0', 10),
      saves: parseInt(analyticsSumRes.rows[0]?.saves || '0', 10),
    };

    return NextResponse.json({
      success: true,
      counts,
      sums,
      recent: recentLogs,
    });
  } catch (error: any) {
    console.error('Error fetching analytics summaries:', error);
    // Graceful fallback to prevent frontend dashboard crashing if tables are missing
    return NextResponse.json({
      success: false,
      error: error.message,
      counts: {
        images: 0,
        videos: 0,
        imagesQueue: 0,
        videosQueue: 0,
        postedInstaImages: 0,
        postedInstaVideos: 0,
        postedYtVideos: 0,
      },
      sums: {
        impressions: 0,
        reach: 0,
        likes: 0,
        comments: 0,
        shares: 0,
        saves: 0,
      },
      recent: [],
    });
  }
}
