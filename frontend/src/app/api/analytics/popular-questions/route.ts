import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const timeRange = searchParams.get('time_range') || 'L7D';
    const limit = searchParams.get('limit') || '5';
    
    // Forward request to backend
    const response = await fetch(
      `${BACKEND_URL}/api/v1/analytics/popular-questions?time_range=${timeRange}&limit=${limit}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Error fetching popular questions:', error);
    
    // Return fallback questions in Vietnamese and English
    const fallbackQuestions = [
      "Điều kiện tuyển sinh năm 2025 như thế nào?",
      "Học phí của trường là bao nhiêu?", 
      "Các ngành đào tạo của trường?",
      "Thông tin về ký túc xá?",
      "Cơ hội việc làm sau tốt nghiệp?"
    ];

    return NextResponse.json({
      popular_questions: fallbackQuestions.map((q, i) => ({
        question: q,
        count: Math.floor(Math.random() * 100) + 50, // Random count for fallback
        last_asked: new Date().toISOString()
      })),
      total_count: fallbackQuestions.length,
      time_range: timeRange,
      data_source: "fallback"
    });
  }
}