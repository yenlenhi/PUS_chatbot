"""
Embedding service using Vietnamese SBERT with Redis caching
"""

import numpy as np
import torch
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from src.services.cache_service import CacheService
from src.utils.logger import log
from config.settings import (
    EMBEDDING_MODEL,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
    REDIS_CACHE_TTL,
    ENABLE_REDIS_CACHE,
)


class EmbeddingService:
    """Service for creating embeddings using Vietnamese SBERT with caching"""

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None,
    ):
        """
        Initialize embedding service

        Args:
            model_name: Name of the sentence transformer model
            use_cache: Whether to use Redis caching
            cache_ttl: Cache time-to-live in seconds (uses default if None)
        """
        self.model_name = model_name
        self.model = None
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl or REDIS_CACHE_TTL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Initialize model
        self._load_model()

        # Initialize cache if enabled
        self.cache = None
        if self.use_cache and ENABLE_REDIS_CACHE:
            try:
                self.cache = CacheService(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    password=REDIS_PASSWORD,
                    ttl=self.cache_ttl,
                )
                if self.cache.is_connected():
                    log.info("✅ Embedding cache service connected")
                else:
                    log.warning("⚠️ Cache service not connected, running without cache")
                    self.cache = None
            except Exception as e:
                log.warning(f"⚠️ Failed to initialize cache: {e}")
                self.cache = None
        elif not ENABLE_REDIS_CACHE:
            log.info("ℹ️ Redis cache disabled via ENABLE_REDIS_CACHE setting")

    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            log.info(f"🤖 Loading embedding model: {self.model_name}")
            log.info(f"📍 Using device: {self.device}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            log.info("✅ Embedding model loaded successfully")

        except Exception as e:
            log.error(f"❌ Failed to load embedding model: {e}")
            # Fallback to a more common model
            try:
                log.info("🔄 Trying fallback model: all-MiniLM-L6-v2")
                self.model = SentenceTransformer("all-MiniLM-L6-v2", device=self.device)
                log.info("✅ Fallback embedding model loaded successfully")

            except Exception as e2:
                log.error(f"❌ Failed to load fallback model: {e2}")
                raise RuntimeError("Could not load any embedding model")

    def create_embedding(self, text: str) -> np.ndarray:
        """
        Create embedding for a single text with caching

        Args:
            text: Input text

        Returns:
            Embedding vector as numpy array
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")

        # Try to get from cache first
        if self.cache and self.cache.is_connected():
            cached_emb = self.cache.get_embedding(text)
            if cached_emb is not None:
                return np.array(cached_emb)

        try:
            # Generate new embedding
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

            # Cache the embedding
            if self.cache and self.cache.is_connected():
                self.cache.set_embedding(text, embedding.tolist(), ttl=self.cache_ttl)

            return embedding

        except Exception as e:
            log.error(f"❌ Error creating embedding: {e}")
            raise

    def create_embeddings_batch(
        self, texts: List[str], batch_size: int = 32, show_progress: bool = False
    ) -> np.ndarray:
        """
        Create embeddings for multiple texts in batches with caching

        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            show_progress: Show progress bar

        Returns:
            Array of embedding vectors
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")

        if not texts:
            return np.array([])

        try:
            log.info(f"📝 Creating embeddings for {len(texts)} texts")

            # Try to get from cache in batch
            embeddings_list = []
            texts_to_encode = []
            text_indices = {}  # Map text to its original index

            if self.cache and self.cache.is_connected():
                batch_results = self.cache.get_embeddings_batch(texts)

                for i, text in enumerate(texts):
                    cached_emb = batch_results.get(text)
                    if cached_emb is not None:
                        embeddings_list.append((i, np.array(cached_emb)))
                    else:
                        texts_to_encode.append(text)
                        text_indices[text] = i

                cache_hits = len(embeddings_list)
                log.info(f"🎯 Cache hits: {cache_hits}/{len(texts)}")
            else:
                texts_to_encode = texts
                text_indices = {text: i for i, text in enumerate(texts)}

            # Encode uncached texts
            if texts_to_encode:
                log.info(f"🔄 Encoding {len(texts_to_encode)} uncached texts")

                # Process in batches to manage memory
                new_embeddings = []

                for i in range(0, len(texts_to_encode), batch_size):
                    batch_texts = texts_to_encode[i : i + batch_size]
                    batch_embeddings = self.model.encode(
                        batch_texts,
                        convert_to_numpy=True,
                        normalize_embeddings=True,
                        show_progress_bar=show_progress and len(texts_to_encode) > 100,
                    )
                    new_embeddings.append(batch_embeddings)

                    if i % (batch_size * 10) == 0:  # Log progress every 10 batches
                        log.info(
                            f"Processed {min(i + batch_size, len(texts_to_encode))}/{len(texts_to_encode)} texts"
                        )

                # Concatenate all new embeddings
                new_embeddings = np.vstack(new_embeddings)

                # Cache new embeddings in batch
                if self.cache and self.cache.is_connected():
                    pairs = [
                        (text, emb.tolist())
                        for text, emb in zip(texts_to_encode, new_embeddings)
                    ]
                    cached_count = self.cache.set_embeddings_batch(
                        pairs, ttl=self.cache_ttl
                    )
                    log.info(f"💾 Cached {cached_count} new embeddings")

                # Add to embeddings list with original indices
                for text, emb in zip(texts_to_encode, new_embeddings):
                    original_idx = text_indices[text]
                    embeddings_list.append((original_idx, emb))

            # Sort by original index and extract embeddings
            embeddings_list.sort(key=lambda x: x[0])
            final_embeddings = np.array([emb for _, emb in embeddings_list])

            log.info(f"✅ Created embeddings with shape: {final_embeddings.shape}")

            return final_embeddings

        except Exception as e:
            log.error(f"❌ Error creating batch embeddings: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by the model

        Returns:
            Embedding dimension
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")

        # Create a dummy embedding to get dimension
        dummy_embedding = self.create_embedding("test")
        return dummy_embedding.shape[0]

    def compute_similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)

    def find_most_similar(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: np.ndarray,
        top_k: int = 5,
    ) -> List[tuple]:
        """
        Find most similar embeddings to query

        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: Array of candidate embeddings
            top_k: Number of top results to return

        Returns:
            List of (index, similarity_score) tuples
        """
        if len(candidate_embeddings) == 0:
            return []

        # Compute similarities
        similarities = []
        for i, candidate in enumerate(candidate_embeddings):
            similarity = self.compute_similarity(query_embedding, candidate)
            similarities.append((i, similarity))

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats or empty dict if cache not available
        """
        if self.cache and self.cache.is_connected():
            return self.cache.get_cache_stats()
        return {"cache_enabled": False}

    def clear_cache(self) -> bool:
        """
        Clear all embedding cache

        Returns:
            True if successful, False otherwise
        """
        if self.cache and self.cache.is_connected():
            return self.cache.clear_embedding_cache() > 0
        return False

    def close(self):
        """Close cache connection"""
        if self.cache:
            self.cache.close()

    def __repr__(self) -> str:
        """String representation"""
        cache_status = (
            "enabled" if self.cache and self.cache.is_connected() else "disabled"
        )
        return f"EmbeddingService(model={self.model_name}, device={self.device}, cache={cache_status})"
