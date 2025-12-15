// Analytics Types for Dashboard

export type TimeRange = 'L7D' | 'MTD' | 'YTD' | 'custom';

// ==================== SYSTEM INSIGHTS ====================

export interface TokenUsage {
  date: string;
  hour?: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  estimated_cost: number;
}

export interface SystemAccessMetrics {
  date: string;
  hour?: number;
  total_requests: number;
  unique_sessions: number;
  blocked_requests: number;
}

export interface SystemInsights {
  token_usage_daily: TokenUsage[];
  token_usage_hourly: TokenUsage[];
  total_tokens: number;
  total_estimated_cost: number;
  access_daily: SystemAccessMetrics[];
  access_hourly: SystemAccessMetrics[];
  total_requests: number;
  total_blocked: number;
  period_start: string;
  period_end: string;
}

// ==================== USER INSIGHTS ====================

export interface UserFrequency {
  frequency: string;
  user_count: number;
  percentage: number;
}

export interface UserSegment {
  segment: string;
  min_questions: number;
  user_count: number;
  percentage: number;
}

export interface TopicInterest {
  topic: string;
  query_count: number;
  percentage: number;
}

export interface PopularQuestion {
  question: string;
  count: number;
  last_asked?: string;
}

export interface UserFunnelStage {
  stage: string;
  count: number;
  percentage: number;
  conversion_rate?: number;
}

export interface DailyUsers {
  date: string;
  unique_users: number;
  new_users: number;
  returning_users: number;
}

export interface UserInsights {
  daily_users: DailyUsers[];
  total_unique_users: number;
  return_frequency: UserFrequency[];
  user_segments: UserSegment[];
  new_users_ytd: number;
  retain_users_ytd: number;
  topics: TopicInterest[];
  popular_questions: PopularQuestion[];
  funnel: UserFunnelStage[];
  period_start: string;
  period_end: string;
}

// ==================== CHAT INSIGHTS ====================

export interface ChatMetrics {
  date: string;
  user_messages: number;
  ai_responses: number;
  likes: number;
  dislikes: number;
  avg_messages_per_conversation: number;
  avg_conversation_duration_seconds: number;
}

export interface UnansweredQuestion {
  question: string;
  count: number;
  last_occurrence: string;
}

export interface LowRatedResponse {
  query: string;
  answer: string;
  dislike_count: number;
  source_files: string[];
}

export interface ChatInsights {
  daily_metrics: ChatMetrics[];
  total_user_messages: number;
  total_ai_responses: number;
  like_rate: number;
  dislike_rate: number;
  avg_messages_per_conversation: number;
  avg_conversation_duration_seconds: number;
  unanswered_questions: UnansweredQuestion[];
  low_rated_responses: LowRatedResponse[];
  period_start: string;
  period_end: string;
}

// ==================== DOCUMENT INSIGHTS ====================

export interface CategoryStats {
  category: string;
  document_count: number;
  total_size_bytes: number;
  active_count: number;
  inactive_count: number;
}

export interface TopDocument {
  filename: string;
  retrieval_count: number;
  positive_feedback: number;
  negative_feedback: number;
  effectiveness_score: number;
}

export interface DocumentGrowth {
  month: string;
  new_documents: number;
  total_documents: number;
  total_size_bytes: number;
}

export interface DocumentInsights {
  total_documents: number;
  total_size_bytes: number;
  active_documents: number;
  inactive_documents: number;
  category_stats: CategoryStats[];
  top_retrieved_documents: TopDocument[];
  growth_trend: DocumentGrowth[];
  period_start: string;
  period_end: string;
}

// ==================== BUSINESS INSIGHTS ====================

export interface ContentGap {
  topic: string;
  query_count: number;
  document_coverage: number;
  suggested_action: string;
}

export interface QualityScore {
  category: string;
  score: number;
  weight: number;
}

export interface BusinessInsights {
  estimated_hours_saved: number;
  estimated_queries_handled: number;
  avg_response_time_seconds: number;
  content_gaps: ContentGap[];
  overall_quality_score: number;
  quality_breakdown: QualityScore[];
  period_start: string;
  period_end: string;
}

// ==================== DASHBOARD OVERVIEW ====================

export interface DashboardOverview {
  total_conversations: number;
  total_messages: number;
  total_documents: number;
  total_users: number;
  conversations_change: number;
  messages_change: number;
  documents_change: number;
  users_change: number;
  avg_response_time_ms: number;
  response_time_change: number;
  satisfaction_rate: number;
  satisfaction_change: number;
  today_conversations: number;
  today_messages: number;
  today_new_users: number;
}

// ==================== FILTER OPTIONS ====================

export interface AnalyticsFilter {
  timeRange: TimeRange;
  startDate?: string;
  endDate?: string;
  category?: string;
}

// ==================== CHART DATA ====================

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface LineChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor?: string;
    backgroundColor?: string;
  }[];
}

export interface BarChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
  }[];
}

export interface PieChartData {
  labels: string[];
  datasets: {
    data: number[];
    backgroundColor: string[];
  }[];
}
