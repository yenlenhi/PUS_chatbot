"""
Fixed admission FAQ answers for the 2026 intake.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Optional


def _normalize(text: Optional[str]) -> str:
    if not text:
        return ""

    normalized = unicodedata.normalize("NFD", text)
    normalized = normalized.replace("đ", "d").replace("Đ", "D")
    normalized = "".join(
        ch for ch in normalized if unicodedata.category(ch) != "Mn"
    ).lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _build_fixed_faq_catalog() -> list[Dict[str, Any]]:
    return [
        {
            "key": "quota_t04",
            "question": "Chỉ tiêu tuyển sinh vào Trường Đại học An Ninh Nhân Dân?",
            "match": lambda q: "chi tieu" in q
            and ("an ninh nhan dan" in q or "t04" in q),
            "sources": [
                "Thông báo chỉ tiêu tuyển sinh tuyển mới đào tạo trình độ đại học năm 2026",
                "Bảng chỉ tiêu tuyển sinh CAND năm 2026",
            ],
            "answer": """### Chỉ tiêu tuyển sinh năm 2026 vào Trường Đại học An ninh nhân dân (T04)

| Trường/nhóm ngành | Ký hiệu trường | Mã ngành | Địa bàn tuyển sinh | Tổng chỉ tiêu | Phương thức 1 | Phương thức 2 |
| --- | --- | --- | --- | ---: | --- | --- |
| Trường Đại học An ninh nhân dân (T04) - Nhóm ngành nghiệp vụ An ninh | ANS | 7860100 | Phía Nam | 100 | Nam 45, Nữ 5 | Nam 45, Nữ 5 |

### Tóm tắt nhanh

| Nội dung | Giá trị |
| --- | --- |
| Tổng chỉ tiêu | 100 |
| Nhóm ngành | Nghiệp vụ An ninh |
| Mã ngành | 7860100 |
| Ký hiệu trường | ANS |
| Địa bàn tuyển sinh | Phía Nam |

Ghi chú: Bảng bạn cung cấp thể hiện chỉ tiêu của Trường Đại học An ninh nhân dân (T04) cho nhóm ngành nghiệp vụ An ninh, chia theo Phương thức 1 và Phương thức 2.""",
        },
        {
            "key": "exam_codes",
            "question": "Ký hiệu mã bài thi đánh giá của Bộ Công an?",
            "match": lambda q: (
                "ma bai thi" in q
                or "ky hieu ma bai thi" in q
                or "ma bai danh gia" in q
            )
            and ("bo cong an" in q or "danh gia" in q),
            "sources": [
                "Tổ chức Bài thi đánh giá của Bộ Công an năm 2026",
            ],
            "answer": """### Ký hiệu mã bài thi đánh giá của Bộ Công an năm 2026

| Mã bài thi | Phần tự luận bắt buộc | Trắc nghiệm bắt buộc | Trắc nghiệm tự chọn |
| --- | --- | --- | --- |
| CA1 | Ngữ văn | Toán, Lịch sử, Ngôn ngữ Anh | Vật lí |
| CA2 | Ngữ văn | Toán, Lịch sử, Ngôn ngữ Anh | Hóa học |
| CA3 | Ngữ văn | Toán, Lịch sử, Ngôn ngữ Anh | Sinh học |
| CA4 | Ngữ văn | Toán, Lịch sử, Ngôn ngữ Anh | Địa lí |

### Thông tin tổ chức bài thi

| Nội dung | Giá trị |
| --- | --- |
| Số mã bài thi | 4 mã |
| Thời gian làm bài | 180 phút |
| Ngày thi | 21/6/2026 |
| Hình thức thi | Thi viết |

Thí sinh chọn 1 trong 4 mã bài thi để đăng ký dự thi.""",
        },
        {
            "key": "exam_structure",
            "question": "Câu trúc đề thi tuyển sinh đại học chính quy tuyển mới?",
            "match": lambda q: (
                "cau truc de thi" in q
                or "cau truc bai thi" in q
                or "de thi tuyen sinh" in q
            )
            and ("dai hoc chinh quy" in q or "tuyen moi" in q or "tuyen sinh" in q),
            "sources": [
                "Cấu trúc đề thi tuyển sinh đại học chính quy tuyển mới năm 2026",
            ],
            "answer": """### Cấu trúc đề thi tuyển sinh đại học chính quy tuyển mới

