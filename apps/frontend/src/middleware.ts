import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const role = request.cookies.get('role')?.value;
  
  const path = request.nextUrl.pathname;
  const isLoginPage = path === '/login';
  const isPublicPage = path === '/documentation';

  // Protect dashboard routes
  if (!token && !isLoginPage && !isPublicPage) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Redirect authenticated users away from login
  if (token && isLoginPage) {
    if (role === 'STUDENT') return NextResponse.redirect(new URL('/student', request.url));
    if (role === 'ADVISOR') return NextResponse.redirect(new URL('/advisor', request.url));
    if (role === 'ADMIN') return NextResponse.redirect(new URL('/admin', request.url));
    if (role === 'PRODI') return NextResponse.redirect(new URL('/prodi', request.url));
    if (role === 'DEKAN') return NextResponse.redirect(new URL('/dekan', request.url));
    if (role === 'WD1') return NextResponse.redirect(new URL('/wd1', request.url));
    if (role === 'KASUBAG_AKADEMIK') return NextResponse.redirect(new URL('/kasubag-akademik', request.url));
  }

  // Simple RBAC
  if (path.startsWith('/student') && role !== 'STUDENT') {
     return NextResponse.redirect(new URL('/login', request.url));
  }
  
  if (path.startsWith('/advisor') && role !== 'ADVISOR') {
     return NextResponse.redirect(new URL('/login', request.url));
  }

  if (path.startsWith('/admin') && role !== 'ADMIN') {
     return NextResponse.redirect(new URL('/login', request.url));
  }

  if (path.startsWith('/prodi') && role !== 'PRODI') {
     return NextResponse.redirect(new URL('/login', request.url));
  }

  if (path.startsWith('/dekan') && role !== 'DEKAN' && role !== 'ADMIN') {
     return NextResponse.redirect(new URL('/login', request.url));
  }

  if (path.startsWith('/wd1') && role !== 'WD1' && role !== 'ADMIN') {
     return NextResponse.redirect(new URL('/login', request.url));
  }

  if (path.startsWith('/kasubag-akademik') && role !== 'KASUBAG_AKADEMIK' && role !== 'ADMIN') {
     return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'],
};
