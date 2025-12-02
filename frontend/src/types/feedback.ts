// Feedback Types for University Chatbot

export type FeedbackRating = 'positive' | 'negative' | 'neutral';

export interface FeedbackRequest {
  conversation_id: string;
  message_id?: string;
  query: string;
  answer: string;
  rating: FeedbackRating;
  comment?: string;
  chunk_ids?: number[];
  user_id?: string;
  session_id?: string;
}

export interface FeedbackResponse {
  id: number;
  status: string;
  message: string;
}

export interface FeedbackRecord {
  id: number;
  conversation_id: string;
  message_id?: string;
  query: string;
  answer: string;
  rating: FeedbackRating;
  comment?: string;
  chunk_ids: number[];
  user_id?: string;
  session_id?: string;
  created_at: string;
}

export interface FeedbackStats {
  total_feedback: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  positive_rate: number;
  negative_rate: number;
  avg_response_quality: number;
}

export interface FeedbackTimeStats {
  date: string;
  total: number;
  positive: number;
  negative: number;
  neutral: number;
}

export interface ChunkPerformance {
  chunk_id: number;
  source_file: string;
  times_used: number;
  positive_feedback: number;
  negative_feedback: number;
  effectiveness_score: number;
}

export interface DashboardMetrics {
  overall_stats: FeedbackStats;
  daily_stats: FeedbackTimeStats[];
  avg_response_time_ms: number;
  total_queries: number;
  queries_with_feedback: number;
  feedback_rate: number;
  top_chunks: ChunkPerformance[];
  worst_chunks: ChunkPerformance[];
  recent_negative_feedback: FeedbackRecord[];
}

export interface FeedbackReport {
  report_date: string;
  period_days: number;
  summary: {
    total_feedback: number;
    positive_rate: number;
    negative_rate: number;
    avg_response_quality: number;
    feedback_rate: number;
  };
  daily_breakdown: FeedbackTimeStats[];
  top_performing_chunks: ChunkPerformance[];
  worst_performing_chunks: ChunkPerformance[];
  retrieval_weights_updated: number;
  training_samples_available: number;
  recommendations: string[];
}
