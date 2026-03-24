import { NextRequest, NextResponse } from 'next/server';

const getBackendUrl = () =>
  (process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  const { filename } = await params;
  const backendUrl = getBackendUrl();
  const search = request.nextUrl.search;

  try {
    const response = await fetch(
      `${backendUrl}/api/v1/documents/${encodeURIComponent(filename)}${search}`,
      {
        cache: 'no-store',
      }
    );

    if (!response.ok) {
      const detail = await response.text();
      return NextResponse.json(
        { detail: detail || 'Failed to fetch document' },
        { status: response.status }
      );
    }

    const headers = new Headers();
    for (const headerName of [
      'content-type',
      'content-disposition',
      'x-page-number',
      'cache-control',
    ]) {
      const headerValue = response.headers.get(headerName);
      if (headerValue) {
        headers.set(headerName, headerValue);
      }
    }

    return new Response(response.body, {
      status: response.status,
      headers,
    });
  } catch (error) {
    console.error('Document proxy error:', error);
    return NextResponse.json(
      { detail: 'Document service unavailable' },
      { status: 502 }
    );
  }
}
