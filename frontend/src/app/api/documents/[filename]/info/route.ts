import { NextResponse } from 'next/server';

const getBackendUrl = () =>
  (process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ filename: string }> }
) {
  const { filename } = await params;
  const backendUrl = getBackendUrl();

  try {
    const response = await fetch(
      `${backendUrl}/api/v1/documents/${encodeURIComponent(filename)}/info`,
      {
        cache: 'no-store',
      }
    );

    if (!response.ok) {
      const detail = await response.text();
      return NextResponse.json(
        { detail: detail || 'Failed to fetch document metadata' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Document info proxy error:', error);
    return NextResponse.json(
      { detail: 'Document metadata service unavailable' },
      { status: 502 }
    );
  }
}
