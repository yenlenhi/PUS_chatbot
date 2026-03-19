"""
Quick Test Script for RAG Optimization Features
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from src.services.gemini_service import _needs_realtime_info
from config.settings import STRICT_MODE, CONFIDENCE_THRESHOLD

print("=" * 60)
print("TEST 1: Google Search Keywords Detection")
print("=" * 60)

test_queries = [
    ("Ai là hiệu trưởng hiện tại?", True),
    ("Điểm chuẩn năm 2025?", True),
    ("Lịch khai giảng năm nay?", True),
    ("Thông báo mới nhất?", True),
    ("Quy chế đào tạo là gì?", False),
    ("Thủ tục xin nghỉ học?", False),
]

passed = 0
for query, expected in test_queries:
    result = _needs_realtime_info(query)
    status = "PASS" if result == expected else "FAIL"
    if result == expected:
        passed += 1
    print(f"[{status}] '{query[:35]}...' -> GG Search: {result} (expected: {expected})")

print(f"\nResult: {passed}/{len(test_queries)} passed\n")

print("=" * 60)
print("TEST 2: STRICT_MODE Configuration")
print("=" * 60)
print(f"STRICT_MODE = {STRICT_MODE}")
print(f"CONFIDENCE_THRESHOLD = {CONFIDENCE_THRESHOLD}")

if STRICT_MODE and CONFIDENCE_THRESHOLD == 0.6:
    print("[PASS] Configuration is correct")
else:
    print("[FAIL] Configuration mismatch")

print("\n" + "=" * 60)
print("TEST 3: Fallback Response Function")
print("=" * 60)

try:
    from src.services.rag_service import RAGService
    rag = RAGService()
    
    # Test fallback response exists
    if hasattr(rag, '_get_fallback_response'):
        response = rag._get_fallback_response("test query", 0.3, "vi")
        if "5 chủ đề" in response or "Tuyển sinh" in response:
            print("[PASS] Fallback response contains 5 topics")
        else:
            print("[FAIL] Fallback response missing topics")
    else:
        print("[FAIL] _get_fallback_response method not found")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "=" * 60)
print("ALL QUICK TESTS COMPLETED")
print("=" * 60)
