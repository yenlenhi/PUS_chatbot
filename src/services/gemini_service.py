import requests
import json
import gzip
from config.settings import (
    GEMINI_API_KEY,
    GEMINI_API_URL,
    ENABLE_GEMINI_NORMALIZATION,
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_TEMPERATURE,
)
from src.utils.logger import log


def normalize_question(question: str) -> str:
    """
    Normalizes and standardizes a user question using Gemini AI before semantic search.

    Args:
        question (str): The raw user question

    Returns:
        str: The normalized/standardized question, or original question if normalization fails
    """
    # Check if normalization is enabled
    if not ENABLE_GEMINI_NORMALIZATION:
        log.info("Gemini normalization is disabled, returning original question")
        return question

    if not GEMINI_API_KEY:
        log.warning("GEMINI_API_KEY not set, returning original question")
        return question

    # Create a prompt for question normalization
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
        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "contents": [{"parts": [{"text": normalization_prompt}]}],
            "generationConfig": {
                "temperature": 0.3,  # Lower temperature for more consistent normalization
                "maxOutputTokens": 1024,
            },
        }

        log.info(f"Normalizing question with Gemini: {question[:50]}...")

        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            data=json.dumps(data),
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            log.debug(f"Gemini normalization response: {result}")

            if "candidates" in result and result["candidates"]:
                candidate = result["candidates"][0]
                content = candidate.get("content", {})
                finish_reason = candidate.get("finishReason", "")

                # Handle MAX_TOKENS in normalization
                if finish_reason == "MAX_TOKENS":
                    log.warning("Normalization hit MAX_TOKENS, using original question")
                    return question

                if "parts" in content and content["parts"]:
                    normalized_question = content["parts"][0].get("text", "").strip()

                    if normalized_question and len(normalized_question) > 0:
                        log.info(
                            f"Question normalized: '{question}' -> '{normalized_question}'"
                        )
                        return normalized_question
                else:
                    log.warning(f"Gemini response has no text parts: {content}")
            else:
                log.warning(f"Gemini response has no candidates: {result}")
        else:
            log.warning(
                f"Gemini API returned status {response.status_code}: {response.text[:200]}"
            )

        log.warning("Gemini normalization failed, using original question")
        return question

    except Exception as e:
        log.error(f"Error normalizing question with Gemini: {e}")
        return question


def generate_response(
    prompt: str, conversation_history: list = None, temperature: float = 0.7
) -> str | None:
    """
    Generates a response from the Gemini API (non-streaming).

    Args:
        prompt (str): The user's prompt.
        conversation_history (list, optional): The history of the conversation.
        temperature (float): Temperature for generation.

    Returns:
        str | None: The generated text from Gemini, or None if an error occurs.
    """
    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY is not set in the environment variables.")
        return None

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": (
                temperature if temperature is not None else GEMINI_TEMPERATURE
            ),
            "maxOutputTokens": GEMINI_MAX_OUTPUT_TOKENS,
            "topP": 0.95,
            "topK": 40,
        },
    }

    try:
        log.debug(f"Sending request to Gemini API...")

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
                    log.warning("Gemini hit MAX_TOKENS limit.")
                    if "parts" in content and content["parts"]:
                        partial_text = content["parts"][0].get("text", "").strip()
                        if partial_text:
                            return (
                                partial_text
                                + "\n\n[Câu trả lời đã bị cắt ngắn do giới hạn độ dài.]"
                            )

                if "parts" in content and content["parts"]:
                    generated_text = content["parts"][0].get("text", "").strip()
                    if generated_text:
                        log.info("Successfully received response from Gemini.")
                        return generated_text

            log.warning(f"Gemini response format unexpected: {result}")
            return None
        else:
            log.error(f"Gemini API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        log.error(f"Error calling Gemini API: {e}")
        return None


def generate_response_stream(
    prompt: str, conversation_history: list = None, temperature: float = 0.7
):
    """
    Generates a streaming response from the Gemini API.
    Yields text chunks as they arrive from the API.

    Args:
        prompt (str): The user's prompt.
        conversation_history (list, optional): The history of the conversation.
        temperature (float): Temperature for response generation.

    Yields:
        str: Text chunks from Gemini as they arrive
    """
    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY is not set.")
        yield "Error: API key not configured"
        return

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": (
                temperature if temperature is not None else GEMINI_TEMPERATURE
            ),
            "maxOutputTokens": GEMINI_MAX_OUTPUT_TOKENS,
            "topP": 0.95,
            "topK": 40,
        },
    }

    try:
        log.info("Sending streaming request to Gemini API...")

        # Use streaming endpoint
        stream_url = GEMINI_API_URL.replace(
            ":generateContent", ":streamGenerateContent"
        )

        # Make streaming request with alt=sse for Server-Sent Events
        response = requests.post(
            f"{stream_url}?key={GEMINI_API_KEY}&alt=sse",
            headers=headers,
            data=json.dumps(data),
            timeout=180,
            stream=True,
        )

        log.info(f"Gemini streaming API status: {response.status_code}")

        if response.status_code == 200:
            log.info("Successfully connected to Gemini streaming API")

            # Check if response is gzipped by examining content-encoding header
            content_encoding = response.headers.get("content-encoding", "").lower()
            is_gzipped = content_encoding == "gzip"

            if is_gzipped:
                log.info("Response is gzipped, decompressing...")
                # Read all compressed data
                compressed_data = response.content
                # Decompress
                decompressed_data = gzip.decompress(compressed_data).decode("utf-8")
                # Split into lines
                lines = decompressed_data.split("\n")
            else:
                # Use iter_lines for non-gzipped response
                lines = [line for line in response.iter_lines(decode_unicode=True)]

            # Process Server-Sent Events or newline-delimited JSON
            for line in lines:
                if not line or not line.strip():
                    continue

                # Handle both SSE format "data: {...}" and raw JSON
                json_str = line
                if line.startswith("data: "):
                    json_str = line[6:]  # Remove "data: " prefix
                elif line.startswith("[") or line.startswith("{"):
                    # Already JSON
                    pass
                else:
                    # Skip non-JSON lines
                    continue

                try:
                    chunk_data = json.loads(json_str)

                    # Extract text from chunk
                    if "candidates" in chunk_data and chunk_data["candidates"]:
                        candidate = chunk_data["candidates"][0]
                        content = candidate.get("content", {})

                        if "parts" in content and content["parts"]:
                            text_chunk = content["parts"][0].get("text", "")
                            if text_chunk:
                                yield text_chunk

                        # Check finish reason
                        finish_reason = candidate.get("finishReason", "")
                        if finish_reason:
                            log.info(f"Stream finished: {finish_reason}")
                            if finish_reason == "MAX_TOKENS":
                                yield "\n\n[Câu trả lời đã bị cắt ngắn do giới hạn độ dài.]"
                            return

                except json.JSONDecodeError as e:
                    log.warning(f"Could not parse chunk: {e}, line: {json_str[:100]}")
                    continue

            log.info("Streaming completed successfully")
        else:
            log.error(
                f"Gemini API error: {response.status_code} - {response.text[:500]}"
            )
            yield f"Error: API returned status {response.status_code}"

    except requests.exceptions.RequestException as e:
        log.error(f"Error calling Gemini streaming API: {e}")
        yield f"Error: {str(e)}"
    except Exception as e:
        log.error(f"An unexpected error in Gemini streaming service: {e}")
        yield f"Error: {str(e)}"


