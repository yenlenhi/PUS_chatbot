export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Source[];
  confidence?: number;
  sender?: 'user' | 'bot'; // For backward compatibility
}

export interface Source {
  title: string;
  filename: string;
  page?: number;
  url?: string;
  content?: string;
  confidence?: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
}