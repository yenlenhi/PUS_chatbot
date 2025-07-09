import { ChatRequest, ChatResponse, SearchRequest, SearchResponse, HealthResponse } from '@/types/api';

// API Base URL - có thể config từ environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function for API calls
const apiCall = async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
  const url = `${API_BASE_URL}${endpoint}`;

  console.log(`API Request: ${options.method || 'GET'} ${url}`);

  try {
    const response = await fetch(url, {
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

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
        
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/chat`, {
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
                } catch (e) {
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
      sources: response.sources.map(source => ({ title: source })),
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
  getConversation: async (conversationId: string): Promise<any> => {
    return apiCall(`/api/v1/conversation/${conversationId}`);
  },
};

export default chatAPI;





