import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Call backend feedback service
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    console.log(`Calling backend feedback: ${backendUrl}/api/v1/feedback`);

    const response = await fetch(`${backendUrl}/api/v1/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    console.log(`Backend feedback response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend feedback error: ${response.status} - ${errorText}`);
      throw new Error(`Backend feedback API error: ${response.status}`);
    }

    const data = await response.json();
    console.log('Backend feedback response:', data);

    return NextResponse.json(data);

  } catch (error) {
    console.error('Feedback API error:', error);

    // Return error response
    return NextResponse.json(
      { 
        success: false, 
        message: 'Không thể gửi phản hồi. Vui lòng thử lại sau.' 
      },
      { status: 500 }
    );
  }
}
