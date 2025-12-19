import { ChatRequest, ChatResponse, SearchRequest, SearchResponse, HealthResponse, ChatHistoryResponse, ConversationDetail, ChatHistoryStats, ChatHistoryExport, Document, DocumentListResponse, UploadResponse, DeleteDocumentResponse, ToggleActiveResponse } from '@/types/api';
import { Message } from '@/types';

// API Base URL - có thể config từ environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function for API calls
const apiCall = async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
  const url = `${API_BASE_URL}${endpoint}`;

  console.log(`API Request: ${options.method || 'GET'} ${url}`);

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);
    
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    clearTimeout(timeoutId);

    console.log(`API Response: ${response.status} ${url}`);

    if (!response.ok) {
      let errorMessage = 'Đã xảy ra lỗi không xác định.';

      if (response.status === 422) {
        errorMessage = 'Dữ liệu đầu vào không hợp lệ.';
      } else if (response.status === 500) {
        errorMessage = 'Lỗi server. Vui lòng thử lại sau.';
      } else {
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // Ignore JSON parse error
        }
      }

      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Không thể kết nối đến server. Vui lòng kiểm tra server có đang chạy không.');
    }

    throw error;
  }
};

// API Functions
const STREAM_TIMEOUT = 30000; // 30 seconds

export const chatAPI = {
  // Cải thiện phương thức streaming
  sendMessageStream: async (request: ChatRequest, onChunk: (chunk: string) => void): Promise<ChatResponse> => {
    // Tạo promise với timeout
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error('Stream request timeout')), STREAM_TIMEOUT);
    });
    
    // Tạo promise cho stream processing
    const streamPromise = (async () => {
      try {
        console.log("Sending streaming request:", request);
        
        const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
          },
          body: JSON.stringify(request),
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error(`API error (${response.status}):`, errorText);
          throw new Error(`API error: ${response.status} - ${errorText}`);
        }

        // Kiểm tra nếu response là stream
        if (response.body) {
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let buffer = '';
          let fullResponse: ChatResponse = {
            answer: '',
            sources: [],
            confidence: 0,
            conversation_id: '',
          };

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            // Decode chunk và thêm vào buffer
            const chunk = decoder.decode(value, { stream: true });
            console.log("Received chunk:", chunk);
            buffer += chunk;
            
            // Xử lý từng dòng trong buffer
            let newlineIndex;
            while ((newlineIndex = buffer.indexOf('\n')) >= 0) {
              const line = buffer.slice(0, newlineIndex);
              buffer = buffer.slice(newlineIndex + 1);
              
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                try {
                  // Nếu là JSON hoàn chỉnh
                  if (data.includes('"answer"') || data.includes('"sources"') || data.includes('"confidence"')) {
                    const jsonData = JSON.parse(data);
                    fullResponse = {
                      ...fullResponse,
                      ...jsonData
                    };
                    onChunk(jsonData.answer || '');
                  } else {
                    // Nếu chỉ là một phần của câu trả lời
                    onChunk(data);
                    fullResponse.answer += data;
                  }
                } catch {
                  console.log("Not JSON, treating as text chunk:", data);
                  // Nếu không phải JSON, coi như là một phần của câu trả lời
                  onChunk(data);
                  fullResponse.answer += data;
                }
              }
            }
          }
          
          console.log("Stream completed, full response:", fullResponse);
          
          // Thêm fallback nếu không nhận được dữ liệu
          if (!fullResponse.answer && !fullResponse.sources.length) {
            console.warn('No answer received from stream, using fallback');
            return {
              answer: 'Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này. Vui lòng thử lại sau.',
              sources: [],
              confidence: 0,
              conversation_id: request.conversation_id || '',
            };
          }
          
          return fullResponse;
        } else {
          // Fallback nếu không phải stream
          console.log("Not a stream response, parsing as JSON");
          const data = await response.json();
          console.log("Parsed JSON response:", data);
          onChunk(data.answer || '');
          return data;
        }
      } catch (error) {
        console.error("Error in sendMessageStream:", error);
        throw error;
      }
    })();
    
    // Race giữa stream và timeout
    try {
      return await Promise.race([streamPromise, timeoutPromise]);
    } catch (error) {
      console.error('Stream error or timeout:', error);
      onChunk('Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn.');
      return {
        answer: 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn.',
        sources: [],
        confidence: 0,
        conversation_id: request.conversation_id || '',
      };
    }
  },
  
  // Giữ lại phương thức cũ để tương thích ngược
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    return apiCall<ChatResponse>('/api/v1/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },
  
  // Thêm hàm helper để chuyển đổi ChatResponse thành dạng Message
  formatChatResponseToMessage: (response: ChatResponse, messageId: string): Message => {
    return {
      id: messageId,
      role: 'assistant',
      content: response.answer,
      timestamp: new Date().toISOString(),
      sources: response.sources.map(source => ({ title: source, filename: source })),
      confidence: response.confidence
    };
  },
  
  // Search documents
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    return apiCall<SearchResponse>('/api/v1/search', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  // Health check
  healthCheck: async (): Promise<HealthResponse> => {
    return apiCall<HealthResponse>('/api/v1/health');
  },

  // Get conversation history
  getConversation: async (conversationId: string): Promise<unknown> => {
    return apiCall(`/api/v1/conversation/${conversationId}`);
  },
};

// ==================== Chat History API ====================

export const chatHistoryAPI = {
  // Get all conversations with pagination
  getConversations: async (
    limit: number = 50,
    offset: number = 0,
    search?: string,
    status?: string
  ): Promise<ChatHistoryResponse> => {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());
    if (search) params.append('search', search);
    if (status && status !== 'all') params.append('status', status);
    
    return apiCall<ChatHistoryResponse>(`/api/v1/admin/chat-history?${params.toString()}`);
  },

  // Get conversation detail
  getConversationDetail: async (conversationId: string): Promise<ConversationDetail> => {
    return apiCall<ConversationDetail>(`/api/v1/admin/chat-history/${encodeURIComponent(conversationId)}`);
  },

  // Delete conversation
  deleteConversation: async (conversationId: string): Promise<{ success: boolean; message: string }> => {
    return apiCall(`/api/v1/admin/chat-history/${encodeURIComponent(conversationId)}`, {
      method: 'DELETE',
    });
  },

  // Get chat statistics
  getStats: async (): Promise<ChatHistoryStats> => {
    return apiCall<ChatHistoryStats>('/api/v1/admin/chat-history/stats/overview');
  },

  // Export conversations
  exportConversations: async (startDate?: string, endDate?: string): Promise<ChatHistoryExport> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    return apiCall<ChatHistoryExport>(`/api/v1/admin/chat-history/export${queryString ? `?${queryString}` : ''}`);
  },
};

