import { NextRequest } from 'next/server';

interface ImagePayload {
  base64: string;
  mimeType: string;
  name: string;
}

export async function POST(request: NextRequest) {
  try {
    const { message, conversation_id, images, language } = await request.json();

    if (!message && (!images || images.length === 0)) {
      return new Response(
        JSON.stringify({ error: 'Message or images are required' }),
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // Call backend RAG streaming service
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    console.log(`Calling backend streaming: ${backendUrl}/api/v1/chat/stream`);
    console.log(`Language: ${language || 'vi'}`);

    const response = await fetch(`${backendUrl}/api/v1/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message || '',
        conversation_id: conversation_id || 'web-chat-stream',
        language: language || 'vi',
        images: images?.map((img: ImagePayload) => ({
          base64: img.base64,
          mime_type: img.mimeType,
          name: img.name
        })) || []
      }),
    });

    console.log(`Backend streaming response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend streaming error: ${response.status} - ${errorText}`);
      throw new Error(`Backend streaming API error: ${response.status}`);
    }

    // Return the streaming response directly
    return new Response(response.body, {
      status: 200,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no', // Disable nginx buffering
      },
    });

  } catch (error) {
    console.error('Chat streaming API error:', error);
    
    // Return error as SSE format
    const errorMessage = `data: ${JSON.stringify({
      type: 'error', 
      message: 'Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu. Vui lòng thử lại sau.'
    })}\n\n`;

    return new Response(errorMessage, {
      status: 200,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  }
}