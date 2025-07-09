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
  return sources.map(source => ({ title: source }));
};

