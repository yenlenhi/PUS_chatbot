"""
API routes cho trang 80 năm lực lượng Tham mưu CAND.
Sử dụng prompt riêng, không dùng RAG từ database.
"""

import time
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.gemini_service import generate_response
from src.utils.logger import log

router = APIRouter(prefix="/thammuu", tags=["Tham Muu CAND"])


class ThamMuuChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None


class ThamMuuChatResponse(BaseModel):
    answer: str
    conversation_id: str
    processing_time: float


DEFAULT_THAMMUU_SYSTEM_PROMPT = """Bạn là Trợ lý AI của cuộc thi Tìm hiểu 80 năm Ngày truyền thống lực lượng Tham mưu Công an nhân dân (18/4/1946 - 18/4/2026).

Vai trò của bạn:
- Cung cấp thông tin về lịch sử, truyền thống và đóng góp của lực lượng Tham mưu CAND.
- Hỗ trợ người dùng tìm hiểu về cuộc thi kỷ niệm 80 năm.

Kiến thức cốt lõi:
- 18/4/1946 là mốc thành lập Ban Tham mưu thuộc Nha Công an Trung ương.
- Tiền thân là Phòng Chính trị thuộc Sở Cảnh sát Bắc Bộ, thành lập tháng 8/1945.
- Các giai đoạn phát triển chính: 1946-1954, 1954-1975, 1975-1986, 1986-đến nay.
- Chức năng: tham mưu cho Đảng ủy Công an Trung ương và lãnh đạo Bộ Công an, tổng hợp và đánh giá tình hình, theo dõi và đôn đốc thực hiện các nghị quyết, công tác pháp chế và cải cách hành chính.
- Thành tích: nhiều huân chương, danh hiệu Anh hùng Lực lượng vũ trang nhân dân, đóng góp quan trọng cho sự nghiệp bảo vệ an ninh quốc gia.
- Truyền thống: Vì nước quên thân, vì dân phục vụ; đoàn kết; kỷ luật; gắn bó với nhân dân.
- Về cuộc thi: chủ đề Tìm hiểu 80 năm Ngày truyền thống lực lượng Tham mưu Công an nhân dân, phục vụ công tác tuyên truyền, giáo dục truyền thống.

Quy tắc:
- Chỉ trả lời các câu hỏi liên quan đến lực lượng Tham mưu CAND, lịch sử CAND hoặc cuộc thi.
- Nếu câu hỏi ngoài phạm vi, lịch sự từ chối và hướng người dùng đặt câu hỏi phù hợp.
- Không bịa đặt thông tin. Nếu không chắc chắn, nói rõ giới hạn và khuyến khích tìm nguồn chính thống.
- Tuyệt đối không tiết lộ bạn là Gemini, ChatGPT hay bất kỳ mô hình AI cụ thể nào.

Phong cách trả lời:
- Thân thiện, trang trọng, rõ ràng, dễ đọc.
- Ưu tiên câu trả lời có cấu trúc và dễ ghi nhớ.
"""


def generate_thammuu_response(
    prompt: str, system_prompt: str, temperature: float = 0.7
) -> str | None:
    full_prompt = f"{system_prompt}\n\n---\n\nCâu hỏi của người dùng: {prompt}"
    return generate_response(prompt=full_prompt, temperature=temperature)


@router.post("/chat", response_model=ThamMuuChatResponse)
async def thammuu_chat_endpoint(request: ThamMuuChatRequest):
    start_time = time.time()

    try:
        log.info(f"[ThamMuu] Received chat request: {request.message[:50]}...")
        system_prompt = request.system_prompt or DEFAULT_THAMMUU_SYSTEM_PROMPT
        answer = generate_thammuu_response(
            prompt=request.message,
            system_prompt=system_prompt,
            temperature=0.7,
        )

        if not answer:
            answer = (
                "Xin lỗi, tôi không thể xử lý câu hỏi của bạn lúc này.\n\n"
                "Vui lòng thử lại sau hoặc đặt câu hỏi liên quan đến lịch sử, truyền thống, "
                "thành tích và cuộc thi Tìm hiểu 80 năm lực lượng Tham mưu CAND."
            )

        processing_time = round(time.time() - start_time, 2)
        return ThamMuuChatResponse(
            answer=answer,
            conversation_id=request.conversation_id or "thammuu-default",
            processing_time=processing_time,
        )
    except Exception as exc:
        log.error(f"[ThamMuu] Error in chat endpoint: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/health")
async def thammuu_health_check():
    return {
        "status": "healthy",
        "service": "ThamMuu CAND 80 Years",
        "description": "API cho trang Tìm hiểu 80 năm lực lượng Tham mưu CAND",
    }
