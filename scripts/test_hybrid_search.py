"""
Test hybrid search functionality
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.hybrid_retrieval_service import HybridRetrievalService
from src.services.embedding_service import EmbeddingService
from src.utils.logger import log


def test_hybrid_search():
    """Test hybrid search with a sample query"""
    try:
        # Initialize services
        log.info("🔧 Initializing services...")
        embedding_service = EmbeddingService()
        retrieval_service = HybridRetrievalService()

        # Test query
        query = "Điều kiện tốt nghiệp của sinh viên là gì?"
        log.info(f"🔍 Testing query: {query}")

        # Create query embedding
        log.info("📝 Creating query embedding...")
        query_embedding = embedding_service.create_embedding(query)

        if query_embedding is None:
            log.error("❌ Failed to create query embedding")
            return False

        log.info(f"✅ Query embedding shape: {query_embedding.shape}")

        # Perform hybrid search
        log.info("🔄 Performing hybrid search...")
        results = retrieval_service.hybrid_search(
            query=query, query_embedding=query_embedding, top_k=5
        )

        # Display results
        log.info(f"✅ Found {len(results)} results")

        for i, result in enumerate(results, 1):
            log.info(f"\n--- Result {i} ---")
            log.info(f"Chunk ID: {result.get('chunk_id')}")
            log.info(f"Score: {result.get('score', 0):.4f}")
            log.info(f"Content: {result.get('content', '')[:200]}...")
            log.info(f"Source: {result.get('source_file', 'N/A')}")

        return True

    except Exception as e:
        log.error(f"❌ Error in test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    log.info("=" * 60)
    log.info("Testing Hybrid Search")
    log.info("=" * 60)

    success = test_hybrid_search()

    if success:
        log.info("=" * 60)
        log.info("✅ Test completed successfully")
        log.info("=" * 60)
    else:
        log.error("=" * 60)
        log.error("❌ Test failed")
        log.error("=" * 60)
        sys.exit(1)
