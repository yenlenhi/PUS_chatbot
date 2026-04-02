import re
import unicodedata
from typing import Iterator, Optional

from config.settings import (
    ENABLE_GEMINI_NORMALIZATION,
    ENABLE_GOOGLE_SEARCH_GROUNDING,
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_TEMPERATURE,
)
from src.services.google_genai_client import (
    build_multimodal_contents,
    build_text_config,
    default_text_model,
    default_vision_model,
    extract_finish_reason,
    extract_text_from_response,
    generate_content_once,
    generate_content_stream_once,
    get_candidate_auth_configs,
    is_max_tokens_finish_reason,
    log_auth_attempt,
    mark_auth_failure,
    mark_auth_success,
)
from src.utils.admission_document_priority import is_personnel_query
from src.utils.logger import log


def _normalize_grounding_query(query: str) -> str:
    normalized = unicodedata.normalize("NFD", query or "")
    normalized = normalized.replace("đ", "d").replace("Đ", "D")
    normalized = "".join(
        ch for ch in normalized if unicodedata.category(ch) != "Mn"
    ).lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _needs_realtime_info(query: str) -> bool:
    if not ENABLE_GOOGLE_SEARCH_GROUNDING:
        return False

    normalized_query = _normalize_grounding_query(query)
    personnel_news_terms = (
        "bo nhiem",
        "mien nhiem",
        "dieu dong",
        "thong bao quyet dinh",
        "quyet dinh moi",
        "tin tuc",
        "su kien",
        "hoi nghi",
        "vua qua",
        "moi nhat",
        "cap nhat moi",
    )

    if is_personnel_query(query) and not any(
        term in normalized_query for term in personnel_news_terms
    ):
        return False

    realtime_keywords = [
        "hiện tại",
        "hien tai",
        "hiện nay",
        "hien nay",
        "bây giờ",
        "bay gio",
        "mới nhất",
        "moi nhat",
        "gần đây",
        "gan day",
        "vừa qua",
        "vua qua",
        "mới đây",
        "moi day",
        "hôm nay",
        "hom nay",
        "tuần này",
        "tuan nay",
        "tháng này",
        "thang nay",
        "năm 2024",
        "nam 2024",
        "năm 2025",
        "nam 2025",
        "năm 2026",
        "nam 2026",
        "2024",
        "2025",
        "2026",
        "hiệu trưởng",
        "hieu truong",
        "phó hiệu trưởng",
        "pho hieu truong",
        "ban giám hiệu",
        "ban giam hieu",
        "giám đốc",
        "giam doc",
        "bí thư",
        "bi thu",
        "bổ nhiệm",
        "bo nhiem",
        "trưởng khoa",
        "truong khoa",
        "phó khoa",
        "pho khoa",
        "phó trưởng khoa",
        "pho truong khoa",
        "trưởng phòng",
        "truong phong",
        "phó phòng",
        "pho phong",
        "phó trưởng phòng",
        "pho truong phong",
        "trưởng bộ môn",
        "truong bo mon",
        "chủ nhiệm khoa",
        "chu nhiem khoa",
        "chủ nhiệm bộ môn",
        "chu nhiem bo mon",
        "lãnh đạo",
        "lanh dao",
        "cán bộ",
        "can bo",
        "giảng viên",
        "giang vien",
        "ai là",
        "ai la",
        "ai đang",
        "ai dang",
        "người đứng đầu",
        "nguoi dung dau",
        "thông báo mới",
        "thong bao moi",
        "tin tức",
        "tin tuc",
        "sự kiện",
        "su kien",
        "khai giảng",
        "khai giang",
        "tốt nghiệp",
        "tot nghiep",
        "lễ",
        "le",
        "hội nghị",
        "hoi nghi",
        "cập nhật",
        "cap nhat",
        "thay đổi mới",
        "thay doi moi",
        "quy định mới",
        "quy dinh moi",
    ]

    query_lower = query.lower()
    return any(keyword in query_lower for keyword in realtime_keywords)


