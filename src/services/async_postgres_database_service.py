"""
Async PostgreSQL database service for managing document chunks and embeddings with pgvector
"""

from typing import List, Optional, Dict, Any, AsyncGenerator
import numpy as np
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from src.utils.logger import log
from src.models.schemas import DocumentChunk
from config.settings import DATABASE_URL
from contextlib import asynccontextmanager


class AsyncPostgresDatabaseService:
    """Async service for PostgreSQL database operations with pgvector"""

    def __init__(self, database_url: str = DATABASE_URL):
        """
        Initialize async PostgreSQL database service

        Args:
            database_url: PostgreSQL connection string
        """
        # Convert sync URL to async URL for asyncpg
        if database_url and database_url.startswith("postgresql://"):
            self.database_url = database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        elif database_url and database_url.startswith("postgres://"):
            self.database_url = database_url.replace(
                "postgres://", "postgresql+asyncpg://", 1
            )
        else:
            self.database_url = database_url

        self.engine = None
        self.async_session_factory = None
        self._initialized = False

    async def initialize(self):
        """Initialize database connection and create tables"""
        if self._initialized:
            return

        try:
            # Create async engine with pgbouncer compatibility
            # Use NullPool and connect_args to disable prepared statements
            from sqlalchemy.pool import NullPool

            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                poolclass=NullPool,  # Use NullPool for pgbouncer compatibility
                connect_args={
                    "statement_cache_size": 0,  # Disable prepared statements for pgbouncer
                    "prepared_statement_cache_size": 0,  # Also disable prepared statement cache
                },
            )

            # Create async session factory
            self.async_session_factory = async_sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

            # Test connection
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                log.info("✅ Async PostgreSQL connection successful")

                # Check pgvector extension
                result = await conn.execute(
                    text("SELECT * FROM pg_extension WHERE extname = 'vector'")
                )
                if result.fetchone():
                    log.info("✅ pgvector extension is installed")
                else:
                    log.warning(
                        "⚠️ pgvector extension not found, attempting to create..."
                    )
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    log.info("✅ pgvector extension created")

            # Create tables
            await self._create_tables()
            self._initialized = True

        except Exception as e:
            log.error(f"❌ Error initializing async database: {e}")
            raise

    async def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            async with self.engine.begin() as conn:
                # Create chunks table
                await conn.execute(
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

                # Create embeddings table
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS embeddings (
                        id SERIAL PRIMARY KEY,
                        chunk_id INTEGER NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
                        embedding vector(768) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create indexes for better performance
                await conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_chunks_source_file 
                    ON chunks(source_file)
                """
                    )
                )

                await conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_chunks_heading_text 
                    ON chunks(heading_text)
                """
                    )
                )

                await conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id 
                    ON embeddings(chunk_id)
                """
                    )
                )

                # Create vector similarity index
                await conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
                    ON embeddings USING ivfflat (embedding vector_cosine_ops) 
                    WITH (lists = 100)
                """
                    )
                )

                log.info("✅ Database tables and indexes created successfully")

        except Exception as e:
            log.error(f"❌ Error creating tables: {e}")
            raise

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        if not self._initialized:
            await self.initialize()

        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def store_chunks_and_embeddings(
        self, chunks: List[DocumentChunk], embeddings: List[np.ndarray]
    ) -> List[int]:
        """
        Store document chunks and their embeddings

        Args:
            chunks: List of document chunks
            embeddings: List of embedding vectors

        Returns:
            List of chunk IDs
        """
        if not chunks or not embeddings:
            return []

        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        chunk_ids = []

        async with self.get_session() as session:
            try:
                # Insert chunks
                for chunk in chunks:
                    result = await session.execute(
                        text(
                            """
                        INSERT INTO chunks (
                            content, source_file, page_number, chunk_index,
                            heading_text, heading_level, heading_number,
                            parent_heading, is_sub_chunk, sub_chunk_index,
                            total_sub_chunks, chunk_type, word_count, char_count
                        ) VALUES (
                            :content, :source_file, :page_number, :chunk_index,
                            :heading_text, :heading_level, :heading_number,
                            :parent_heading, :is_sub_chunk, :sub_chunk_index,
                            :total_sub_chunks, :chunk_type, :word_count, :char_count
                        ) RETURNING id
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
                    chunk_id = result.fetchone()[0]
                    chunk_ids.append(chunk_id)

                # Insert embeddings
                for chunk_id, embedding in zip(chunk_ids, embeddings):
                    # Convert numpy array to list for PostgreSQL
                    embedding_list = embedding.tolist()

                    await session.execute(
                        text(
                            """
                        INSERT INTO embeddings (chunk_id, embedding)
                        VALUES (:chunk_id, :embedding)
                        """
                        ),
                        {"chunk_id": chunk_id, "embedding": embedding_list},
                    )

                await session.commit()
                log.info(f"✅ Stored {len(chunks)} chunks and embeddings")
                return chunk_ids

            except Exception as e:
                await session.rollback()
                log.error(f"❌ Error storing chunks and embeddings: {e}")
                raise

    async def search_similar_chunks(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        source_file: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            source_file: Optional source file filter

        Returns:
            List of similar chunks with metadata
        """
        query_list = query_embedding.tolist()

        async with self.get_session() as session:
            try:
                # Build query with optional source file filter
                where_clause = ""
                params = {"embedding": query_list, "top_k": top_k}

                if source_file:
                    where_clause = "WHERE c.source_file = :source_file"
                    params["source_file"] = source_file

                query = f"""
                SELECT 
                    c.id,
                    c.content,
                    c.source_file,
                    c.page_number,
                    c.chunk_index,
                    c.heading_text,
                    c.heading_level,
                    c.heading_number,
                    c.parent_heading,
                    c.is_sub_chunk,
                    c.sub_chunk_index,
                    c.total_sub_chunks,
                    c.chunk_type,
                    c.word_count,
                    c.char_count,
                    c.created_at,
                    1 - (e.embedding <=> :embedding) AS similarity_score
                FROM chunks c
                JOIN embeddings e ON c.id = e.chunk_id
                {where_clause}
                ORDER BY e.embedding <=> :embedding
                LIMIT :top_k
                """

                result = await session.execute(text(query), params)
                rows = result.fetchall()

                results = []
                for row in rows:
                    results.append(
                        {
                            "id": row[0],
                            "content": row[1],
                            "source_file": row[2],
                            "page_number": row[3],
                            "chunk_index": row[4],
                            "heading_text": row[5],
                            "heading_level": row[6],
                            "heading_number": row[7],
                            "parent_heading": row[8],
                            "is_sub_chunk": row[9],
                            "sub_chunk_index": row[10],
                            "total_sub_chunks": row[11],
                            "chunk_type": row[12],
                            "word_count": row[13],
                            "char_count": row[14],
                            "created_at": row[15],
                            "similarity_score": float(row[16]),
                        }
                    )

                log.info(f"Found {len(results)} similar chunks")
                return results

            except Exception as e:
                log.error(f"❌ Error searching similar chunks: {e}")
                raise

    async def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict[str, Any]]:
        """Get chunk by ID"""
        async with self.get_session() as session:
            try:
                result = await session.execute(
                    text(
                        """
                    SELECT 
                        id, content, source_file, page_number, chunk_index,
                        heading_text, heading_level, heading_number,
                        parent_heading, is_sub_chunk, sub_chunk_index,
                        total_sub_chunks, chunk_type, word_count, char_count,
                        created_at
                    FROM chunks WHERE id = :chunk_id
                    """
                    ),
                    {"chunk_id": chunk_id},
                )

                row = result.fetchone()
                if not row:
                    return None

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
                    "is_sub_chunk": row[9],
                    "sub_chunk_index": row[10],
                    "total_sub_chunks": row[11],
                    "chunk_type": row[12],
                    "word_count": row[13],
                    "char_count": row[14],
                    "created_at": row[15],
                }

            except Exception as e:
                log.error(f"❌ Error getting chunk by ID: {e}")
                raise

    async def delete_document_chunks(self, source_file: str) -> int:
        """
        Delete all chunks for a specific document

        Args:
            source_file: Source file name

        Returns:
            Number of deleted chunks
        """
        async with self.get_session() as session:
            try:
                # Delete embeddings first (due to foreign key constraint)
                await session.execute(
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
                result = await session.execute(
                    text("DELETE FROM chunks WHERE source_file = :source_file"),
                    {"source_file": source_file},
                )

                deleted_count = result.rowcount
                await session.commit()

                log.info(f"✅ Deleted {deleted_count} chunks for {source_file}")
                return deleted_count

            except Exception as e:
                await session.rollback()
                log.error(f"❌ Error deleting document chunks: {e}")
                raise

    async def get_document_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        async with self.get_session() as session:
            try:
                # Get chunk count by source file
                result = await session.execute(
                    text(
                        """
                    SELECT 
                        source_file,
                        COUNT(*) as chunk_count,
                        MIN(created_at) as first_added,
                        MAX(created_at) as last_added
                    FROM chunks 
                    GROUP BY source_file
                    ORDER BY chunk_count DESC
                    """
                    )
                )

                documents = []
                total_chunks = 0

                for row in result.fetchall():
                    doc_info = {
                        "source_file": row[0],
                        "chunk_count": row[1],
                        "first_added": row[2],
                        "last_added": row[3],
                    }
                    documents.append(doc_info)
                    total_chunks += row[1]

                # Get total embedding count
                result = await session.execute(text("SELECT COUNT(*) FROM embeddings"))
                total_embeddings = result.fetchone()[0]

                return {
                    "total_documents": len(documents),
                    "total_chunks": total_chunks,
                    "total_embeddings": total_embeddings,
                    "documents": documents,
                }

            except Exception as e:
                log.error(f"❌ Error getting document stats: {e}")
                raise

    async def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            if not self._initialized:
                await self.initialize()

            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            log.error(f"❌ Database health check failed: {e}")
            return False

    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            log.info("✅ Database connection closed")


# Global async database service instance
_async_db_service = None


async def get_async_database_service() -> AsyncPostgresDatabaseService:
    """Get or create async database service instance"""
    global _async_db_service

    if _async_db_service is None:
        _async_db_service = AsyncPostgresDatabaseService()
        await _async_db_service.initialize()

    return _async_db_service
