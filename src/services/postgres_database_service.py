"""
PostgreSQL database service for managing document chunks and embeddings with pgvector
"""

from typing import List, Optional, Dict, Any
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.utils.logger import log
from src.models.schemas import DocumentChunk
from config.settings import DATABASE_URL


class PostgresDatabaseService:
    """Service for PostgreSQL database operations with pgvector"""

    def __init__(self, database_url: str = DATABASE_URL):
        """
        Initialize PostgreSQL database service

        Args:
            database_url: PostgreSQL connection string
        """
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._init_database()

    def _init_database(self):
        """Initialize database connection and create tables"""
        try:
            # Create engine
            self.engine = create_engine(
                self.database_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verify connections before using
            )

            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                log.info("✅ PostgreSQL connection successful")

                # Check pgvector extension
                result = conn.execute(
                    text("SELECT * FROM pg_extension WHERE extname = 'vector'")
                )
                if result.fetchone():
                    log.info("✅ pgvector extension is installed")
                else:
                    log.warning(
                        "⚠️ pgvector extension not found, attempting to create..."
                    )
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    conn.commit()
                    log.info("✅ pgvector extension created")

            # Create tables
            self._create_tables()

        except Exception as e:
            log.error(f"❌ Error initializing database: {e}")
            raise

    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            with self.engine.connect() as conn:
                # Create chunks table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS chunks (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        source_file VARCHAR(255) NOT NULL,
                        page_number INTEGER,
                        chunk_index INTEGER NOT NULL,
                        heading_text TEXT,
                        heading_level INTEGER,
                        heading_number VARCHAR(50),
                        parent_heading TEXT,
                        is_sub_chunk BOOLEAN DEFAULT FALSE,
                        sub_chunk_index INTEGER,
                        total_sub_chunks INTEGER,
                        chunk_type VARCHAR(50) DEFAULT 'content',
                        word_count INTEGER,
                        char_count INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create embeddings table with pgvector
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS embeddings (
                        id SERIAL PRIMARY KEY,
                        chunk_id INTEGER NOT NULL UNIQUE,
                        embedding vector(384),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
                    )
                """
                    )
                )

                # Create conversations table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id SERIAL PRIMARY KEY,
                        conversation_id VARCHAR(255) UNIQUE NOT NULL,
                        user_message TEXT NOT NULL,
                        assistant_response TEXT NOT NULL,
                        sources TEXT,
                        confidence FLOAT,
                        processing_time FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create indexes
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_file)"
                    )
                )
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id)"
                    )
                )
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_conversations_id ON conversations(conversation_id)"
                    )
                )

                # Create vector index for similarity search
                conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
                    ON embeddings USING ivfflat (embedding vector_cosine_ops) 
                    WITH (lists = 100)
                """
                    )
                )

                conn.commit()
                log.info("✅ Database tables created successfully")

        except Exception as e:
            log.error(f"❌ Error creating tables: {e}")
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
            session = self.SessionLocal()
            chunk_ids = []

            for chunk in chunks:
                # Insert chunk
                result = session.execute(
                    text(
                        """
                    INSERT INTO chunks (
                        content, source_file, page_number, chunk_index,
                        heading_text, heading_level, heading_number, parent_heading,
                        is_sub_chunk, sub_chunk_index, total_sub_chunks, chunk_type,
                        word_count, char_count
                    )
                    VALUES (
                        :content, :source_file, :page_number, :chunk_index,
                        :heading_text, :heading_level, :heading_number, :parent_heading,
                        :is_sub_chunk, :sub_chunk_index, :total_sub_chunks, :chunk_type,
                        :word_count, :char_count
                    )
                    RETURNING id
                """
                    ),
                    {
                        "content": chunk.content,
                        "source_file": chunk.source_file,
                        "page_number": chunk.page_number,
                        "chunk_index": chunk.chunk_index,
                        "heading_text": chunk.heading_text,
                        "heading_level": chunk.heading_level,
                        "heading_number": chunk.heading_number,
                        "parent_heading": chunk.parent_heading,
                        "is_sub_chunk": chunk.is_sub_chunk,
                        "sub_chunk_index": chunk.sub_chunk_index,
                        "total_sub_chunks": chunk.total_sub_chunks,
                        "chunk_type": chunk.chunk_type,
                        "word_count": chunk.word_count,
                        "char_count": chunk.char_count,
                    },
                )

                chunk_id = result.scalar()
                chunk_ids.append(chunk_id)

            session.commit()
            log.info(f"✅ Inserted {len(chunks)} chunks into database")
            return chunk_ids

        except Exception as e:
            session.rollback()
            log.error(f"❌ Error inserting chunks: {e}")
            raise
        finally:
            session.close()

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
            session = self.SessionLocal()

            for chunk_id, embedding in zip(chunk_ids, embeddings):
                # Convert numpy array to list for pgvector
                embedding_list = embedding.tolist()

                session.execute(
                    text(
                        """
                    INSERT INTO embeddings (chunk_id, embedding)
                    VALUES (:chunk_id, :embedding)
                    ON CONFLICT (chunk_id) DO UPDATE SET embedding = :embedding
                """
                    ),
                    {"chunk_id": chunk_id, "embedding": embedding_list},
                )

            session.commit()
            log.info(f"✅ Inserted {len(embeddings)} embeddings into database")

        except Exception as e:
            session.rollback()
            log.error(f"❌ Error inserting embeddings: {e}")
            raise
        finally:
            session.close()

    def get_chunk_count(self) -> int:
        """Get the total number of chunks in database"""
        try:
            session = self.SessionLocal()
            result = session.execute(text("SELECT COUNT(*) FROM chunks"))
            count = result.scalar()
            return count
        except Exception as e:
            log.error(f"❌ Error getting chunk count: {e}")
            return 0
        finally:
            session.close()

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Retrieve all chunks from the database"""
        try:
            session = self.SessionLocal()
            result = session.execute(
                text(
                    """
                SELECT id, content, source_file, page_number, heading_text
                FROM chunks ORDER BY id
            """
                )
            )
            rows = result.fetchall()
            return [
                {
                    "id": row[0],
                    "content": row[1],
                    "source_file": row[2],
                    "page_number": row[3],
                    "heading_text": row[4],
                }
                for row in rows
            ]
        except Exception as e:
            log.error(f"❌ Error retrieving all chunks: {e}")
            return []
        finally:
            session.close()

    def get_all_embeddings(self) -> tuple:
        """
        Get all embeddings from database

        Returns:
            Tuple of (chunk_ids, embeddings_array)
        """
        try:
            session = self.SessionLocal()
            result = session.execute(
                text(
                    """
                SELECT chunk_id, embedding
                FROM embeddings
                ORDER BY chunk_id
            """
                )
            )

            chunk_ids = []
            embeddings = []

            for chunk_id, embedding in result.fetchall():
                chunk_ids.append(chunk_id)
                # embedding is already a list from pgvector
                embeddings.append(np.array(embedding, dtype=np.float32))

            if embeddings:
                embeddings_array = np.vstack(embeddings)
            else:
                embeddings_array = np.array([])

            return chunk_ids, embeddings_array

        except Exception as e:
            log.error(f"❌ Error getting embeddings: {e}")
            raise
        finally:
            session.close()

    def delete_chunks_by_file(self, source_file: str) -> bool:
        """Delete all chunks and their embeddings for a specific file"""
        try:
            session = self.SessionLocal()

            # Delete embeddings first (due to foreign key)
            session.execute(
                text(
                    """
                DELETE FROM embeddings
                WHERE chunk_id IN (
                    SELECT id FROM chunks WHERE source_file = :source_file
                )
            """
                ),
                {"source_file": source_file},
            )

            # Delete chunks
            session.execute(
                text("DELETE FROM chunks WHERE source_file = :source_file"),
                {"source_file": source_file},
            )

            session.commit()
            log.info(f"✅ Deleted all chunks for file: {source_file}")
            return True

        except Exception as e:
            session.rollback()
            log.error(f"❌ Error deleting chunks for file {source_file}: {e}")
            return False
        finally:
            session.close()

    def clear_all_data(self):
        """Clear all data from database"""
        try:
            session = self.SessionLocal()

            session.execute(text("DELETE FROM embeddings"))
            session.execute(text("DELETE FROM chunks"))

            session.commit()
            log.info("✅ Cleared all data from database")

        except Exception as e:
            session.rollback()
            log.error(f"❌ Error clearing database: {e}")
            raise
        finally:
            session.close()

    def get_chunk_by_source_and_index(
        self, source_file: str, chunk_index: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get chunk by source file and chunk index

        Args:
            source_file: Source file name
            chunk_index: Chunk index

        Returns:
            Chunk dictionary or None if not found
        """
        try:
            session = self.SessionLocal()
            result = session.execute(
                text(
                    """
                SELECT id, content, source_file, page_number, chunk_index,
                       heading_text, heading_level, heading_number, parent_heading
                FROM chunks
                WHERE source_file = :source_file AND chunk_index = :chunk_index
                LIMIT 1
            """
                ),
                {"source_file": source_file, "chunk_index": chunk_index},
            )

            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "content": row[1],
                    "source_file": row[2],
                    "page_number": row[3],
                    "chunk_index": row[4],
                    "heading_text": row[5],
                    "heading_level": row[6],
                    "heading_number": row[7],
                    "parent_heading": row[8],
                }
            return None
        except Exception as e:
            log.error(f"❌ Error getting chunk by source and index: {e}")
            return None
        finally:
            session.close()

    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        try:
            session = self.SessionLocal()

            # Count chunks
            chunk_count = session.execute(text("SELECT COUNT(*) FROM chunks")).scalar()

            # Count embeddings
            embedding_count = session.execute(
                text("SELECT COUNT(*) FROM embeddings")
            ).scalar()

            # Count unique source files
            file_count = session.execute(
                text("SELECT COUNT(DISTINCT source_file) FROM chunks")
            ).scalar()

            return {
                "total_chunks": chunk_count,
                "total_embeddings": embedding_count,
                "unique_files": file_count,
            }

        except Exception as e:
            log.error(f"❌ Error getting database stats: {e}")
            raise
        finally:
            session.close()

    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            log.info("✅ Database connection closed")
