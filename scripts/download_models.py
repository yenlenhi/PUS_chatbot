"""
Pre-download embedding models for Docker build
This script is used during Docker build to ensure models are cached
"""

import os
from sentence_transformers import SentenceTransformer

# Set cache directories
cache_dir = os.environ.get('TRANSFORMERS_CACHE', '/root/.cache/huggingface')
os.makedirs(cache_dir, exist_ok=True)

print("=" * 60)
print("📥 Pre-downloading Embedding Models for Docker Build")
print("=" * 60)

# Primary model: Vietnamese SBERT
try:
    print("\n🔄 Downloading primary model: keepitreal/vietnamese-sbert")
    model = SentenceTransformer('keepitreal/vietnamese-sbert', cache_folder=cache_dir)
    print("✅ keepitreal/vietnamese-sbert downloaded successfully")
    print(f"   Embedding dimension: {model.get_sentence_embedding_dimension()}")
    
    # Test the model
    test_embedding = model.encode("Test sentence")
    print(f"   Test embedding shape: {test_embedding.shape}")
    
except Exception as e:
    print(f"❌ Failed to download keepitreal/vietnamese-sbert: {e}")
    exit(1)

# Fallback model 1: all-MiniLM-L6-v2
try:
    print("\n🔄 Downloading fallback model 1: all-MiniLM-L6-v2")
    model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=cache_dir)
    print("✅ all-MiniLM-L6-v2 downloaded successfully")
    print(f"   Embedding dimension: {model.get_sentence_embedding_dimension()}")
    
except Exception as e:
    print(f"⚠️ Failed to download fallback model 1: {e}")

# Fallback model 2: paraphrase-multilingual-MiniLM-L12-v2
try:
    print("\n🔄 Downloading fallback model 2: paraphrase-multilingual-MiniLM-L12-v2")
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', cache_folder=cache_dir)
    print("✅ paraphrase-multilingual-MiniLM-L12-v2 downloaded successfully")
    print(f"   Embedding dimension: {model.get_sentence_embedding_dimension()}")
    
except Exception as e:
    print(f"⚠️ Failed to download fallback model 2: {e}")

print("\n" + "=" * 60)
print("✅ Model pre-download completed successfully")
print("=" * 60)
print(f"📁 Models cached in: {cache_dir}")
print("🚀 Ready for offline deployment")
