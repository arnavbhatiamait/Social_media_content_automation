import { NextRequest, NextResponse } from 'next/server';
import { verifySessionToken } from '../../../lib/token';

export async function GET(req: NextRequest) {
  const token = req.cookies.get('session_token')?.value;

  if (!token) {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }

  const payload = await verifySessionToken(token);

  if (!payload) {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }

  return NextResponse.json({
    authenticated: true,
    user: {
      username: payload.username,
    },
  });
}
