"""
Test script for EmbeddingService with caching
"""

import sys
import os
import time
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.embedding_service import EmbeddingService
from src.utils.logger import log


def test_embedding_service():
    """Test EmbeddingService with caching functionality"""
    
    print("\n" + "=" * 70)
    print("🧪 Testing EmbeddingService with Redis Caching")
    print("=" * 70 + "\n")
    
    # Initialize embedding service with cache
    print("Test 1: Initialize EmbeddingService")
    print("-" * 70)
    embedding_service = EmbeddingService(use_cache=True)
    print(f"Service: {embedding_service}")
    print()
    
    # Test 2: Single embedding (first time - should compute)
    print("Test 2: Single Embedding (First Time - No Cache)")
    print("-" * 70)
    test_text = "Machine learning is a subset of artificial intelligence"
    
    start_time = time.time()
    embedding1 = embedding_service.create_embedding(test_text)
    time1 = time.time() - start_time
    
    print(f"Text: {test_text}")
    print(f"Embedding shape: {embedding1.shape}")
    print(f"Embedding sample: {embedding1[:5]}")
    print(f"Time taken: {time1:.4f}s")
    print()
    
    # Test 3: Same embedding (second time - should use cache)
    print("Test 3: Same Embedding (Second Time - From Cache)")
    print("-" * 70)
    
    start_time = time.time()
    embedding2 = embedding_service.create_embedding(test_text)
    time2 = time.time() - start_time
    
    print(f"Embedding shape: {embedding2.shape}")
    print(f"Time taken: {time2:.4f}s")
    print(f"Speedup: {time1/time2:.2f}x faster")
    print(f"Embeddings match: {np.allclose(embedding1, embedding2)}")
    print()
    
    # Test 4: Batch embeddings with partial cache
    print("Test 4: Batch Embeddings (Partial Cache)")
    print("-" * 70)
    
    batch_texts = [
        "Machine learning is a subset of artificial intelligence",  # Cached
        "Deep learning uses neural networks",  # New
        "Natural language processing analyzes text",  # New
        "Computer vision processes images",  # New
    ]
    
    start_time = time.time()
    batch_embeddings = embedding_service.create_embeddings_batch(batch_texts)
    batch_time = time.time() - start_time
    
    print(f"Batch size: {len(batch_texts)}")
    print(f"Embeddings shape: {batch_embeddings.shape}")
    print(f"Time taken: {batch_time:.4f}s")
    print(f"First embedding matches cached: {np.allclose(batch_embeddings[0], embedding1)}")
    print()
    
    # Test 5: Same batch (all from cache)
    print("Test 5: Same Batch (All From Cache)")
    print("-" * 70)
    
    start_time = time.time()
    batch_embeddings2 = embedding_service.create_embeddings_batch(batch_texts)
    batch_time2 = time.time() - start_time
    
    print(f"Time taken: {batch_time2:.4f}s")
    print(f"Speedup: {batch_time/batch_time2:.2f}x faster")
    print(f"All embeddings match: {np.allclose(batch_embeddings, batch_embeddings2)}")
    print()
    
    # Test 6: Similarity computation
    print("Test 6: Similarity Computation")
    print("-" * 70)
    
    query_text = "AI and machine learning"
    query_emb = embedding_service.create_embedding(query_text)
    
    similarities = []
    for i, text in enumerate(batch_texts):
        sim = embedding_service.compute_similarity(query_emb, batch_embeddings[i])
        similarities.append((text, sim))
        print(f"Similarity with '{text[:40]}...': {sim:.4f}")
    
    print()
    
    # Test 7: Find most similar
    print("Test 7: Find Most Similar")
    print("-" * 70)
    
    top_results = embedding_service.find_most_similar(
        query_emb, batch_embeddings, top_k=2
    )
    
    print(f"Query: {query_text}")
    print(f"Top {len(top_results)} most similar:")
    for idx, score in top_results:
        print(f"  {idx+1}. {batch_texts[idx][:50]}... (score: {score:.4f})")
    print()
    
    # Test 8: Cache statistics
    print("Test 8: Cache Statistics")
    print("-" * 70)
    
    cache_stats = embedding_service.get_cache_stats()
    if cache_stats.get("cache_enabled", True):
        print(f"Total keys: {cache_stats.get('total_keys', 0)}")
        print(f"Embedding keys: {cache_stats.get('embedding_keys', 0)}")
        print(f"Memory used: {cache_stats.get('memory_used_mb', 0)} MB")
        print(f"Hit rate: {cache_stats.get('hit_rate', 0)}%")
        print(f"Cache hits: {cache_stats.get('keyspace_hits', 0)}")
        print(f"Cache misses: {cache_stats.get('keyspace_misses', 0)}")
    else:
        print("Cache not enabled")
    print()
    
    # Test 9: Vietnamese text
    print("Test 9: Vietnamese Text Support")
    print("-" * 70)
    
    vietnamese_texts = [
        "Học máy là một nhánh của trí tuệ nhân tạo",
        "Xử lý ngôn ngữ tự nhiên phân tích văn bản",
        "Thị giác máy tính xử lý hình ảnh",
    ]
    
    start_time = time.time()
    vn_embeddings = embedding_service.create_embeddings_batch(vietnamese_texts)
    vn_time = time.time() - start_time
    
    print(f"Vietnamese texts: {len(vietnamese_texts)}")
    print(f"Embeddings shape: {vn_embeddings.shape}")
    print(f"Time taken: {vn_time:.4f}s")
    print()
    
    # Test 10: Final cache stats
    print("Test 10: Final Cache Statistics")
    print("-" * 70)
    
    final_stats = embedding_service.get_cache_stats()
    if final_stats.get("cache_enabled", True):
        print(f"Total cached embeddings: {final_stats.get('embedding_keys', 0)}")
        print(f"Total memory: {final_stats.get('memory_used_mb', 0)} MB")
        print(f"Overall hit rate: {final_stats.get('hit_rate', 0)}%")
    print()
    
    print("=" * 70)
    print("✅ All tests completed successfully!")
    print("=" * 70)
    
    # Cleanup
    embedding_service.close()


if __name__ == "__main__":
    test_embedding_service()

