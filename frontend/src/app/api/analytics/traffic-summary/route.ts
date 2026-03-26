import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/analytics/traffic-summary`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      next: { revalidate: 60 },
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching traffic summary:', error);

    return NextResponse.json(
      {
        online_now: 0,
        today_views: 0,
        month_views: 0,
        total_views: 0,
        last_updated_at: new Date().toISOString(),
        data_source: 'fallback',
      },
      { status: 200 }
    );
  }
}
