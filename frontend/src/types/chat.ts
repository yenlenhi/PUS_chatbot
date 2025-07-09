export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Source[];
  confidence?: number;
  isStreaming?: boolean; // Thêm flag để đánh dấu đang streaming
  error?: boolean; // Thêm flag để đánh dấu lỗi
}