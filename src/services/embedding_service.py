"""
Embedding service using Vietnamese SBERT
"""
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from src.utils.logger import log
from config.settings import EMBEDDING_MODEL


class EmbeddingService:
    """Service for creating embeddings using Vietnamese SBERT"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize embedding service
        
        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            log.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            log.info("Embedding model loaded successfully")
            
        except Exception as e:
            log.error(f"Failed to load embedding model: {e}")
            # Fallback to a more common model
            try:
                log.info("Trying fallback model: all-MiniLM-L6-v2")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                log.info("Fallback embedding model loaded successfully")
                
            except Exception as e2:
                log.error(f"Failed to load fallback model: {e2}")
                raise RuntimeError("Could not load any embedding model")
    
    def create_embedding(self, text: str) -> np.ndarray:
        """
        Create embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
            
        except Exception as e:
            log.error(f"Error creating embedding: {e}")
            raise
    
    def create_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Create embeddings for multiple texts in batches
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            Array of embedding vectors
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        
        if not texts:
            return np.array([])
        
        try:
            log.info(f"Creating embeddings for {len(texts)} texts")
            
            # Process in batches to manage memory
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.model.encode(
                    batch_texts, 
                    convert_to_numpy=True,
                    show_progress_bar=True if len(texts) > 100 else False
                )
                all_embeddings.append(batch_embeddings)
                
                if i % (batch_size * 10) == 0:  # Log progress every 10 batches
                    log.info(f"Processed {min(i + batch_size, len(texts))}/{len(texts)} texts")
            
            # Concatenate all embeddings
            embeddings = np.vstack(all_embeddings)
            log.info(f"Created embeddings with shape: {embeddings.shape}")
            
            return embeddings
            
        except Exception as e:
            log.error(f"Error creating batch embeddings: {e}")
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
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
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
    
    def find_most_similar(self, query_embedding: np.ndarray, 
                         candidate_embeddings: np.ndarray, 
                         top_k: int = 5) -> List[tuple]:
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
