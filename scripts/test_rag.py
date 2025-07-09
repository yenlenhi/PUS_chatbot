"""
Script to test RAG service functionality
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.services.rag_service import RAGService
from src.utils.logger import log


def test_ollama_connection():
    """Test Ollama connection and model availability"""
    log.info("Testing Ollama connection...")
    
    rag_service = RAGService()
    health = rag_service.ollama_service.check_health()
    
    log.info(f"Ollama health status: {health}")
    
    if health['status'] == 'healthy':
        if not health.get('target_model_available', False):
            log.warning(f"Target model {rag_service.ollama_service.model} not available")
            log.info("Attempting to pull model...")
            
            if rag_service.ollama_service.pull_model():
                log.info("Model pulled successfully")
            else:
                log.error("Failed to pull model")
                return False
        else:
            log.info("Target model is available")
        
        return True
    else:
        log.error("Ollama service is not healthy")
        return False


def test_rag_pipeline():
    """Test the complete RAG pipeline"""
    log.info("Testing RAG pipeline...")
    
    rag_service = RAGService()
    
    # Test queries
    test_queries = [
        "Điều kiện tuyển sinh vào trường là gì?",
        "Có những ngành nào được đào tạo?",
        "Thời gian nộp hồ sơ tuyển sinh như thế nào?",
        "Học phí của trường bao nhiêu?",
        "Địa chỉ của trường ở đâu?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        log.info(f"\n--- Test Query {i}: {query} ---")
        
        try:
            result = rag_service.generate_answer(query)
            
            log.info(f"Answer: {result['answer'][:200]}...")
            log.info(f"Sources: {result['sources']}")
            log.info(f"Confidence: {result['confidence']:.3f}")
            log.info(f"Conversation ID: {result['conversation_id']}")
            
        except Exception as e:
            log.error(f"Error processing query: {e}")


def test_system_health():
    """Test overall system health"""
    log.info("Testing system health...")
    
    rag_service = RAGService()
    health = rag_service.check_system_health()
    
    log.info(f"Overall status: {health['overall_status']}")
    
    for component, status in health['components'].items():
        log.info(f"{component}: {status}")


def main():
    """Main test function"""
    log.info("Starting RAG service tests...")
    
    # Test 1: System health
    test_system_health()
    
    # Test 2: Ollama connection
    if not test_ollama_connection():
        log.error("Ollama connection failed. Please ensure Ollama is running.")
        log.info("To start Ollama, run: ollama serve")
        return
    
    # Test 3: RAG pipeline
    test_rag_pipeline()
    
    log.info("RAG service tests completed!")


if __name__ == "__main__":
    main()
