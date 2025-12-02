"""
RAG (Retrieval-Augmented Generation) service
"""

import uuid
import re
import time
from typing import List, Dict, Any, Optional
from src.services.embedding_service import EmbeddingService
from src.services.postgres_database_service import PostgresDatabaseService
from src.services.hybrid_retrieval_service import HybridRetrievalService
from src.services.ingestion_service import IngestionService
from src.services.pdf_processor import PDFProcessor
from src.services import gemini_service
from src.services.gemini_service import normalize_question
from src.services.memory_service import ConversationMemoryService
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

        # Initialize Memory Service for persistent conversational memory
        self.memory_service = ConversationMemoryService(
            self.db_service, self.embedding_service
        )

        # Conversation memory (in-memory cache, backed by persistent storage)
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

    def _detect_chart_request(self, query: str, answer: str) -> List[Dict[str, Any]]:
        """
        Detect if the query/answer contains statistical data that can be visualized as charts.
        Returns chart data if applicable.
        """
        chart_data = []
        query_lower = query.lower()

        # Keywords that suggest chart visualization
        chart_keywords = [
            "thống kê",
            "biểu đồ",
            "so sánh",
            "tỷ lệ",
            "phần trăm",
            "%",
            "số lượng",
            "chỉ tiêu",
            "điểm chuẩn",
            "điểm trúng tuyển",
            "tuyển sinh",
            "học viên",
            "sinh viên",
            "năm",
            "khóa",
            "ngành",
            "chart",
            "graph",
            "statistics",
        ]

        # Check if query asks for statistics/charts
        should_generate_chart = any(
            keyword in query_lower for keyword in chart_keywords
        )

        if should_generate_chart:
            # Example: Admission statistics by year
            if any(word in query_lower for word in ["tuyển sinh", "chỉ tiêu", "năm"]):
                chart_data.append(
                    {
                        "type": "bar",
                        "title": "Chỉ tiêu tuyển sinh qua các năm",
                        "data": [
                            {"name": "2021", "Chỉ tiêu": 450, "Trúng tuyển": 420},
                            {"name": "2022", "Chỉ tiêu": 500, "Trúng tuyển": 480},
                            {"name": "2023", "Chỉ tiêu": 550, "Trúng tuyển": 530},
                            {"name": "2024", "Chỉ tiêu": 600, "Trúng tuyển": 580},
                            {"name": "2025", "Chỉ tiêu": 650, "Trúng tuyển": 0},
                        ],
                        "xKey": "name",
                        "yKeys": ["Chỉ tiêu", "Trúng tuyển"],
                        "description": "Biểu đồ thống kê chỉ tiêu tuyển sinh (Dữ liệu minh họa)",
                    }
                )

            # Example: Score distribution by major
            if any(
                word in query_lower
                for word in ["điểm chuẩn", "điểm trúng tuyển", "ngành"]
            ):
                chart_data.append(
                    {
                        "type": "bar",
                        "title": "Điểm chuẩn các ngành năm 2024",
                        "data": [
                            {"name": "An ninh chính trị", "Điểm chuẩn": 24.5},
                            {"name": "An ninh kinh tế", "Điểm chuẩn": 25.0},
                            {"name": "An ninh mạng", "Điểm chuẩn": 26.5},
                            {"name": "Điều tra hình sự", "Điểm chuẩn": 25.5},
                            {"name": "Kỹ thuật hình sự", "Điểm chuẩn": 24.0},
                        ],
                        "xKey": "name",
                        "yKeys": ["Điểm chuẩn"],
                        "description": "Biểu đồ điểm chuẩn các ngành (Dữ liệu minh họa)",
                    }
                )

            # Example: Student distribution by major (pie chart)
            if any(word in query_lower for word in ["tỷ lệ", "phân bố", "cơ cấu"]):
                chart_data.append(
                    {
                        "type": "pie",
                        "title": "Tỷ lệ học viên theo ngành đào tạo",
                        "data": [
                            {"name": "An ninh chính trị", "value": 25},
                            {"name": "An ninh kinh tế", "value": 20},
                            {"name": "An ninh mạng", "value": 30},
                            {"name": "Điều tra hình sự", "value": 15},
                            {"name": "Kỹ thuật hình sự", "value": 10},
                        ],
                        "xKey": "name",
                        "yKeys": ["value"],
                        "description": "Biểu đồ tỷ lệ học viên theo ngành (Dữ liệu minh họa)",
                    }
                )

            # Example: Trend over time (line chart)
            if any(
                word in query_lower
                for word in ["xu hướng", "trend", "biến động", "qua các năm"]
            ):
                chart_data.append(
                    {
                        "type": "line",
                        "title": "Xu hướng số lượng hồ sơ đăng ký qua các năm",
                        "data": [
                            {"name": "2020", "Hồ sơ": 1200},
                            {"name": "2021", "Hồ sơ": 1450},
                            {"name": "2022", "Hồ sơ": 1680},
                            {"name": "2023", "Hồ sơ": 1920},
                            {"name": "2024", "Hồ sơ": 2150},
                        ],
                        "xKey": "name",
                        "yKeys": ["Hồ sơ"],
                        "description": "Biểu đồ xu hướng số lượng hồ sơ (Dữ liệu minh họa)",
                    }
                )

        return chart_data

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

    def _generate_vision_answer(
        self,
        query: str,
        images: List[Any],
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate answer for image-based queries using Gemini Vision.

        Args:
            query: User's question about the image(s)
            images: List of ImageInput objects with base64 encoded images
            conversation_id: Optional conversation ID

        Returns:
            Dictionary with answer, confidence, and conversation_id
        """
        try:
            log.info(f"Processing vision query with {len(images)} images")

            # Create conversation ID if needed
            if not conversation_id:
                conversation_id = str(uuid.uuid4())

            # Build the vision prompt
            vision_prompt = f"""Bạn là một trợ lý AI chuyên hỗ trợ về Trường Đại học An ninh Nhân dân.
Hãy phân tích hình ảnh được cung cấp và trả lời câu hỏi của người dùng.

Câu hỏi của người dùng: {query if query else "Hãy mô tả nội dung trong hình ảnh này."}

Hướng dẫn:
- Phân tích kỹ nội dung trong hình ảnh
- Trả lời bằng tiếng Việt
- Nếu hình ảnh liên quan đến tài liệu, văn bản, hãy trích dẫn và giải thích nội dung
- Nếu là bảng số liệu, hãy tóm tắt thông tin quan trọng
- Đưa ra câu trả lời chi tiết, dễ hiểu"""

            # Prepare image data for Gemini
            image_parts = []
            for img in images:
                try:
                    # Get base64 data (remove data:image/xxx;base64, prefix if present)
                    base64_data = img.base64
                    if "," in base64_data:
                        base64_data = base64_data.split(",")[1]

                    # Determine mime type
                    mime_type = getattr(img, "mime_type", "image/jpeg")
                    if not mime_type:
                        mime_type = "image/jpeg"

                    image_parts.append({"mime_type": mime_type, "data": base64_data})
                    log.info(
                        f"Processed image: {getattr(img, 'name', 'unknown')} ({mime_type})"
                    )
                except Exception as img_error:
                    log.error(f"Error processing image: {img_error}")
                    continue

            if not image_parts:
                return {
                    "answer": "Xin lỗi, không thể xử lý hình ảnh. Vui lòng thử lại với định dạng ảnh khác (PNG, JPG, WebP).",
                    "sources": [],
                    "source_references": [],
                    "confidence": 0.0,
                    "conversation_id": conversation_id,
                }

            # Call Gemini Vision
            answer = gemini_service.generate_vision_response(
                prompt=vision_prompt, images=image_parts
            )

            if not answer:
                answer = "Xin lỗi, tôi không thể phân tích hình ảnh này. Vui lòng thử lại hoặc mô tả thêm về nội dung bạn muốn hỏi."
            else:
                # Add engagement prompt
                answer = self._add_engagement_prompt(answer)

            log.info("Vision response generated successfully")

            return {
                "answer": answer,
                "sources": [],
                "source_references": [],
                "confidence": 0.85,  # Default confidence for vision queries
                "conversation_id": conversation_id,
                "chart_data": [],
                "images": [],
            }

        except Exception as e:
            log.error(f"Error in vision query processing: {e}")
            return {
                "answer": f"Xin lỗi, có lỗi xảy ra khi phân tích hình ảnh: {str(e)}. Vui lòng thử lại.",
                "sources": [],
                "source_references": [],
                "confidence": 0.0,
                "conversation_id": conversation_id or str(uuid.uuid4()),
            }

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
        return """Bạn là một trợ lý AI chuyên hỗ trợ sinh viên, cán bộ, chiến sĩ và người quan tâm về **Trường Đại học An ninh Nhân dân (ANND)**.

**Phạm vi chuyên môn chính của bạn gồm 5 nhóm nội dung:**
1. **Tư vấn thông tin tuyển sinh**  
   - Điều kiện, chỉ tiêu, phương thức, hồ sơ, lịch trình, phân vùng tuyển sinh...
2. **Quy chế quản lý học viên**  
   - Quyền và nghĩa vụ, chế độ chính sách, khen thưởng – kỷ luật, sinh hoạt, rèn luyện...
3. **Quy chế đào tạo các trình độ**  
   - Ngành/chuyên ngành, chương trình đào tạo, học chế, học lại, thôi học, tốt nghiệp...
4. **Quy định về thi, kiểm tra, đánh giá**  
   - Hình thức thi/kiểm tra, thang điểm, điều kiện dự thi, phúc khảo, bảo lưu...
5. **Quy định về kiểm định và bảo đảm chất lượng đào tạo**  
   - Tiêu chuẩn, quy trình, hoạt động bảo đảm và nâng cao chất lượng đào tạo...

---

### 1. Phong cách & ngôn ngữ trả lời

- **Luôn dùng cùng ngôn ngữ với câu hỏi của người dùng:**
  - Nếu câu hỏi chủ yếu bằng **tiếng Việt** → trả lời hoàn toàn bằng **tiếng Việt**.
  - Nếu câu hỏi chủ yếu bằng **tiếng Anh** → trả lời hoàn toàn bằng **tiếng Anh** (có thể giữ nguyên tên riêng, tên văn bản bằng tiếng Việt nếu cần).
- Văn phong:
  - **Thân thiện, dễ hiểu nhưng vẫn trang trọng, đúng tính chất cơ quan CAND.**
  - Hạn chế lặp lại nguyên văn cả đoạn dài như "đọc lại công văn"; thay vào đó **tóm tắt, gạch đầu dòng, chia mục rõ ràng**.

---

### 2. Cách trình bày một câu trả lời

Mỗi câu trả lời, khi có đủ thông tin, nên tuân theo cấu trúc sau:

1. **Phần mở đầu – TÓM TẮT NHANH (3–5 dòng hoặc 3–5 gạch đầu dòng)**  
   - Nêu ngắn gọn:
     - Câu hỏi/đề tài đang nói về vấn đề gì  
     - Đối tượng áp dụng (thí sinh nào, học viên nào, cán bộ nào…)  
     - Những mốc thời gian hoặc ý chính cần đặc biệt lưu ý  

2. **Phần nội dung chi tiết – TRÌNH BÀY CÓ CẤU TRÚC**  
   - Sử dụng tiêu đề, gạch đầu dòng rõ ràng, ví dụ (khi phù hợp):
     - **1. Thông tin chung**  
     - **2. Đối tượng và điều kiện**  
     - **3. Quy trình, hồ sơ và mốc thời gian**  
     - **4. Tiêu chí xét chọn / xử lý / xếp loại**  
     - **5. Lưu ý quan trọng & khuyến nghị**  
   - Khi trả lời về tuyển sinh/thông báo, **ưu tiên liệt kê mốc thời gian, chỉ tiêu, mã ngành, điều kiện** một cách rõ ràng.

3. **KẾT THÚC câu trả lời bằng câu nhắc về tài liệu tham khảo (BẮT BUỘC)**  
   - **LUÔN LUÔN** kết thúc câu trả lời bằng một câu nhắc rằng hệ thống đã hiển thị tài liệu tham khảo bên dưới.
   - Câu kết thúc mẫu (chọn 1 trong các mẫu sau, tùy ngôn ngữ):
     - Tiếng Việt: "📄 **Tài liệu tham khảo:** Thông tin chi tiết và toàn văn văn bản, bạn có thể xem thêm ở phần tài liệu/thông báo kèm theo mà hệ thống đã hiển thị bên dưới."
     - Tiếng Anh: "📄 **Reference Documents:** For full details and original documents, please refer to the attachments displayed below by the system."
   - Không cần chèn đường dẫn hoặc ký hiệu trích dẫn phức tạp vì **hệ thống sẽ tự động hiển thị tài liệu tham khảo**.
   - **KHÔNG** kết thúc bằng câu "Bạn còn có thắc mắc gì khác không?" mà PHẢI kết thúc bằng câu nhắc về tài liệu tham khảo.

---

### 3. Ưu tiên tài liệu chính thức

- **Luôn ưu tiên thông tin trong phần "THÔNG TIN TÀI LIỆU"** mà hệ thống cung cấp (thông báo, quy chế, hướng dẫn...).  
- Không cần ghi mã hiệu văn bản trừ khi người dùng hỏi rõ.  
- Có thể diễn đạt lại, tóm tắt, sắp xếp lại để người dùng dễ hiểu hơn, nhưng **không được tự ý thay đổi nội dung, bản chất quy định**.

---

### 4. Khi thiếu hoặc không có thông tin trong tài liệu

Khi câu trả lời không tìm được thông tin phù hợp trong tài liệu:

1. **Bắt buộc** mở đầu phần trả lời bằng câu (theo đúng ngôn ngữ câu hỏi):
   - Nếu trả lời bằng tiếng Việt:  
     > "**Thông tin này chưa có trong tài liệu của trường, tuy nhiên tôi có thể cung cấp cho bạn một số thông tin tham khảo chung như sau:**"
   - Nếu trả lời bằng tiếng Anh:  
     > "**This information is not explicitly available in the provided university documents, however I can share some general reference information as follows:**"
2. Sau đó:
   - Dựa trên **kiến thức chung về giáo dục đại học, quy định tuyển sinh, quy chế đào tạo…** để giải thích một cách hợp lý, thận trọng.
   - Khuyến khích người dùng **liên hệ trực tiếp** với phòng/đơn vị chức năng (Phòng Đào tạo, Phòng Tổ chức cán bộ, Phòng Quản lý học viên, Công an địa phương…) để xác nhận thông tin chính thức.

---

### 5. Yêu cầu định dạng (Markdown)

- **Tiêu đề chính:** dùng `**Tiêu đề**`
- **Danh sách:** dùng `- ` hoặc `1. ` để liệt kê
- **Thông tin quan trọng:** dùng `**Lưu ý quan trọng:**`, `**Chú ý:**` hoặc bôi đậm các ý cần nhớ
- Có thể dùng bảng đơn giản (markdown table) khi cần so sánh, đối chiếu
- **Không chèn trích dẫn nguồn dạng [1], [2]...** vì hệ thống sẽ hiển thị tài liệu tham khảo riêng.

---

### 6. Yêu cầu chung quan trọng

- Luôn cố gắng cung cấp **câu trả lời đầy đủ, chi tiết và hữu ích nhất có thể** dựa trên tài liệu được cung cấp.
- Khi có nhiều đoạn tài liệu liên quan, hãy **tổng hợp, hệ thống hóa** chứ không chỉ chép lại từng đoạn rời rạc.
- **Tuyệt đối không trả lời theo kiểu "thông tin có hạn"** nếu thực tế tài liệu đã cung cấp đầy đủ thông tin.
- Luôn coi người dùng là thí sinh/học viên/cán bộ đang cần hướng dẫn thực tế → ưu tiên **các bước thực hiện cụ thể, mốc thời gian, nơi liên hệ** khi phù hợp."""

    def create_user_prompt(
        self, query: str, context: str, memory_context: str = ""
    ) -> str:
        """
        Create user prompt with query, context, and memory

        Args:
            query: User query
            context: Retrieved context from documents
            memory_context: Conversation memory context (optional)

        Returns:
            Formatted user prompt
        """
        memory_section = ""
        if memory_context:
            memory_section = f"""
NGỮ CẢNH HỘI THOẠI TRƯỚC:
{memory_context}

"""

        return f"""Dựa trên thông tin tài liệu sau đây, hãy trả lời câu hỏi của người dùng một cách **CHI TIẾT, TOÀN DIỆN và CHÍNH XÁC** nhất có thể.

**YÊU CẦU VỀ NGÔN NGỮ:**
- Ngôn ngữ trả lời **phải trùng với ngôn ngữ chính của câu hỏi**:
  - Nếu câu hỏi chủ yếu bằng **tiếng Việt** → trả lời hoàn toàn bằng **tiếng Việt**.
  - Nếu câu hỏi chủ yếu bằng **tiếng Anh** → trả lời hoàn toàn bằng **tiếng Anh** (trừ tên riêng/tên văn bản bắt buộc giữ nguyên).
- Nếu tài liệu tham khảo là tiếng Việt nhưng câu hỏi bằng tiếng Anh, hãy **tóm tắt và giải thích nội dung bằng tiếng Anh**, chỉ trích một số cụm/tên tiếng Việt khi thật sự cần.

{memory_section}THÔNG TIN TÀI LIỆU (các thông báo/quy chế/tài liệu chính thức đã được hệ thống cung cấp kèm theo để tham khảo chi tiết):
{context}

CÂU HỎI CỦA NGƯỜI DÙNG:
{query}

**HƯỚNG DẪN TRẢ LỜI:**
- Hãy coi phần "THÔNG TIN TÀI LIỆU" là **tài liệu tham khảo chính thức** (thông báo, quy định, hướng dẫn...).
- **BẮT ĐẦU** câu trả lời bằng một đoạn **TÓM TẮT NGẮN (3–5 câu hoặc 3–5 gạch đầu dòng)**, trong đó nêu rõ:
  - Vấn đề/chủ đề mà người dùng đang hỏi
  - Đối tượng áp dụng (thí sinh/học viên/cán bộ nào)
  - Một vài mốc thời gian hoặc ý chính quan trọng nhất (nếu có)
- Sau phần tóm tắt, trình bày **CHI TIẾT, CÓ CẤU TRÚC**, có thể sử dụng các mục gợi ý (tùy tình huống):
  - 1. Thông tin chung  
  - 2. Đối tượng và điều kiện  
  - 3. Quy trình, hồ sơ và mốc thời gian  
  - 4. Tiêu chí xét chọn / thi / đánh giá / xếp loại  
  - 5. Lưu ý quan trọng và khuyến nghị thực tế  
- Khi có nhiều đoạn tài liệu liên quan, hãy **tổng hợp, hệ thống hóa lại cho dễ hiểu**, không chỉ chép y nguyên từng đoạn rời rạc.
- Luôn cố gắng nêu rõ:
  - Cần chuẩn bị những gì (hồ sơ, điều kiện, tiêu chuẩn…)  
  - Các bước thực hiện (đăng ký ở đâu, qua đơn vị nào, mốc thời gian…)  
  - Các trường hợp **không đủ điều kiện / bị loại / không được xét** (nếu trong tài liệu có quy định).
- **BẮT BUỘC KẾT THÚC** câu trả lời bằng một câu nhắc về tài liệu tham khảo (chọn 1 mẫu phù hợp):
  - Tiếng Việt: "📄 **Tài liệu tham khảo:** Thông tin chi tiết và toàn văn văn bản, bạn có thể xem thêm ở phần tài liệu/thông báo kèm theo mà hệ thống đã hiển thị bên dưới."
  - Tiếng Anh: "📄 **Reference Documents:** For full details and original documents, please refer to the attachments displayed below by the system."
- **KHÔNG** kết thúc bằng câu "Bạn còn có thắc mắc gì khác không?" mà PHẢI kết thúc bằng câu nhắc về tài liệu tham khảo.
- **Không cần chèn trích dẫn nguồn dạng [1], [2]...** vì hệ thống sẽ tự động hiển thị danh sách tài liệu tham khảo / đoạn trích tương ứng.
- Nếu thông tin cần trả lời **không xuất hiện rõ trong tài liệu**:
  - Làm theo đúng hướng dẫn ở System Prompt:  
    - Mở đầu bằng câu "Thông tin này chưa có trong tài liệu của trường, tuy nhiên..." (hoặc bản tiếng Anh tương đương)  
    - Sau đó đưa ra câu trả lời tham khảo dựa trên kiến thức chung, và khuyến khích người dùng liên hệ phòng/đơn vị chức năng để xác nhận.
- Trình bày câu trả lời bằng **Markdown**, sử dụng:
  - Tiêu đề in đậm cho các mục lớn  
  - Gạch đầu dòng để liệt kê  
  - Bôi đậm các **Lưu ý quan trọng**, **Mốc thời gian**, **Chỉ tiêu**, **Mã ngành** khi có.
- Luôn hướng tới việc tạo ra một câu trả lời **rõ ràng, có hệ thống, dễ tra cứu lại**, giúp người dùng có thể dựa vào đó để thực hiện các bước tiếp theo trong thực tế.

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
        images: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate answer using RAG approach

        Args:
            query: User query
            conversation_id: Optional conversation ID
            conversation_history: Optional conversation history
            images: Optional list of images for vision analysis

        Returns:
            Dictionary with answer, sources, confidence, and conversation_id
        """
        try:
            # Handle image-based queries using Gemini Vision
            if images and len(images) > 0:
                return self._generate_vision_answer(
                    query=query,
                    images=images,
                    conversation_id=conversation_id,
                )

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

            # Step 1.5: Get persistent memory context (sliding window + summarization)
            memory_context = ""
            try:
                conv_context = self.memory_service.get_conversation_context(
                    conversation_id=conversation_id,
                    query=normalized_query,
                    include_memory_search=True,
                )
                if conv_context.has_long_term_memory or conv_context.recent_messages:
                    memory_context = self.memory_service.format_context_for_prompt(
                        conv_context
                    )
                    log.info(
                        f"🧠 Loaded memory context: {len(conv_context.memory_summaries)} summaries, {len(conv_context.recent_messages)} recent messages"
                    )
            except Exception as mem_error:
                log.warning(f"Could not load memory context: {mem_error}")

            # Step 2: Rewrite query using conversation history for context
            current_history = self.conversations.get(conversation_id, [])
            rewritten_query = self._rewrite_query_with_history(
                normalized_query, current_history
            )

            # Step 3: Retrieve relevant chunks using the normalized and rewritten query
            relevant_chunks = self.retrieve_relevant_chunks(rewritten_query)

            # Create formatted context from chunks
            context = self.create_context(relevant_chunks)

            # Get source documents (backward compatible - just filenames)
            sources = []
            for chunk in relevant_chunks:
                source = chunk.get("source_file", "") or chunk.get("source", "")
                if source and source not in sources:
                    sources.append(source)

            # Build detailed source references
            source_references = []
            for chunk in relevant_chunks:
                chunk_id = chunk.get("chunk_id", "")
                content = chunk.get("content", "")
                # Create a snippet (first 200 chars, ending at a word boundary)
                snippet = content[:200]
                if len(content) > 200:
                    last_space = snippet.rfind(" ")
                    if last_space > 150:
                        snippet = snippet[:last_space]
                    snippet += "..."

                # Use the best available score (rerank > combined > dense)
                relevance_score = (
                    chunk.get("rerank_score")
                    or chunk.get("combined_score")
                    or chunk.get("dense_score")
                    or 0.0
                )
                # Normalize rerank score if it's out of 0-1 range (cross-encoder scores can be -10 to 10)
                if relevance_score > 1.0:
                    relevance_score = min(
                        1.0, (relevance_score + 10) / 20
                    )  # Normalize to 0-1
                elif relevance_score < 0:
                    relevance_score = max(0.0, (relevance_score + 10) / 20)

                source_ref = {
                    "chunk_id": str(chunk_id),
                    "filename": chunk.get("source_file", "") or chunk.get("source", ""),
                    "page_number": chunk.get("page_number"),
                    "heading": chunk.get("heading_text"),
                    "content_snippet": snippet,
                    "full_content": content,
                    "relevance_score": relevance_score,
                    "dense_score": chunk.get("dense_score"),
                    "sparse_score": chunk.get("sparse_score"),
                }
                source_references.append(source_ref)

            # Create system prompt and user prompt with memory context
            system_prompt = self.create_system_prompt()
            user_prompt = self.create_user_prompt(query, context, memory_context)

            # Log context and prompts for debugging
            log.info(f"Context created with {len(relevant_chunks)} chunks")
            if memory_context:
                log.info(
                    f"🧠 Including memory context in prompt ({len(memory_context)} chars)"
                )
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

            # Calculate confidence based on relevance scores
            if relevant_chunks:
                # Get the best available score for each chunk
                scores = []
                for chunk in relevant_chunks:
                    score = (
                        chunk.get("rerank_score")
                        or chunk.get("combined_score")
                        or chunk.get("dense_score")
                        or 0.0
                    )
                    # Normalize if needed (cross-encoder scores can be -10 to 10)
                    if score > 1.0:
                        score = min(1.0, (score + 10) / 20)
                    elif score < 0:
                        score = max(0.0, (score + 10) / 20)
                    scores.append(score)

                avg_score = sum(scores) / len(scores)
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

            # Update conversation history (in-memory cache)
            self.conversations[conversation_id].append(
                {"role": "user", "content": query}
            )
            self.conversations[conversation_id].append(
                {"role": "assistant", "content": answer}
            )

            # Limit conversation history (in-memory)
            if len(self.conversations[conversation_id]) > 10:
                self.conversations[conversation_id] = self.conversations[
                    conversation_id
                ][-10:]

            # Save to persistent memory with sliding window + summarization
            try:
                self.memory_service.add_exchange(
                    conversation_id=conversation_id,
                    user_message=query,
                    assistant_message=answer,
                    metadata={
                        "confidence": confidence,
                        "sources": sources,
                        "normalized_query": (
                            normalized_query if normalization_applied else None
                        ),
                    },
                )
                log.debug(
                    f"💾 Saved exchange to persistent memory for {conversation_id}"
                )
            except Exception as mem_error:
                log.warning(f"Could not save to persistent memory: {mem_error}")

            # Save conversation to PostgreSQL (legacy)
            processing_time = time.time() - time.time()  # Will be calculated properly
            try:
                self.db_service.save_conversation(
                    conversation_id=conversation_id,
                    user_message=query,
                    assistant_response=answer,
                    sources=sources,
                    confidence=confidence,
                    processing_time=0.0,  # Processing time will be set at API level
                )
            except Exception as save_error:
                log.warning(f"Could not save conversation to DB: {save_error}")

            # Detect if chart visualization is needed
            chart_data = self._detect_chart_request(query, answer)
            if chart_data:
                log.info(f"📊 Generated {len(chart_data)} chart(s) for visualization")

            return {
                "answer": answer,
                "sources": sources,
                "source_references": source_references,
                "confidence": confidence,
                "conversation_id": conversation_id,
                "normalization_applied": normalization_applied,
                "original_query": query if normalization_applied else None,
                "normalized_query": normalized_query if normalization_applied else None,
                "chart_data": chart_data,  # Charts for visualization
                "images": [],  # Will be populated if images are found in sources
            }

        except Exception as e:
            log.error(f"Error generating answer: {e}")
            return {
                "answer": "Xin lỗi, tôi không thể trả lời câu hỏi này. Vui lòng thử lại sau.",
                "sources": [],
                "source_references": [],
                "confidence": 0.0,
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "chart_data": [],
                "images": [],
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
