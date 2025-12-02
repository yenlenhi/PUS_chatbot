export interface Message {
  id: string;
  role?: 'user' | 'assistant';
  content: string;
  timestamp: string | Date;
  sources?: Source[];
  confidence?: number;
  isStreaming?: boolean; // Thêm flag để đánh dấu đang streaming
  error?: boolean; // Thêm flag để đánh dấu lỗi
  sender?: 'user' | 'bot'; // For backward compatibility
  userQuery?: string; // Original user query (for feedback)
  chunkIds?: number[]; // Chunk IDs used in response (for feedback)
}