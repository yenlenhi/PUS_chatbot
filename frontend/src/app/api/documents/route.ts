import { NextResponse } from 'next/server';

const getBackendUrl = () =>
  (process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export async function GET() {
  try {
    const response = await fetch(`${getBackendUrl()}/api/v1/documents`, {
      cache: 'no-store',
    });

    if (!response.ok) {
      const detail = await response.text();
      return NextResponse.json(
        { detail: detail || 'Failed to fetch documents' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Document list proxy error:', error);
    return NextResponse.json(
      { detail: 'Document service unavailable' },
      { status: 502 }
    );
  }
}
