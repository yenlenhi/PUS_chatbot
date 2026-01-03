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
                # Use EMBEDDING_DIMENSION from settings (default: 384)
                from config.settings import EMBEDDING_DIMENSION

                conn.execute(
                    text(
                        f"""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        id SERIAL PRIMARY KEY,
                        chunk_id INTEGER NOT NULL UNIQUE,
                        embedding vector({EMBEDDING_DIMENSION}),
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
                        conversation_id VARCHAR(255) NOT NULL,
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

    def get_all_chunks(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """Retrieve all chunks from the database

        Args:
            active_only: If True, only return active chunks (is_active=true)
        """
        try:
            session = self.SessionLocal()

            if active_only:
                query = """
                    SELECT id, content, source_file, page_number, heading_text
                    FROM chunks WHERE is_active = true ORDER BY id
                """
            else:
                query = """
                    SELECT id, content, source_file, page_number, heading_text
                    FROM chunks ORDER BY id
                """

            result = session.execute(text(query))
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

    # ==================== Chat History Methods ====================

    def save_conversation(
        self,
        conversation_id: str,
        user_message: str,
        assistant_response: str,
        sources: List[str] = None,
        confidence: float = 0.0,
        processing_time: float = 0.0,
        images: List[str] = None,
    ) -> int:
        """
        Save a conversation turn to database

        Args:
            conversation_id: Unique conversation ID
            user_message: User's message
            assistant_response: Assistant's response
            sources: List of source documents
            confidence: Confidence score
            processing_time: Processing time in seconds
            images: List of image URLs from Supabase Storage

        Returns:
            ID of inserted conversation record
        """
        try:
            session = self.SessionLocal()
            import json

            sources_json = json.dumps(sources or [], ensure_ascii=False)
            images_json = (
                json.dumps(images or [], ensure_ascii=False) if images else None
            )

            result = session.execute(
                text(
                    """
                INSERT INTO conversations 
                (conversation_id, user_message, assistant_response, sources, confidence, processing_time, images)
                VALUES (:conversation_id, :user_message, :assistant_response, :sources, :confidence, :processing_time, :images)
                RETURNING id
            """
                ),
                {
                    "conversation_id": conversation_id,
                    "user_message": user_message,
                    "assistant_response": assistant_response,
                    "sources": sources_json,
                    "confidence": confidence,
                    "processing_time": processing_time,
                    "images": images_json,
                },
            )

            record_id = result.scalar()
            session.commit()
            log.debug(f"✅ Saved conversation turn: {conversation_id}")
            return record_id

        except Exception as e:
            session.rollback()
            log.error(f"❌ Error saving conversation: {e}")
            return -1
        finally:
            session.close()

    def get_all_conversations(
        self,
        limit: int = 100,
        offset: int = 0,
        search_term: str = None,
        status_filter: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all conversations with pagination and filtering

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            search_term: Optional search term for filtering
            status_filter: Optional status filter ('active', 'completed', 'all')

        Returns:
            List of conversation summaries
        """
        try:
            session = self.SessionLocal()

            # Build query with optional filters
            query = """
                WITH conversation_stats AS (
                    SELECT 
                        conversation_id,
                        COUNT(*) as message_count,
                        MIN(created_at) as first_message,
                        MAX(created_at) as last_message,
                        AVG(confidence) as avg_confidence,
                        SUM(processing_time) as total_processing_time
                    FROM conversations
                    GROUP BY conversation_id
                )
                SELECT 
                    cs.conversation_id,
                    cs.message_count,
                    cs.first_message,
                    cs.last_message,
                    cs.avg_confidence,
                    cs.total_processing_time,
                    (SELECT user_message FROM conversations 
                     WHERE conversation_id = cs.conversation_id 
                     ORDER BY created_at ASC LIMIT 1) as first_query
                FROM conversation_stats cs
            """

            params = {"limit": limit, "offset": offset}

            if search_term:
                query += """
                    WHERE cs.conversation_id IN (
                        SELECT DISTINCT conversation_id FROM conversations
                        WHERE user_message ILIKE :search_term 
                           OR assistant_response ILIKE :search_term
                    )
                """
                params["search_term"] = f"%{search_term}%"

            query += " ORDER BY cs.last_message DESC LIMIT :limit OFFSET :offset"

            result = session.execute(text(query), params)
            rows = result.fetchall()

            conversations = []
            for row in rows:
                # Determine status based on last activity
                from datetime import datetime

                last_message = row[3]
                is_active = (
                    datetime.now() - last_message
                ).total_seconds() < 1800  # 30 minutes

                if status_filter and status_filter != "all":
                    if status_filter == "active" and not is_active:
                        continue
                    if status_filter == "completed" and is_active:
                        continue

                conversations.append(
                    {
                        "id": row[0],
                        "conversation_id": row[0],
                        "message_count": row[1],
                        "first_message": row[2].isoformat() if row[2] else None,
                        "last_message": row[3].isoformat() if row[3] else None,
                        "avg_confidence": round(row[4], 2) if row[4] else 0,
                        "total_processing_time": round(row[5], 2) if row[5] else 0,
                        "first_query": (
                            row[6][:100] + "..."
                            if row[6] and len(row[6]) > 100
                            else row[6]
                        ),
                        "status": "active" if is_active else "completed",
                    }
                )

            return conversations

        except Exception as e:
            log.error(f"❌ Error getting conversations: {e}")
            return []
        finally:
            session.close()

    def get_conversation_detail(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get detailed conversation history

        Args:
            conversation_id: Conversation ID

        Returns:
            Dictionary with conversation details and messages
        """
        try:
            session = self.SessionLocal()
            import json

            result = session.execute(
                text(
                    """
                SELECT id, user_message, assistant_response, sources, 
                       confidence, processing_time, created_at, images
                FROM conversations
                WHERE conversation_id = :conversation_id
                ORDER BY created_at ASC
            """
                ),
                {"conversation_id": conversation_id},
            )

            rows = result.fetchall()
            if not rows:
                return None

            messages = []
            total_processing_time = 0
            avg_confidence = 0

            for row in rows:
                sources = []
                if row[3]:
                    try:
                        sources = json.loads(row[3])
                    except:
                        sources = []

                images = []
                if row[7]:  # images column
                    try:
                        images = json.loads(row[7])
                    except:
                        images = []

                messages.append(
                    {
                        "id": row[0],
                        "user_message": row[1],
                        "assistant_response": row[2],
                        "sources": sources,
                        "confidence": row[4],
                        "processing_time": row[5],
                        "timestamp": row[6].isoformat() if row[6] else None,
                        "images": images,
                    }
                )
                total_processing_time += row[5] or 0
                avg_confidence += row[4] or 0

            if messages:
                avg_confidence = avg_confidence / len(messages)

            return {
                "conversation_id": conversation_id,
                "message_count": len(messages),
                "messages": messages,
                "total_processing_time": round(total_processing_time, 2),
                "avg_confidence": round(avg_confidence, 2),
                "first_message": messages[0]["timestamp"] if messages else None,
                "last_message": messages[-1]["timestamp"] if messages else None,
            }

        except Exception as e:
            log.error(f"❌ Error getting conversation detail: {e}")
            return None
        finally:
            session.close()

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and all its messages

        Args:
            conversation_id: Conversation ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.SessionLocal()

            result = session.execute(
                text(
                    "DELETE FROM conversations WHERE conversation_id = :conversation_id"
                ),
                {"conversation_id": conversation_id},
            )

            session.commit()
            deleted_count = result.rowcount
            log.info(
                f"✅ Deleted conversation: {conversation_id} ({deleted_count} messages)"
            )
            return deleted_count > 0

        except Exception as e:
            session.rollback()
            log.error(f"❌ Error deleting conversation: {e}")
            return False
        finally:
            session.close()

    def get_conversation_stats(self) -> Dict[str, Any]:
        """
        Get chat history statistics

        Returns:
            Dictionary with various statistics
        """
        try:
            session = self.SessionLocal()

            # Total conversations
            total_conversations = session.execute(
                text("SELECT COUNT(DISTINCT conversation_id) FROM conversations")
            ).scalar()

            # Total messages
            total_messages = session.execute(
                text("SELECT COUNT(*) FROM conversations")
            ).scalar()

            # Today's conversations
            today_conversations = session.execute(
                text(
                    """
                SELECT COUNT(DISTINCT conversation_id) FROM conversations
                WHERE DATE(created_at) = CURRENT_DATE
            """
                )
            ).scalar()

            # Average confidence
            avg_confidence = session.execute(
                text("SELECT AVG(confidence) FROM conversations")
            ).scalar()

            # Average processing time
            avg_processing_time = session.execute(
                text("SELECT AVG(processing_time) FROM conversations")
            ).scalar()

            # Popular topics (based on first message keywords)
            popular_topics = session.execute(
                text(
                    """
                SELECT 
                    CASE 
                        WHEN user_message ILIKE '%tuyển sinh%' THEN 'Tuyển sinh'
                        WHEN user_message ILIKE '%học phí%' OR user_message ILIKE '%chi phí%' THEN 'Học phí'
                        WHEN user_message ILIKE '%đào tạo%' OR user_message ILIKE '%chương trình%' THEN 'Đào tạo'
                        WHEN user_message ILIKE '%ký túc xá%' OR user_message ILIKE '%nội trú%' THEN 'Ký túc xá'
                        WHEN user_message ILIKE '%việc làm%' OR user_message ILIKE '%nghề nghiệp%' THEN 'Việc làm'
                        ELSE 'Khác'
                    END as topic,
                    COUNT(*) as count
                FROM conversations
                GROUP BY topic
                ORDER BY count DESC
                LIMIT 5
            """
                )
            ).fetchall()

            # Active conversations (last 30 minutes)
            active_conversations = session.execute(
                text(
                    """
                SELECT COUNT(DISTINCT conversation_id) FROM conversations
                WHERE created_at > NOW() - INTERVAL '30 minutes'
            """
                )
            ).scalar()

            return {
                "total_conversations": total_conversations or 0,
                "total_messages": total_messages or 0,
                "today_conversations": today_conversations or 0,
                "active_conversations": active_conversations or 0,
                "avg_confidence": round(avg_confidence or 0, 2),
                "avg_processing_time": round(avg_processing_time or 0, 2),
                "popular_topics": [
                    {"topic": row[0], "count": row[1]} for row in popular_topics
                ],
            }

        except Exception as e:
            log.error(f"❌ Error getting conversation stats: {e}")
            return {
                "total_conversations": 0,
                "total_messages": 0,
                "today_conversations": 0,
                "active_conversations": 0,
                "avg_confidence": 0,
                "avg_processing_time": 0,
                "popular_topics": [],
            }
        finally:
            session.close()

    def export_conversations(
        self, start_date: str = None, end_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        Export conversations for a date range

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of all conversations with messages
        """
        try:
            session = self.SessionLocal()
            import json

            query = """
                SELECT conversation_id, user_message, assistant_response, 
                       sources, confidence, processing_time, created_at
                FROM conversations
            """
            params = {}

            if start_date and end_date:
                query += " WHERE DATE(created_at) BETWEEN :start_date AND :end_date"
                params["start_date"] = start_date
                params["end_date"] = end_date

            query += " ORDER BY conversation_id, created_at"

            result = session.execute(text(query), params)
            rows = result.fetchall()

            conversations = {}
            for row in rows:
                conv_id = row[0]
                if conv_id not in conversations:
                    conversations[conv_id] = {
                        "conversation_id": conv_id,
                        "messages": [],
                    }

                sources = []
                if row[3]:
                    try:
                        sources = json.loads(row[3])
                    except:
                        sources = []

                conversations[conv_id]["messages"].append(
                    {
                        "user_message": row[1],
                        "assistant_response": row[2],
                        "sources": sources,
                        "confidence": row[4],
                        "processing_time": row[5],
                        "timestamp": row[6].isoformat() if row[6] else None,
                    }
                )

            return list(conversations.values())

        except Exception as e:
            log.error(f"❌ Error exporting conversations: {e}")
            return []
        finally:
            session.close()

    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            log.info("✅ Database connection closed")
