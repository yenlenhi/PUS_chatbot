'use client';

import React, { useState, useEffect } from 'react';
import {
  ThumbsUp,
  ThumbsDown,
  TrendingUp,
  TrendingDown,
  MessageSquare,
  BarChart3,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
} from 'lucide-react';
import type {
  DashboardMetrics,
  FeedbackTimeStats,
  ChunkPerformance,
  FeedbackRecord,
} from '@/types/feedback';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

const FeedbackDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboard = async () => {
    try {
      setRefreshing(true);
      const response = await fetch(`${API_BASE}/api/v1/feedback/dashboard`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      setMetrics(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard:', err);
      setError('Không thể tải dữ liệu dashboard. Vui lòng thử lại.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    // Auto refresh every 5 minutes
    const interval = setInterval(fetchDashboard, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-red-600" />
        <span className="ml-2 text-gray-600">Đang tải dữ liệu...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-red-700">
          <AlertTriangle className="w-5 h-5" />
          <span>{error}</span>
        </div>
        <button
          onClick={fetchDashboard}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Thử lại
        </button>
      </div>
    );
  }

  if (!metrics) return null;

  const { overall_stats, daily_stats, top_chunks, worst_chunks, recent_negative_feedback } = metrics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">📊 Feedback Dashboard</h1>
        <button
          onClick={fetchDashboard}
          disabled={refreshing}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Làm mới
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Tổng phản hồi"
          value={overall_stats.total_feedback}
          icon={<MessageSquare className="w-6 h-6" />}
          color="blue"
        />
        <StatCard
          title="Tỷ lệ tích cực"
          value={`${overall_stats.positive_rate}%`}
          icon={<ThumbsUp className="w-6 h-6" />}
          color="green"
          subtitle={`${overall_stats.positive_count} phản hồi`}
        />
        <StatCard
          title="Tỷ lệ tiêu cực"
          value={`${overall_stats.negative_rate}%`}
          icon={<ThumbsDown className="w-6 h-6" />}
          color="red"
          subtitle={`${overall_stats.negative_count} phản hồi`}
        />
        <StatCard
          title="Chất lượng TB"
          value={`${(overall_stats.avg_response_quality * 100).toFixed(0)}%`}
          icon={<BarChart3 className="w-6 h-6" />}
          color="purple"
        />
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          title="Thời gian phản hồi TB"
          value={`${metrics.avg_response_time_ms.toFixed(0)}ms`}
          icon={<Clock className="w-6 h-6" />}
          color="orange"
        />
        <StatCard
          title="Tổng truy vấn"
          value={metrics.total_queries}
          icon={<FileText className="w-6 h-6" />}
          color="indigo"
        />
        <StatCard
          title="Tỷ lệ có feedback"
          value={`${metrics.feedback_rate}%`}
          icon={<CheckCircle className="w-6 h-6" />}
          color="teal"
          subtitle={`${metrics.queries_with_feedback} có phản hồi`}
        />
      </div>

      {/* Daily Stats Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-600" />
          Thống kê 7 ngày gần nhất
        </h2>
        <DailyStatsChart dailyStats={daily_stats} />
      </div>

      {/* Chunk Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Chunks */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            Top Chunks Hiệu quả
          </h2>
          <ChunkList chunks={top_chunks} type="top" />
        </div>

        {/* Worst Chunks */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingDown className="w-5 h-5 text-red-600" />
            Chunks Cần Cải thiện
          </h2>
          <ChunkList chunks={worst_chunks} type="worst" />
        </div>
      </div>

      {/* Recent Negative Feedback */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-orange-600" />
          Phản hồi tiêu cực gần đây
        </h2>
        <NegativeFeedbackList records={recent_negative_feedback} />
      </div>
    </div>
  );
};

// Stat Card Component
interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  subtitle?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, subtitle }) => {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
    indigo: 'bg-indigo-50 text-indigo-600',
    teal: 'bg-teal-50 text-teal-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color] || colorClasses.blue}`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

// Daily Stats Chart Component
const DailyStatsChart: React.FC<{ dailyStats: FeedbackTimeStats[] }> = ({ dailyStats }) => {
  if (!dailyStats || dailyStats.length === 0) {
    return <p className="text-gray-500 text-center py-4">Chưa có dữ liệu</p>;
  }

  const maxTotal = Math.max(...dailyStats.map((d) => d.total), 1);

  return (
    <div className="space-y-3">
      {dailyStats.map((stat) => (
        <div key={stat.date} className="flex items-center gap-4">
          <span className="text-sm text-gray-600 w-24">{stat.date}</span>
          <div className="flex-1 flex items-center gap-1 h-6">
            <div
              className="h-full bg-green-500 rounded-l"
              style={{ width: `${(stat.positive / maxTotal) * 100}%` }}
              title={`Tích cực: ${stat.positive}`}
            />
            <div
              className="h-full bg-gray-400"
              style={{ width: `${(stat.neutral / maxTotal) * 100}%` }}
              title={`Trung lập: ${stat.neutral}`}
            />
            <div
              className="h-full bg-red-500 rounded-r"
              style={{ width: `${(stat.negative / maxTotal) * 100}%` }}
              title={`Tiêu cực: ${stat.negative}`}
            />
          </div>
          <span className="text-sm text-gray-500 w-12 text-right">{stat.total}</span>
        </div>
      ))}
      <div className="flex items-center gap-4 mt-4 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-green-500 rounded" />
          <span>Tích cực</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-gray-400 rounded" />
          <span>Trung lập</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-red-500 rounded" />
          <span>Tiêu cực</span>
        </div>
      </div>
    </div>
  );
};

// Chunk List Component
const ChunkList: React.FC<{ chunks: ChunkPerformance[]; type: 'top' | 'worst' }> = ({
  chunks,
  type,
}) => {
  if (!chunks || chunks.length === 0) {
    return <p className="text-gray-500 text-center py-4">Chưa có dữ liệu</p>;
  }

  return (
    <div className="space-y-3">
      {chunks.map((chunk) => (
        <div key={chunk.chunk_id} className="border rounded-lg p-3">
          <div className="flex items-center justify-between">
            <span className="font-medium text-sm">Chunk #{chunk.chunk_id}</span>
            <span
              className={`text-sm font-semibold ${
                type === 'top' ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {(chunk.effectiveness_score * 100).toFixed(0)}%
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1 truncate">{chunk.source_file}</p>
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span>Sử dụng: {chunk.times_used}</span>
            <span className="text-green-600">👍 {chunk.positive_feedback}</span>
            <span className="text-red-600">👎 {chunk.negative_feedback}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

// Negative Feedback List Component
const NegativeFeedbackList: React.FC<{ records: FeedbackRecord[] }> = ({ records }) => {
  if (!records || records.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
        <p>Không có phản hồi tiêu cực gần đây!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {records.map((record) => (
        <div key={record.id} className="border-l-4 border-red-500 bg-red-50 rounded-r-lg p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-800">
                <span className="text-gray-500">Q:</span> {record.query}
              </p>
              <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                <span className="text-gray-500">A:</span> {record.answer.substring(0, 200)}...
              </p>
              {record.comment && (
                <p className="text-sm text-red-700 mt-2 italic">
                  <span className="text-gray-500">💬</span> {record.comment}
                </p>
              )}
            </div>
            <span className="text-xs text-gray-400 ml-4">
              {new Date(record.created_at).toLocaleDateString('vi-VN')}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default FeedbackDashboard;
