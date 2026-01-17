import {
  TimeRange,
  SystemInsights,
  UserInsights,
  ChatInsights,
  DocumentInsights,
  BusinessInsights,
  DashboardOverview,
  AnalyticsFilter,
} from '@/types/analytics';

// API Base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function for API calls
const apiCall = async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
  const url = `${API_BASE_URL}${endpoint}`;

  console.log(`Analytics API Request: ${options.method || 'GET'} ${url}`);

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
    console.error('Analytics API Error:', error);

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Không thể kết nối đến server.');
    }

    throw error;
  }
};

// Build query params from filter
const buildQueryParams = (filter: AnalyticsFilter): string => {
  const params = new URLSearchParams();
  params.append('time_range', filter.timeRange);

  if (filter.timeRange === 'custom' && filter.startDate && filter.endDate) {
    params.append('start_date', filter.startDate);
    params.append('end_date', filter.endDate);
  }

  if (filter.category) {
    params.append('category', filter.category);
  }

  return params.toString();
};

// Analytics API Functions
export const analyticsAPI = {
  // Get dashboard overview
  getOverview: async (): Promise<DashboardOverview> => {
    return apiCall<DashboardOverview>('/api/v1/analytics/overview');
  },

  // Get system insights
  getSystemInsights: async (filter: AnalyticsFilter = { timeRange: 'L7D' }): Promise<SystemInsights> => {
    const query = buildQueryParams(filter);
    return apiCall<SystemInsights>(`/api/v1/analytics/system?${query}`);
  },

  // Get user insights
  getUserInsights: async (filter: AnalyticsFilter = { timeRange: 'L7D' }): Promise<UserInsights> => {
    const query = buildQueryParams(filter);
    return apiCall<UserInsights>(`/api/v1/analytics/users?${query}`);
  },

  // Get chat insights
  getChatInsights: async (filter: AnalyticsFilter = { timeRange: 'L7D' }): Promise<ChatInsights> => {
    const query = buildQueryParams(filter);
    return apiCall<ChatInsights>(`/api/v1/analytics/chat?${query}`);
  },

  // Get document insights
  getDocumentInsights: async (filter: AnalyticsFilter = { timeRange: 'L7D' }): Promise<DocumentInsights> => {
    const query = buildQueryParams(filter);
    return apiCall<DocumentInsights>(`/api/v1/analytics/documents?${query}`);
  },

  // Get business insights
  getBusinessInsights: async (filter: AnalyticsFilter = { timeRange: 'L7D' }): Promise<BusinessInsights> => {
    const query = buildQueryParams(filter);
    return apiCall<BusinessInsights>(`/api/v1/analytics/business?${query}`);
  },

  // Get popular questions from real data
  getPopularQuestions: async (filter: AnalyticsFilter = { timeRange: 'L7D' }, limit: number = 10) => {
    const query = buildQueryParams(filter);
    const params = new URLSearchParams(query);
    params.append('limit', limit.toString());
    return apiCall(`/api/v1/analytics/popular-questions?${params.toString()}`);
  },

  // Get all insights at once
  getAllInsights: async (filter: AnalyticsFilter = { timeRange: 'L7D' }) => {
    const [overview, system, users, chat, documents, business] = await Promise.all([
      analyticsAPI.getOverview(),
      analyticsAPI.getSystemInsights(filter),
      analyticsAPI.getUserInsights(filter),
      analyticsAPI.getChatInsights(filter),
      analyticsAPI.getDocumentInsights(filter),
      analyticsAPI.getBusinessInsights(filter),
    ]);

    return { overview, system, users, chat, documents, business };
  },

  // Export Data
  exportData: async (type: string, filter: AnalyticsFilter = { timeRange: 'L7D' }) => {
    const query = buildQueryParams(filter);
    const url = `${API_BASE_URL}/api/v1/admin/analytics/export?${query}&type=${type}&format=excel`;

    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('Export failed');
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `export_${type}_${new Date().toISOString().slice(0, 10)}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
      return true;
    } catch (error) {
      console.error("Export error:", error);
      throw error;
    }
  },
};

// Utility functions for formatting
export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toLocaleString();
};

export const formatBytes = (bytes: number): string => {
  if (bytes >= 1073741824) {
    return (bytes / 1073741824).toFixed(2) + ' GB';
  }
  if (bytes >= 1048576) {
    return (bytes / 1048576).toFixed(2) + ' MB';
  }
  if (bytes >= 1024) {
    return (bytes / 1024).toFixed(2) + ' KB';
  }
  return bytes + ' B';
};

export const formatCurrency = (amount: number): string => {
  return amount.toLocaleString('vi-VN') + ' ₫';
};

export const formatPercentage = (value: number): string => {
  return value.toFixed(1) + '%';
};

export const formatDuration = (seconds: number): string => {
  if (seconds >= 3600) {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
  }
  if (seconds >= 60) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  }
  return `${seconds.toFixed(1)}s`;
};

export const getTimeRangeLabel = (timeRange: TimeRange): string => {
  switch (timeRange) {
    case 'L7D':
      return '7 ngày qua';
    case 'MTD':
      return 'Tháng này';
    case 'YTD':
      return 'Năm nay';
    case 'custom':
      return 'Tùy chỉnh';
    default:
      return '7 ngày qua';
  }
};

export default analyticsAPI;
