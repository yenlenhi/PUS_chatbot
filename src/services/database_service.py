"""
Database service for managing document chunks and embeddings
"""

import sqlite3
import numpy as np
from typing import List, Optional, Dict, Any
from pathlib import Path
from src.utils.logger import log
from src.models.schemas import DocumentChunk
from config.settings import DATABASE_PATH


class DatabaseService:
    """Service for managing SQLite database operations"""

    def __init__(self, db_path: str = DATABASE_PATH):
        """
        Initialize database service

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create chunks table with enhanced metadata
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS chunks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        source_file TEXT NOT NULL,
                        page_number INTEGER,
                        chunk_index INTEGER NOT NULL,
                        heading_text TEXT,
                        heading_level INTEGER,
                        heading_number TEXT,
                        parent_heading TEXT,
                        is_sub_chunk BOOLEAN DEFAULT FALSE,
                        sub_chunk_index INTEGER,
                        total_sub_chunks INTEGER,
                        chunk_type TEXT DEFAULT 'content',
                        word_count INTEGER,
                        char_count INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create embeddings table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS embeddings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chunk_id INTEGER NOT NULL,
                        embedding BLOB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (chunk_id) REFERENCES chunks (id)
                    )
                """
                )

                # Create indexes for better performance
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_chunks_source
                    ON chunks (source_file)
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id
                    ON embeddings (chunk_id)
                """
                )

                conn.commit()
                log.info("Database initialized successfully")

        except Exception as e:
            log.error(f"Error initializing database: {e}")
            raise

    def insert_chunks(self, chunks: List[DocumentChunk]) -> List[int]:
        """
        Insert document chunks into database

        Args:
            chunks: List of document chunks

        Returns:
            List of inserted chunk IDs
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                chunk_ids = []
                for chunk in chunks:
                    cursor.execute(
                        """
                        INSERT INTO chunks (
                            content, source_file, page_number, chunk_index,
                            heading_text, heading_level, heading_number, parent_heading,
                            is_sub_chunk, sub_chunk_index, total_sub_chunks, chunk_type,
                            word_count, char_count
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            chunk.content,
                            chunk.source_file,
                            chunk.page_number,
                            chunk.chunk_index,
                            chunk.heading_text,
                            chunk.heading_level,
                            chunk.heading_number,
                            chunk.parent_heading,
                            chunk.is_sub_chunk,
                            chunk.sub_chunk_index,
                            chunk.total_sub_chunks,
                            chunk.chunk_type,
                            chunk.word_count,
                            chunk.char_count,
                        ),
                    )

                    chunk_ids.append(cursor.lastrowid)

                conn.commit()
                log.info(f"Inserted {len(chunks)} chunks into database")
                return chunk_ids

        except Exception as e:
            log.error(f"Error inserting chunks: {e}")
            raise

    def insert_embeddings(self, chunk_ids: List[int], embeddings: np.ndarray):
        """
        Insert embeddings into database

        Args:
            chunk_ids: List of chunk IDs
            embeddings: Array of embedding vectors
        """
        if len(chunk_ids) != len(embeddings):
            raise ValueError("Number of chunk IDs must match number of embeddings")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for chunk_id, embedding in zip(chunk_ids, embeddings):
                    # Convert numpy array to bytes
                    embedding_bytes = embedding.tobytes()

                    cursor.execute(
                        """
                        INSERT INTO embeddings (chunk_id, embedding)
                        VALUES (?, ?)
                    """,
                        (chunk_id, embedding_bytes),
                    )

                conn.commit()
                log.info(f"Inserted {len(embeddings)} embeddings into database")

        except Exception as e:
            log.error(f"Error inserting embeddings: {e}")
            raise

    def clear_all_data(self):
        """Clear all chunks and embeddings from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Clear embeddings first (due to foreign key constraint)
                cursor.execute("DELETE FROM embeddings")

                # Clear chunks
                cursor.execute("DELETE FROM chunks")

                conn.commit()
                log.info("Cleared all data from database")

        except Exception as e:
            log.error(f"Error clearing database: {e}")
            raise

    def get_chunk_count(self) -> int:
        """Get the total number of chunks in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM chunks")
                count = cursor.fetchone()[0]
                return count

        except Exception as e:
            log.error(f"Error getting chunk count: {e}")
            return 0

    def get_processed_files(self) -> List[str]:
        """Get list of file names that are fully processed (all chunks have embeddings)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Only return files where ALL chunks have corresponding embeddings
                cursor.execute(
                    """
                    SELECT DISTINCT c.source_file
                    FROM chunks c
                    WHERE NOT EXISTS (
                        SELECT 1 FROM chunks c2
                        WHERE c2.source_file = c.source_file
                        AND c2.id NOT IN (
                            SELECT chunk_id FROM embeddings
                        )
                    )
                    ORDER BY c.source_file
                    """
                )
                rows = cursor.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            log.error(f"Error getting processed files: {e}")
            return []

    def get_chunks_without_embeddings(self) -> List[Dict[str, Any]]:
        """Get chunks that don't have corresponding embeddings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT c.id, c.source_file, c.content, c.chunk_index
                    FROM chunks c
                    LEFT JOIN embeddings e ON c.id = e.chunk_id
                    WHERE e.chunk_id IS NULL
                    ORDER BY c.source_file, c.chunk_index
                    """
                )
                rows = cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "source_file": row[1],
                        "content": row[2],
                        "chunk_index": row[3],
                    }
                    for row in rows
                ]
        except Exception as e:
            log.error(f"Error getting chunks without embeddings: {e}")
            return []

    def delete_chunks_by_file(self, source_file: str) -> bool:
        """Delete all chunks and their embeddings for a specific file"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # First delete embeddings for chunks of this file
                cursor.execute(
                    """
                    DELETE FROM embeddings
                    WHERE chunk_id IN (
                        SELECT id FROM chunks WHERE source_file = ?
                    )
                    """,
                    (source_file,),
                )

                # Then delete chunks
                cursor.execute(
                    "DELETE FROM chunks WHERE source_file = ?", (source_file,)
                )

                conn.commit()
                log.info(f"Deleted all chunks and embeddings for file: {source_file}")
                return True

        except Exception as e:
            log.error(f"Error deleting chunks for file {source_file}: {e}")
            return False

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Retrieve all chunks from the database for BM25 corpus."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, content, source_file, page_number, heading_text
                    FROM chunks ORDER BY id
                    """
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            log.error(f"Error retrieving all chunks: {e}")
            return []

    def get_all_embeddings(self) -> tuple:
        """
        Get all embeddings from database

        Returns:
            Tuple of (chunk_ids, embeddings_array)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT chunk_id, embedding
                    FROM embeddings
                    ORDER BY chunk_id
                """
                )

                chunk_ids = []
                embeddings = []

                for chunk_id, embedding_bytes in cursor.fetchall():
                    chunk_ids.append(chunk_id)

                    # Convert bytes back to numpy array
                    embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                    embeddings.append(embedding)

                if embeddings:
                    embeddings_array = np.vstack(embeddings)
                else:
                    embeddings_array = np.array([])

                return chunk_ids, embeddings_array

        except Exception as e:
            log.error(f"Error getting embeddings: {e}")
            raise

    def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict[str, Any]]:
        """
        Get chunk by ID

        Args:
            chunk_id: Chunk ID

        Returns:
            Chunk dictionary or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, content, source_file, page_number, chunk_index,
                           heading_text, heading_level, heading_number, parent_heading
                    FROM chunks
                    WHERE id = ?
                """,
                    (chunk_id,),
                )

                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None

        except Exception as e:
            log.error(f"Error getting chunk by ID: {e}")
            return None

    def clear_all_data(self):
        """Clear all data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("DELETE FROM embeddings")
                cursor.execute("DELETE FROM chunks")

                conn.commit()
                log.info("Cleared all data from database")

        except Exception as e:
            log.error(f"Error clearing database: {e}")
            raise

    def get_database_stats(self) -> Dict[str, int]:
        """
        Get database statistics

        Returns:
            Dictionary with database stats
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Count chunks
                cursor.execute("SELECT COUNT(*) FROM chunks")
                chunk_count = cursor.fetchone()[0]

                # Count embeddings
                cursor.execute("SELECT COUNT(*) FROM embeddings")
                embedding_count = cursor.fetchone()[0]

                # Count unique source files
                cursor.execute("SELECT COUNT(DISTINCT source_file) FROM chunks")
                file_count = cursor.fetchone()[0]

                return {
                    "total_chunks": chunk_count,
                    "total_embeddings": embedding_count,
                    "unique_files": file_count,
                }

        except Exception as e:
            log.error(f"Error getting database stats: {e}")
            raise
