"""
Test Gemini normalization function
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.gemini_service import normalize_question

if __name__ == "__main__":
    print("Testing Gemini Normalization...\n")

    test_questions = [
        "học phí ĐH là bao nhiu?",  # typos, abbreviation
        "xét tuyển thế nào",  # vague
        "khi nào thi",  # very short
        "Điều kiện để được xét tuyển vào trường là gì?",  # good question
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"{i}. Original: {question}")
        normalized = normalize_question(question)
        print(f"   Normalized: {normalized}")
        print()
