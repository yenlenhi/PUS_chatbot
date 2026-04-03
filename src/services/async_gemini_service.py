"""
Async GenAI service backed by the official google-genai SDK.
"""

from typing import AsyncGenerator, Dict, List, Optional

from config.settings import (
    ENABLE_GEMINI_NORMALIZATION,
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
    generate_content_once_async,
    generate_content_stream_once_async,
    get_candidate_auth_configs,
    is_max_tokens_finish_reason,
    log_auth_attempt,
    mark_auth_failure,
    mark_auth_success,
)
from src.utils.logger import log


async def close_async_client():
    """
    Backward-compatible no-op. The SDK clients are short-lived and closed per request.
    """


async def normalize_question_async(question: str) -> str:
    if not ENABLE_GEMINI_NORMALIZATION:
        log.debug("Gemini normalization is disabled, returning original question")
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
            log_auth_attempt(auth, index, len(auth_configs), "Async question normalization")
            response = await generate_content_once_async(
                auth=auth,
                model=default_text_model(),
                contents=normalization_prompt,
                config=config,
            )
            mark_auth_success(auth)
        except Exception as exc:
            mark_auth_failure(auth, exc)
            log.warning(f"[ASYNC] Normalization failed on {auth.display_name}: {exc}")
            continue

        finish_reason = extract_finish_reason(response)
        if is_max_tokens_finish_reason(finish_reason):
            return question

        normalized_question = extract_text_from_response(response)
        if normalized_question:
            return normalized_question

    return question


async def generate_response_async(
    prompt: str,
    conversation_history: list = None,
    temperature: float = None,
    enable_grounding: bool = None,
) -> Optional[str]:
    del conversation_history
    auth_configs = get_candidate_auth_configs()
    if not auth_configs:
        log.error("No GenAI credentials are configured.")
        return None

    config = build_text_config(
        temperature=temperature if temperature is not None else GEMINI_TEMPERATURE,
        max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
        enable_google_search=bool(enable_grounding),
    )

    last_error: Exception | None = None
    for index, auth in enumerate(auth_configs, start=1):
        try:
            log_auth_attempt(auth, index, len(auth_configs), "Async generate response")
            response = await generate_content_once_async(
                auth=auth,
                model=default_text_model(),
                contents=prompt,
                config=config,
            )
            mark_auth_success(auth)
        except Exception as exc:
            last_error = exc
            mark_auth_failure(auth, exc)
            log.warning(f"[ASYNC] Response generation failed on {auth.display_name}: {exc}")
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

    log.error(f"[ASYNC] All GenAI credentials failed: {last_error}")
    return None


async def generate_response_stream_async(
    prompt: str,
    conversation_history: list = None,
    temperature: float = None,
    enable_grounding: bool = None,
) -> AsyncGenerator[str, None]:
    del conversation_history
    auth_configs = get_candidate_auth_configs()
    if not auth_configs:
        log.error("No GenAI credentials are configured.")
        yield "Error: API key not configured"
        return

    config = build_text_config(
        temperature=temperature if temperature is not None else GEMINI_TEMPERATURE,
        max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
        enable_google_search=bool(enable_grounding),
    )

    last_error: Exception | None = None
    for index, auth in enumerate(auth_configs, start=1):
        yielded_any = False
        try:
            log_auth_attempt(auth, index, len(auth_configs), "Async stream response")
            async for chunk in generate_content_stream_once_async(
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
                yield f"\n\n[Streaming interrupted: {exc}]"
                return
            mark_auth_failure(auth, exc)
            log.warning(f"[ASYNC] Streaming failed on {auth.display_name}: {exc}")
            continue

    yield f"Error: {last_error or 'all GenAI credentials failed'}"


async def generate_vision_response_async(
    prompt: str,
    images: List[Dict[str, str]],
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
            log_auth_attempt(auth, index, len(auth_configs), "Async vision response")
            response = await generate_content_once_async(
                auth=auth,
                model=default_vision_model(),
                contents=contents,
                config=config,
            )
            mark_auth_success(auth)
        except Exception as exc:
            last_error = exc
            mark_auth_failure(auth, exc)
            log.warning(f"[ASYNC] Vision generation failed on {auth.display_name}: {exc}")
            continue

        generated_text = extract_text_from_response(response)
        if generated_text:
            return generated_text

    log.error(f"[ASYNC] All GenAI credentials failed for vision request: {last_error}")
    return None


class AsyncGeminiService:
    @staticmethod
    async def generate_response(
        prompt: str, conversation_history: list = None, temperature: float = None
    ):
        return await generate_response_async(prompt, conversation_history, temperature)

    @staticmethod
    async def generate_response_stream(
        prompt: str, conversation_history: list = None, temperature: float = None
    ):
        async for chunk in generate_response_stream_async(
            prompt, conversation_history, temperature
        ):
            yield chunk

    @staticmethod
    async def generate_vision_response(
        prompt: str, images: list, temperature: float = 0.7
    ):
        return await generate_vision_response_async(prompt, images, temperature)

    @staticmethod
    async def normalize_question(question: str):
        return await normalize_question_async(question)


async_gemini_service = AsyncGeminiService()
