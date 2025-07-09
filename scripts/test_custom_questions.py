"""
Script to test chatbot with custom questions
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.rag_service import RAGService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def test_custom_questions():
    """Test chatbot with custom questions"""
    rag_service = RAGService()
    
    # Add your custom questions here
    custom_questions = [
        "Đại học an ninh nhân dân là trường gì?",
        "Tuyển sinh",
        "Thông tin tuyển sinh",
        # "Học phí của trường bao nhiêu?",
        # Thêm câu hỏi của bạn ở đây
    ]
    
    for i, question in enumerate(custom_questions, 1):
        log.info(f"\n--- Test Question {i}: {question} ---")
        
        try:
            result = rag_service.generate_answer(question)
            
            log.info(f"Answer: {result['answer']}")
            log.info(f"Sources: {result['sources']}")
            log.info(f"Confidence: {result['confidence']:.3f}")
            log.info(f"Conversation ID: {result['conversation_id']}")
            
        except Exception as e:
            log.error(f"Error processing question: {e}")

if __name__ == "__main__":
    test_custom_questions()