def generate_vision_response(
    prompt: str, images: list, temperature: float = 0.7
) -> str | None:
    """
    Generates a response from the Gemini Vision API with image analysis.

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
    vision_api_url = GEMINI_API_URL.replace("gemini-1.5-pro", "gemini-2.0-flash")
    if (
        "gemini-2.0-flash" not in vision_api_url
        and "gemini-pro-vision" not in vision_api_url
    ):
        vision_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    headers = {
        "Content-Type": "application/json",
    }

    # Build parts with images and text
    parts = []

    # Add images first
    for img in images:
        parts.append(
            {
                "inline_data": {
                    "mime_type": img.get("mime_type", "image/jpeg"),
                    "data": img.get("data", ""),
                }
            }
        )

    # Add text prompt
    parts.append({"text": prompt})

    data = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 2048,
        },
    }

    try:
        log.info(f"Sending request to Gemini Vision API with {len(images)} images...")

        response = requests.post(
            f"{vision_api_url}?key={GEMINI_API_KEY}",
            headers=headers,
            data=json.dumps(data),
            timeout=180,
        )

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and result["candidates"]:
                content = result["candidates"][0].get("content", {})
                if "parts" in content and content["parts"]:
                    generated_text = content["parts"][0].get("text", "").strip()

                    if not generated_text:
                        log.warning("Gemini Vision returned empty response")
                        return None

                    log.info("Successfully received response from Gemini Vision.")
                    return generated_text

            log.warning(f"Gemini Vision response format unexpected: {result}")
            return None
        else:
            log.error(
                f"Gemini Vision API error: {response.status_code} - {response.text}"
            )
            return None

    except requests.exceptions.RequestException as e:
        log.error(f"Error calling Gemini Vision API: {e}")
        return None
    except Exception as e:
        log.error(f"An unexpected error occurred in Gemini Vision service: {e}")
        return None


# Create a singleton instance for easy import
class GeminiService:
    """Singleton wrapper for Gemini API functions"""

    @staticmethod
    def generate_response(
        prompt: str, conversation_history: list = None, temperature: float = 0.7
    ):
        return generate_response(prompt, conversation_history, temperature)

    @staticmethod
    def generate_response_stream(
        prompt: str, conversation_history: list = None, temperature: float = 0.7
    ):
        return generate_response_stream(prompt, conversation_history, temperature)

    @staticmethod
    def generate_vision_response(prompt: str, images: list, temperature: float = 0.7):
        return generate_vision_response(prompt, images, temperature)

    @staticmethod
    def normalize_question(question: str):
        return normalize_question(question)


gemini_service = GeminiService()
