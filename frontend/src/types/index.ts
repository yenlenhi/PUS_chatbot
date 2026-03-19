// Chart data type for visualization
export interface ChartData {
  type: 'bar' | 'line' | 'pie' | 'area';
  title?: string;
  data: Array<Record<string, string | number>>;
  xKey?: string;
  yKeys?: string[];
  labels?: string[];
  description?: string;
}

// Image data type for displaying images
export interface ImageData {
  src: string; // URL or base64
  alt?: string;
  caption?: string;
  source_file?: string;
  page_number?: number;
}

// Uploaded image from user
export interface UploadedImage {
  id: string;
  name: string;
  mimeType: string;
  preview: string;
  base64: string;
  file?: File; // Optional, only present client-side
}

// File attachment (forms, templates, etc.)
export interface FileAttachment {
  file_name: string;
  file_type: string;
  download_url: string;
  description?: string;
  file_size?: number;
  category?: string;
}

export interface PerformanceMetrics {
  total_ms: number;
  stages: Record<string, number>;
  time_to_first_token_ms?: number | null;
  retrieval_cache_hit: boolean;
  attachment_lookup_skipped: boolean;
  needs_grounding: boolean;
  normalization_applied: boolean;
  rewrite_applied: boolean;
  memory_loaded: boolean;
  retrieved_chunk_count: number;
  response_path: 'rag' | 'policy' | 'vision' | 'error' | string;
  policy_applied?: string | null;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string | Date;
  followUpQuestions?: string[];
  sources?: Source[];
  sourceReferences?: SourceReference[];
  attachments?: FileAttachment[]; // File attachments
  confidence?: number;
  sender?: 'user' | 'bot'; // For backward compatibility
  userQuery?: string; // Original user query (for feedback)
  chunkIds?: number[]; // Chunk IDs used in response (for feedback)
  chartData?: ChartData[]; // Charts to display
  images?: ImageData[]; // Images to display
  uploadedImages?: UploadedImage[]; // Images uploaded by user
  performance?: PerformanceMetrics;
}

export interface Source {
  title: string;
  filename: string;
  page?: number;
  url?: string;
  content?: string;
  confidence?: number;
}

export interface SourceReference {
  chunk_id: string;
  filename: string;
  page_number: number | null;
  heading: string | null;
  content_snippet: string;
  full_content: string;
  relevance_score: number;
  dense_score: number | null;
  sparse_score: number | null;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
}

export interface ChatApiResponse {
  response: string;
  answer?: string;
  follow_up_questions?: string[];
  confidence: number;
  sources: string[];
  source_references: SourceReference[];
  attachments?: FileAttachment[];
  conversation_id?: string;
  processing_time?: number;
  chart_data?: ChartData[]; // Charts from backend
  images?: ImageData[]; // Images from backend
  performance?: PerformanceMetrics;
  error?: string;
  detail?: string;
}
