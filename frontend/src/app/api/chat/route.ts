import { NextRequest, NextResponse } from 'next/server';

interface ImagePayload {
  base64: string;
  mimeType: string;
  name: string;
}

interface BackendErrorPayload {
  error?: string;
  detail?: string;
}

async function readBackendError(response: Response): Promise<BackendErrorPayload> {
  try {
    return await response.json();
  } catch {
    const detail = await response.text();
    return { detail: detail || `Backend API error: ${response.status}` };
  }
}

export async function POST(request: NextRequest) {
  try {
    const { message, conversation_id, conversation_history, images, language } = await request.json();

    if (!message && (!images || images.length === 0)) {
      return NextResponse.json(
        { error: 'Message or images are required' },
        { status: 400 }
      );
    }

    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    const response = await fetch(`${backendUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message || '',
        conversation_id: conversation_id || 'web-chat',
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
      const errorPayload = await readBackendError(response);
      return NextResponse.json(
        {
          error: errorPayload.error || 'Chat backend error',
          detail: errorPayload.detail || 'Không thể xử lý yêu cầu lúc này.',
        },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      response: data.answer || data.response,
      answer: data.answer || data.response,
      confidence: data.confidence ?? 0,
      sources: data.sources || [],
      source_references: data.source_references || [],
      attachments: data.attachments || [],
      conversation_id: data.conversation_id,
      processing_time: data.processing_time,
      chart_data: data.chart_data || [],
      images: data.images || [],
    });
  } catch (error) {
    console.error('Chat API error:', error);

    return NextResponse.json(
      {
        error: 'Chat API unavailable',
        detail: 'Không thể kết nối tới dịch vụ chatbot lúc này. Vui lòng thử lại sau.',
      },
      { status: 502 }
    );
  }
}
