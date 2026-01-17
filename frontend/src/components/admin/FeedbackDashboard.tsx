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
  Search,
  Filter,
  Download,
  MoreVertical,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
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
      <div className="flex flex-col items-center justify-center h-96">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-gray-200 border-t-red-600 rounded-full animate-spin"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <BarChart3 className="w-6 h-6 text-red-600" />
          </div>
        </div>
        <span className="mt-4 text-gray-500 font-medium">Đang tải dữ liệu báo cáo...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center max-w-lg mx-auto mt-10">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-red-800 mb-2">Đã xảy ra lỗi</h3>
        <p className="text-red-600 mb-6">{error}</p>
        <button
          onClick={fetchDashboard}
          className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors shadow-sm font-medium"
        >
          Thử lại
        </button>
      </div>
    );
  }

  if (!metrics) return null;

  const { overall_stats, daily_stats, top_chunks, worst_chunks, recent_negative_feedback } = metrics;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tổng quan phản hồi</h1>
          <p className="text-gray-500 mt-1">Theo dõi chất lượng câu trả lời và ý kiến người dùng</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400 hidden sm:inline">
            Cập nhật: {new Date().toLocaleTimeString('vi-VN')}
          </span>
          <button
            onClick={fetchDashboard}
            disabled={refreshing}
            className={`flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 rounded-lg shadow-sm transition-all ${refreshing ? 'opacity-70 cursor-not-allowed' : ''
              }`}
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Làm mới</span>
          </button>
        </div>
      </div>

      {/* Stats Cards Row 1 - Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Tổng phản hồi"
          value={overall_stats.total_feedback}
          icon={<MessageSquare className="w-6 h-6 text-white" />}
          gradient="from-blue-500 to-blue-600"
          trend="+12%" // Mock data for visual, replace with real if available
          trendUp={true}
        />
        <StatCard
          title="Tỷ lệ tích cực"
          value={`${overall_stats.positive_rate}%`}
          icon={<ThumbsUp className="w-6 h-6 text-white" />}
          gradient="from-green-500 to-green-600"
          subtitle={`${overall_stats.positive_count} đánh giá tốt`}
        />
        <StatCard
          title="Tỷ lệ tiêu cực"
          value={`${overall_stats.negative_rate}%`}
          icon={<ThumbsDown className="w-6 h-6 text-white" />}
          gradient="from-red-500 to-red-600"
          subtitle={`${overall_stats.negative_count} đánh giá xấu`}
          trend="-2%"
          trendUp={true} // Lower is better for negative rate :)
        />
        <StatCard
          title="Điểm chất lượng"
          value={`${(overall_stats.avg_response_quality * 100).toFixed(0)}`}
          suffix="/ 100"
          icon={<BarChart3 className="w-6 h-6 text-white" />}
          gradient="from-purple-500 to-purple-600"
          subtitle="Trung bình đánh giá"
        />
      </div>

      {/* Stats Cards Row 2 - Operational */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <OperationalCard
          title="Thời gian phản hồi TB"
          value={`${metrics.avg_response_time_ms.toFixed(0)}ms`}
          icon={<Clock className="w-5 h-5" />}
          color="text-orange-600"
          bg="bg-orange-50"
          borderColor="border-orange-100"
        />
        <OperationalCard
          title="Tổng truy vấn xử lý"
          value={metrics.total_queries}
          icon={<Search className="w-5 h-5" />}
          color="text-indigo-600"
          bg="bg-indigo-50"
          borderColor="border-indigo-100"
        />
        <OperationalCard
          title="Tỷ lệ người dùng phản hồi"
          value={`${metrics.feedback_rate}%`}
          icon={<CheckCircle className="w-5 h-5" />}
          color="text-teal-600"
          bg="bg-teal-50"
          borderColor="border-teal-100"
          subtitle={`${metrics.queries_with_feedback} / ${metrics.total_queries} lượt`}
        />
      </div>

      {/* Main Chart Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                Xu hướng phản hồi (7 ngày)
              </h2>
            </div>
          </div>
          <div className="h-[350px] w-full">
            <DailyStatsChart dailyStats={daily_stats} />
          </div>
        </div>

        {/* Top/Worst Chunks Tabs */}
        <div className="lg:col-span-1 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col">
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-600" />
              Hiệu suất Kiến thức
            </h2>
          </div>

          <div className="flex-1 overflow-hidden flex flex-col p-4">
            <h3 className="text-sm font-semibold text-green-700 uppercase tracking-wider mb-3 px-2">Top Hiệu quả nhất</h3>
            <div className="flex-1 overflow-y-auto pr-2 mb-4 custom-scrollbar">
              <ChunkList chunks={top_chunks} type="top" />
            </div>

            <h3 className="text-sm font-semibold text-red-700 uppercase tracking-wider mb-3 px-2 pt-4 border-t border-gray-100">Top Cần cải thiện</h3>
            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
              <ChunkList chunks={worst_chunks} type="worst" />
            </div>
          </div>
        </div>
      </div>

      {/* Recent Negative Feedback */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-6 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            Phản hồi cần chú ý gần đây
          </h2>
          <div className="flex gap-2">
            <button className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 transition-colors" title="Filter">
              <Filter className="w-4 h-4" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 transition-colors" title="Export">
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="p-6 bg-gray-50/50">
          <NegativeFeedbackList records={recent_negative_feedback} />
        </div>
      </div>
    </div>
  );
};

