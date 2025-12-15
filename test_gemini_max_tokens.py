"""
Test script for Gemini API with new MAX_TOKENS handling
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.gemini_service import generate_response

if __name__ == "__main__":
    print("Testing Gemini with MAX_TOKENS fix...\n")

    # Test with a prompt that should work
    test_prompt = """
Hãy giải thích ngắn gọn về quy trình xét tuyển đại học.
"""

    print(f"Prompt: {test_prompt.strip()}\n")
    print("Calling Gemini API...\n")

    response = generate_response(test_prompt)

    if response:
        print("✅ Success!")
        print(f"\nResponse:\n{response}\n")
    else:
        print("❌ Failed to get response")