def get_grounding_instruction(query: str, language: str = "vi") -> str:
    if not _needs_realtime_info(query):
        return ""

    if language == "en":
        return (
            "\n\nCRITICAL: This question needs current information. "
            "Prefer Google Search grounding results over older document context.\n"
        )

    return (
        "\n\nQUAN TRỌNG: Câu hỏi này cần thông tin hiện tại. "
        "Hãy ưu tiên kết quả Google Search grounding hơn tài liệu cũ.\n"
    )


def _build_generation_config(
    *,
    temperature: float,
    max_output_tokens: int,
    enable_grounding: bool,
):
    return build_text_config(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        enable_google_search=enable_grounding,
    )


def normalize_question(question: str) -> str:
    if not ENABLE_GEMINI_NORMALIZATION:
        log.info("Gemini normalization is disabled, returning original question")
        return question

    auth_configs = get_candidate_auth_configs()
    if not auth_configs:
        log.warning("No GenAI credentials configured, returning original question")
        return question

    normalization_prompt = f"""
Bạn là một chuyên gia chuẩn hóa câu hỏi cho hệ thống tìm kiếm tài liệu tuyển sinh đại học.

Nhiệm vụ: Chuẩn hóa câu hỏi sau để tối ưu hóa việc tìm kiếm ngữ nghĩa trong cơ sở dữ liệu tài liệu:

Câu hỏi gốc: "{question}"

Hãy:
1. Sửa lỗi chính tả và ngữ pháp
2. Chuẩn hóa thuật ngữ giáo dục
3. Mở rộng từ viết tắt nếu cần
4. Làm rõ nghĩa nếu câu hỏi mơ hồ
5. Giữ nguyên ý nghĩa và ngữ cảnh tuyển sinh

Chỉ trả về câu hỏi đã chuẩn hóa, không giải thích.
""".strip()

    config = build_text_config(temperature=0.3, max_output_tokens=256)

    for index, auth in enumerate(auth_configs, start=1):
        try:
            log_auth_attempt(auth, index, len(auth_configs), "Question normalization")
            response = generate_content_once(
                auth=auth,
                model=default_text_model(),
                contents=normalization_prompt,
                config=config,
            )
            mark_auth_success(auth)
        except Exception as exc:
            mark_auth_failure(auth, exc)
            log.warning(f"Normalization failed on {auth.display_name}: {exc}")
            continue

        finish_reason = extract_finish_reason(response)
        if is_max_tokens_finish_reason(finish_reason):
            log.warning("Normalization hit MAX_TOKENS, using original question")
            return question

        normalized_question = extract_text_from_response(response)
        if normalized_question:
            log.info(
                f"Question normalized with {auth.display_name}: "
                f"'{question[:40]}' -> '{normalized_question[:40]}'"
            )
            return normalized_question

    log.warning("Normalization failed on all configured GenAI credentials")
    return question


def generate_response(
    prompt: str,
    conversation_history: list | None = None,
    temperature: float = 0.7,
    enable_grounding: bool | None = None,
) -> Optional[str]:
    del conversation_history
    auth_configs = get_candidate_auth_configs()
    if not auth_configs:
        log.error("No GenAI credentials are configured.")
        return None

    use_grounding = bool(enable_grounding)
    config = _build_generation_config(
        temperature=temperature if temperature is not None else GEMINI_TEMPERATURE,
        max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
        enable_grounding=use_grounding,
    )

    last_error: Exception | None = None
    for index, auth in enumerate(auth_configs, start=1):
        try:
            log_auth_attempt(auth, index, len(auth_configs), "Generate response")
            response = generate_content_once(
                auth=auth,
                model=default_text_model(),
                contents=prompt,
                config=config,
            )
            mark_auth_success(auth)
        except Exception as exc:
            last_error = exc
            mark_auth_failure(auth, exc)
            log.warning(f"Response generation failed on {auth.display_name}: {exc}")
            continue

        generated_text = extract_text_from_response(response)
        if not generated_text:
            finish_reason = extract_finish_reason(response)
            if is_max_tokens_finish_reason(finish_reason):
                return "[Câu trả lời đã bị cắt ngắn do giới hạn độ dài.]"
            return None

        finish_reason = extract_finish_reason(response)
        if is_max_tokens_finish_reason(finish_reason):
            return generated_text + "\n\n[Câu trả lời đã bị cắt ngắn do giới hạn độ dài.]"
        return generated_text

    log.error(f"All GenAI credentials failed: {last_error}")
    return None


