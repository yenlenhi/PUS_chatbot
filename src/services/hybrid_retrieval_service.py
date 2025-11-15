"""
Hybrid Retrieval Service combining dense (vector) and sparse (BM25) search
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from rank_bm25 import BM25Okapi
from sqlalchemy import text
from src.utils.logger import log
from config.settings import (
    DENSE_WEIGHT,
    DENSE_SIMILARITY_THRESHOLD,
    SPARSE_SIMILARITY_THRESHOLD,
    TOP_K_RESULTS,
)


class HybridRetrievalService:
    """Service for hybrid retrieval combining dense and sparse search"""

    def __init__(self, db_service, embedding_service):
        """
        Initialize Hybrid Retrieval Service

        Args:
            db_service: PostgreSQL database service
            embedding_service: Embedding service for generating vectors
        """
        self.db_service = db_service
        self.embedding_service = embedding_service
        self.bm25_index = None
        self.chunk_ids_list = []
        self.chunks_dict = {}
        self._build_bm25_index()

    def _build_bm25_index(self):
        """Build BM25 index from all chunks"""
        try:
            log.info("🔨 Building BM25 index...")

            # Get all chunks
            chunks = self.db_service.get_all_chunks()

            if not chunks:
                log.warning("⚠️ No chunks found for BM25 indexing")
                return

            # Prepare corpus for BM25
            corpus = []
            self.chunk_ids_list = []
            self.chunks_dict = {}

            for chunk in chunks:
                # Tokenize content (simple split by whitespace)
                tokens = chunk["content"].lower().split()
                corpus.append(tokens)

                chunk_id = chunk["id"]
                self.chunk_ids_list.append(chunk_id)
                self.chunks_dict[chunk_id] = chunk

            # Build BM25 index
            self.bm25_index = BM25Okapi(corpus)

            log.info(f"✅ BM25 index built with {len(corpus)} documents")

        except Exception as e:
            log.error(f"❌ Error building BM25 index: {e}")
            raise

    def _dense_search(
        self, query_embedding: np.ndarray, top_k: int = TOP_K_RESULTS
    ) -> List[Tuple[int, float]]:
        """
        Perform dense vector search using pgvector

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of (chunk_id, similarity_score) tuples
        """
        try:
            session = self.db_service.SessionLocal()

            # Convert embedding to list for SQL
            embedding_list = query_embedding.tolist()

            # Use pgvector cosine similarity
            result = session.execute(
                text("""
                SELECT chunk_id, 1 - (embedding <=> :query_embedding) as similarity
                FROM embeddings
                WHERE 1 - (embedding <=> :query_embedding) > :threshold
                ORDER BY similarity DESC
                LIMIT :top_k
            """),
                {
                    "query_embedding": embedding_list,
                    "threshold": DENSE_SIMILARITY_THRESHOLD,
                    "top_k": top_k,
                },
            )

            results = [(row[0], float(row[1])) for row in result.fetchall()]
            log.info(f"🔍 Dense search found {len(results)} results")
            return results

        except Exception as e:
            log.error(f"❌ Error in dense search: {e}")
            return []
        finally:
            session.close()

    def _sparse_search(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Tuple[int, float]]:
        """
        Perform sparse BM25 search

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            List of (chunk_id, bm25_score) tuples
        """
        try:
            if self.bm25_index is None:
                log.warning("⚠️ BM25 index not initialized")
                return []

            # Tokenize query
            query_tokens = query.lower().split()

            # Get BM25 scores
            scores = self.bm25_index.get_scores(query_tokens)

            # Get top-k results
            top_indices = np.argsort(scores)[::-1][:top_k]

            results = []
            for idx in top_indices:
                score = float(scores[idx])
                if score > SPARSE_SIMILARITY_THRESHOLD:
                    chunk_id = self.chunk_ids_list[idx]
                    results.append((chunk_id, score))

            log.info(f"🔍 Sparse search found {len(results)} results")
            return results

        except Exception as e:
            log.error(f"❌ Error in sparse search: {e}")
            return []

    def hybrid_search(
        self,
        query: str,
        query_embedding: np.ndarray,
        top_k: int = TOP_K_RESULTS,
        dense_weight: float = DENSE_WEIGHT,
    ) -> List[Dict]:
        """
        Perform hybrid search combining dense and sparse results

        Args:
            query: Query text
            query_embedding: Query embedding vector
            top_k: Number of results to return
            dense_weight: Weight for dense search (0-1)

        Returns:
            List of search results with combined scores
        """
        try:
            log.info("🔄 Starting hybrid search...")

            # Perform dense search
            dense_results = self._dense_search(query_embedding, top_k * 2)

            # Perform sparse search
            sparse_results = self._sparse_search(query, top_k * 2)

            # Combine results
            combined_scores = {}

            # Add dense results
            for chunk_id, score in dense_results:
                combined_scores[chunk_id] = {
                    "dense_score": score,
                    "sparse_score": 0.0,
                    "chunk": self.chunks_dict.get(chunk_id),
                }

            # Add sparse results
            for chunk_id, score in sparse_results:
                if chunk_id not in combined_scores:
                    combined_scores[chunk_id] = {
                        "dense_score": 0.0,
                        "sparse_score": score,
                        "chunk": self.chunks_dict.get(chunk_id),
                    }
                else:
                    combined_scores[chunk_id]["sparse_score"] = score

            # Calculate combined scores
            results = []
            for chunk_id, scores_dict in combined_scores.items():
                combined_score = (
                    dense_weight * scores_dict["dense_score"]
                    + (1 - dense_weight) * scores_dict["sparse_score"]
                )

                chunk = scores_dict["chunk"]
                if chunk:
                    results.append(
                        {
                            "chunk_id": chunk_id,
                            "content": chunk["content"],
                            "source": chunk["source_file"],
                            "page_number": chunk["page_number"],
                            "heading_text": chunk["heading_text"],
                            "dense_score": scores_dict["dense_score"],
                            "sparse_score": scores_dict["sparse_score"],
                            "combined_score": combined_score,
                        }
                    )

            # Sort by combined score and return top-k
            results.sort(key=lambda x: x["combined_score"], reverse=True)
            results = results[:top_k]

            log.info(f"✅ Hybrid search completed with {len(results)} results")
            return results

        except Exception as e:
            log.error(f"❌ Error in hybrid search: {e}")
            return []

    def rebuild_bm25_index(self):
        """Rebuild BM25 index (call after adding new chunks)"""
        log.info("🔄 Rebuilding BM25 index...")
        self._build_bm25_index()
        log.info("✅ BM25 index rebuilt")

    def get_retrieval_stats(self) -> Dict:
        """Get retrieval service statistics"""
        return {
            "bm25_index_size": len(self.chunk_ids_list) if self.bm25_index else 0,
            "dense_weight": DENSE_WEIGHT,
            "sparse_weight": 1 - DENSE_WEIGHT,
            "dense_threshold": DENSE_SIMILARITY_THRESHOLD,
            "sparse_threshold": SPARSE_SIMILARITY_THRESHOLD,
        }

