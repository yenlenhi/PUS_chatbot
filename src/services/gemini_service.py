import requests
import json
from config.settings import GEMINI_API_KEY, GEMINI_API_URL
from src.utils.logger import log

def generate_response(prompt: str, conversation_history: list = None) -> str | None:
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
        'Content-Type': 'application/json',
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        log.info(f"Sending request to Gemini API with prompt: {prompt[:100]}...")
        # API key is passed as a query parameter in the URL for Gemini
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            data=json.dumps(data),
            timeout=180  # 180-second timeout
        )

        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and result['candidates']:
                content = result['candidates'][0].get('content', {})
                if 'parts' in content and content['parts']:
                    generated_text = content['parts'][0].get('text', '').strip()
                    
                    if not generated_text:
                        log.warning("Gemini returned empty response")
                        return None
                    
                    log.info(f"Successfully received response from Gemini.")
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

