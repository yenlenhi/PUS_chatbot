"""
API routes cho trang 80 năm lực lượng Tham mưu CAND
Sử dụng prompt riêng, không dùng RAG từ database
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import time
import requests
import json
from config.settings import GEMINI_API_KEY, GEMINI_API_URL, GEMINI_MAX_OUTPUT_TOKENS
from src.utils.logger import log

# Create router
router = APIRouter(prefix="/thammuu", tags=["Tham Muu CAND"])


class ThamMuuChatRequest(BaseModel):
    """Request model for ThamMuu chat"""

    message: str
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None


class ThamMuuChatResponse(BaseModel):
    """Response model for ThamMuu chat"""

    answer: str
    conversation_id: str
    processing_time: float


# Default system prompt cho trang Tham mưu CAND
DEFAULT_THAMMUU_SYSTEM_PROMPT = """Bạn là **Trợ lý AI của cuộc thi Tìm hiểu 80 năm Ngày truyền thống lực lượng Tham mưu Công an nhân dân (18/4/1946 – 18/4/2026)**.

**VAI TRÒ CỦA BẠN:**
Bạn là một trợ lý AI thông minh, chuyên cung cấp thông tin về lịch sử, truyền thống, và những đóng góp của lực lượng Tham mưu Công an nhân dân (CAND) Việt Nam trong 80 năm qua.

**KIẾN THỨC CỐT LÕI:**

### 1. Lịch sử hình thành
- **18/4/1946**: Ban Tham mưu thuộc Nha Công an Trung ương được thành lập theo Sắc lệnh số 23/SL của Chủ tịch Hồ Chí Minh, đánh dấu sự ra đời của lực lượng Tham mưu Công an nhân dân.
- Tiền thân là Phòng Chính trị thuộc Sở Cảnh sát Bắc Bộ (thành lập tháng 8/1945)
- Qua các thời kỳ, lực lượng đã phát triển thành Cục Tham mưu, Văn phòng Bộ Công an

### 2. Các giai đoạn phát triển
- **1946-1954**: Thời kỳ kháng chiến chống thực dân Pháp
- **1954-1975**: Thời kỳ kháng chiến chống đế quốc Mỹ
- **1975-1986**: Thời kỳ khôi phục và xây dựng đất nước
- **1986-nay**: Thời kỳ đổi mới và hội nhập quốc tế

### 3. Chức năng, nhiệm vụ
- Tham mưu cho Đảng ủy Công an Trung ương và lãnh đạo Bộ Công an
- Xây dựng chiến lược, kế hoạch công tác công an
- Tổng hợp, phân tích, đánh giá tình hình an ninh quốc gia
- Theo dõi, đôn đốc việc thực hiện các nghị quyết, chương trình công tác
- Công tác pháp chế, cải cách hành chính, thông tin tuyên truyền

### 4. Thành tích nổi bật
- Được tặng thưởng Huân chương Hồ Chí Minh
- Được tặng thưởng nhiều Huân chương Quân công, Huân chương Chiến công
- Danh hiệu Anh hùng Lực lượng vũ trang nhân dân
- Nhiều tập thể và cá nhân được phong tặng danh hiệu Anh hùng

### 5. Truyền thống vẻ vang
- "Vì nước quên thân, vì dân phục vụ"
- Tinh thần đoàn kết, kỷ luật nghiêm minh
- Không ngừng học tập, nâng cao trình độ chuyên môn
- Gắn bó mật thiết với nhân dân

### 6. Về cuộc thi
- **Tên cuộc thi**: Tìm hiểu 80 năm Ngày truyền thống lực lượng Tham mưu Công an nhân dân
- **Thời gian**: Kỷ niệm 80 năm (18/4/1946 – 18/4/2026)
- **Mục đích**: Tuyên truyền, giáo dục truyền thống vẻ vang của lực lượng
- **Đối tượng**: Cán bộ, chiến sĩ Công an và nhân dân

**PHONG CÁCH TRẢ LỜI:**
- Thân thiện, nhiệt tình nhưng vẫn trang trọng
- Sử dụng ngôn ngữ dễ hiểu, phổ thông
- Trình bày có cấu trúc rõ ràng (gạch đầu dòng, tiêu đề)
- Sử dụng emoji phù hợp (🎖️, 🇻🇳, ⭐, 📜, 🏆) để tạo sinh động
- Khơi gợi lòng tự hào về truyền thống lực lượng Tham mưu CAND
- Kết thúc câu trả lời bằng việc khuyến khích tìm hiểu thêm hoặc tham gia cuộc thi

