import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.services.rag_service import RAGService
from src.utils.logger import log
import uuid

def test_conversational_rag():
    """Test the RAG pipeline with conversation history"""
    log.info("--- Testing Conversational RAG ---")
    
    rag_service = RAGService()
    conversation_id = str(uuid.uuid4())
    
    # --- Turn 1 ---
    query1 = "Trường có những ngành nào?"
    log.info(f"\n[Turn 1] User: {query1}")
    
    result1 = rag_service.generate_answer(query=query1, conversation_id=conversation_id)
    log.info(f"[Turn 1] Bot: {result1['answer']}")
    log.info("-" * 20)
    
    # --- Turn 2 ---
    query2 = "còn điều kiện tuyển sinh thì sao?"
    log.info(f"\n[Turn 2] User: {query2}")
    
    # In a real app, you would pass the conversation history from the client.
    # Here, we rely on the service's internal memory using the conversation_id.
    result2 = rag_service.generate_answer(query=query2, conversation_id=conversation_id)
    log.info(f"[Turn 2] Bot: {result2['answer']}")
    log.info(f"Sources: {result2['sources']}")
    log.info("-" * 20)

    # --- Turn 3 ---
    query3 = "Địa chỉ của trường ở đâu?"
    log.info(f"\n[Turn 3] User: {query3}")
    result3 = rag_service.generate_answer(query=query3, conversation_id=conversation_id)
    log.info(f"[Turn 3] Bot: {result3['answer']}")
    log.info(f"Sources: {result3['sources']}")
    log.info("-" * 20)

    # --- Turn 4 ---
    query4 = "còn website thì sao?"
    log.info(f"\n[Turn 4] User: {query4}")
    result4 = rag_service.generate_answer(query=query4, conversation_id=conversation_id)
    log.info(f"[Turn 4] Bot: {result4['answer']}")
    log.info(f"Sources: {result4['sources']}")
    log.info("-" * 20)


if __name__ == "__main__":
    test_conversational_rag()

