import { NextRequest } from 'next/server';

interface ImagePayload {
  base64: string;
  mimeType: string;
  name: string;
}

export async function POST(request: NextRequest) {
  try {
    const { message, conversation_id, conversation_history, images, language } = await request.json();

    if (!message && (!images || images.length === 0)) {
      return new Response(
        JSON.stringify({ error: 'Message or images are required' }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }

    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    const response = await fetch(`${backendUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({
        message: message || '',
        conversation_id: conversation_id || 'web-chat-stream',
        conversation_history: conversation_history || [],
        language: language || 'vi',
        images: images?.map((img: ImagePayload) => ({
          base64: img.base64,
          mime_type: img.mimeType,
          name: img.name,
        })) || [],
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      const errorMessage = `data: ${JSON.stringify({
        type: 'error',
        message: errorText || 'Không thể xử lý yêu cầu lúc này.',
      })}\n\n`;

      return new Response(errorMessage, {
        status: response.status,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    }

    return new Response(response.body, {
      status: 200,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
      },
    });
  } catch (error) {
    console.error('Chat streaming API error:', error);

    const errorMessage = `data: ${JSON.stringify({
      type: 'error',
      message: 'Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu. Vui lòng thử lại sau.',
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
