"""
RAG (Retrieval-Augmented Generation) service
"""
import uuid
import re
from typing import List, Dict, Any, Optional, Tuple
from src.services.embedding_service import EmbeddingService
from src.services.database_service import DatabaseService
from src.services.ollama_service import OllamaService
from src.utils.logger import log
from src.utils.vietnamese_text_formatter import format_vietnamese_text
from config.settings import FAISS_INDEX_PATH, TOP_K_RESULTS, SIMILARITY_THRESHOLD
import faiss
import numpy as np
from pathlib import Path
import pickle

class RAGService:
    """Service for Retrieval-Augmented Generation"""
    
    def __init__(self):
        """Initialize RAG service with all required components"""
        self.embedding_service = EmbeddingService()
        self.db_service = DatabaseService()
        self.ollama_service = OllamaService()
        
        # Trực tiếp load FAISS index thay vì qua service
        self.index = None
        self.id_map = {}
        self.load_faiss_index()
        
        # Conversation memory
        self.conversations = {}
    
    def load_faiss_index(self):
        """Load FAISS index directly using faiss library"""
        try:
            index_file = str(Path(FAISS_INDEX_PATH)) + ".index"
            metadata_file = str(Path(FAISS_INDEX_PATH)) + ".metadata"
            
            if not Path(index_file).exists() or not Path(metadata_file).exists():
                log.warning(f"FAISS index files not found at {index_file}")
                return False
            
            # Load FAISS index directly
            self.index = faiss.read_index(index_file)
            
            # Load metadata
            with open(metadata_file, 'rb') as f:
                metadata = pickle.load(f)
            
            self.id_map = metadata.get('id_map', {})
            log.info(f"FAISS index loaded successfully with {self.index.ntotal} vectors")
            return True
            
        except Exception as e:
            log.error(f"Error loading FAISS index: {e}")
            return False
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks using FAISS directly"""
        try:
            # Create query embedding
            query_embedding = self.embedding_service.create_embedding(query)
            
            # Prepare query vector
            query_vector = np.array(query_embedding).reshape(1, -1).astype(np.float32)
            faiss.normalize_L2(query_vector)
            
            # Search directly with FAISS
            distances, indices = self.index.search(query_vector, top_k * 2)
            
            # Process results
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx != -1:  # FAISS returns -1 for empty slots
                    chunk_id = self.id_map.get(int(idx))
                    if chunk_id is not None:
                        # Get chunk data from database
                        chunk = self.db_service.get_chunk_by_id(chunk_id)
                        if chunk:
                            # Convert distance to similarity score (higher is better)
                            similarity_score = float(distance)
                            results.append({
                                'id': chunk_id,
                                'content': chunk['content'],
                                'source_file': chunk['source_file'],
                                'page_number': chunk.get('page_number', 'N/A'),
                                'heading': chunk.get('heading', ''),
                                'similarity_score': similarity_score
                            })
            
            log.info(f"Search results for '{query}': {len(results)} results found")
            return results[:top_k]
            
        except Exception as e:
            log.error(f"Error retrieving relevant chunks: {str(e)}")
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
        lines = content.strip().split('\n')
        if not lines:
            return None
        
        first_line = lines[0].strip()
        
        # Check if first line matches heading pattern
        heading_patterns = [
            r'^\s*(\d+)\.\s+(.+)$',
            r'^\s*(\d+\.\d+)\.\s+(.+)$',
            r'^\s*(\d+\.\d+\.\d+)\.\s+(.+)$'
        ]
        
        for pattern in heading_patterns:
            match = re.match(pattern, first_line)
            if match:
                return first_line
        
        return None
    
    def create_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Create context string from retrieved chunks
        
        Args:
            chunks: List of chunk dictionaries
        
        Returns:
            Formatted context string
        """
        if not chunks:
            return "Không tìm thấy thông tin liên quan trong tài liệu."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get('source_file', 'Unknown')
            page = chunk.get('page_number', 'N/A')
            content = chunk.get('content', '')
            score = chunk.get('similarity_score', 0)
            heading = chunk.get('heading', '')
            
            # Format the context part
            if heading:
                context_part = f"[Tài liệu {i}: {source}, Trang {page}, Mục: {heading}, Độ liên quan: {score:.3f}]\n{content}\n"
            else:
                context_part = f"[Tài liệu {i}: {source}, Trang {page}, Độ liên quan: {score:.3f}]\n{content}\n"
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def create_system_prompt(self) -> str:
        """
        Create system prompt for the chatbot

        Returns:
            System prompt string
        """
        return """Bạn là trợ lý AI tư vấn tuyển sinh Trường Đại học An ninh Nhân dân.

NHIỆM VỤ: Trả lời câu hỏi về tuyển sinh dựa CHÍNH XÁC trên tài liệu được cung cấp.

QUY TẮC BẮT BUỘC:
1. CHỈ sử dụng thông tin từ tài liệu được cung cấp
2. KHÔNG tạo ra thông tin không có trong tài liệu
3. KHÔNG lặp lại nội dung
4. Trả lời ngắn gọn, rõ ràng bằng tiếng Việt
5. Nếu không có thông tin, nói "Thông tin này không có trong tài liệu"

ĐỊNH DẠNG TRẢ LỜI:
- Trả lời trực tiếp câu hỏi
- Liệt kê thông tin theo từng mục nếu có nhiều điểm
- Kết thúc ngay khi đã trả lời đầy đủ"""
    
    def create_user_prompt(self, query: str, context: str) -> str:
        """
        Create user prompt with query and context

        Args:
            query: User query
            context: Retrieved context

        Returns:
            Formatted user prompt
        """
        return f"""Dựa trên thông tin tài liệu sau đây, hãy trả lời câu hỏi của người dùng một cách chi tiết và chính xác:

THÔNG TIN TÀI LIỆU:
{context}

CÂU HỎI: {query}

Trả lời:"""
    
    def generate_answer(
        self, 
        query: str, 
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None
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
                    if isinstance(message, dict) and 'role' in message and 'content' in message:
                        if message['role'] in ['user', 'assistant']:
                            self.conversations[conversation_id].append({
                                'role': message['role'],
                                'content': message['content']
                            })
        
            # Retrieve relevant chunks
            relevant_chunks = self.retrieve_relevant_chunks(query)
            
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
            log.debug(f"User prompt: {user_prompt[:200]}...")

            # Generate answer using Ollama
            log.info("Calling Ollama service to generate response...")
            answer = self.ollama_service.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )

            log.info(f"Ollama response received: {answer is not None}")
            if answer:
                log.debug(f"Answer preview: {answer[:100]}...")

            # Calculate confidence based on similarity scores
            if relevant_chunks:
                avg_score = sum(chunk.get('similarity_score', 0) for chunk in relevant_chunks) / len(relevant_chunks)
                confidence = min(avg_score / 5.0, 1.0)  # Normalize to 0-1 range
                log.info(f"Calculated confidence: {confidence:.3f} from avg score: {avg_score:.3f}")
            else:
                confidence = 0.0
                log.warning("No relevant chunks found, confidence set to 0")

            # Handle case where Ollama returns None
            if answer is None:
                log.error("Ollama returned None response")
                answer = "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau."
                confidence = 0.0
            elif not answer.strip():
                log.error("Ollama returned empty response")
                answer = "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau."
                confidence = 0.0
            else:
                log.info(f"Raw answer from Ollama: {repr(answer)}")
                # Format Vietnamese text for proper spelling and grammar
                formatted_answer = format_vietnamese_text(answer)
                log.info(f"Formatted answer: {repr(formatted_answer)}")
                answer = formatted_answer
                log.info("Answer formatted successfully")
            
            # Update conversation history
            self.conversations[conversation_id].append({"role": "user", "content": query})
            self.conversations[conversation_id].append({"role": "assistant", "content": answer})
            
            # Limit conversation history
            if len(self.conversations[conversation_id]) > 10:
                self.conversations[conversation_id] = self.conversations[conversation_id][-10:]
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "conversation_id": conversation_id
            }
        
        except Exception as e:
            log.error(f"Error generating answer: {e}")
            return {
                "answer": "Xin lỗi, tôi không thể trả lời câu hỏi này. Vui lòng thử lại sau.",
                "sources": [],
                "confidence": 0.0,
                "conversation_id": conversation_id or str(uuid.uuid4())
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
        health_status = {
            'overall_status': 'healthy',
            'components': {}
        }
        
        # Check Ollama
        ollama_health = self.ollama_service.check_health()
        health_status['components']['ollama'] = ollama_health
        
        # Check FAISS index
        try:
            if self.index is not None:
                faiss_stats = {
                    'status': 'healthy',
                    'total_vectors': self.index.ntotal,
                    'dimension': self.index.d,
                    'id_map_size': len(self.id_map)
                }
            else:
                faiss_stats = {
                    'status': 'unhealthy',
                    'error': 'FAISS index not loaded'
                }
            health_status['components']['faiss'] = faiss_stats
        except Exception as e:
            health_status['components']['faiss'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Check database
        try:
            db_stats = self.db_service.get_database_stats()
            health_status['components']['database'] = {
                'status': 'healthy',
                'stats': db_stats
            }
        except Exception as e:
            health_status['components']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Check embedding service
        try:
            embedding_dim = self.embedding_service.get_embedding_dimension()
            health_status['components']['embedding'] = {
                'status': 'healthy',
                'dimension': embedding_dim
            }
        except Exception as e:
            health_status['components']['embedding'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Determine overall status
        component_statuses = [comp.get('status', 'unknown') for comp in health_status['components'].values()]
        if any(status == 'unhealthy' for status in component_statuses):
            health_status['overall_status'] = 'unhealthy'
        elif any(status == 'unknown' for status in component_statuses):
            health_status['overall_status'] = 'degraded'
        
        return health_status