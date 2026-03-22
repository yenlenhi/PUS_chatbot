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


_PRIMARY_SCHOOL_TERMS = (
    "an ninh nhan dan",
    "truong dai hoc an ninh nhan dan",
    "t04",
    "ans",
)
_OTHER_SCHOOL_TERMS = (
    "hoc vien an ninh nhan dan",
    "hoc vien canh sat nhan dan",
    "truong dai hoc canh sat nhan dan",
    "truong dai hoc phong chay chua chay",
    "truong dai hoc ky thuat hau can cand",
    "t01",
    "t02",
    "t03",
    "t05",
    "t06",
    "csh",
    "tdhc",
    "pccc",
)
_SYSTEM_WIDE_TERMS = (
    "cac truong cand",
    "toan khoi cand",
    "toan nganh cong an",
    "bo cong an",
)


def _is_primary_school_quota_query(normalized_query: str) -> bool:
    if "chi tieu" not in normalized_query:
        return False

    if any(term in normalized_query for term in _SYSTEM_WIDE_TERMS):
        return False

    if any(term in normalized_query for term in _OTHER_SCHOOL_TERMS):
        return False

    if any(term in normalized_query for term in _PRIMARY_SCHOOL_TERMS):
        return True

    return any(
        term in normalized_query for term in ("to hop", "xet tuyen", "tuyen sinh")
    )


