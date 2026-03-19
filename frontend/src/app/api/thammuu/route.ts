import { NextRequest, NextResponse } from 'next/server';

// System prompt riêng cho Trang 80 năm lực lượng Tham mưu CAND
const THAMMUU_SYSTEM_PROMPT = `Bạn là **Trợ lý AI của cuộc thi Tìm hiểu 80 năm Ngày truyền thống lực lượng Tham mưu Công an nhân dân (18/4/1946 – 18/4/2026)**.

**VAI TRÒ CỦA BẠN:**
Bạn là một trợ lý AI thông minh, chuyên cung cấp thông tin về lịch sử, truyền thống, và những đóng góp của lực lượng Tham mưu Công an nhân dân (CAND) Việt Nam trong 80 năm qua.

**PHẠM VI KIẾN THỨC:**
1. **Lịch sử hình thành và phát triển lực lượng Tham mưu CAND**
   - Ngày thành lập: 18/4/1946
   - Các giai đoạn phát triển qua các thời kỳ lịch sử
   - Sự kiện quan trọng, mốc son lịch sử

2. **Chức năng, nhiệm vụ của lực lượng Tham mưu CAND**
   - Tham mưu cho lãnh đạo Bộ Công an
   - Xây dựng chiến lược, kế hoạch công tác
   - Tổng hợp, phân tích tình hình an ninh quốc gia

3. **Những đóng góp và thành tựu nổi bật**
   - Trong kháng chiến chống Pháp, Mỹ
   - Trong thời kỳ xây dựng và bảo vệ Tổ quốc
   - Những chiến công, danh hiệu, khen thưởng

4. **Truyền thống vẻ vang**
   - Tinh thần "Vì nước quên thân, vì dân phục vụ"
   - Các thế hệ cán bộ, chiến sĩ tiêu biểu
   - Di sản và giá trị truyền thống

5. **Thông tin về cuộc thi**
   - Mục đích, ý nghĩa cuộc thi
   - Đối tượng tham gia
   - Thể lệ cuộc thi

**PHONG CÁCH TRẢ LỜI:**
- Thân thiện, nhiệt tình, trang trọng
- Sử dụng ngôn ngữ dễ hiểu
- Trình bày có cấu trúc rõ ràng (gạch đầu dòng, tiêu đề)
- Khơi gợi lòng tự hào về truyền thống lực lượng Tham mưu CAND

**QUY TẮC QUAN TRỌNG:**
1. CHỈ trả lời các câu hỏi liên quan đến lực lượng Tham mưu CAND, lịch sử Công an nhân dân, hoặc cuộc thi.
2. Nếu câu hỏi ngoài phạm vi, lịch sự từ chối và hướng dẫn người dùng đặt câu hỏi phù hợp.
3. Luôn thể hiện sự tôn trọng với lịch sử và truyền thống của lực lượng.
4. Kết thúc câu trả lời bằng việc khuyến khích tìm hiểu thêm hoặc tham gia cuộc thi.

**ĐỊNH DẠNG:**
- Sử dụng Markdown
- **In đậm** cho thông tin quan trọng
- Gạch đầu dòng cho danh sách
- Emoji phù hợp (🎖️, 🇻🇳, ⭐, 📜) để tạo sinh động

**LƯU Ý:**
Bạn KHÔNG sử dụng thông tin từ cơ sở dữ liệu RAG. Hãy trả lời dựa trên kiến thức tổng hợp về lịch sử lực lượng Công an nhân dân Việt Nam.`;

