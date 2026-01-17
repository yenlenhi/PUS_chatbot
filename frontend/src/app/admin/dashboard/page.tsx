'use client';

import React, { useState, useEffect, useCallback } from 'react';
import AdminLayout from '@/components/admin/AdminLayout';
import {
  Users,
  MessageSquare,
  FileText,
  TrendingUp,
  Activity,
  Clock,
  BarChart3,
  PieChart,
  Target,
  Zap,
  ThumbsUp,
  ThumbsDown,
  HelpCircle,
  FolderOpen,
  Lightbulb,
  Award,
  Loader2,
  RefreshCw,
  Download,
} from 'lucide-react';
import {
  TimeRangeFilter,
  MetricCard,
  InsightsSection,
  FunnelChart,
  ContentGapCard,
  QualityScoreCard,
} from '@/components/admin/analytics';
import InteractiveLineChart from '@/components/admin/analytics/InteractiveLineChart';
import InteractiveBarChart from '@/components/admin/analytics/InteractiveBarChart';
import InteractivePieChart from '@/components/admin/analytics/InteractivePieChart';
import { analyticsAPI, formatNumber, formatBytes, formatCurrency, formatDuration } from '@/services/analytics';
import { useLanguage } from '@/i18n/LanguageContext';
import {
  AnalyticsFilter,
  DashboardOverview,
  SystemInsights,
  UserInsights,
  ChatInsights,
  DocumentInsights,
  BusinessInsights,
} from '@/types/analytics';

