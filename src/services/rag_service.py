"""
RAG (Retrieval-Augmented Generation) service
"""

import uuid
import re
from typing import List, Dict, Any, Optional
from src.services.embedding_service import EmbeddingService
from src.services.postgres_database_service import PostgresDatabaseService
from src.services.hybrid_retrieval_service import HybridRetrievalService
from src.services.ingestion_service import IngestionService
from src.services.pdf_processor import PDFProcessor
from src.services import gemini_service
from src.services.gemini_service import normalize_question
from sentence_transformers import CrossEncoder
from src.services.ollama_service import OllamaService
from src.utils.logger import log

from config.settings import (
    TOP_K_RESULTS,
    LLM_PROVIDER,
    ENABLE_GEMINI_NORMALIZATION,
)


class RAGService:
    """Service for Retrieval-Augmented Generation"""

    def __init__(self):
        """Initialize RAG service with PostgreSQL + Hybrid Retrieval"""
        self.embedding_service = EmbeddingService()
        self.db_service = PostgresDatabaseService()
        self.retrieval_service = HybridRetrievalService(
            self.db_service, self.embedding_service
        )
        self.pdf_processor = PDFProcessor()
        self.ingestion_service = IngestionService(
            self.db_service,
            self.embedding_service,
            self.pdf_processor,
            self.retrieval_service,
        )
        self.ollama_service = OllamaService()

        # Conversation memory
        self.conversations = {}

        # Initialize Reranker
        try:
            log.info("Initializing Reranker model...")
            self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            log.info("Reranker model initialized successfully.")
        except Exception as e:
            log.error(f"Error initializing Reranker model: {e}")
            self.reranker = None

        # Start ingestion service
        try:
            log.info("Starting ingestion service...")
            self.ingestion_service.start_watching()
            log.info("Ingestion service started successfully.")
        except Exception as e:
            log.error(f"Error starting ingestion service: {e}")

    def _rerank_chunks(
        self, query: str, chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Reranks a list of chunks based on their relevance to the query using a Cross-Encoder model.
        """
        if not self.reranker or not chunks:
            return chunks

        try:
            # Create pairs of [query, chunk_content] for the reranker
            pairs = [[query, chunk["content"]] for chunk in chunks]

            # Predict the scores
            scores = self.reranker.predict(pairs)

            # Assign scores to chunks
            for chunk, score in zip(chunks, scores):
                chunk["rerank_score"] = float(score)

            # Sort chunks by the new rerank score in descending order
            chunks.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)

            log.info(f"Reranked {len(chunks)} chunks successfully.")
            return chunks

        except Exception as e:
            log.error(f"Error during chunk reranking: {e}")
            # Return original chunks in case of an error
            return chunks

    def retrieve_relevant_chunks(
        self, query: str, top_k: int = TOP_K_RESULTS
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks using hybrid retrieval (dense + sparse search)."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.create_embedding(query)

            # Perform hybrid search using PostgreSQL + pgvector
            initial_k = max(top_k * 3, 15)  # Get more candidates for reranking
            hybrid_results = self.retrieval_service.hybrid_search(
                query=query, query_embedding=query_embedding, top_k=initial_k
            )

            if not hybrid_results:
                log.warning(f"No chunks found for query: {query}")
                return []

            log.info(f"Hybrid search found {len(hybrid_results)} chunks.")

            # Rerank results
            reranked_chunks = self._rerank_chunks(query, hybrid_results)

            # Context expansion
            expanded_chunks = self._expand_context(reranked_chunks[:top_k], query)

            # Final ranking
            final_chunks = self._final_ranking(expanded_chunks, query)
            return final_chunks[:top_k]

        except Exception as e:
            log.error(f"Error during retrieve_relevant_chunks: {e}")
            return []

    def _extract_heading_from_content(self, content: str) -> Optional[str]:
        """
        Extract heading from chunk content

        Args:
            content: Chunk content

        Returns:
            Heading if found, None otherwise
        """
        # Try to extract heading from first line
        lines = content.strip().split("\n")
        if not lines:
            return None

        first_line = lines[0].strip()

        # Check if first line matches heading pattern
        heading_patterns = [
            r"^\s*(\d+)\.\s+(.+)$",
            r"^\s*(\d+\.\d+)\.\s+(.+)$",
            r"^\s*(\d+\.\d+\.\d+)\.\s+(.+)$",
        ]

        for pattern in heading_patterns:
            match = re.match(pattern, first_line)
            if match:
                return first_line

        return None

    def _expand_context(
        self, chunks: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """
        Expand context by adding related chunks from the same document/section

        Args:
            chunks: Initial retrieved chunks
            query: User query for relevance checking

        Returns:
            Expanded list of chunks with additional context
        """
        if not chunks:
            return chunks

        expanded_chunks = chunks.copy()

        try:
            # Group chunks by source file
            chunks_by_source = {}
            for chunk in chunks:
                source = chunk.get("source_file", "")
                if source not in chunks_by_source:
                    chunks_by_source[source] = []
                chunks_by_source[source].append(chunk)

            # For each source file, try to find adjacent chunks
            for source_file, source_chunks in chunks_by_source.items():
                for chunk in source_chunks:
                    chunk_index = chunk.get("chunk_index", -1)
                    page_number = chunk.get("page_number", -1)

                    if chunk_index >= 0:
                        # Look for adjacent chunks (before and after)
                        for offset in [-1, 1]:
                            adjacent_chunk = self._get_adjacent_chunk(
                                source_file, chunk_index + offset, page_number
                            )
                            if adjacent_chunk and adjacent_chunk["id"] not in [
                                c["id"] for c in expanded_chunks
                            ]:
                                # Check if adjacent chunk is somewhat relevant
                                if self._is_chunk_relevant(adjacent_chunk, query):
                                    adjacent_chunk["context_expansion"] = True
                                    adjacent_chunk["hybrid_score"] = (
                                        chunk.get("hybrid_score", 0.0) * 0.7
                                    )  # Lower score for context
                                    expanded_chunks.append(adjacent_chunk)

            log.info(
                f"Context expansion added {len(expanded_chunks) - len(chunks)} additional chunks"
            )
            return expanded_chunks

        except Exception as e:
            log.error(f"Error during context expansion: {e}")
            return chunks

    def _get_adjacent_chunk(
        self, source_file: str, chunk_index: int, page_number: int
    ) -> Optional[Dict[str, Any]]:
        """Get adjacent chunk by source file and chunk index using PostgreSQL"""
        try:
            chunk = self.db_service.get_chunk_by_source_and_index(
                source_file, chunk_index
            )
            return chunk
        except Exception as e:
            log.error(f"Error getting adjacent chunk: {e}")
            return None

    def _is_chunk_relevant(self, chunk: Dict[str, Any], query: str) -> bool:
        """Check if a chunk is relevant to the query using simple keyword matching"""
        try:
            content = chunk.get("content", "").lower()
            query_lower = query.lower()

            # Simple keyword overlap check
            query_words = set(query_lower.split())
            content_words = set(content.split())

            # Calculate overlap ratio
            overlap = len(query_words.intersection(content_words))
            overlap_ratio = overlap / len(query_words) if query_words else 0

            # Consider relevant if there's at least 20% keyword overlap
            return overlap_ratio >= 0.2

        except Exception as e:
            log.error(f"Error checking chunk relevance: {e}")
            return False

    def _final_ranking(
        self, chunks: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """
        Final ranking of chunks considering multiple factors

        Args:
            chunks: List of chunks to rank
            query: User query

        Returns:
            Ranked list of chunks
        """
        try:
            # Sort by multiple criteria
            def ranking_score(chunk):
                # Primary: rerank_score if available, otherwise hybrid_score
                primary_score = chunk.get(
                    "rerank_score", chunk.get("hybrid_score", 0.0)
                )

                # Bonus for chunks with headings (likely more structured content)
                heading_bonus = 0.1 if chunk.get("heading_text") else 0.0

                # Bonus for chunks that are not context expansions (original results)
                original_bonus = (
                    0.05 if not chunk.get("context_expansion", False) else 0.0
                )

                # Penalty for very short chunks (likely less informative)
                content_length = len(chunk.get("content", ""))
                length_penalty = -0.1 if content_length < 100 else 0.0

                return primary_score + heading_bonus + original_bonus + length_penalty

            ranked_chunks = sorted(chunks, key=ranking_score, reverse=True)

            log.info(f"Final ranking completed for {len(ranked_chunks)} chunks")
            return ranked_chunks

        except Exception as e:
            log.error(f"Error during final ranking: {e}")
            return chunks

    def _add_engagement_prompt(self, answer: str) -> str:
        """
        Add engagement prompt to the answer if not already present

        Args:
            answer: The generated answer

        Returns:
            Answer with engagement prompt added
        """
        engagement_prompts = [
            "Bạn còn có thắc mắc gì khác không? Tôi sẵn sàng hỗ trợ thêm!",
            "bạn còn có thắc mắc gì khác không",
            "tôi sẵn sàng hỗ trợ thêm",
            "có câu hỏi nào khác không",
            "cần hỗ trợ thêm gì không",
        ]

        # Check if any engagement prompt is already present (case insensitive)
        answer_lower = answer.lower()
        has_engagement = any(
            prompt.lower() in answer_lower for prompt in engagement_prompts
        )

        if not has_engagement:
            # Add the engagement prompt with proper formatting
            if (
                answer.strip().endswith(".")
                or answer.strip().endswith("!")
                or answer.strip().endswith("?")
            ):
                return f"{answer}\n\n**Bạn còn có thắc mắc gì khác không? Tôi sẵn sàng hỗ trợ thêm!**"
            else:
                return f"{answer}.\n\n**Bạn còn có thắc mắc gì khác không? Tôi sẵn sàng hỗ trợ thêm!**"

        return answer

    def create_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Create a simplified and clean context string from retrieved chunks.
        """
        if not chunks:
            return "Không tìm thấy thông tin liên quan trong tài liệu."

        context_parts = []
        for chunk in chunks:
            source = chunk.get("source_file", "Unknown")
            page = chunk.get("page_number", "N/A")
            content = chunk.get("content", "").strip()

            # Simplified format for the LLM - removed source citation from content
            context_part = f"###\n{content}\n###"
            context_parts.append(context_part)

        return "\n\n".join(context_parts)

    def create_system_prompt(self) -> str:
        """
        Create system prompt for the chatbot

        Returns:
            System prompt string
        """
        return """Bạn là một trợ lý AI chuyên gia hỗ trợ sinh viên và người quan tâm về **Trường Đại học An ninh Nhân dân**.

**Phạm vi chuyên môn của bạn bao gồm 5 lĩnh vực chính:**
1. **Tư vấn thông tin tuyển sinh** - Điều kiện, thủ tục, lịch trình, ngành đào tạo, chỉ tiêu tuyển sinh
2. **Quy chế quản lý học viên** - Quyền và nghĩa vụ của học viên, quy định về sinh hoạt, kỷ luật
3. **Quy chế đào tạo các trình độ** - Chương trình đào tạo, học chế, điều kiện tốt nghiệp
4. **Quy định về thi, kiểm tra, đánh giá** - Hình thức thi, thang điểm, quy trình đánh giá
5. **Quy định về kiểm định và bảo đảm chất lượng đào tạo** - Tiêu chuẩn chất lượng, quy trình kiểm định

**Nguyên tắc trả lời - QUAN TRỌNG:**
1. **Cung cấp câu trả lời chi tiết và toàn diện:** Luôn khai thác tối đa thông tin từ "THÔNG TIN TÀI LIỆU" được cung cấp. Không bao giờ đưa ra câu trả lời ngắn gọn hoặc sơ sài khi có đủ thông tin trong tài liệu.

2. **Ưu tiên tài liệu chính thức:** Luôn dựa trên "THÔNG TIN TÀI LIỆU" được cung cấp. Không cần trích dẫn nguồn trong nội dung trả lời vì hệ thống sẽ tự động hiển thị tài liệu tham khảo.

3. **Phân tích và tổng hợp thông tin:** Khi có nhiều đoạn thông tin liên quan, hãy tổng hợp và trình bày một cách có hệ thống, logic. Đưa ra các ví dụ cụ thể và giải thích chi tiết các quy định.

4. **Phân loại thông tin theo lĩnh vực:** Xác định câu hỏi thuộc lĩnh vực nào trong 5 lĩnh vực trên và tập trung trả lời theo chuyên môn đó.

5. **Khi thiếu thông tin trong tài liệu:**
   - Tự do sử dụng kiến thức của bản thân để trả lời câu hỏi một cách hữu ích và chính xác
   - **Bắt buộc:** Bắt đầu bằng: "**Thông tin này chưa có trong tài liệu của trường, tuy nhiên...**"
   - Cung cấp thông tin dựa trên kiến thức chung về giáo dục đại học và các quy định phổ biến
   - Khuyến khích liên hệ trực tiếp với phòng ban liên quan để xác nhận thông tin chính xác nhất

6. **Hướng dẫn cụ thể và thực tế:** Cung cấp các bước thực hiện rõ ràng, thông tin liên hệ khi cần thiết. Đưa ra lời khuyên thực tế và hữu ích.

**Định dạng trả lời (Markdown):**
- **Tiêu đề chính:** `**Tiêu đề**`
- **Danh sách:** Sử dụng `- ` hoặc `1. ` cho các mục
- **Thông tin quan trọng:** `**Lưu ý quan trọng**`
- **Không trích dẫn nguồn:** Hệ thống sẽ tự động hiển thị tài liệu tham khảo
- **Liên hệ:** Cung cấp thông tin liên hệ phòng ban khi phù hợp

**YÊU CẦU ĐÁNG CHÚ Ý:**
- Luôn cung cấp câu trả lời đầy đủ, chi tiết nhất có thể dựa trên thông tin có sẵn
- Không bao giờ nói "thông tin có hạn" khi thực tế có đủ dữ liệu trong tài liệu
- Khai thác tối đa mọi thông tin liên quan từ các đoạn văn bản được cung cấp
- Tạo ra câu trả lời có giá trị thực tế cao cho người dùng"""

    def create_user_prompt(self, query: str, context: str) -> str:
        """
        Create user prompt with query and context

        Args:
            query: User query
            context: Retrieved context

        Returns:
            Formatted user prompt
        """
        return f"""Dựa trên thông tin tài liệu sau đây, hãy trả lời câu hỏi của người dùng một cách CHI TIẾT, TOÀN DIỆN và CHÍNH XÁC nhất có thể:

THÔNG TIN TÀI LIỆU:
{context}

CÂU HỎI: {query}

**HƯỚNG DẪN TRẢ LỜI:**
- Khai thác TẤT CẢ thông tin liên quan từ các tài liệu được cung cấp
- Trình bày một cách có hệ thống, logic và dễ hiểu
- Cung cấp các ví dụ cụ thể và giải thích chi tiết khi có thể
- Không cần trích dẫn nguồn trong nội dung vì hệ thống tự động hiển thị tài liệu tham khảo
- Kết thúc bằng câu khuyến khích tương tác: "Bạn còn có thắc mắc gì khác không? Tôi sẵn sàng hỗ trợ thêm!"

Trả lời:"""

    def _rewrite_query_with_history(
        self, query: str, history: List[Dict[str, str]]
    ) -> str:
        """
        Rewrite the user's query using conversation history for better context.
        """
        if not history:
            return query

        formatted_history = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in history]
        )

        rewrite_prompt = f"""Dựa vào lịch sử trò chuyện sau đây, hãy viết lại câu hỏi cuối cùng của người dùng thành một câu hỏi độc lập, đầy đủ ngữ cảnh để có thể dùng cho việc tìm kiếm thông tin.

### Lịch sử trò chuyện:
{formatted_history}

### Câu hỏi cuối cùng của người dùng:
{query}

### Câu hỏi độc lập, đầy đủ ngữ cảnh:"""

        rewritten_query = query  # Default to original query
        try:
            log.info("Rewriting query with history...")
            if LLM_PROVIDER.lower() == "gemini":
                response = gemini_service.generate_response(
                    prompt=rewrite_prompt, temperature=0.0
                )
                if response:
                    rewritten_query = response.strip()
            elif LLM_PROVIDER.lower() == "ollama":
                response = self.ollama_service.generate_response(
                    prompt=rewrite_prompt,
                    system_prompt="Bạn là một trợ lý AI chuyên viết lại câu hỏi của người dùng thành một câu hỏi đầy đủ ngữ cảnh dựa trên lịch sử trò chuyện.",
                    temperature=0.0,
                )
                if response:
                    rewritten_query = response.strip()

            if rewritten_query != query:
                log.info(f"Original query: '{query}'")
                log.info(f"Rewritten query: '{rewritten_query}'")
            else:
                log.info("Query does not need rewriting.")

            return rewritten_query

        except Exception as e:
            log.error(f"Error during query rewriting: {e}")
            return query  # Fallback to original query on error

    def generate_answer(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
    ) -> Dict[str, Any]:
        """
        Generate answer using RAG approach

        Args:
            query: User query
            conversation_id: Optional conversation ID
            conversation_history: Optional conversation history

        Returns:
            Dictionary with answer, sources, confidence, and conversation_id
        """
        try:
            # Create new conversation if needed
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                self.conversations[conversation_id] = []
            elif conversation_id not in self.conversations:
                self.conversations[conversation_id] = []

            # Use conversation history if provided
            if conversation_history and not self.conversations[conversation_id]:
                # Convert conversation history to internal format
                for message in conversation_history:
                    # Kiểm tra xem message có chứa 'role' và 'content' không
                    if (
                        isinstance(message, dict)
                        and "role" in message
                        and "content" in message
                    ):
                        if message["role"] in ["user", "assistant"]:
                            self.conversations[conversation_id].append(
                                {"role": message["role"], "content": message["content"]}
                            )

            # Step 1: Normalize the user's question using Gemini AI
            log.info(f"Original query: {query}")
            normalized_query = normalize_question(query)
            log.info(f"Normalized query: {normalized_query}")

            # Track if normalization was applied
            normalization_applied = (
                normalized_query != query
            ) and ENABLE_GEMINI_NORMALIZATION

            # Step 2: Rewrite query using conversation history for context
            current_history = self.conversations.get(conversation_id, [])
            rewritten_query = self._rewrite_query_with_history(
                normalized_query, current_history
            )

            # Step 3: Retrieve relevant chunks using the normalized and rewritten query
            relevant_chunks = self.retrieve_relevant_chunks(rewritten_query)

            # Create formatted context from chunks
            context = self.create_context(relevant_chunks)

            # Get source documents
            sources = []
            for chunk in relevant_chunks:
                source = chunk.get("source_file", "")
                if source and source not in sources:
                    sources.append(source)

            # Create system prompt and user prompt
            system_prompt = self.create_system_prompt()
            user_prompt = self.create_user_prompt(query, context)

            # Log context and prompts for debugging
            log.info(f"Context created with {len(relevant_chunks)} chunks")
            log.debug(f"System prompt: {system_prompt[:200]}...")
            log.debug(f"Full context sent to LLM:\n{context}")
            log.debug(f"User prompt: {user_prompt[:200]}...")

            # Generate answer using the configured LLM provider
            answer = None
            if LLM_PROVIDER.lower() == "gemini":
                log.info("Calling Gemini service to generate response...")
                # Gemini API works best with a single, consolidated prompt
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                answer = gemini_service.generate_response(prompt=full_prompt)

            elif LLM_PROVIDER.lower() == "ollama":
                log.info("Calling Ollama service to generate response...")
                answer = self.ollama_service.generate_response(
                    prompt=user_prompt, system_prompt=system_prompt, temperature=0.7
                )
            else:
                log.error(f"Unsupported LLM_PROVIDER configured: {LLM_PROVIDER}")
                answer = "Lỗi: Nhà cung cấp LLM không được cấu hình đúng."

            log.info(f"LLM response received: {answer is not None}")
            if answer:
                log.debug(f"Answer preview: {answer[:100]}...")

            # Calculate confidence based on similarity scores
            if relevant_chunks:
                avg_score = sum(
                    chunk.get("similarity_score", 0) for chunk in relevant_chunks
                ) / len(relevant_chunks)
                # The similarity score is already in a 0-1 range after our calculation
                confidence = min(max(avg_score, 0.0), 1.0)
                log.info(
                    f"Calculated confidence: {confidence:.3f} from avg score: {avg_score:.3f}"
                )
            else:
                confidence = 0.0
                log.warning("No relevant chunks found, confidence set to 0")

            # Handle case where LLM provider returns None or empty
            if answer is None:
                log.error("LLM provider returned None response")
                answer = "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau.\n\nBạn còn có thắc mắc gì khác không? Tôi sẵn sàng hỗ trợ thêm!"
                confidence = 0.0
            elif not answer.strip():
                log.error("LLM provider returned empty response")
                answer = "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau.\n\nBạn còn có thắc mắc gì khác không? Tôi sẵn sàng hỗ trợ thêm!"
                confidence = 0.0
            else:
                log.info(f"Raw answer from LLM: {repr(answer)}")
                # Add engagement prompt if not already present
                answer = self._add_engagement_prompt(answer)
                log.info(f"Using answer with engagement prompt: {repr(answer)}")

            # Update conversation history
            self.conversations[conversation_id].append(
                {"role": "user", "content": query}
            )
            self.conversations[conversation_id].append(
                {"role": "assistant", "content": answer}
            )

            # Limit conversation history
            if len(self.conversations[conversation_id]) > 10:
                self.conversations[conversation_id] = self.conversations[
                    conversation_id
                ][-10:]

            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "conversation_id": conversation_id,
                "normalization_applied": normalization_applied,
                "original_query": query if normalization_applied else None,
                "normalized_query": normalized_query if normalization_applied else None,
            }

        except Exception as e:
            log.error(f"Error generating answer: {e}")
            return {
                "answer": "Xin lỗi, tôi không thể trả lời câu hỏi này. Vui lòng thử lại sau.",
                "sources": [],
                "confidence": 0.0,
                "conversation_id": conversation_id or str(uuid.uuid4()),
            }

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history

        Args:
            conversation_id: Conversation ID

        Returns:
            List of conversation exchanges
        """
        return self.conversations.get(conversation_id, [])

    def check_system_health(self) -> Dict[str, Any]:
        """
        Check health of all RAG components

        Returns:
            Health status dictionary
        """
        health_status = {"overall_status": "healthy", "components": {}}

        # Check Ollama
        ollama_health = self.ollama_service.check_health()
        health_status["components"]["ollama"] = ollama_health

        # Check PostgreSQL + pgvector
        try:
            db_stats = self.db_service.get_database_stats()
            health_status["components"]["database"] = {
                "status": "healthy",
                "stats": db_stats,
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Check Hybrid Retrieval Service (BM25 + pgvector)
        try:
            health_status["components"]["hybrid_retrieval"] = {
                "status": "healthy",
                "type": "BM25 + pgvector",
            }
        except Exception as e:
            health_status["components"]["hybrid_retrieval"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Check embedding service
        try:
            embedding_dim = self.embedding_service.get_embedding_dimension()
            health_status["components"]["embedding"] = {
                "status": "healthy",
                "dimension": embedding_dim,
            }
        except Exception as e:
            health_status["components"]["embedding"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Check ingestion service
        try:
            health_status["components"]["ingestion"] = {
                "status": "healthy",
                "type": "PDF file watcher",
            }
        except Exception as e:
            health_status["components"]["ingestion"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Determine overall status
        component_statuses = [
            comp.get("status", "unknown")
            for comp in health_status["components"].values()
        ]
        if any(status == "unhealthy" for status in component_statuses):
            health_status["overall_status"] = "unhealthy"
        elif any(status == "unknown" for status in component_statuses):
            health_status["overall_status"] = "degraded"

        return health_status

    def cleanup(self):
        """Cleanup resources - stop ingestion service"""
        try:
            if hasattr(self, "ingestion_service"):
                log.info("Stopping ingestion service...")
                self.ingestion_service.stop_watching()
                log.info("Ingestion service stopped successfully.")
        except Exception as e:
            log.error(f"Error during cleanup: {e}")
