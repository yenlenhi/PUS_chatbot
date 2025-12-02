"""
FAISS service for vector similarity search
"""

import faiss
import numpy as np
import pickle
from typing import List
from pathlib import Path
from src.utils.logger import log
from config.settings import FAISS_INDEX_PATH


class FAISSService:
    """Service for FAISS vector database operations"""

    def __init__(self):
        """Initialize FAISS service"""
        self.index = None
        self.id_map = {}  # Maps FAISS internal IDs to chunk IDs
        self.dimension = None
        self.is_loaded = False
        self.index_path = Path(FAISS_INDEX_PATH)  # Thêm đường dẫn từ settings

    def create_index(self, embeddings: np.ndarray, chunk_ids: List[int]):
        """
        Create FAISS index from embeddings

        Args:
            embeddings: Array of embedding vectors
            chunk_ids: List of corresponding chunk IDs
        """
        if len(embeddings) == 0:
            raise ValueError("Cannot create index with empty embeddings")

        if len(embeddings) != len(chunk_ids):
            raise ValueError("Number of embeddings must match number of chunk IDs")

        try:
            # Get embedding dimension
            self.dimension = embeddings.shape[1]
            log.info(f"Creating FAISS index with dimension: {self.dimension}")

            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)

            # Create index - using IndexFlatIP for cosine similarity
            self.index = faiss.IndexFlatIP(self.dimension)

            # Add embeddings to index
            self.index.add(embeddings.astype(np.float32))

            # Create ID mapping
            self.id_map = {i: chunk_id for i, chunk_id in enumerate(chunk_ids)}

            log.info(f"Created FAISS index with {self.index.ntotal} vectors")

        except Exception as e:
            log.error(f"Error creating FAISS index: {e}")
            raise

    def save_index(self):
        """Save FAISS index to disk"""
        if self.index is None:
            raise RuntimeError("No index to save")

        try:
            # Save FAISS index
            index_file = str(self.index_path) + ".index"
            faiss.write_index(self.index, index_file)

            # Save chunk IDs mapping
            metadata_file = str(self.index_path) + ".metadata"
            metadata = {"id_map": self.id_map, "dimension": self.dimension}

            with open(metadata_file, "wb") as f:
                pickle.dump(metadata, f)

            log.info(f"Saved FAISS index to {index_file}")
            log.info(f"Saved metadata to {metadata_file}")

        except Exception as e:
            log.error(f"Error saving FAISS index: {e}")
            raise

    def load_index(self) -> bool:
        """
        Load FAISS index from disk

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            index_file = str(self.index_path) + ".index"
            metadata_file = str(self.index_path) + ".metadata"

            if not Path(index_file).exists() or not Path(metadata_file).exists():
                log.warning(f"FAISS index files not found at {index_file}")
                return False

            # Load FAISS index
            self.index = faiss.read_index(index_file)

            # Load metadata
            with open(metadata_file, "rb") as f:
                metadata = pickle.load(f)

            self.id_map = metadata.get("id_map", {})
            self.dimension = metadata.get("dimension")
            self.is_loaded = True

            log.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            return True

        except Exception as e:
            log.error(f"Error loading FAISS index: {e}")
            return False

    def search(self, query_embedding, top_k=5):
        """Search for similar vectors in the FAISS index"""
        if not self.is_loaded:
            log.warning("FAISS index not loaded. Loading now...")
            if not self.load_index():
                log.error("Failed to load FAISS index")
                return []

        # Reshape query embedding to match FAISS requirements
        query_embedding = np.array(query_embedding).reshape(1, -1).astype("float32")

        # Perform search
        try:
            distances, indices = self.index.search(query_embedding, top_k)

            # Convert to list of (id, score) tuples
            results = []
            for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
                if idx != -1:  # FAISS returns -1 for empty slots
                    chunk_id = self.id_map.get(idx)
                    if chunk_id is not None:
                        # Convert distance to similarity score (for inner product)
                        similarity_score = float(distance)
                        results.append((chunk_id, similarity_score))

            return results
        except Exception as e:
            log.error(f"Error searching FAISS index: {e}")
            return []

    def get_index_stats(self) -> dict:
        """
        Get FAISS index statistics

        Returns:
            Dictionary with index stats
        """
        if self.index is None:
            return {"status": "not_loaded"}

        return {
            "status": "loaded",
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__,
        }

    def rebuild_index(self, embeddings: np.ndarray, chunk_ids: List[int]):
        """
        Rebuild the FAISS index with new data

        Args:
            embeddings: New embedding vectors
            chunk_ids: New chunk IDs
        """
        log.info("Rebuilding FAISS index...")

        # Create new index
        self.create_index(embeddings, chunk_ids)

        # Save to disk
        self.save_index()

        log.info("FAISS index rebuilt successfully")

    def add_vectors(self, embeddings: np.ndarray, chunk_ids: List[int]):
        """
        Add new vectors to existing index

        Args:
            embeddings: New embedding vectors to add
            chunk_ids: Corresponding chunk IDs
        """
        if self.index is None:
            raise RuntimeError("Index not loaded or created")

        if len(embeddings) != len(chunk_ids):
            raise ValueError("Number of embeddings must match number of chunk IDs")

        try:
            # Get current number of vectors in index
            current_count = self.index.ntotal

            # Normalize new embeddings
            embeddings_copy = embeddings.copy().astype(np.float32)
            faiss.normalize_L2(embeddings_copy)

            # Add to index
            self.index.add(embeddings_copy)

            # Update id_map with new chunk IDs
            for i, chunk_id in enumerate(chunk_ids):
                self.id_map[current_count + i] = chunk_id

            log.info(
                f"Added {len(embeddings)} vectors to FAISS index (total: {self.index.ntotal})"
            )

        except Exception as e:
            log.error(f"Error adding vectors to FAISS index: {e}")
            raise
            raise
