import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const limit = searchParams.get('limit') || '5';
    
    // Forward request to backend
    const response = await fetch(
      `${BACKEND_URL}/api/v1/analytics/suggested-questions?limit=${limit}`,
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
    
    // Handle different response formats from backend
    let questions: string[] = [];
    
    if (Array.isArray(data)) {
      // If data is already an array of questions
      questions = data.map((item: any) => 
        typeof item === 'string' ? item : item.question || String(item)
      );
    } else if (data.popular_questions && Array.isArray(data.popular_questions)) {
      // If data has popular_questions array
      questions = data.popular_questions.map((item: any) => item.question);
    } else {
      // Fallback
      questions = [];
    }
    
    return NextResponse.json(questions);

  } catch (error) {
    console.error('Error fetching suggested questions:', error);
    
    const searchParams = request.nextUrl.searchParams;
    const limit = searchParams.get('limit') || '5';
    
    // Return fallback questions
    const fallbackQuestions = [
      "Điều kiện tuyển sinh và các phương thức xét tuyển của trường?",
      "Quy chế đào tạo theo tín chỉ là gì?",
      "Quy định về thi, kiểm tra và đánh giá kết quả học tập?",
      "Các quy định về quản lý và chế độ chính sách học viên?",
      "Tiêu chuẩn và quy trình bảo đảm chất lượng đào tạo?"
    ];

    return NextResponse.json(fallbackQuestions.slice(0, parseInt(limit)));
  }
}