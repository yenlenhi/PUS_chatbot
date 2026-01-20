"""
Async Gemini Service - High-performance async LLM client using httpx.

This module provides async versions of Gemini API calls to avoid blocking
the event loop and improve concurrency in FastAPI.
"""

import httpx
import json
import gzip
from typing import Optional, List, Dict, Any, AsyncGenerator
from config.settings import (
    GEMINI_API_KEY,
    GEMINI_API_URL,
    ENABLE_GEMINI_NORMALIZATION,
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_TEMPERATURE,
)
from src.utils.logger import log
from src.services.gemini_service import _needs_realtime_info


# Shared async client with connection pooling (singleton pattern)
_async_client: Optional[httpx.AsyncClient] = None


async def get_async_client() -> httpx.AsyncClient:
    """Get or create a shared async HTTP client with connection pooling."""
    global _async_client
    if _async_client is None or _async_client.is_closed:
        _async_client = httpx.AsyncClient(
            timeout=httpx.Timeout(180.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=50),
        )
    return _async_client


async def close_async_client():
    """Close the shared async client (call on shutdown)."""
    global _async_client
    if _async_client is not None and not _async_client.is_closed:
        await _async_client.aclose()
        _async_client = None


async def normalize_question_async(question: str) -> str:
    """
    Async version: Normalizes and standardizes a user question using Gemini AI.

    Args:
        question (str): The raw user question

    Returns:
        str: The normalized/standardized question, or original question if normalization fails
    """
    if not ENABLE_GEMINI_NORMALIZATION:
        log.debug("Gemini normalization is disabled, returning original question")
        return question

    if not GEMINI_API_KEY:
        log.warning("GEMINI_API_KEY not set, returning original question")
        return question

    normalization_prompt = f"""
Bạn là một chuyên gia chuẩn hóa câu hỏi cho hệ thống tìm kiếm tài liệu tuyển sinh đại học.

Nhiệm vụ: Chuẩn hóa câu hỏi sau để tối ưu hóa việc tìm kiếm ngữ nghĩa trong cơ sở dữ liệu tài liệu:

Câu hỏi gốc: "{question}"

Hãy:
1. Sửa lỗi chính tả và ngữ pháp
2. Chuẩn hóa thuật ngữ giáo dục (VD: "học phí" thay vì "tiền học")
3. Mở rộng từ viết tắt (VD: "ĐH" thành "đại học")
4. Làm rõ nghĩa nếu câu hỏi mơ hồ
5. Giữ nguyên ý nghĩa và ngữ cảnh tuyển sinh

Chỉ trả về câu hỏi đã chuẩn hóa, không giải thích:
"""

    try:
        client = await get_async_client()
        data = {
            "contents": [{"parts": [{"text": normalization_prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 256,  # Normalization doesn't need much output
            },
        }

        log.info(f"[ASYNC] Normalizing question: {question[:50]}...")

        response = await client.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            content=json.dumps(data),
        )

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and result["candidates"]:
                candidate = result["candidates"][0]
                content = candidate.get("content", {})
                finish_reason = candidate.get("finishReason", "")

                if finish_reason == "MAX_TOKENS":
                    log.warning("Normalization hit MAX_TOKENS, using original question")
                    return question

                if "parts" in content and content["parts"]:
                    normalized = content["parts"][0].get("text", "").strip()
                    if normalized:
                        log.info(f"[ASYNC] Normalized: '{question[:30]}...' -> '{normalized[:30]}...'")
                        return normalized

        log.warning(f"Normalization failed (status={response.status_code})")
        return question

    except Exception as e:
        log.error(f"[ASYNC] Error normalizing question: {e}")
        return question


async def generate_response_async(
    prompt: str,
    conversation_history: list = None,
    temperature: float = None,
    enable_grounding: bool = None,  # NEW: Override for Google Search Grounding
) -> Optional[str]:
    """
    Async version: Generates a response from the Gemini API (non-streaming).

    Args:
        prompt (str): The user's prompt.
        conversation_history (list, optional): The history of the conversation.
        temperature (float): Temperature for generation.
        enable_grounding (bool, optional): Force enable/disable Google Search Grounding.
            If None, auto-detect based on query content.

    Returns:
        str | None: The generated text from Gemini, or None if an error occurs.
    """
    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY is not set in the environment variables.")
        return None

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature if temperature is not None else GEMINI_TEMPERATURE,
            "maxOutputTokens": GEMINI_MAX_OUTPUT_TOKENS,
            "topP": 0.95,
            "topK": 40,
        },
    }
    
    # NEW: Add Google Search Grounding tool if needed for real-time info
    if enable_grounding is None:
        enable_grounding = _needs_realtime_info(prompt)
    
    if enable_grounding:
        data["tools"] = [{"google_search": {}}]
        log.info("[ASYNC] Google Search Grounding ENABLED for real-time information")

    try:
        client = await get_async_client()
        log.debug("[ASYNC] Sending request to Gemini API...")

        response = await client.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            content=json.dumps(data),
        )

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and result["candidates"]:
                candidate = result["candidates"][0]
                content = candidate.get("content", {})
                finish_reason = candidate.get("finishReason", "")

                if finish_reason == "MAX_TOKENS":
                    log.warning("Gemini hit MAX_TOKENS limit.")
                    if "parts" in content and content["parts"]:
                        partial_text = content["parts"][0].get("text", "").strip()
                        if partial_text:
                            return partial_text + "\n\n[Câu trả lời đã bị cắt ngắn do giới hạn độ dài.]"

                if "parts" in content and content["parts"]:
                    generated_text = content["parts"][0].get("text", "").strip()
                    if generated_text:
                        log.info("[ASYNC] Successfully received response from Gemini.")
                        return generated_text

            log.warning(f"Gemini response format unexpected: {result}")
            return None
        else:
            log.error(f"Gemini API error: {response.status_code} - {response.text[:200]}")
            return None

    except Exception as e:
        log.error(f"[ASYNC] Error calling Gemini API: {e}")
        return None


