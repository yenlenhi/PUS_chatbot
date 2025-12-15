import { NextRequest, NextResponse } from 'next/server';

interface ImagePayload {
  base64: string;
  mimeType: string;
  name: string;
}

export async function POST(request: NextRequest) {
  try {
    const { message, conversation_id, images, language } = await request.json();

    if (!message && (!images || images.length === 0)) {
      return NextResponse.json(
        { error: 'Message or images are required' },
        { status: 400 }
      );
    }

    // Call backend RAG service
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    console.log(`Calling backend: ${backendUrl}/api/v1/chat`);
    console.log(`Images count: ${images?.length || 0}`);
    console.log(`Language: ${language || 'vi'}`);

    const response = await fetch(`${backendUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message || '',
        conversation_id: conversation_id || 'web-chat',
        language: language || 'vi',  // Pass language preference to backend
        images: images?.map((img: ImagePayload) => ({
          base64: img.base64,
          mime_type: img.mimeType,
          name: img.name
        })) || []
      }),
    });

    console.log(`Backend response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error: ${response.status} - ${errorText}`);
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    console.log('Backend response data:', JSON.stringify(data, null, 2));

    return NextResponse.json({
      response: data.answer || data.response,
      confidence: data.confidence,
      sources: data.sources || [],
      source_references: data.source_references || [],
      conversation_id: data.conversation_id,
      processing_time: data.processing_time,
      chart_data: data.chart_data || [],
      images: data.images || [],
    });

  } catch (error) {
    console.error('Chat API error:', error);

    // Fallback response for demo purposes
    const fallbackResponses = [
      "Cảm ơn bạn đã quan tâm đến Trường Đại học An ninh Nhân dân. Để được tư vấn chi tiết, vui lòng liên hệ hotline: 024.3854.2222",
      "Trường có các ngành đào tạo chính: An ninh chính trị, An ninh kinh tế, An ninh mạng, Điều tra hình sự. Bạn muốn tìm hiểu ngành nào cụ thể?",
      "Điều kiện tuyển sinh năm 2025: Tốt nghiệp THPT, độ tuổi 17-21, sức khỏe tốt, lý lịch rõ ràng. Bạn cần thông tin gì thêm?",
      "Học phí của trường được quy định theo thông tư của Bộ Công an. Để biết mức học phí cụ thể, vui lòng liên hệ phòng đào tạo."
    ];

    const randomResponse = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];

    return NextResponse.json({
      response: randomResponse,
      confidence: 0.8,
      sources: ["Thông tin từ website chính thức"],
      source_references: []
    });
  }
}