def generate_response_stream(
    prompt: str,
    conversation_history: list | None = None,
    temperature: float = 0.7,
    enable_grounding: bool | None = None,
) -> Iterator[str]:
    del conversation_history
    auth_configs = get_candidate_auth_configs()
    if not auth_configs:
        log.error("No GenAI credentials are configured.")
        yield "Error: API key not configured"
        return

    use_grounding = bool(enable_grounding)
    config = _build_generation_config(
        temperature=temperature if temperature is not None else GEMINI_TEMPERATURE,
        max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
        enable_grounding=use_grounding,
    )

    last_error: Exception | None = None
    for index, auth in enumerate(auth_configs, start=1):
        yielded_any = False
        try:
            log_auth_attempt(auth, index, len(auth_configs), "Stream response")
            for chunk in generate_content_stream_once(
                auth=auth,
                model=default_text_model(),
                contents=prompt,
                config=config,
            ):
                chunk_text = extract_text_from_response(chunk)
                if chunk_text:
                    yielded_any = True
                    yield chunk_text

                finish_reason = extract_finish_reason(chunk)
                if is_max_tokens_finish_reason(finish_reason):
                    yield "\n\n[Câu trả lời đã bị cắt ngắn do giới hạn độ dài.]"
                    mark_auth_success(auth)
                    return

            mark_auth_success(auth)
            return
        except Exception as exc:
            last_error = exc
            if yielded_any:
                log.error(f"Streaming interrupted after partial output on {auth.display_name}: {exc}")
                yield f"\n\n[Streaming interrupted: {exc}]"
                return
            mark_auth_failure(auth, exc)
            log.warning(f"Streaming failed on {auth.display_name}: {exc}")
            continue

    yield f"Error: {last_error or 'all GenAI credentials failed'}"


def generate_vision_response(
    prompt: str,
    images: list[dict[str, str]],
    temperature: float = 0.7,
) -> Optional[str]:
    auth_configs = get_candidate_auth_configs()
    if not auth_configs:
        log.error("No GenAI credentials are configured.")
        return None

    if not images:
        log.error("No images provided for vision analysis.")
        return None

    contents = build_multimodal_contents(prompt, images, prompt_last=True)
    config = build_text_config(
        temperature=temperature,
        max_output_tokens=2048,
    )

    last_error: Exception | None = None
    for index, auth in enumerate(auth_configs, start=1):
        try:
            log_auth_attempt(auth, index, len(auth_configs), "Vision response")
            response = generate_content_once(
                auth=auth,
                model=default_vision_model(),
                contents=contents,
                config=config,
            )
            mark_auth_success(auth)
        except Exception as exc:
            last_error = exc
            mark_auth_failure(auth, exc)
            log.warning(f"Vision generation failed on {auth.display_name}: {exc}")
            continue

        generated_text = extract_text_from_response(response)
        if generated_text:
            return generated_text

    log.error(f"All GenAI credentials failed for vision request: {last_error}")
    return None


class GeminiService:
    @staticmethod
    def generate_response(
        prompt: str,
        conversation_history: list | None = None,
        temperature: float = 0.7,
    ):
        return generate_response(prompt, conversation_history, temperature)

    @staticmethod
    def generate_response_stream(
        prompt: str,
        conversation_history: list | None = None,
        temperature: float = 0.7,
    ):
        return generate_response_stream(prompt, conversation_history, temperature)

    @staticmethod
    def generate_vision_response(
        prompt: str, images: list[dict[str, str]], temperature: float = 0.7
    ):
        return generate_vision_response(prompt, images, temperature)

    @staticmethod
    def normalize_question(question: str):
        return normalize_question(question)


gemini_service = GeminiService()
