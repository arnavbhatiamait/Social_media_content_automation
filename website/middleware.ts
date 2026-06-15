import { NextRequest, NextResponse } from 'next/server';
import { verifySessionToken } from './app/lib/token';

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const token = req.cookies.get('session_token')?.value;

  const isAuth = token ? await verifySessionToken(token) : null;

  // Protect /dashboard paths
  if (pathname.startsWith('/dashboard')) {
    if (!isAuth) {
      const url = req.nextUrl.clone();
      url.pathname = '/login';
      // Pass the original path as a query param for redirection if needed
      url.searchParams.set('from', pathname);
      return NextResponse.redirect(url);
    }
  }

  // Redirect authenticated users away from /login or / root to /dashboard
  if (pathname === '/login' || pathname === '/') {
    if (isAuth) {
      const url = req.nextUrl.clone();
      url.pathname = '/dashboard';
      return NextResponse.redirect(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/login', '/'],
};