async def generate_response_stream_async(
    prompt: str,
    conversation_history: list = None,
    temperature: float = None,
    enable_grounding: bool = None,  # NEW: Override for Google Search Grounding
) -> AsyncGenerator[str, None]:
    """
    Async version: Generates a streaming response from the Gemini API.
    Yields text chunks as they arrive from the API.

    Args:
        prompt (str): The user's prompt.
        conversation_history (list, optional): The history of the conversation.
        temperature (float): Temperature for response generation.
        enable_grounding (bool, optional): Force enable/disable Google Search Grounding.
            If None, auto-detect based on query content.

    Yields:
        str: Text chunks from Gemini as they arrive
    """
    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY is not set.")
        yield "Error: API key not configured"
        return

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature if temperature is not None else GEMINI_TEMPERATURE,
            "maxOutputTokens": GEMINI_MAX_OUTPUT_TOKENS,
            "topP": 0.95,
            "topK": 40,
        },
    }
    
    # NEW: Add Google Search Grounding tool if needed for real-time info
    if enable_grounding is None:
        enable_grounding = _needs_realtime_info(prompt)
    
    if enable_grounding:
        data["tools"] = [{"google_search": {}}]
        log.info("[ASYNC] Google Search Grounding ENABLED for real-time information")

    try:
        # Use streaming endpoint with alt=sse
        stream_url = GEMINI_API_URL.replace(":generateContent", ":streamGenerateContent")

        log.info("[ASYNC] Sending streaming request to Gemini API...")

        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=10.0)) as client:
            async with client.stream(
                "POST",
                f"{stream_url}?key={GEMINI_API_KEY}&alt=sse",
                headers={"Content-Type": "application/json"},
                content=json.dumps(data),
            ) as response:
                log.info(f"[ASYNC] Gemini streaming API status: {response.status_code}")

                if response.status_code == 200:
                    log.info("[ASYNC] Successfully connected to Gemini streaming API")
                    buffer = ""

                    async for chunk in response.aiter_text():
                        buffer += chunk
                        
                        # Process complete SSE events (lines ending with \n\n)
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            
                            if not line:
                                continue
                            
                            # Handle SSE format "data: {...}"
                            json_str = line
                            if line.startswith("data: "):
                                json_str = line[6:]
                            elif not (line.startswith("[") or line.startswith("{")):
                                continue

                            try:
                                chunk_data = json.loads(json_str)
                                
                                if "candidates" in chunk_data and chunk_data["candidates"]:
                                    candidate = chunk_data["candidates"][0]
                                    content = candidate.get("content", {})

                                    if "parts" in content and content["parts"]:
                                        text_chunk = content["parts"][0].get("text", "")
                                        if text_chunk:
                                            yield text_chunk

                                    finish_reason = candidate.get("finishReason", "")
                                    if finish_reason:
                                        log.info(f"[ASYNC] Stream finished: {finish_reason}")
                                        if finish_reason == "MAX_TOKENS":
                                            yield "\n\n[Câu trả lời đã bị cắt ngắn do giới hạn độ dài.]"
                                        return

                            except json.JSONDecodeError:
                                continue

                    log.info("[ASYNC] Streaming completed successfully")
                else:
                    log.error(f"Gemini API error: {response.status_code}")
                    yield f"Error: API returned status {response.status_code}"

    except Exception as e:
        log.error(f"[ASYNC] Error in Gemini streaming: {e}")
        yield f"Error: {str(e)}"


