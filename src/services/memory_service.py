"""
Conversation Memory Service with Sliding Window + Summarization

This service provides persistent conversational memory with:
- Sliding window for recent messages
- Automatic summarization after N turns using LLM
- Memory vector embeddings for semantic search
- Integration with document retrieval
"""

import json
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import text

from src.services.postgres_database_service import PostgresDatabaseService
from src.services.embedding_service import EmbeddingService
from src.models.memory import (
    ConversationMessage,
    ConversationContext,
    MemoryConfig,
    MemoryStats,
    MessageRole,
)
from src.utils.logger import log

# Default configuration
DEFAULT_CONFIG = MemoryConfig(
    max_recent_turns=10,
    summarize_threshold=10,
    max_summary_length=500,
    overlap_turns=2,
    memory_search_top_k=3,
    memory_similarity_threshold=0.5,
)


class ConversationMemoryService:
    """Service for managing persistent conversational memory"""

    def __init__(
        self,
        db_service: PostgresDatabaseService = None,
        embedding_service: EmbeddingService = None,
        config: MemoryConfig = None,
    ):
        """
        Initialize memory service

        Args:
            db_service: PostgreSQL database service
            embedding_service: Embedding service for vector operations
            config: Memory configuration
        """
        self.db_service = db_service or PostgresDatabaseService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.config = config or DEFAULT_CONFIG
        self._init_memory_tables()

    def _init_memory_tables(self):
        """Create memory-related tables if they don't exist"""
        try:
            with self.db_service.engine.connect() as conn:
                # Create conversation_memory table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS conversation_memory (
                        id SERIAL PRIMARY KEY,
                        conversation_id VARCHAR(255) NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        content TEXT NOT NULL,
                        turn_number INTEGER NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB DEFAULT '{}'
                    )
                """
                    )
                )

                # Create memory_summaries table with vector embedding
                # Use EMBEDDING_DIMENSION from settings
                from config.settings import EMBEDDING_DIMENSION

                conn.execute(
                    text(
                        f"""
                    CREATE TABLE IF NOT EXISTS memory_summaries (
                        id SERIAL PRIMARY KEY,
                        conversation_id VARCHAR(255) NOT NULL,
                        summary TEXT NOT NULL,
                        turn_start INTEGER NOT NULL,
                        turn_end INTEGER NOT NULL,
                        embedding vector({EMBEDDING_DIMENSION}),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create indexes
                conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_conv_memory_conv_id 
                    ON conversation_memory(conversation_id)
                """
                    )
                )
                conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_conv_memory_turn 
                    ON conversation_memory(conversation_id, turn_number)
                """
                    )
                )
                conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_memory_summaries_conv_id 
                    ON memory_summaries(conversation_id)
                """
                    )
                )

                conn.commit()
                log.info("✅ Memory tables initialized successfully")

        except Exception as e:
            log.error(f"❌ Error initializing memory tables: {e}")
            raise

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Dict[str, Any] = None,
    ) -> int:
        """
        Add a message to conversation memory

        Args:
            conversation_id: Conversation identifier
            role: Message role (user/assistant)
            content: Message content
            metadata: Optional metadata

        Returns:
            Turn number of the added message
        """
        session = None
        try:
            session = self.db_service.SessionLocal()

            # Get current turn number
            result = session.execute(
                text(
                    """
                SELECT COALESCE(MAX(turn_number), 0) as max_turn
                FROM conversation_memory
                WHERE conversation_id = :conv_id
            """
                ),
                {"conv_id": conversation_id},
            )

            max_turn = result.fetchone()[0]
            new_turn = max_turn + 1

            # Insert message
            session.execute(
                text(
                    """
                INSERT INTO conversation_memory 
                (conversation_id, role, content, turn_number, metadata)
                VALUES (:conv_id, :role, :content, :turn, :metadata)
            """
                ),
                {
                    "conv_id": conversation_id,
                    "role": role,
                    "content": content,
                    "turn": new_turn,
                    "metadata": json.dumps(metadata or {}),
                },
            )

            session.commit()
            log.debug(
                f"📝 Added message to conversation {conversation_id}, turn {new_turn}"
            )

            # Check if summarization is needed
            if new_turn > 0 and new_turn % self.config.summarize_threshold == 0:
                self._trigger_summarization(conversation_id, new_turn)

            return new_turn

        except Exception as e:
            log.error(f"❌ Error adding message: {e}")
            if session:
                session.rollback()
            raise
        finally:
            if session:
                session.close()

    def add_exchange(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
        metadata: Dict[str, Any] = None,
    ) -> Tuple[int, int]:
        """
        Add a user-assistant exchange (2 messages)

        Args:
            conversation_id: Conversation identifier
            user_message: User's message
            assistant_message: Assistant's response
            metadata: Optional metadata

        Returns:
            Tuple of (user_turn, assistant_turn)
        """
        user_turn = self.add_message(conversation_id, "user", user_message, metadata)
        assistant_turn = self.add_message(
            conversation_id, "assistant", assistant_message, metadata
        )
        return user_turn, assistant_turn

    def get_conversation_context(
        self,
        conversation_id: str,
        query: str = None,
        include_memory_search: bool = True,
    ) -> ConversationContext:
        """
        Get conversation context with recent messages and relevant memory

        Args:
            conversation_id: Conversation identifier
            query: Current query for memory search (optional)
            include_memory_search: Whether to search memory summaries

        Returns:
            ConversationContext with recent messages and memory
        """
        session = None
        try:
            session = self.db_service.SessionLocal()

            # Get total turns
            result = session.execute(
                text(
                    """
                SELECT COUNT(*) as total
                FROM conversation_memory
                WHERE conversation_id = :conv_id
            """
                ),
                {"conv_id": conversation_id},
            )
            total_turns = result.fetchone()[0]

            # Get recent messages (within sliding window)
            result = session.execute(
                text(
                    """
                SELECT role, content, turn_number, timestamp
                FROM conversation_memory
                WHERE conversation_id = :conv_id
                ORDER BY turn_number DESC
                LIMIT :limit
            """
                ),
                {
                    "conv_id": conversation_id,
                    "limit": self.config.max_recent_turns
                    * 2,  # *2 for user+assistant pairs
                },
            )

            recent_messages = []
            for row in result.fetchall():
                recent_messages.append(
                    ConversationMessage(
                        conversation_id=conversation_id,
                        role=MessageRole(row[0]),
                        content=row[1],
                        timestamp=row[3],
                    )
                )

            # Reverse to get chronological order
            recent_messages.reverse()

            # Get memory summaries
            memory_summaries = []
            has_long_term_memory = False

            if include_memory_search and query:
                # Search memory by semantic similarity
                memory_summaries = self._search_memory_summaries(conversation_id, query)
                has_long_term_memory = len(memory_summaries) > 0
            else:
                # Get all summaries for this conversation
                result = session.execute(
                    text(
                        """
                    SELECT summary
                    FROM memory_summaries
                    WHERE conversation_id = :conv_id
                    ORDER BY turn_end DESC
                    LIMIT :limit
                """
                    ),
                    {
                        "conv_id": conversation_id,
                        "limit": self.config.memory_search_top_k,
                    },
                )
                memory_summaries = [row[0] for row in result.fetchall()]
                has_long_term_memory = len(memory_summaries) > 0

            return ConversationContext(
                conversation_id=conversation_id,
                recent_messages=recent_messages,
                memory_summaries=memory_summaries,
                total_turns=total_turns,
                has_long_term_memory=has_long_term_memory,
            )

        except Exception as e:
            log.error(f"❌ Error getting conversation context: {e}")
            return ConversationContext(conversation_id=conversation_id)
        finally:
            if session:
                session.close()

    def _search_memory_summaries(
        self,
        conversation_id: str,
        query: str,
    ) -> List[str]:
        """
        Search memory summaries by semantic similarity

        Args:
            conversation_id: Conversation identifier
            query: Search query

        Returns:
            List of relevant memory summaries
        """
        session = None
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.create_embedding(query)
            if query_embedding is None:
                return []

            embedding_str = (
                "[" + ",".join(str(x) for x in query_embedding.tolist()) + "]"
            )

            session = self.db_service.SessionLocal()

            # Search by vector similarity
            result = session.execute(
                text(
                    """
                SELECT summary, 1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
                FROM memory_summaries
                WHERE conversation_id = :conv_id
                AND embedding IS NOT NULL
                AND 1 - (embedding <=> CAST(:query_embedding AS vector)) > :threshold
                ORDER BY similarity DESC
                LIMIT :limit
            """
                ),
                {
                    "conv_id": conversation_id,
                    "query_embedding": embedding_str,
                    "threshold": self.config.memory_similarity_threshold,
                    "limit": self.config.memory_search_top_k,
                },
            )

            summaries = [row[0] for row in result.fetchall()]

            if summaries:
                log.info(f"🧠 Found {len(summaries)} relevant memory summaries")

            return summaries

        except Exception as e:
            log.error(f"❌ Error searching memory summaries: {e}")
            return []
        finally:
            if session:
                session.close()

    def _trigger_summarization(self, conversation_id: str, current_turn: int):
        """
        Trigger summarization of older messages

        Args:
            conversation_id: Conversation identifier
            current_turn: Current turn number
        """
        try:
            log.info(f"🔄 Triggering summarization for conversation {conversation_id}")

            session = None
            session = self.db_service.SessionLocal()

            # Get the last summary end turn (or 0 if none)
            result = session.execute(
                text(
                    """
                SELECT COALESCE(MAX(turn_end), 0) as last_end
                FROM memory_summaries
                WHERE conversation_id = :conv_id
            """
                ),
                {"conv_id": conversation_id},
            )
            last_summarized_turn = result.fetchone()[0]

            # Calculate turns to summarize (with overlap)
            start_turn = max(1, last_summarized_turn - self.config.overlap_turns + 1)
            end_turn = current_turn - self.config.max_recent_turns

            if end_turn <= start_turn:
                log.debug("Not enough turns to summarize yet")
                return

            # Get messages to summarize
            result = session.execute(
                text(
                    """
                SELECT role, content, turn_number
                FROM conversation_memory
                WHERE conversation_id = :conv_id
                AND turn_number >= :start_turn
                AND turn_number <= :end_turn
                ORDER BY turn_number ASC
            """
                ),
                {
                    "conv_id": conversation_id,
                    "start_turn": start_turn,
                    "end_turn": end_turn,
                },
            )

            messages = result.fetchall()
            if not messages:
                return

            # Generate summary using LLM
            summary = self._generate_summary(messages)

            if summary:
                # Generate embedding for the summary
                embedding = self.embedding_service.generate_embedding(summary)
                embedding_str = None
                if embedding is not None:
                    embedding_str = (
                        "[" + ",".join(str(x) for x in embedding.tolist()) + "]"
                    )

                # Save summary
                session.execute(
                    text(
                        """
                    INSERT INTO memory_summaries 
                    (conversation_id, summary, turn_start, turn_end, embedding)
                    VALUES (:conv_id, :summary, :start, :end, CAST(:embedding AS vector))
                """
                    ),
                    {
                        "conv_id": conversation_id,
                        "summary": summary,
                        "start": start_turn,
                        "end": end_turn,
                        "embedding": embedding_str,
                    },
                )

                session.commit()
                log.info(f"✅ Created memory summary for turns {start_turn}-{end_turn}")

        except Exception as e:
            log.error(f"❌ Error during summarization: {e}")
            if session:
                session.rollback()
        finally:
            if session:
                session.close()

    def _generate_summary(self, messages: List[Tuple]) -> Optional[str]:
        """
        Generate summary of messages using LLM

        Args:
            messages: List of (role, content, turn_number) tuples

        Returns:
            Summary string or None
        """
        try:
            from src.services.gemini_service import generate_response

            # Format messages for summarization
            conversation_text = "\n".join(
                [f"{msg[0].upper()}: {msg[1]}" for msg in messages]
            )

            prompt = f"""Hãy tóm tắt ngắn gọn cuộc hội thoại sau đây, giữ lại các thông tin quan trọng và ngữ cảnh chính. Tóm tắt bằng tiếng Việt, tối đa {self.config.max_summary_length} ký tự.

