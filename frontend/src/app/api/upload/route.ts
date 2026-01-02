import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    
    // Get the form data from the request
    const formData = await request.formData();
    
    console.log('[Upload API] Forwarding upload request to:', `${backendUrl}/api/v1/admin/upload`);
    
    // Forward the request to the backend
    const response = await fetch(`${backendUrl}/api/v1/admin/upload`, {
      method: 'POST',
      body: formData,
    });

    // Get the response data
    const data = await response.json();

    if (!response.ok) {
      console.error('[Upload API] Backend error:', data);
      return NextResponse.json(
        { error: data.detail || 'Upload failed', success: false },
        { status: response.status }
      );
    }

    console.log('[Upload API] Upload successful:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('[Upload API] Error:', error);
    return NextResponse.json(
      { error: 'Internal server error during upload', success: false },
      { status: 500 }
    );
  }
}

export const config = {
  api: {
    bodyParser: false, // Disable body parsing, we handle it manually for FormData
  },
};