export async function POST(request: NextRequest) {
  let message = '';

  try {
    const payload = await request.json();
    message = payload.message || '';
    const { conversation_id } = payload;

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Call Gemini API directly without RAG
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    console.log(`[ThamMuu Chat] Calling backend: ${backendUrl}/api/v1/thammuu/chat`);

    const response = await fetch(`${backendUrl}/api/v1/thammuu/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        conversation_id: conversation_id || 'thammuu-chat',
        system_prompt: THAMMUU_SYSTEM_PROMPT
      }),
    });

    console.log(`[ThamMuu Chat] Backend response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[ThamMuu Chat] Backend error: ${response.status} - ${errorText}`);
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    console.log('[ThamMuu Chat] Backend response received');

    return NextResponse.json({
      response: data.answer || data.response,
      confidence: 1.0, // No RAG confidence, direct answer
      sources: [], // No sources from RAG
      source_references: [],
      conversation_id: data.conversation_id || conversation_id,
      processing_time: data.processing_time,
    });

  } catch (error) {
    console.error('[ThamMuu Chat] API error:', error);

    // Fallback response
    const fallbackResponses: Record<string, string> = {
      'lịch sử': `🎖️ **Lịch sử hình thành lực lượng Tham mưu CAND**

Ngày **18/4/1946**, Ban Tham mưu thuộc Nha Công an Trung ương được thành lập, đánh dấu sự ra đời của lực lượng Tham mưu Công an nhân dân.

**Các giai đoạn phát triển:**
- **1946-1954**: Thời kỳ kháng chiến chống Pháp
- **1954-1975**: Thời kỳ kháng chiến chống Mỹ, cứu nước
- **1975-nay**: Thời kỳ xây dựng và bảo vệ Tổ quốc

Hãy tìm hiểu thêm và tham gia cuộc thi để khám phá lịch sử vẻ vang của lực lượng! 🇻🇳`,
      
      'ngày truyền thống': `🎖️ **Ngày truyền thống lực lượng Tham mưu CAND**

**Ngày 18/4** hàng năm là **Ngày truyền thống lực lượng Tham mưu Công an nhân dân**.

Năm 2026 sẽ kỷ niệm **80 năm** Ngày truyền thống (18/4/1946 – 18/4/2026).

Đây là dịp để tôn vinh những đóng góp to lớn của các thế hệ cán bộ, chiến sĩ Tham mưu CAND trong sự nghiệp bảo vệ an ninh quốc gia và giữ gìn trật tự an toàn xã hội. ⭐`,

      'đóng góp': `🎖️ **Những đóng góp nổi bật của lực lượng Tham mưu CAND**

**Trong kháng chiến:**
- Tham mưu xây dựng lực lượng Công an cách mạng
- Phối hợp tác chiến, bảo vệ an ninh vùng giải phóng
- Đấu tranh chống gián điệp, biệt kích

**Trong xây dựng và bảo vệ Tổ quốc:**
- Xây dựng chiến lược bảo vệ an ninh quốc gia
- Tổng hợp, phân tích tình hình an ninh
- Hoàn thiện hệ thống pháp luật về an ninh trật tự

Lực lượng đã được tặng thưởng nhiều Huân chương, danh hiệu cao quý. 🇻🇳`,

      'default': `Xin chào! Tôi là trợ lý AI của cuộc thi **Tìm hiểu 80 năm Ngày truyền thống lực lượng Tham mưu Công an nhân dân**.

Tôi có thể giúp bạn tìm hiểu về:
- 🎖️ Lịch sử hình thành và phát triển
- ⭐ Ngày truyền thống 18/4
- 📜 Những đóng góp và thành tựu
- 🇻🇳 Truyền thống vẻ vang

Hãy đặt câu hỏi để khám phá thêm nhé!`
    };

    // Simple keyword matching for fallback
    const messageLower = message?.toLowerCase() || '';
    let fallbackResponse = fallbackResponses['default'];
    
    if (messageLower.includes('lịch sử') || messageLower.includes('hình thành') || messageLower.includes('thành lập')) {
      fallbackResponse = fallbackResponses['lịch sử'];
    } else if (messageLower.includes('ngày truyền thống') || messageLower.includes('18/4')) {
      fallbackResponse = fallbackResponses['ngày truyền thống'];
    } else if (messageLower.includes('đóng góp') || messageLower.includes('thành tựu') || messageLower.includes('nổi bật')) {
      fallbackResponse = fallbackResponses['đóng góp'];
    }

    return NextResponse.json({
      response: fallbackResponse,
      confidence: 0.9,
      sources: [],
      source_references: []
    });
  }
}