async def generate_vision_response_async(
    prompt: str,
    images: List[Dict[str, str]],
    temperature: float = 0.7,
) -> Optional[str]:
    """
    Async version: Generates a response from the Gemini Vision API with image analysis.

    Args:
        prompt (str): The user's prompt/question about the image(s).
        images (list): List of dictionaries with 'mime_type' and 'data' (base64) keys.
        temperature (float): Creativity level for the response.

    Returns:
        str | None: The generated text from Gemini Vision, or None if an error occurs.
    """
    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY is not set in the environment variables.")
        return None

    if not images:
        log.error("No images provided for vision analysis.")
        return None

    # Use gemini-2.0-flash model which supports vision
    vision_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    # Build parts with images and text
    parts = []
    for img in images:
        parts.append({
            "inline_data": {
                "mime_type": img.get("mime_type", "image/jpeg"),
                "data": img.get("data", ""),
            }
        })
    parts.append({"text": prompt})

    data = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 2048,
        },
    }

    try:
        client = await get_async_client()
        log.info(f"[ASYNC] Sending request to Gemini Vision API with {len(images)} images...")

        response = await client.post(
            f"{vision_api_url}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            content=json.dumps(data),
        )

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and result["candidates"]:
                content = result["candidates"][0].get("content", {})
                if "parts" in content and content["parts"]:
                    generated_text = content["parts"][0].get("text", "").strip()
                    if generated_text:
                        log.info("[ASYNC] Successfully received response from Gemini Vision.")
                        return generated_text

            log.warning(f"Gemini Vision response format unexpected: {result}")
            return None
        else:
            log.error(f"Gemini Vision API error: {response.status_code} - {response.text[:200]}")
            return None

    except Exception as e:
        log.error(f"[ASYNC] Error calling Gemini Vision API: {e}")
        return None


# Convenience class for consistent import pattern
class AsyncGeminiService:
    """Async wrapper for Gemini API functions (use with await)."""

    @staticmethod
    async def generate_response(
        prompt: str, conversation_history: list = None, temperature: float = None
    ):
        return await generate_response_async(prompt, conversation_history, temperature)

    @staticmethod
    async def generate_response_stream(
        prompt: str, conversation_history: list = None, temperature: float = None
    ):
        async for chunk in generate_response_stream_async(prompt, conversation_history, temperature):
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