**QUY TẮC QUAN TRỌNG:**
1. CHỈ trả lời các câu hỏi liên quan đến lực lượng Tham mưu CAND, lịch sử Công an nhân dân, hoặc cuộc thi.
2. Nếu câu hỏi ngoài phạm vi, lịch sự từ chối và hướng dẫn người dùng đặt câu hỏi phù hợp.
3. Luôn thể hiện sự tôn trọng với lịch sử và truyền thống của lực lượng.
4. KHÔNG bịa đặt thông tin. Nếu không chắc chắn, hãy nói rõ và khuyến khích tìm hiểu từ nguồn chính thống.
5. **TUYỆT ĐỐI KHÔNG** tiết lộ bạn là Gemini, ChatGPT, hay bất kỳ mô hình AI cụ thể nào. KHÔNG nói bạn được tạo bởi Google, OpenAI hay bất kỳ công ty nào. Khi bị hỏi "bạn là ai?", chỉ trả lời rằng bạn là Trợ lý AI của cuộc thi Tìm hiểu 80 năm lực lượng Tham mưu CAND.
"""


def generate_thammuu_response(
    prompt: str, system_prompt: str, temperature: float = 0.7
) -> str | None:
    """
    Generate response using Gemini API with custom system prompt for ThamMuu page.
    KHÔNG sử dụng RAG.
    """
    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY is not set in the environment variables.")
        return None

    headers = {
        "Content-Type": "application/json",
    }

    # Combine system prompt and user prompt
    full_prompt = f"{system_prompt}\n\n---\n\n**Câu hỏi của người dùng:** {prompt}"

    data = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": GEMINI_MAX_OUTPUT_TOKENS,
            "topP": 0.95,
            "topK": 40,
        },
    }

    try:
        log.info(f"[ThamMuu] Sending request to Gemini API: {prompt[:100]}...")

        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            data=json.dumps(data),
            timeout=180,
        )

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and result["candidates"]:
                candidate = result["candidates"][0]
                content = candidate.get("content", {})
                finish_reason = candidate.get("finishReason", "")

                if finish_reason == "MAX_TOKENS":
                    log.warning("[ThamMuu] Gemini hit MAX_TOKENS limit")
                    if "parts" in content and content["parts"]:
                        partial_text = content["parts"][0].get("text", "").strip()
                        if partial_text:
                            return (
                                partial_text
                                + "\n\n[Câu trả lời đã bị cắt ngắn. Vui lòng hỏi câu hỏi ngắn gọn hơn.]"
                            )

                if "parts" in content and content["parts"]:
                    generated_text = content["parts"][0].get("text", "").strip()
                    if generated_text:
                        log.info(
                            "[ThamMuu] Successfully received response from Gemini."
                        )
                        return generated_text

            log.warning(f"[ThamMuu] Gemini response format unexpected: {result}")
            return None
        else:
            log.error(
                f"[ThamMuu] Gemini API error: {response.status_code} - {response.text}"
            )
            return None

    except requests.exceptions.RequestException as e:
        log.error(f"[ThamMuu] Error calling Gemini API: {e}")
        return None
    except Exception as e:
        log.error(f"[ThamMuu] Unexpected error: {e}")
        return None


@router.post("/chat", response_model=ThamMuuChatResponse)
async def thammuu_chat_endpoint(request: ThamMuuChatRequest):
    """
    Chat endpoint cho trang 80 năm lực lượng Tham mưu CAND.
    Sử dụng prompt riêng, KHÔNG dùng RAG từ database.
    """
    start_time = time.time()

    try:
        log.info(f"[ThamMuu] Received chat request: {request.message[:50]}...")

        # Use custom system prompt if provided, otherwise use default
        system_prompt = request.system_prompt or DEFAULT_THAMMUU_SYSTEM_PROMPT

        # Generate response using Gemini (no RAG)
        answer = generate_thammuu_response(
            prompt=request.message, system_prompt=system_prompt, temperature=0.7
        )

        if not answer:
            answer = """🎖️ Xin lỗi, tôi không thể xử lý câu hỏi của bạn lúc này.

Vui lòng thử lại sau hoặc đặt câu hỏi khác về:
- Lịch sử lực lượng Tham mưu CAND
- Ngày truyền thống 18/4
- Những đóng góp và thành tựu
- Thông tin về cuộc thi

🇻🇳 Cảm ơn bạn đã quan tâm đến cuộc thi Tìm hiểu 80 năm Ngày truyền thống lực lượng Tham mưu Công an nhân dân!"""

        processing_time = round(time.time() - start_time, 2)

        return ThamMuuChatResponse(
            answer=answer,
            conversation_id=request.conversation_id or "thammuu-default",
            processing_time=processing_time,
        )

    except Exception as e:
        log.error(f"[ThamMuu] Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def thammuu_health_check():
    """Health check endpoint for ThamMuu API"""
    return {
        "status": "healthy",
        "service": "ThamMuu CAND 80 Years",
        "description": "API cho trang Tìm hiểu 80 năm lực lượng Tham mưu CAND",
    }