Cuộc hội thoại:
{conversation_text}

Tóm tắt:"""

            summary = generate_response(prompt, temperature=0.3)

            if summary:
                # Truncate if too long
                if len(summary) > self.config.max_summary_length:
                    summary = summary[: self.config.max_summary_length] + "..."

                log.debug(f"📝 Generated summary: {summary[:100]}...")
                return summary

            return None

        except Exception as e:
            log.error(f"❌ Error generating summary: {e}")
            return None

    def format_context_for_prompt(
        self,
        context: ConversationContext,
        include_memory: bool = True,
    ) -> str:
        """
        Format conversation context for LLM prompt

        Args:
            context: Conversation context
            include_memory: Whether to include memory summaries

        Returns:
            Formatted context string
        """
        parts = []

        # Add memory summaries first (long-term context)
        if include_memory and context.memory_summaries:
            memory_text = "\n".join([f"- {s}" for s in context.memory_summaries])
            parts.append(f"📚 Ngữ cảnh từ cuộc hội thoại trước:\n{memory_text}")

        # Add recent messages
        if context.recent_messages:
            recent_text = "\n".join(
                [
                    f"{'Người dùng' if m.role == MessageRole.USER else 'Trợ lý'}: {m.content}"
                    for m in context.recent_messages[
                        -self.config.max_recent_turns * 2 :
                    ]
                ]
            )
            parts.append(f"💬 Hội thoại gần đây:\n{recent_text}")

        return "\n\n".join(parts) if parts else ""

    def get_memory_stats(self, conversation_id: str) -> MemoryStats:
        """
        Get statistics about conversation memory

        Args:
            conversation_id: Conversation identifier

        Returns:
            MemoryStats object
        """
        session = None
        try:
            session = self.db_service.SessionLocal()

            # Get message stats
            result = session.execute(
                text(
                    """
                SELECT 
                    COUNT(*) as total_messages,
                    MAX(turn_number) as total_turns,
                    MIN(timestamp) as oldest,
                    MAX(timestamp) as newest,
                    SUM(LENGTH(content)) as total_size
                FROM conversation_memory
                WHERE conversation_id = :conv_id
            """
                ),
                {"conv_id": conversation_id},
            )

            row = result.fetchone()

            # Get summary count
            result = session.execute(
                text(
                    """
                SELECT COUNT(*) as total_summaries
                FROM memory_summaries
                WHERE conversation_id = :conv_id
            """
                ),
                {"conv_id": conversation_id},
            )

            summary_count = result.fetchone()[0]

            return MemoryStats(
                conversation_id=conversation_id,
                total_messages=row[0] or 0,
                total_summaries=summary_count or 0,
                total_turns=row[1] or 0,
                oldest_message=row[2],
                newest_message=row[3],
                memory_size_bytes=row[4] or 0,
            )

        except Exception as e:
            log.error(f"❌ Error getting memory stats: {e}")
            return MemoryStats(
                conversation_id=conversation_id,
                total_messages=0,
                total_summaries=0,
                total_turns=0,
                oldest_message=None,
                newest_message=None,
                memory_size_bytes=0,
            )
        finally:
            if session:
                session.close()

    def clear_conversation_memory(self, conversation_id: str) -> bool:
        """
        Clear all memory for a conversation

        Args:
            conversation_id: Conversation identifier

        Returns:
            True if successful
        """
        session = None
        try:
            session = self.db_service.SessionLocal()

            session.execute(
                text(
                    """
                DELETE FROM conversation_memory
                WHERE conversation_id = :conv_id
            """
                ),
                {"conv_id": conversation_id},
            )

            session.execute(
                text(
                    """
                DELETE FROM memory_summaries
                WHERE conversation_id = :conv_id
            """
                ),
                {"conv_id": conversation_id},
            )

            session.commit()
            log.info(f"🗑️ Cleared memory for conversation {conversation_id}")
            return True

        except Exception as e:
            log.error(f"❌ Error clearing memory: {e}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close()

    def search_all_memories(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search across all conversation memories (for global context)

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of relevant memories with metadata
        """
        session = None
        try:
            query_embedding = self.embedding_service.create_embedding(query)
            if query_embedding is None:
                return []

            embedding_str = (
                "[" + ",".join(str(x) for x in query_embedding.tolist()) + "]"
            )

            session = self.db_service.SessionLocal()

            result = session.execute(
                text(
                    """
                SELECT 
                    conversation_id,
                    summary,
                    turn_start,
                    turn_end,
                    1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
                FROM memory_summaries
                WHERE embedding IS NOT NULL
                AND 1 - (embedding <=> CAST(:query_embedding AS vector)) > :threshold
                ORDER BY similarity DESC
                LIMIT :limit
            """
                ),
                {
                    "query_embedding": embedding_str,
                    "threshold": self.config.memory_similarity_threshold,
                    "limit": top_k,
                },
            )

            memories = []
            for row in result.fetchall():
                memories.append(
                    {
                        "conversation_id": row[0],
                        "summary": row[1],
                        "turn_range": f"{row[2]}-{row[3]}",
                        "similarity": float(row[4]),
                    }
                )

            return memories

        except Exception as e:
            log.error(f"❌ Error searching all memories: {e}")
            return []
        finally:
            if session:
                session.close()