def _build_fixed_faq_catalog() -> list[Dict[str, Any]]:
    return [
        {
            "key": "quota_t04",
            "question": "Chỉ tiêu tuyển sinh vào Trường Đại học An Ninh Nhân Dân?",
            "match": _is_primary_school_quota_query,
            "sources": [
                "Thông báo chỉ tiêu tuyển sinh tuyển mới đào tạo trình độ đại học năm 2026",
                "Bảng chỉ tiêu tuyển sinh CAND năm 2026",
            ],
            "follow_up_questions": [
                "Điều kiện sơ tuyển vào Trường Đại học An Ninh Nhân Dân là gì?",
                "Hồ sơ sơ tuyển cần chuẩn bị những gì?",
                "Tổ hợp xét tuyển và mã bài thi đánh giá áp dụng cho T04 là gì?",
            ],
            "answer": """### Chỉ tiêu tuyển sinh năm 2026 vào Trường Đại học An ninh nhân dân (T04)

Thông tin dưới đây tóm lược chỉ tiêu tuyển sinh năm 2026 của Trường Đại học An ninh nhân dân (T04), ký hiệu trường ANS, đối với nhóm ngành nghiệp vụ An ninh tại địa bàn phía Nam:

| Trường/nhóm ngành | Ký hiệu trường | Mã ngành | Địa bàn tuyển sinh | Tổng chỉ tiêu | PT1 Nam | PT1 Nữ | PT2, PT3 Nam | PT2, PT3 Nữ | Tổ hợp xét tuyển | Mã bài thi đánh giá |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Trường Đại học An ninh nhân dân (T04) - Nhóm ngành nghiệp vụ An ninh | ANS | 7860100 | Phía Nam | 220 | 10 | 1 | 188 | 21 | A00, A01, C03, D01, X02, X03, X04 | CA1, CA2, CA3, CA4 |

### Tóm tắt nhanh

| Nội dung | Giá trị |
| --- | --- |
| Tổng chỉ tiêu | 220 |
| Nhóm ngành | Nghiệp vụ An ninh |
| Mã ngành | 7860100 |
| Ký hiệu trường | ANS |
| Địa bàn tuyển sinh | Phía Nam |
| Tổ hợp xét tuyển | A00, A01, C03, D01, X02, X03, X04 |
| Mã bài thi đánh giá | CA1, CA2, CA3, CA4 |

Tóm lại, tổng chỉ tiêu của T04 là `220`, đồng thời áp dụng các tổ hợp xét tuyển và mã bài thi đánh giá như trong bảng trên để bạn tiện đối chiếu.""",
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
            "follow_up_questions": [
                "Nên chọn mã CA1, CA2, CA3 hay CA4 như thế nào?",
                "Ngày thi và thời gian làm bài cụ thể ra sao?",
                "Cách đăng ký mã bài thi đánh giá của Bộ Công an như thế nào?",
            ],
            "answer": """### Ký hiệu mã bài thi đánh giá của Bộ Công an năm 2026

Bài thi đánh giá của Bộ Công an năm 2026 gồm 4 mã bài thi. Mỗi thí sinh chọn 1 mã phù hợp với môn tự chọn của mình, còn phần tự luận và phần trắc nghiệm bắt buộc là khung chung. Bảng dưới đây giúp bạn nhìn ra ngay sự khác nhau giữa các mã:

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

Điểm khác nhau chính giữa các mã CA1 đến CA4 nằm ở môn trắc nghiệm tự chọn, nên bạn nên chọn mã phù hợp với thế mạnh và tổ hợp dự định đăng ký.""",
        },
        {
            "key": "exam_structure",
            "question": "Cấu trúc đề thi tuyển sinh đại học chính quy tuyển mới?",
            "match": lambda q: (
                "cau truc de thi" in q
                or "cau truc bai thi" in q
                or "de thi tuyen sinh" in q
            )
            and ("dai hoc chinh quy" in q or "tuyen moi" in q or "tuyen sinh" in q),
            "sources": [
                "Cấu trúc đề thi tuyển sinh đại học chính quy tuyển mới năm 2026",
            ],
            "follow_up_questions": [
                "Bài thi có bao nhiêu câu và bao nhiêu điểm?",
                "Phần tự chọn của từng mã CA khác nhau thế nào?",
                "Tỷ lệ kiến thức lớp 10, 11, 12 được phân bố ra sao?",
            ],
            "answer": """### Cấu trúc đề thi tuyển sinh đại học chính quy tuyển mới

Nếu bạn muốn hình dung nhanh đề thi năm 2026 gồm những phần nào, bảng dưới đây sẽ cho bạn cái nhìn tổng quát trước khi đi vào từng thành phần chi tiết. Bài thi được thiết kế theo 3 phần, làm trong 180 phút và chấm trên thang điểm 100.

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

Môn trắc nghiệm tự chọn sẽ thay đổi theo mã bài thi: Vật lí (CA1), Hóa học (CA2), Sinh học (CA3) hoặc Địa lí (CA4).""",
        },
        {
            "key": "admission_methods",
            "question": "Các phương thức tuyển sinh?",
            "match": lambda q: "phuong thuc tuyen sinh" in q
            or ("cac phuong thuc" in q and "tuyen sinh" in q),
            "sources": [
                "Phương thức tuyển sinh đại học chính quy tuyển mới năm 2026",
            ],
            "follow_up_questions": [
                "Điều kiện áp dụng từng phương thức tuyển sinh là gì?",
                "Phương thức 2 cần những chứng chỉ ngoại ngữ nào?",
                "Phương thức 3 tính điểm xét tuyển ra sao?",
            ],
            "answer": """### Các phương thức tuyển sinh

Trong kỳ tuyển sinh đại học chính quy tuyển mới năm 2026, khối trường Công an nhân dân áp dụng 3 phương thức tuyển sinh chính. Mỗi phương thức có điều kiện và cách sử dụng kết quả khác nhau, nên bạn nên nhìn tổng thể trước rồi mới đi sâu vào phương thức phù hợp với hồ sơ của mình.

| Phương thức | Nội dung |
| --- | --- |
| Phương thức 1 | Tuyển thẳng theo quy chế tuyển sinh hiện hành của Bộ Giáo dục và Đào tạo và quy định của Bộ Công an |
| Phương thức 2 | Xét tuyển kết hợp chứng chỉ ngoại ngữ quốc tế với kết quả Bài thi đánh giá của Bộ Công an |
| Phương thức 3 | Xét tuyển kết hợp kết quả thi tốt nghiệp trung học phổ thông với kết quả Bài thi đánh giá của Bộ Công an |

### Lưu ý

| Nội dung | Ghi chú |
| --- | --- |
| Bài thi dùng để kết hợp | Bài thi đánh giá của Bộ Công an |
| Đối với phương thức 2 | Cần có chứng chỉ ngoại ngữ quốc tế theo quy định |
| Đối với phương thức 3 | Kết hợp điểm thi tốt nghiệp THPT và bài thi đánh giá của Bộ Công an |

Nếu bạn đang cân nhắc lựa chọn phương thức, bước tiếp theo nên là đối chiếu điều kiện áp dụng, hồ sơ cần nộp và cách tính điểm của từng phương thức.""",
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
                "follow_up_questions": item.get("follow_up_questions", []),
                "confidence": 0.98,
            }

    return None