const DashboardPage = () => {
  const { t } = useLanguage();
  const [filter, setFilter] = useState<AnalyticsFilter>({ timeRange: 'L7D' });
  const [activeTab, setActiveTab] = useState<'system' | 'users' | 'chat' | 'documents' | 'business'>('system');
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Data states
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [systemInsights, setSystemInsights] = useState<SystemInsights | null>(null);
  const [userInsights, setUserInsights] = useState<UserInsights | null>(null);
  const [chatInsights, setChatInsights] = useState<ChatInsights | null>(null);
  const [documentInsights, setDocumentInsights] = useState<DocumentInsights | null>(null);
  const [businessInsights, setBusinessInsights] = useState<BusinessInsights | null>(null);
  const [popularQuestions, setPopularQuestions] = useState<any>(null);

  // Export state
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async (type: string) => {
    try {
      setIsExporting(true);
      await analyticsAPI.exportData(type, filter);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Xuất dữ liệu thất bại. Vui lòng thử lại.');
    } finally {
      setIsExporting(false);
      setShowExportMenu(false);
    }
  };

  const fetchAllData = useCallback(async () => {
    try {
      const [overviewData, systemData, userData, chatData, docData, businessData, popularQuestionsData] = await Promise.all([
        analyticsAPI.getOverview(),
        analyticsAPI.getSystemInsights(filter),
        analyticsAPI.getUserInsights(filter),
        analyticsAPI.getChatInsights(filter),
        analyticsAPI.getDocumentInsights(filter),
        analyticsAPI.getBusinessInsights(filter),
        analyticsAPI.getPopularQuestions(filter, 10),
      ]);

      setOverview(overviewData);
      setSystemInsights(systemData);
      setUserInsights(userData);
      setChatInsights(chatData);
      setDocumentInsights(docData);
      setBusinessInsights(businessData);
      setPopularQuestions(popularQuestionsData);
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    }
  }, [filter]);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await fetchAllData();
      setIsLoading(false);
    };
    loadData();
  }, [fetchAllData]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchAllData();
    setIsRefreshing(false);
  };

  const handleFilterChange = (newFilter: AnalyticsFilter) => {
    setFilter(newFilter);
  };

  const tabs = [
    { id: 'system', label: t('systemMetrics'), icon: Activity },
    { id: 'users', label: t('userMetrics'), icon: Users },
    { id: 'chat', label: t('chatMetrics'), icon: MessageSquare },
    { id: 'documents', label: t('documentMetrics'), icon: FileText },
    { id: 'business', label: t('businessMetrics'), icon: Lightbulb },
  ];

  if (isLoading) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <Loader2 className="w-10 h-10 animate-spin text-red-600 mx-auto mb-4" />
            <p className="text-gray-600">{t('loading')}</p>
          </div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-4 sm:space-y-6">
        {/* Header with Filter */}
        <div className="flex flex-col gap-3 sm:gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Dashboard Analytics</h1>
            <p className="text-sm sm:text-base text-gray-600">Theo dõi và phân tích hiệu suất hệ thống</p>
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-end gap-2 sm:gap-3">
            {/* Export Data Button */}
            <div className="relative">
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                disabled={isExporting}
                className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                {isExporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                <span className="hidden sm:inline">Export</span>
              </button>

              {showExportMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-50">
                  <div className="px-3 py-2 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase">
                    Chọn loại dữ liệu
                  </div>
                  {[
                    { id: 'system', label: 'Chỉ số hệ thống' },
                    { id: 'users', label: 'Chỉ số người dùng' },
                    { id: 'chat', label: 'Chỉ số tin nhắn' },
                    { id: 'documents', label: 'Chỉ số tài liệu' },
                    { id: 'business', label: 'Chỉ số kinh doanh' },
                  ].map((item) => (
                    <button
                      key={item.id}
                      onClick={() => handleExport(item.id)}
                      disabled={isExporting}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-red-600 disabled:opacity-50"
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="self-start sm:self-auto p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
              title="Làm mới dữ liệu"
            >
              <RefreshCw className={`w-4 h-4 sm:w-5 sm:h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
            <TimeRangeFilter
              value={filter.timeRange}
              startDate={filter.startDate}
              endDate={filter.endDate}
              onChange={handleFilterChange}
            />
          </div>
        </div>

        {/* Overview Stats */}
        {overview && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
            <MetricCard
              title="Tổng số cuộc hội thoại"
              value={formatNumber(overview.total_conversations)}
              change={overview.conversations_change}
              icon={MessageSquare}
              iconColor="bg-blue-500"
              subtitle={`Hôm nay: ${overview.today_conversations}`}
            />
            <MetricCard
              title="Người dùng"
              value={formatNumber(overview.total_users)}
              change={overview.users_change}
              icon={Users}
              iconColor="bg-green-500"
              subtitle={`Mới hôm nay: ${overview.today_new_users}`}
            />
            <MetricCard
              title="Tài liệu hệ thống"
              value={formatNumber(overview.total_documents)}
              change={overview.documents_change}
              icon={FileText}
              iconColor="bg-purple-500"
            />
            <MetricCard
              title="Thời gian phản hồi TB"
              value={`${(overview.avg_response_time_ms / 1000).toFixed(1)}s`}
              change={overview.response_time_change}
              icon={Clock}
              iconColor="bg-yellow-500"
              trend={overview.response_time_change < 0 ? 'up' : 'down'}
            />
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-2 sm:space-x-4 overflow-x-auto pb-px">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={`flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 sm:py-3 text-xs sm:text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab === tab.id
                    ? 'border-red-600 text-red-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                    }`}
                >
                  <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  <span className="hidden xs:inline sm:inline">{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="space-y-4 sm:space-y-6">
          {/* System Insights */}
          {activeTab === 'system' && systemInsights && (
            <>
              {/* Token Usage */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-6">
                <InsightsSection title="Token Usage theo ngày" icon={Zap}>
                  <div className="grid grid-cols-2 gap-2 sm:gap-3 mb-3 sm:mb-4">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-2.5 sm:p-3.5 border border-blue-200">
                      <p className="text-xs text-blue-600 font-medium mb-1">Tổng tokens</p>
                      <p className="text-lg sm:text-xl font-bold text-blue-700">
                        {formatNumber(systemInsights.total_tokens)}
                      </p>
                    </div>
                    <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-2.5 sm:p-3.5 border border-green-200">
                      <p className="text-xs text-green-600 font-medium mb-1">Chi phí ước tính</p>
                      <p className="text-lg sm:text-xl font-bold text-green-700">
                        {formatCurrency(systemInsights.total_estimated_cost)}
                      </p>
                    </div>
                  </div>
                  <InteractiveLineChart
                    data={systemInsights.token_usage_daily.map((d) => ({
                      date: d.date.slice(5),
                      value: d.total_tokens,
                    }))}
                    title="Token Usage Daily"
                    color="#3b82f6"
                    height={250}
                    showBrush={true}
                  />
                </InsightsSection>

                <InsightsSection title="Token Usage theo giờ (24h)" icon={Clock}>
                  <InteractiveBarChart
                    data={systemInsights.token_usage_hourly.map((d) => ({
                      label: `${d.hour}h`,
                      value: d.total_tokens,
                    }))}
                    title="Hourly Distribution"
                    color="#8b5cf6"
                    height={230}
                  />
                </InsightsSection>
              </div>

              {/* Access Metrics */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-6">
                <InsightsSection title="Lượt truy cập theo ngày" icon={TrendingUp}>
                  <div className="grid grid-cols-2 gap-2 sm:gap-3 mb-3 sm:mb-4">
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-2.5 sm:p-3.5 border border-purple-200">
                      <p className="text-xs text-purple-600 font-medium mb-1">Tổng requests</p>
                      <p className="text-lg sm:text-xl font-bold text-purple-700">
                        {formatNumber(systemInsights.total_requests)}
                      </p>
                    </div>
                    <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-2.5 sm:p-3.5 border border-red-200">
                      <p className="text-xs text-red-600 font-medium mb-1">Bị chặn</p>
                      <p className="text-lg sm:text-xl font-bold text-red-700">
                        {formatNumber(systemInsights.total_blocked)}
                      </p>
                    </div>
                  </div>
                  <InteractiveLineChart
                    data={systemInsights.access_daily.map((d) => ({
                      date: d.date.slice(5),
                      value: d.total_requests,
                    }))}
                    title="Daily Access"
                    color="#9333ea"
                    height={250}
                    showBrush={true}
                  />
                </InsightsSection>

                <InsightsSection title="Lượt truy cập theo giờ (24h)" icon={Activity}>
                  <InteractiveBarChart
                    data={systemInsights.access_hourly.map((d) => ({
                      label: `${d.hour}h`,
                      value: d.total_requests,
                    }))}
                    title="Hourly Distribution"
                    color="#8b5cf6"
                    height={230}
                  />
                </InsightsSection>
              </div>
            </>
          )}

          {/* User Insights */}
          {activeTab === 'users' && userInsights && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <MetricCard
                  title="Unique Users"
                  value={formatNumber(userInsights.total_unique_users)}
                  icon={Users}
                  iconColor="bg-blue-500"
                />
                <MetricCard
                  title="New Users (YTD)"
                  value={formatNumber(userInsights.new_users_ytd)}
                  icon={Users}
                  iconColor="bg-green-500"
                />
                <MetricCard
                  title="Retain Users (YTD)"
                  value={formatNumber(userInsights.retain_users_ytd)}
                  icon={Users}
                  iconColor="bg-purple-500"
                />
                <MetricCard
                  title="Retention Rate"
                  value={`${((userInsights.retain_users_ytd / (userInsights.new_users_ytd + userInsights.retain_users_ytd)) * 100).toFixed(1)}%`}
                  icon={Target}
                  iconColor="bg-orange-500"
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <InsightsSection title="Unique Users theo ngày" icon={Users}>
                  <InteractiveLineChart
                    data={userInsights.daily_users.map((d) => ({
                      date: d.date.slice(5),
                      value: d.unique_users,
                    }))}
                    title="Daily Unique Users"
                    color="#3b82f6"
                    height={300}
                    showBrush={true}
                  />
                </InsightsSection>

                <InsightsSection title="Tần suất quay lại" icon={RefreshCw}>
                  <InteractivePieChart
                    data={userInsights.return_frequency.map((d, i) => ({
                      label: d.frequency,
                      value: d.user_count,
                      color: ['#dc2626', '#f97316', '#eab308', '#22c55e'][i % 4],
                    }))}
                    title="Return Frequency"
                    size={320}
                    innerRadius={70}
                  />
                </InsightsSection>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <InsightsSection title="User Segmentation" icon={PieChart}>
                  <div className="space-y-4">
                    {userInsights.user_segments.map((segment, index) => (
                      <div key={index}>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm text-gray-700">{segment.segment}</span>
                          <span className="text-sm font-medium">{segment.user_count} users ({segment.percentage}%)</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-red-500 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${segment.percentage}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </InsightsSection>

                <InsightsSection title="User Funnel" icon={Target}>
                  <FunnelChart data={userInsights.funnel} />
                </InsightsSection>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <InsightsSection title="Chủ đề quan tâm" icon={BarChart3}>
                  <InteractiveBarChart
                    data={userInsights.topics.map((t) => ({
                      label: t.topic,
                      value: t.query_count,
                    }))}
                    title="Popular Topics"
                    color="#f59e0b"
                    height={300}
                    horizontal={true}
                  />
                </InsightsSection>

                <InsightsSection title="Câu hỏi phổ biến" icon={HelpCircle}>
                  <div className="space-y-3">
                    {/* Hiển thị thông tin data source */}
                    <div className="flex items-center justify-between mb-3 pb-2 border-b border-gray-100">
                      <span className="text-xs text-gray-500">
                        {popularQuestions?.data_source === 'real' ?
                          `📊 Dữ liệu thực tế (${popularQuestions.total_count} câu hỏi)` :
                          '📋 Dữ liệu mẫu'
                        }
                      </span>
                      <span className="text-xs text-gray-400">
                        {popularQuestions?.time_range === 'L7D' ? '7 ngày qua' : popularQuestions?.time_range}
                      </span>
                    </div>
                    {(popularQuestions?.popular_questions || userInsights.popular_questions).slice(0, 5).map((q: any, index: number) => (
                      <div key={index} className="flex items-start space-x-3 pb-3 border-b border-gray-100 last:border-0">
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-xs font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-900 line-clamp-2">{q.question}</p>
                          <div className="flex items-center justify-between mt-1">
                            <p className="text-xs text-gray-500">{q.count} lượt hỏi</p>
                            {q.last_asked && (
                              <p className="text-xs text-gray-400">
                                Lần cuối: {new Date(q.last_asked).toLocaleDateString('vi-VN')}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </InsightsSection>
              </div>
            </>
          )}

          {/* Chat Insights */}
          {activeTab === 'chat' && chatInsights && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <MetricCard
                  title="Tổng tin nhắn"
                  value={formatNumber(chatInsights.total_user_messages)}
                  icon={MessageSquare}
                  iconColor="bg-blue-500"
                />
                <MetricCard
                  title="Tỷ lệ hài lòng"
                  value={`${chatInsights.like_rate.toFixed(1)}%`}
                  icon={ThumbsUp}
                  iconColor="bg-green-500"
                />
                <MetricCard
                  title="Tỷ lệ không hài lòng"
                  value={`${chatInsights.dislike_rate.toFixed(1)}%`}
                  icon={ThumbsDown}
                  iconColor="bg-red-500"
                />
                <MetricCard
                  title="Tin nhắn/hội thoại"
                  value={chatInsights.avg_messages_per_conversation.toFixed(1)}
                  icon={BarChart3}
                  iconColor="bg-purple-500"
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <InsightsSection title="Tin nhắn theo ngày" icon={MessageSquare}>
                  <InteractiveLineChart
                    data={chatInsights.daily_metrics.map((d) => ({
                      date: d.date.slice(5),
                      value: d.user_messages,
                    }))}
                    title="Daily Messages"
                    color="#10b981"
                    height={300}
                    showBrush={true}
                  />
                </InsightsSection>

                <InsightsSection title="Feedback theo ngày" icon={ThumbsUp}>
                  <div className="space-y-4">
                    {chatInsights.daily_metrics.slice(-5).map((d, index) => (
                      <div key={index} className="flex items-center space-x-4">
                        <span className="text-sm text-gray-600 w-16">{d.date.slice(5)}</span>
                        <div className="flex-1 flex items-center space-x-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-4 overflow-hidden flex">
                            <div
                              className="bg-green-500 h-4"
                              style={{ width: `${(d.likes / (d.likes + d.dislikes || 1)) * 100}%` }}
                            />
                            <div
                              className="bg-red-500 h-4"
                              style={{ width: `${(d.dislikes / (d.likes + d.dislikes || 1)) * 100}%` }}
                            />
                          </div>
                        </div>
                        <span className="text-xs text-gray-500 w-16">
                          {d.likes} / {d.dislikes}
                        </span>
                      </div>
                    ))}
                  </div>
                </InsightsSection>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <InsightsSection title="Câu hỏi chưa trả lời được" icon={HelpCircle}>
                  <div className="space-y-3">
                    {chatInsights.unanswered_questions.map((q, index) => (
                      <div key={index} className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                        <p className="text-sm text-gray-900">{q.question}</p>
                        <p className="text-xs text-orange-600 mt-1">{q.count} lần xuất hiện</p>
                      </div>
                    ))}
                  </div>
                </InsightsSection>

                <InsightsSection title="Câu trả lời cần cải thiện" icon={ThumbsDown}>
                  <div className="space-y-3">
                    {chatInsights.low_rated_responses.map((r, index) => (
                      <div key={index} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-sm font-medium text-gray-900">{r.query}</p>
                        <p className="text-xs text-gray-600 mt-1 line-clamp-2">{r.answer}</p>
                        <p className="text-xs text-red-600 mt-1">{r.dislike_count} không thích</p>
                      </div>
                    ))}
                  </div>
                </InsightsSection>
              </div>
            </>
          )}

          {/* Document Insights */}
          {activeTab === 'documents' && documentInsights && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <MetricCard
                  title="Tổng tài liệu"
                  value={formatNumber(documentInsights.total_documents)}
                  icon={FileText}
                  iconColor="bg-blue-500"
                />
                <MetricCard
                  title="Dung lượng"
                  value={formatBytes(documentInsights.total_size_bytes)}
                  icon={FolderOpen}
                  iconColor="bg-purple-500"
                />
                <MetricCard
                  title="Đang hoạt động"
                  value={formatNumber(documentInsights.active_documents)}
                  icon={FileText}
                  iconColor="bg-green-500"
                />
                <MetricCard
                  title="Không hoạt động"
                  value={formatNumber(documentInsights.inactive_documents)}
                  icon={FileText}
                  iconColor="bg-gray-500"
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <InsightsSection title="Tài liệu theo danh mục" icon={PieChart}>
                  <InteractivePieChart
                    data={documentInsights.category_stats.map((c, i) => ({
                      label: c.category,
                      value: c.document_count,
                      color: ['#dc2626', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6'][i % 6],
                    }))}
                    title="Documents by Category"
                    size={320}
                    innerRadius={70}
                  />
                </InsightsSection>

                <InsightsSection title="Dung lượng theo danh mục" icon={BarChart3}>
                  <InteractiveBarChart
                    data={documentInsights.category_stats.map((c) => ({
                      label: c.category,
                      value: c.total_size_bytes / 1048576, // Convert to MB
                    }))}
                    title="Storage by Category (MB)"
                    color="#06b6d4"
                    height={300}
                    horizontal={true}
                  />
                  <p className="text-xs text-gray-500 mt-2">Đơn vị: MB</p>
                </InsightsSection>
              </div>

              <InsightsSection title="Top tài liệu được truy xuất" icon={TrendingUp}>
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-2 text-sm font-medium text-gray-600">Tài liệu</th>
                        <th className="text-right py-2 text-sm font-medium text-gray-600">Lượt truy xuất</th>
                        <th className="text-right py-2 text-sm font-medium text-gray-600">👍</th>
                        <th className="text-right py-2 text-sm font-medium text-gray-600">👎</th>
                        <th className="text-right py-2 text-sm font-medium text-gray-600">Điểm</th>
                      </tr>
                    </thead>
                    <tbody>
                      {documentInsights.top_retrieved_documents.map((doc, index) => (
                        <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 text-sm text-gray-900">{doc.filename}</td>
                          <td className="py-3 text-sm text-gray-600 text-right">{doc.retrieval_count}</td>
                          <td className="py-3 text-sm text-green-600 text-right">{doc.positive_feedback}</td>
                          <td className="py-3 text-sm text-red-600 text-right">{doc.negative_feedback}</td>
                          <td className="py-3 text-right">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${doc.effectiveness_score >= 0.8 ? 'bg-green-100 text-green-700' :
                              doc.effectiveness_score >= 0.6 ? 'bg-yellow-100 text-yellow-700' :
                                'bg-red-100 text-red-700'
                              }`}>
                              {(doc.effectiveness_score * 100).toFixed(0)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </InsightsSection>

              <InsightsSection title="Xu hướng tài liệu" icon={TrendingUp}>
                <InteractiveLineChart
                  data={documentInsights.growth_trend.map((d) => ({
                    date: d.month.slice(5),
                    value: d.total_documents,
                  }))}
                  title="Document Growth"
                  color="#8b5cf6"
                  height={300}
                  showBrush={true}
                />
              </InsightsSection>
            </>
          )}

          {/* Business Insights */}
          {activeTab === 'business' && businessInsights && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricCard
                  title="Giờ tiết kiệm được"
                  value={`${businessInsights.estimated_hours_saved.toFixed(1)}h`}
                  icon={Clock}
                  iconColor="bg-green-500"
                  subtitle="Ước tính dựa trên số câu hỏi được xử lý"
                />
                <MetricCard
                  title="Câu hỏi đã xử lý"
                  value={formatNumber(businessInsights.estimated_queries_handled)}
                  icon={MessageSquare}
                  iconColor="bg-blue-500"
                />
                <MetricCard
                  title="Thời gian phản hồi TB"
                  value={formatDuration(businessInsights.avg_response_time_seconds)}
                  icon={Zap}
                  iconColor="bg-yellow-500"
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <InsightsSection title="Điểm chất lượng" icon={Award}>
                  <QualityScoreCard
                    overallScore={businessInsights.overall_quality_score}
                    breakdown={businessInsights.quality_breakdown}
                  />
                </InsightsSection>

                <InsightsSection title="Content Gap Analysis" icon={Lightbulb}>
                  <ContentGapCard gaps={businessInsights.content_gaps} />
                </InsightsSection>
              </div>
            </>
          )}
        </div>
      </div>
    </AdminLayout>
  );
};

export default DashboardPage;
