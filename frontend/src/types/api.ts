// API Types for University Chatbot

export interface ChatRequest {
  question: string;
  conversation_id?: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  confidence: number;
  conversation_id: string;
}

export interface SearchRequest {
  query: string;
  top_k?: number;
}

export interface SearchResult {
  content: string;
  source: string;
  page?: number;
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total_found: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  ollama_status: string;
  database_status: string;
}

// Frontend specific types
export interface Source {
  title: string;
  filename: string;
  page?: number;
  url?: string;
  content?: string;
  confidence?: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Source[] | string[];
  confidence?: number;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  conversationId?: string;
  error?: string;
}

// Thêm hàm helper để chuyển đổi sources từ string[] sang Source[]
export const convertSourcesToSourceObjects = (sources: string[]): Source[] => {
  return sources.map(source => ({ title: source, filename: source }));
};

// ==================== Chat History Types ====================

export interface ConversationSummary {
  id: string;
  conversation_id: string;
  message_count: number;
  first_message: string | null;
  last_message: string | null;
  avg_confidence: number;
  total_processing_time: number;
  first_query: string | null;
  status: 'active' | 'completed';
}

export interface ConversationMessage {
  id: number;
  user_message: string;
  assistant_response: string;
  sources: string[];
  confidence: number;
  processing_time: number;
  timestamp: string | null;
}

export interface ConversationDetail {
  conversation_id: string;
  message_count: number;
  messages: ConversationMessage[];
  total_processing_time: number;
  avg_confidence: number;
  first_message: string | null;
  last_message: string | null;
}

export interface ChatHistoryStats {
  total_conversations: number;
  total_messages: number;
  today_conversations: number;
  active_conversations: number;
  avg_confidence: number;
  avg_processing_time: number;
  popular_topics: { topic: string; count: number }[];
}

export interface ChatHistoryResponse {
  conversations: ConversationSummary[];
  total: number;
  limit: number;
  offset: number;
  stats: {
    total_conversations: number;
    active_conversations: number;
    today_conversations: number;
    total_messages: number;
  };
}

export interface ChatHistoryExport {
  export_date: string;
  start_date: string | null;
  end_date: string | null;
  total_conversations: number;
  conversations: {
    conversation_id: string;
    messages: {
      user_message: string;
      assistant_response: string;
      sources: string[];
      confidence: number;
      processing_time: number;
      timestamp: string | null;
    }[];
  }[];
}

// ==================== Chat History Types ====================

export interface ConversationMessage {
  id: number;
  user_message: string;
  assistant_response: string;
  sources: string[];
  confidence: number;
  processing_time: number;
  timestamp: string;
}

export interface ConversationSummary {
  id: string;
  conversation_id: string;
  message_count: number;
  first_message: string;
  last_message: string;
  avg_confidence: number;
  total_processing_time: number;
  first_query: string;
  status: 'active' | 'completed';
}

export interface ConversationDetail {
  conversation_id: string;
  message_count: number;
  messages: ConversationMessage[];
  total_processing_time: number;
  avg_confidence: number;
  first_message: string;
  last_message: string;
}

export interface ChatHistoryResponse {
  conversations: ConversationSummary[];
  total: number;
  limit: number;
  offset: number;
  stats: {
    total_conversations: number;
    active_conversations: number;
    today_conversations: number;
    total_messages: number;
  };
}

export interface ChatHistoryStats {
  total_conversations: number;
  total_messages: number;
  today_conversations: number;
  active_conversations: number;
  avg_confidence: number;
  avg_processing_time: number;
  popular_topics: Array<{
    topic: string;
    count: number;
  }>;
}

export interface ChatHistoryExport {
  export_date: string;
  start_date: string | null;
  end_date: string | null;
  total_conversations: number;
  conversations: Array<{
    conversation_id: string;
    messages: ConversationMessage[];
  }>;
}

// ==================== Document Management Types ====================

export interface Document {
  id: string;
  name: string;
  category: string;
  size: number;
  size_formatted: string;
  uploadDate: string;
  uploadDateTime: string;
  status: 'active' | 'inactive' | 'processing' | 'pending' | 'error';
  is_active: boolean | null;  // null for pending documents
  downloads: number;
  format: string;
  chunks: number;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
  categories: string[];
}

export interface ToggleActiveResponse {
  success: boolean;
  message: string;
  filename: string;
  is_active: boolean;
  chunks_affected: number;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  filename: string;
  file_size: number;
  chunks_created?: number;
  embeddings_created?: number;
  category?: string;
  use_gemini?: boolean;
  status: 'success' | 'warning' | 'error';
}

export interface DeleteDocumentResponse {
  success: boolean;
  message: string;
}