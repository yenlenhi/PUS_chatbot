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
  ChevronLeft,
  ChevronRight,
  User,
  Hash,
  X,
  Eye,
  Calendar
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
} from 'recharts';
import type {
  DashboardMetrics,
  FeedbackTimeStats,
  ChunkPerformance,
  FeedbackRecord,
} from '@/types/feedback';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

const FeedbackDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'history'>('overview');

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      {/* Header & Tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10 px-6 pt-6 pb-0 rounded-t-xl -mx-6 -mt-6 mb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Phản hồi & Đánh giá</h1>
            <p className="text-gray-500 mt-1">Theo dõi chất lượng phản hồi từ người dùng</p>
          </div>
        </div>

        <div className="flex gap-6 overflow-x-auto">
          <button
            onClick={() => setActiveTab('overview')}
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors whitespace-nowrap flex items-center gap-2 ${activeTab === 'overview'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
          >
            <BarChart3 className="w-4 h-4" />
            Tổng quan
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors whitespace-nowrap flex items-center gap-2 ${activeTab === 'history'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
          >
            <Clock className="w-4 h-4" />
            Lịch sử phản hồi
          </button>
        </div>
      </div>

      {activeTab === 'overview' ? <OverviewPanel /> : <HistoryPanel />}
    </div>
  );
};

// ----------------------------------------------------------------------
// OVERVIEW PANEL
// ----------------------------------------------------------------------

const OverviewPanel: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboard = async () => {
    try {
      setRefreshing(true);
      const response = await fetch(`${API_BASE}/api/v1/feedback/dashboard`);
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (err) {
      console.error('Error fetching dashboard:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) return <div className="h-96 flex items-center justify-center text-gray-400">Đang tải dữ liệu...</div>;
  if (!metrics) return <div className="p-8 text-center text-red-500 bg-red-50 rounded-xl">Lỗi tải dữ liệu</div>;

  const { overall_stats, daily_stats, top_chunks, worst_chunks } = metrics;

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Tổng phản hồi"
          value={overall_stats.total_feedback}
          icon={<MessageSquare className="w-5 h-5 text-blue-600" />}
          bg="bg-blue-50"
          border="border-blue-100"
        />
        <StatCard
          title="Tỷ lệ tích cực"
          value={`${overall_stats.positive_rate}%`}
          subtitle={`${overall_stats.positive_count} đánh giá tốt`}
          icon={<ThumbsUp className="w-5 h-5 text-green-600" />}
          bg="bg-green-50"
          border="border-green-100"
          trendUp={true}
        />
        <StatCard
          title="Tỷ lệ tiêu cực"
          value={`${overall_stats.negative_rate}%`}
          subtitle={`${overall_stats.negative_count} đánh giá xấu`}
          icon={<ThumbsDown className="w-5 h-5 text-red-600" />}
          bg="bg-red-50"
          border="border-red-100"
          trendUp={false}
        />
        <StatCard
          title="Chất lượng TB"
          value={`${(overall_stats.avg_response_quality * 10).toFixed(1)}/10`}
          icon={<TrendingUp className="w-5 h-5 text-purple-600" />}
          bg="bg-purple-50"
          border="border-purple-100"
        />
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-gray-800">Xu hướng phản hồi (7 ngày)</h3>
            <button onClick={fetchDashboard} className="p-2 hover:bg-gray-100 rounded-lg text-gray-500">
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
          <div className="h-[300px]">
            <DailyStatsChart dailyStats={daily_stats} />
          </div>
        </div>

        <div className="lg:col-span-1 flex flex-col gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex-1">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-500" />
              Cần cải thiện
            </h3>
            <div className="space-y-3 h-[280px] overflow-y-auto custom-scrollbar pr-2">
              {worst_chunks.length === 0 ? (
                <p className="text-gray-400 text-sm text-center py-4">Chưa có dữ liệu chunk kém hiệu quả</p>
              ) : (
                worst_chunks.map((chunk) => (
                  <div key={chunk.chunk_id} className="p-3 bg-red-50 border border-red-100 rounded-lg">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs font-mono font-medium text-red-600">ID: {chunk.chunk_id}</span>
                      <span className="text-xs font-bold text-red-700">{Math.round(chunk.effectiveness_score * 100)}%</span>
                    </div>
                    <p className="text-xs text-gray-700 line-clamp-2 mb-2" title={chunk.source_file}>
                      {(chunk.source_file || '').split('/').pop()}
                    </p>
                    <div className="flex gap-3 text-[10px] text-gray-500">
                      <span className="flex items-center gap-1"><ThumbsUp className="w-3 h-3" /> {chunk.positive_feedback}</span>
                      <span className="flex items-center gap-1"><ThumbsDown className="w-3 h-3" /> {chunk.negative_feedback}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ----------------------------------------------------------------------
// HISTORY PANEL
// ----------------------------------------------------------------------

const HistoryPanel: React.FC = () => {
  const [feedback, setFeedback] = useState<FeedbackRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState<FeedbackRecord | null>(null);

  // Filters
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [filterRating, setFilterRating] = useState<'positive' | 'negative' | 'neutral' | ''>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchQuery), 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
      });
      if (filterRating) queryParams.append('rating', filterRating);
      if (debouncedSearch) queryParams.append('search', debouncedSearch);

      const res = await fetch(`${API_BASE}/api/v1/feedback/list?${queryParams}`);
      if (res.ok) {
        const data = await res.json();
        setFeedback(data.records);
        setTotal(data.total);
      }
    } catch (e) {
      console.error("Error fetching history", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [offset, filterRating, debouncedSearch]);

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col overflow-hidden min-h-[600px]">
      {/* Toolbar */}
      <div className="p-4 border-b border-gray-100 flex flex-col md:flex-row gap-4 justify-between items-center bg-gray-50/50">
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Tìm kiếm nội dung, câu hỏi..."
            className="w-full pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <select
            className="px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
            value={filterRating}
            onChange={(e) => {
              setFilterRating(e.target.value as any);
              setOffset(0);
            }}
          >
            <option value="">Tất cả đánh giá</option>
            <option value="positive">Tích cực (👍)</option>
            <option value="negative">Tiêu cực (👎)</option>
            <option value="neutral">Trung lập</option>
          </select>

          <button
            onClick={fetchHistory}
            className="p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-500"
            title="Làm mới"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-left border-collapse">
          <thead className="bg-gray-50 sticky top-0 z-10 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            <tr>
              <th className="px-6 py-3 border-b border-gray-200">Thời gian</th>
              <th className="px-6 py-3 border-b border-gray-200">Đánh giá</th>
              <th className="px-6 py-3 border-b border-gray-200 w-1/3">Câu hỏi</th>
              <th className="px-6 py-3 border-b border-gray-200 w-1/3">Phản hồi của Bot</th>
              <th className="px-6 py-3 border-b border-gray-200 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading && feedback.length === 0 ? (
              <tr><td colSpan={5} className="p-8 text-center text-gray-400">Đang tải dữ liệu...</td></tr>
            ) : feedback.length === 0 ? (
              <tr><td colSpan={5} className="p-8 text-center text-gray-400">Không tìm thấy dữ liệu phù hợp</td></tr>
            ) : (
              feedback.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50 transition-colors group">
                  <td className="px-6 py-4 text-sm text-gray-500 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <Clock className="w-3 h-3" />
                      {new Date(item.created_at).toLocaleDateString('vi-VN')}
                    </div>
                    <div className="text-xs text-gray-400 mt-1 pl-5">
                      {new Date(item.created_at).toLocaleTimeString('vi-VN')}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${item.rating === 'positive' ? 'bg-green-50 text-green-700 border-green-200' :
                        item.rating === 'negative' ? 'bg-red-50 text-red-700 border-red-200' :
                          'bg-gray-50 text-gray-700 border-gray-200'
                      }`}>
                      {item.rating === 'positive' && <ThumbsUp className="w-3 h-3" />}
                      {item.rating === 'negative' && <ThumbsDown className="w-3 h-3" />}
                      {item.rating === 'neutral' && <div className="w-1.5 h-1.5 rounded-full bg-gray-400" />}
                      {item.rating === 'positive' ? 'Hài lòng' : item.rating === 'negative' ? 'Không tốt' : 'Bình thường'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-sm text-gray-900 line-clamp-2 font-medium" title={item.query}>{item.query}</p>
                    {item.comment && (
                      <div className="mt-1.5 flex items-start gap-1.5 text-xs text-gray-500 italic bg-yellow-50 p-1.5 rounded border border-yellow-100">
                        <MessageSquare className="w-3 h-3 shrink-0 mt-0.5 text-yellow-600" />
                        "{item.comment}"
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-sm text-gray-600 line-clamp-2 font-mono text-xs bg-gray-50 p-1.5 rounded border border-gray-100">
                      {item.answer}
                    </p>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => setSelectedRecord(item)}
                      className="text-gray-400 hover:text-blue-600 hover:bg-blue-50 p-1.5 rounded transition-all"
                      title="Xem chi tiết"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
        <p className="text-sm text-gray-500">
          Hiển thị <span className="font-medium">{feedback.length > 0 ? offset + 1 : 0}</span> - <span className="font-medium">{Math.min(offset + limit, total)}</span> trong số <span className="font-medium">{total}</span>
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={offset === 0}
            className="p-2 bg-white border border-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => setOffset(offset + limit)}
            disabled={offset + limit >= total}
            className="p-2 bg-white border border-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Modal Detail */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <h3 className="font-bold text-gray-900 flex items-center gap-2">
                Chi tiết phản hồi #{selectedRecord.id}
              </h3>
              <button onClick={() => setSelectedRecord(null)} className="p-2 hover:bg-gray-200 rounded-full transition-colors">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto space-y-6">
              {/* Meta Info */}
              <div className="flex flex-wrap gap-4 text-sm text-gray-500 pb-4 border-b border-gray-100">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  {new Date(selectedRecord.created_at).toLocaleString('vi-VN')}
                </div>
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4" />
                  {selectedRecord.session_id || 'Unknown Session'}
                </div>
                <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border ${selectedRecord.rating === 'positive' ? 'bg-green-50 text-green-700 border-green-200' :
                    selectedRecord.rating === 'negative' ? 'bg-red-50 text-red-700 border-red-200' :
                      'bg-gray-50 text-gray-700 border-gray-200'
                  }`}>
                  {selectedRecord.rating === 'positive' ? 'Tích cực' : selectedRecord.rating === 'negative' ? 'Tiêu cực' : 'Trung lập'}
                </div>
              </div>

              {/* Content */}
              <div>
                <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Câu hỏi người dùng</h4>
                <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-100 text-gray-900 font-medium">
                  {selectedRecord.query}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Câu trả lời của Bot</h4>
                <div className="bg-gray-50 p-4 rounded-xl border border-gray-100 text-gray-700 font-mono text-sm leading-relaxed whitespace-pre-wrap">
                  {selectedRecord.answer}
                </div>
              </div>

              {selectedRecord.comment && (
                <div>
                  <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Ý kiến người dùng</h4>
                  <div className="bg-yellow-50 p-4 rounded-xl border border-yellow-100 text-yellow-800 italic flex gap-3">
                    <MessageSquare className="w-5 h-5 shrink-0 mt-0.5 text-yellow-600" />
                    {selectedRecord.comment}
                  </div>
                </div>
              )}

              {selectedRecord.chunk_ids && selectedRecord.chunk_ids.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Chunks đã dùng ({selectedRecord.chunk_ids.length})</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedRecord.chunk_ids.map(id => (
                      <span key={id} className="inline-flex items-center px-2.5 py-1 rounded bg-gray-100 text-gray-600 text-xs font-mono border border-gray-200">
                        <Hash className="w-3 h-3 mr-1 opacity-50" />
                        {id}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <div className="p-4 border-t border-gray-100 bg-gray-50 flex justify-end">
              <button
                onClick={() => setSelectedRecord(null)}
                className="px-5 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors shadow-sm"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ----------------------------------------------------------------------
// HELPER COMPONENTS
// ----------------------------------------------------------------------

const StatCard: React.FC<{
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  bg: string;
  border: string;
  trendUp?: boolean;
}> = ({ title, value, subtitle, icon, bg, border, trendUp }) => {
  return (
    <div className={`bg-white rounded-xl border ${border} p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group`}>
      <div className={`absolute top-0 right-0 p-3 opacity-10 group-hover:scale-110 transition-transform ${bg} rounded-bl-3xl`}>
        {icon}
      </div>
      <div className="flex items-start gap-4">
        <div className={`p-3 rounded-lg ${bg} shrink-0`}>
          {icon}
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <h3 className="text-2xl font-bold text-gray-900 mt-1">{value}</h3>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
      </div>
    </div>
  );
};

const DailyStatsChart: React.FC<{ dailyStats: FeedbackTimeStats[] }> = ({ dailyStats }) => {
  if (!dailyStats || dailyStats.length === 0) return <div className="flex items-center justify-center h-full text-gray-400 pb-8">Chưa có dữ liệu</div>;

  const chartData = dailyStats.map(item => ({
    ...item,
    formattedDate: item.date.split('-').slice(1).reverse().join('/'),
  })).reverse(); // Reverse to show latest on right if API returns descending

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }} barSize={32}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F3F4F6" />
        <XAxis dataKey="formattedDate" axisLine={false} tickLine={false} tick={{ fill: '#9CA3AF', fontSize: 11 }} dy={10} />
        <YAxis axisLine={false} tickLine={false} tick={{ fill: '#9CA3AF', fontSize: 11 }} />
        <Tooltip
          cursor={{ fill: '#F9FAFB' }}
          contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}
        />
        <Legend verticalAlign="top" height={36} iconType="circle" />
        <Bar dataKey="positive" name="Tích cực" stackId="a" fill="#10B981" radius={[0, 0, 4, 4]} />
        <Bar dataKey="neutral" name="Trung lập" stackId="a" fill="#9CA3AF" />
        <Bar dataKey="negative" name="Tiêu cực" stackId="a" fill="#EF4444" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default FeedbackDashboard;
