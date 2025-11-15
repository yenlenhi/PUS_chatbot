#!/usr/bin/env python3
"""
Test script for Gemini question normalization functionality
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.gemini_service import normalize_question


def test_normalization():
    """Test various question normalization scenarios"""

    # Check configuration
    from config.settings import GEMINI_API_KEY, ENABLE_GEMINI_NORMALIZATION

    print("=== Testing Gemini Question Normalization ===\n")
    print(f"GEMINI_API_KEY: {'SET' if GEMINI_API_KEY else 'NOT SET'}")
    print(f"ENABLE_GEMINI_NORMALIZATION: {ENABLE_GEMINI_NORMALIZATION}")
    print()

    test_cases = [
        # Test case 1: Spelling errors
        "hoc phi cua truong la bao nhieu?",
        # Test case 2: Abbreviations
        "ĐH có những ngành gì?",
        # Test case 3: Informal language
        "tiền học như nào vậy?",
        # Test case 4: Unclear question
        "điều kiện vào trường?",
        # Test case 5: Well-formed question (should remain similar)
        "Các ngành đào tạo của trường Đại học An ninh Nhân dân có gì?",
    ]

    for i, question in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"Original: {question}")

        try:
            normalized = normalize_question(question)
            print(f"Normalized: {normalized}")

            if normalized != question:
                print("✅ Normalization applied")
            else:
                print("ℹ️  No normalization needed or normalization disabled")

        except Exception as e:
            print(f"❌ Error: {e}")

        print("-" * 60)


if __name__ == "__main__":
    test_normalization()