// ---------------------------
// Sub Components
// ---------------------------

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  gradient: string;
  subtitle?: string;
  trend?: string;
  trendUp?: boolean;
  suffix?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, gradient, subtitle, trend, trendUp, suffix }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 relative overflow-hidden group hover:shadow-md transition-all duration-300">
      <div className={`absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform duration-500`}>
        <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${gradient}`}></div>
      </div>

      <div className="relative z-10">
        <div className="flex items-start justify-between">
          <div className={`p-3 rounded-lg bg-gradient-to-br ${gradient} shadow-lg shadow-${gradient.split('-')[1]}-500/30`}>
            {icon}
          </div>
          {trend && (
            <div className={`flex items-center gap-1 text-sm font-medium ${trendUp ? 'text-green-600' : 'text-red-600'} bg-${trendUp ? 'green' : 'red'}-50 px-2 py-1 rounded-full`}>
              {trendUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              {trend}
            </div>
          )}
        </div>

        <div className="mt-4">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <div className="flex items-baseline gap-1 mt-1">
            <h3 className="text-3xl font-bold text-gray-900">{value}</h3>
            {suffix && <span className="text-sm text-gray-400 font-medium">{suffix}</span>}
          </div>
          {subtitle && <p className="text-sm text-gray-400 mt-2">{subtitle}</p>}
        </div>
      </div>
    </div>
  );
};

interface OperationalCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  bg: string;
  borderColor: string;
  subtitle?: string;
}

const OperationalCard: React.FC<OperationalCardProps> = ({ title, value, icon, color, bg, borderColor, subtitle }) => {
  return (
    <div className={`bg-white rounded-xl border ${borderColor} p-4 flex items-center gap-4 hover:shadow-sm transition-shadow`}>
      <div className={`p-3 rounded-lg ${bg} ${color}`}>
        {icon}
      </div>
      <div>
        <p className="text-sm text-gray-500 font-medium">{title}</p>
        <div className="flex items-center gap-2">
          <p className={`text-xl font-bold ${color}`}>{value}</p>
          {subtitle && <span className="text-xs text-gray-400">{subtitle}</span>}
        </div>
      </div>
    </div>
  )
}

const DailyStatsChart: React.FC<{ dailyStats: FeedbackTimeStats[] }> = ({ dailyStats }) => {
  if (!dailyStats || dailyStats.length === 0) {
    return <div className="flex items-center justify-center h-full text-gray-400">Chưa có dữ liệu biểu đồ</div>;
  }

  // Transform data for Recharts, ensuring dates are formatted nicely
  const chartData = dailyStats.map(item => ({
    ...item,
    formattedDate: item.date.split('-').slice(1).reverse().join('/'), // simple format
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={chartData}
        margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        barSize={32}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
        <XAxis
          dataKey="date"
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#6B7280', fontSize: 12 }}
          dy={10}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#6B7280', fontSize: 12 }}
        />
        <Tooltip
          cursor={{ fill: '#F3F4F6' }}
          contentStyle={{
            backgroundColor: '#fff',
            borderRadius: '8px',
            border: 'none',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          }}
        />
        <Legend
          verticalAlign="top"
          height={36}
          iconType="circle"
          formatter={(value) => <span className="text-sm font-medium text-gray-600 ml-1">{value === 'positive' ? 'Tích cực' : value === 'negative' ? 'Tiêu cực' : 'Trung bình'}</span>}
        />
        <Bar dataKey="positive" name="positive" stackId="a" fill="#10B981" radius={[0, 0, 4, 4]} />
        <Bar dataKey="neutral" name="neutral" stackId="a" fill="#9CA3AF" />
        <Bar dataKey="negative" name="negative" stackId="a" fill="#EF4444" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};

const ChunkList: React.FC<{ chunks: ChunkPerformance[]; type: 'top' | 'worst' }> = ({ chunks, type }) => {
  if (!chunks || chunks.length === 0) {
    return <p className="text-gray-500 text-sm text-center py-4 italic">Chưa có dữ liệu</p>;
  }

  return (
    <div className="space-y-3">
      {chunks.map((chunk) => {
        const score = Math.round(chunk.effectiveness_score * 100);
        return (
          <div key={chunk.chunk_id} className="group relative bg-white border border-gray-200 rounded-lg p-3 hover:border-gray-300 transition-colors">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-medium text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                  #{chunk.chunk_id}
                </span>
              </div>
              <span
                className={`text-sm font-bold ${type === 'top' ? 'text-green-600' : 'text-red-600'
                  }`}
              >
                {score}%
              </span>
            </div>

            <p className="text-sm text-gray-800 line-clamp-2 mb-2 font-medium" title={chunk.source_file}>
              {chunk.source_file.split('/').pop()}
            </p>

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{chunk.times_used} lần dùng</span>
              <div className="flex gap-2">
                <span className="flex items-center gap-1 text-green-600/80"><ThumbsUp className="w-3 h-3" /> {chunk.positive_feedback}</span>
                <span className="flex items-center gap-1 text-red-600/80"><ThumbsDown className="w-3 h-3" /> {chunk.negative_feedback}</span>
              </div>
            </div>

            {/* Progress Bar Background */}
            <div className="absolute bottom-0 left-0 h-1 bg-gray-100 w-full rounded-b-lg overflow-hidden">
              <div
                className={`h-full ${type === 'top' ? 'bg-green-500' : 'bg-red-500'}`}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  );
};

const NegativeFeedbackList: React.FC<{ records: FeedbackRecord[] }> = ({ records }) => {
  if (!records || records.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 bg-white rounded-xl border border-dashed border-gray-300">
        <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-3">
          <CheckCircle className="w-8 h-8 text-green-500" />
        </div>
        <p className="font-medium">Tuyệt vời!</p>
        <p className="text-sm mt-1">Không có phản hồi tiêu cực nào gần đây.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {records.map((record) => (
        <div key={record.id} className="bg-white border border-red-100 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>

          <div className="flex justify-between items-start mb-4 pl-2">
            <span className="text-xs text-gray-400 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(record.created_at).toLocaleDateString('vi-VN')}
            </span>
            <span className="px-2 py-1 bg-red-50 text-red-600 text-xs font-medium rounded-full border border-red-100">
              Tiêu cực
            </span>
          </div>

          <div className="space-y-3 pl-2">
            <div>
              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Câu hỏi</h4>
              <p className="text-sm font-medium text-gray-900 line-clamp-2" title={record.query}>{record.query}</p>
            </div>

            <div>
              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Câu trả lời bot</h4>
              <p className="text-sm text-gray-600 line-clamp-3 bg-gray-50 p-2 rounded border border-gray-100 text-xs font-mono">
                {record.answer}
              </p>
            </div>

            {record.comment && (
              <div className="pt-2 border-t border-gray-100 mt-2">
                <div className="flex items-start gap-2">
                  <MessageSquare className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
                  <p className="text-sm text-red-700 italic">"{record.comment}"</p>
                </div>
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-gray-50 flex justify-end pl-2">
            <button className="text-xs text-gray-500 hover:text-red-600 font-medium transition-colors flex items-center gap-1">
              Xem chi tiết <MoreVertical className="w-3 h-3" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default FeedbackDashboard;
