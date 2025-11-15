import requests
import json
from config.settings import GEMINI_API_KEY, GEMINI_API_URL, ENABLE_GEMINI_NORMALIZATION
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
                "maxOutputTokens": 256,  # Shorter response for question normalization
            },
        }

        log.info(f"Normalizing question with Gemini: {question[:50]}...")

        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            data=json.dumps(data),
            timeout=30,  # Shorter timeout for normalization
        )

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and result["candidates"]:
                content = result["candidates"][0].get("content", {})
                if "parts" in content and content["parts"]:
                    normalized_question = content["parts"][0].get("text", "").strip()

                    if normalized_question and len(normalized_question) > 0:
                        log.info(
                            f"Question normalized: '{question}' -> '{normalized_question}'"
                        )
                        return normalized_question

        log.warning("Gemini normalization failed, using original question")
        return question

    except Exception as e:
        log.error(f"Error normalizing question with Gemini: {e}")
        return question  # Fallback to original question


def generate_response(
    prompt: str, conversation_history: list = None, temperature: float = 0.7
) -> str | None:
    """
    Generates a response from the Gemini API.

    Args:
        prompt (str): The user's prompt.
        conversation_history (list, optional): The history of the conversation. Defaults to None.

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
            "temperature": temperature,
            "maxOutputTokens": 2048,
        },
    }

    try:
        log.info(f"Sending request to Gemini API with prompt: {prompt[:100]}...")
        # API key is passed as a query parameter in the URL for Gemini
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            data=json.dumps(data),
            timeout=180,  # 180-second timeout
        )

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and result["candidates"]:
                content = result["candidates"][0].get("content", {})
                if "parts" in content and content["parts"]:
                    generated_text = content["parts"][0].get("text", "").strip()

                    if not generated_text:
                        log.warning("Gemini returned empty response")
                        return None

                    log.info("Successfully received response from Gemini.")
                    return generated_text

            log.warning(f"Gemini response format unexpected: {result}")
            return None
        else:
            log.error(f"Gemini API error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        log.error(f"Error calling Gemini API: {e}")
        return None
    except Exception as e:
        log.error(f"An unexpected error occurred in Gemini service: {e}")
        return None
