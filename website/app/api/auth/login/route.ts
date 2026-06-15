import { NextRequest, NextResponse } from 'next/server';
import { createSessionToken } from '../../../lib/token';

export async function POST(req: NextRequest) {
  try {
    const { password } = await req.json();
    const adminPassword = process.env.WEBSITE_ADMIN_PASSWORD || 'admin123';

    if (password !== adminPassword) {
      return NextResponse.json(
        { error: 'Invalid administrator password.' },
        { status: 401 }
      );
    }

    const token = await createSessionToken({ username: 'admin' });

    const response = NextResponse.json({
      success: true,
      message: 'Authenticated successfully.',
    });

    // Set secure HttpOnly session cookie
    response.cookies.set('session_token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 60 * 24 * 7, // 7 days
    });

    return response;
  } catch (error: any) {
    console.error('Login error:', error);
    return NextResponse.json(
      { error: 'An error occurred during authentication.' },
      { status: 500 }
    );
  }
}
