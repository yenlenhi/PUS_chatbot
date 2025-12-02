"""
Test script for CacheService
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.cache_service import CacheService
from src.utils.logger import log


def test_cache_service():
    """Test CacheService functionality"""
    
    print("\n" + "=" * 60)
    print("🧪 Testing CacheService")
    print("=" * 60 + "\n")
    
    # Initialize cache service
    cache = CacheService(host="localhost", port=6379, db=0, ttl=3600)
    
    # Test 1: Connection
    print("Test 1: Connection Check")
    print(f"Connected: {cache.is_connected()}")
    print(f"Cache Info: {cache}")
    print()
    
    # Test 2: Health Check
    print("Test 2: Health Check")
    health = cache.health_check()
    print(f"Health Status: {health['status']}")
    print(f"Details: {health['details']}")
    print()
    
    # Test 3: Embedding Cache
    print("Test 3: Embedding Cache")
    test_text = "What is machine learning?"
    test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    # Set embedding
    success = cache.set_embedding(test_text, test_embedding)
    print(f"Set embedding: {success}")
    
    # Get embedding
    cached_embedding = cache.get_embedding(test_text)
    print(f"Get embedding: {cached_embedding}")
    print(f"Match: {cached_embedding == test_embedding}")
    print()
    
    # Test 4: Query Result Cache
    print("Test 4: Query Result Cache")
    test_query = "Explain neural networks"
    test_result = {
        "answer": "Neural networks are...",
        "sources": ["doc1", "doc2"],
        "confidence": 0.95
    }
    
    # Set query result
    success = cache.set_query_result(test_query, test_result)
    print(f"Set query result: {success}")
    
    # Get query result
    cached_result = cache.get_query_result(test_query)
    print(f"Get query result: {cached_result}")
    print(f"Match: {cached_result == test_result}")
    print()
    
    # Test 5: Batch Operations
    print("Test 5: Batch Embedding Operations")
    texts = ["text1", "text2", "text3"]
    embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
    
    # Set batch
    pairs = list(zip(texts, embeddings))
    count = cache.set_embeddings_batch(pairs)
    print(f"Batch set: {count} embeddings")
    
    # Get batch
    batch_results = cache.get_embeddings_batch(texts)
    print(f"Batch get: {len(batch_results)} results")
    print(f"All match: {all(batch_results[t] == e for t, e in zip(texts, embeddings))}")
    print()
    
    # Test 6: Cache Statistics
    print("Test 6: Cache Statistics")
    stats = cache.get_cache_stats()
    print(f"Total keys: {stats.get('total_keys', 0)}")
    print(f"Embedding keys: {stats.get('embedding_keys', 0)}")
    print(f"Query keys: {stats.get('query_keys', 0)}")
    print(f"Memory used: {stats.get('memory_used_mb', 0)} MB")
    print(f"Hit rate: {stats.get('hit_rate', 0)}%")
    print()
    
    # Test 7: Selective Cache Clearing
    print("Test 7: Selective Cache Clearing")
    deleted = cache.clear_embedding_cache()
    print(f"Cleared {deleted} embedding cache entries")
    
    deleted = cache.clear_query_cache()
    print(f"Cleared {deleted} query cache entries")
    print()
    
    # Test 8: Final Stats
    print("Test 8: Final Statistics")
    final_stats = cache.get_cache_stats()
    print(f"Total keys after clear: {final_stats.get('total_keys', 0)}")
    print()
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    
    # Close connection
    cache.close()


if __name__ == "__main__":
    test_cache_service()