| Nội dung | Thông tin |
| --- | --- |
| Số phần thi | 3 phần |
| Hình thức | Thi viết |
| Thời gian làm bài | 180 phút |
| Tổng điểm bài thi | 100 điểm |
| Điểm phần tự luận | 25 điểm |
| Điểm phần trắc nghiệm | 75 điểm |

### Cấu trúc chi tiết

| Phần thi | Nội dung | Số câu | Điểm tối đa |
| --- | --- | ---: | ---: |
| Tự luận bắt buộc | 1 câu nghị luận xã hội môn Ngữ văn | 1 | 25 |
| Trắc nghiệm bắt buộc - Toán | Câu hỏi trắc nghiệm | 35 | 35 |
| Trắc nghiệm bắt buộc - Lịch sử | Câu hỏi trắc nghiệm | 10 | 10 |
| Trắc nghiệm bắt buộc - Ngoại ngữ (Tiếng Anh) | Câu hỏi trắc nghiệm | 20 | 15 |
| Trắc nghiệm tự chọn | Chọn 1 môn: Vật lí, Hóa học, Sinh học hoặc Địa lí | 15 | 15 |

### Phân bố kiến thức và độ khó

| Tiêu chí | Tỷ lệ |
| --- | --- |
| Kiến thức lớp 12 | 70% |
| Kiến thức lớp 10, 11 | 30% |
| Mức độ biết, thông hiểu | 30% số câu |
| Mức độ vận dụng | 50% số câu |
| Mức độ vận dụng cao | 20% số câu |

Ghi chú: Môn tự chọn tương ứng theo mã bài thi là Vật lí (CA1), Hóa học (CA2), Sinh học (CA3), Địa lí (CA4).""",
        },
        {
            "key": "admission_methods",
            "question": "Các phương thức tuyển sinh?",
            "match": lambda q: "phuong thuc tuyen sinh" in q
            or ("cac phuong thuc" in q and "tuyen sinh" in q),
            "sources": [
                "Phương thức tuyển sinh đại học chính quy tuyển mới năm 2026",
            ],
            "answer": """### Các phương thức tuyển sinh

| Phương thức | Nội dung |
| --- | --- |
| Phương thức 1 | Tuyển thẳng theo quy chế tuyển sinh hiện hành của Bộ Giáo dục và Đào tạo và quy định của Bộ Công an |
| Phương thức 2 | Xét tuyển kết hợp chứng chỉ ngoại ngữ quốc tế với kết quả Bài thi đánh giá của Bộ Công an |
| Phương thức 3 | Xét tuyển kết hợp kết quả thi tốt nghiệp trung học phổ thông với kết quả Bài thi đánh giá của Bộ Công an |

### Lưu ý

| Nội dung | Ghi chú |
| --- | --- |
| Bài thi sử dụng kết hợp | Bài thi đánh giá của Bộ Công an |
| Đối với phương thức 2 | Cần có chứng chỉ ngoại ngữ quốc tế theo quy định |
| Đối với phương thức 3 | Kết hợp điểm thi tốt nghiệp THPT và bài thi đánh giá của Bộ Công an |

Nếu bạn muốn, tôi có thể tách tiếp từng phương thức thành điều kiện áp dụng, hồ sơ và cách tính điểm.""",
        },
    ]


FIXED_ADMISSION_FAQS = _build_fixed_faq_catalog()


def get_fixed_admission_faq(query: Optional[str]) -> Optional[Dict[str, Any]]:
    normalized_query = _normalize(query)
    if not normalized_query:
        return None

    for item in FIXED_ADMISSION_FAQS:
        if item["match"](normalized_query):
            return {
                "question": item["question"],
                "answer": item["answer"],
                "sources": item["sources"],
                "confidence": 0.98,
            }

    return None
