#!/usr/bin/env python3
"""
Test script for contextual follow-up questions
"""

import sys
import os

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.rag_service import RAGService
import uuid


def test_contextual_followup():
    """Test contextual follow-up questions"""
    print("🧪 Testing Contextual Follow-up Questions\n")

    try:
        # Initialize RAG service
        print("📚 Initializing RAG service...")
        rag_service = RAGService()
        print("✅ RAG service initialized\n")

        # Test queries with different topics
        test_queries = [
            "Điều kiện tuyển sinh năm 2025 như thế nào?",
            "Học phí của trường là bao nhiêu?",
            "Các ngành đào tạo của trường có gì?",
            "Thông tin về ký túc xá?",
            "Cơ hội việc làm sau tốt nghiệp?",
            "Ronaldo sinh năm nào?",  # Out of domain question
        ]

        conversation_id = str(uuid.uuid4())

        for i, query in enumerate(test_queries, 1):
            print(f"🔍 Test {i}: {query}")
            print("-" * 60)

            try:
                # Generate answer
                response = rag_service.generate_answer(
                    query=query, conversation_id=conversation_id, language="vi"
                )

                answer = response.get("answer", "No answer")
                confidence = response.get("confidence", 0.0)

                print(f"📝 Answer: {answer[:200]}...")
                print(f"🎯 Confidence: {confidence:.2f}")

                # Check if answer contains contextual follow-up
                if "**" in answer and (
                    "Bạn có" in answer or "muốn biết thêm" in answer
                ):
                    # Extract follow-up question
                    parts = answer.split("**")
                    if len(parts) >= 3:
                        followup = parts[1]
                        print(f"💬 Follow-up: {followup}")
                        print("✅ Contextual follow-up detected!")
                    else:
                        print("⚠️ Bold formatting found but no clear follow-up")
                else:
                    print("❌ No contextual follow-up detected")

            except Exception as e:
                print(f"❌ Error processing query: {e}")

            print()

    except Exception as e:
        print(f"❌ Test failed: {e}")


def test_topic_extraction():
    """Test topic extraction functionality"""
    print("🔍 Testing Topic Extraction\n")

    try:
        rag_service = RAGService()

        test_queries = [
            "Điều kiện tuyển sinh năm 2025 như thế nào?",
            "Học phí của trường là bao nhiêu?",
            "Các ngành đào tạo của trường có gì?",
            "Thông tin về ký túc xá?",
            "Cơ hội việc làm sau tốt nghiệp?",
            "Quy định thi kiểm tra như thế nào?",
        ]

        for query in test_queries:
            topics = rag_service._extract_key_topics(query)
            print(f"📝 Query: {query}")
            print(f"🏷️ Topics: {topics}")

            # Test contextual follow-up creation
            followup = rag_service._create_contextual_followup(
                query, "Sample answer", "vi"
            )
            print(f"💬 Follow-up: {followup}")
            print()

    except Exception as e:
        print(f"❌ Topic extraction test failed: {e}")


if __name__ == "__main__":
    print("🚀 Testing Contextual Follow-up Features\n")

    test_topic_extraction()
    print("=" * 60)
    test_contextual_followup()

    print("✅ Testing completed!")
