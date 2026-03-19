"""
Admission-domain scope classification and policy responses.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from typing import Literal, Sequence

ScopeType = Literal["admission", "out_of_scope", "ambiguous"]
PolicyType = Literal["out_of_scope", "ambiguous", "insufficient_evidence"]


@dataclass(frozen=True)
class ScopeDecision:
    scope: ScopeType
    reason: str
    matched_keywords: tuple[str, ...] = ()


class AdmissionScopeService:
    """Simple rule-based gate for an admission-only chatbot."""

    _IN_SCOPE_KEYWORDS: Sequence[str] = (
        "tuyen sinh",
        "xet tuyen",
        "phuong thuc",
        "chi tieu",
        "diem chuan",
        "diem xet",
        "diem trung tuyen",
        "nganh",
        "chuyen nganh",
        "to hop",
        "ho so",
        "giay to",
        "so tuyen",
        "nhap hoc",
        "dang ky",
        "nguyen vong",
        "doi tuong tuyen sinh",
        "vung tuyen sinh",
        "hoc phi",
        "le phi",
        "thoi gian tuyen sinh",
        "lich tuyen sinh",
        "moc thoi gian",
        "thi sinh",
        "tieu chuan suc khoe",
        "tieu chuan chinh tri",
        "do tuoi",
        "chieu cao",
        "can nang",
        "uu tien",
        "tuyen thang",
        "ma truong",
        "ma nganh",
        "ma xet tuyen",
        "thong bao tuyen sinh",
        "admission",
        "enrollment",
        "application",
        "eligibility",
        "quota",
        "entry requirements",
        "deadline",
        "tuition",
        "major",
        "majors",
    )

    _OUT_OF_SCOPE_KEYWORDS: Sequence[str] = (
        "lap trinh",
        "python",
        "javascript",
        "code",
        "debug",
        "github",
        "chatgpt",
        "gemini",
        "claude",
        "thoi tiet",
        "bong da",
        "the thao",
        "football",
        "crypto",
        "bitcoin",
        "chung khoan",
        "gia vang",
        "gia usd",
        "phim",
        "am nhac",
        "bai hat",
        "chinh tri",
        "tong thong",
        "thu tuong",
        "tin tuc",
        "suc khoe",
        "benh",
        "thuoc",
        "tinh cam",
        "tu vi",
        "nau an",
        "recipe",
        "du lich",
        "travel",
        "game",
    )

    _GREETING_KEYWORDS: Sequence[str] = (
        "xin chao",
        "chao",
        "hello",
        "hi",
        "alo",
    )

    _AMBIGUOUS_PATTERNS: Sequence[str] = (
        r"^(con|the con|vay thi|the thi|ngoai ra|the nao)$",
        r"^(cai do|noi ro hon|giai thich them)$",
    )

    def classify(self, query: str | None, has_images: bool = False) -> ScopeDecision:
        normalized = self._normalize(query)
        if not normalized:
            reason = "image_only_without_admission_question" if has_images else "empty_query"
            return ScopeDecision(scope="ambiguous", reason=reason)

        token_count = len(normalized.split())
        if any(normalized == greeting or normalized.startswith(f"{greeting} ") for greeting in self._GREETING_KEYWORDS):
            return ScopeDecision(scope="ambiguous", reason="greeting_only")

        in_scope_matches = self._matched_keywords(normalized, self._IN_SCOPE_KEYWORDS)
        if in_scope_matches:
            return ScopeDecision(
                scope="admission",
                reason="matched_admission_keyword",
                matched_keywords=tuple(in_scope_matches),
            )

        out_of_scope_matches = self._matched_keywords(normalized, self._OUT_OF_SCOPE_KEYWORDS)
        if out_of_scope_matches:
            return ScopeDecision(
                scope="out_of_scope",
                reason="matched_non_admission_keyword",
                matched_keywords=tuple(out_of_scope_matches),
            )

        if token_count <= 2 or any(re.match(pattern, normalized) for pattern in self._AMBIGUOUS_PATTERNS):
            return ScopeDecision(scope="ambiguous", reason="query_too_short_or_context_dependent")

        if has_images and token_count < 4:
            return ScopeDecision(scope="ambiguous", reason="image_query_needs_admission_context")

        return ScopeDecision(scope="out_of_scope", reason="no_admission_signal_detected")

    def build_policy_answer(self, policy: PolicyType, language: str = "vi") -> str:
        is_english = language == "en"
        messages = {
            "out_of_scope": {
                "vi": (
                    "Tôi chỉ hỗ trợ thông tin tuyển sinh chính thức của Trường Đại học An ninh Nhân dân. "
                    "Nội dung bạn hỏi hiện nằm ngoài phạm vi hỗ trợ. "
                    "Bạn có thể hỏi về điều kiện tuyển sinh, phương thức xét tuyển, chỉ tiêu, hồ sơ, "
                    "mốc thời gian, đối tượng tuyển sinh hoặc thủ tục nhập học."
                ),
                "en": (
                    "I only support official admission information for the People's Security University. "
                    "Your question is outside the current support scope. "
                    "You can ask about eligibility, admission methods, quotas, required documents, "
                    "timelines, applicant categories, or enrollment procedures."
                ),
            },
            "ambiguous": {
                "vi": (
                    "Tôi chỉ hỗ trợ nội dung tuyển sinh của Trường Đại học An ninh Nhân dân. "
                    "Bạn vui lòng nêu rõ câu hỏi tuyển sinh cần tra cứu, ví dụ: điều kiện tuyển sinh, "
                    "phương thức xét tuyển, chỉ tiêu, hồ sơ hoặc lịch tuyển sinh."
                ),
                "en": (
                    "I only support admission topics for the People's Security University. "
                    "Please restate your question as a specific admission request, for example: eligibility, "
                    "admission method, quota, application documents, or admission timeline."
                ),
            },
            "insufficient_evidence": {
                "vi": (
                    "Tôi chưa có đủ căn cứ từ tài liệu tuyển sinh chính thức để khẳng định thông tin này. "
                    "Bạn vui lòng xem thông báo tuyển sinh mới nhất hoặc liên hệ bộ phận tuyển sinh "
                    "của Trường Đại học An ninh Nhân dân để được xác nhận."
                ),
                "en": (
                    "I do not have enough support from the official admission documents to confirm this information. "
                    "Please check the latest admission notice or contact the admission office of the "
                    "People's Security University for confirmation."
                ),
            },
        }
        return messages[policy]["en" if is_english else "vi"]

    def _matched_keywords(self, normalized_query: str, keywords: Sequence[str]) -> list[str]:
        return [keyword for keyword in keywords if keyword in normalized_query]

    def _normalize(self, text: str | None) -> str:
        if not text:
            return ""
        stripped = unicodedata.normalize("NFD", text)
        stripped = "".join(ch for ch in stripped if unicodedata.category(ch) != "Mn")
        stripped = stripped.lower()
        stripped = re.sub(r"[^a-z0-9\s]", " ", stripped)
        return re.sub(r"\s+", " ", stripped).strip()