// ==================== Documents API ====================

export const documentsAPI = {
  // Get all documents
  getDocuments: async (): Promise<DocumentListResponse> => {
    return apiCall<DocumentListResponse>('/api/v1/admin/documents');
  },

  // Upload a new document
  uploadDocument: async (
    file: File,
    category: string = 'Khác',
    useGemini: boolean = true,
    onProgress?: (progress: number) => void
  ): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    formData.append('use_gemini', String(useGemini));

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  },

  // Delete a document
  deleteDocument: async (filename: string): Promise<DeleteDocumentResponse> => {
    return apiCall<DeleteDocumentResponse>(`/api/v1/admin/documents/${encodeURIComponent(filename)}`, {
      method: 'DELETE',
    });
  },

  // Toggle document active status
  toggleActive: async (filename: string): Promise<ToggleActiveResponse> => {
    return apiCall<ToggleActiveResponse>(`/api/v1/admin/documents/${encodeURIComponent(filename)}/toggle-active`, {
      method: 'PATCH',
    });
  },

  // Get document info
  getDocumentInfo: async (filename: string) => {
    return apiCall(`/api/v1/documents/${encodeURIComponent(filename)}/info`);
  },

  // Download document URL
  getDownloadUrl: (filename: string): string => {
    return `${API_BASE_URL}/api/v1/documents/${encodeURIComponent(filename)}`;
  },
};

export default chatAPI;





