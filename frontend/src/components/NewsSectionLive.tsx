'use client';

import React, { useState, useEffect } from 'react';
import { Calendar, ArrowRight, RefreshCw, ExternalLink, Loader2 } from 'lucide-react';

interface NewsItem {
  id: number;
  title: string;
  excerpt?: string;
  date: string;
  image?: string;
  category: string;
  source?: string;
  url?: string;
}

interface NewsData {
  mainNews: NewsItem[];
  sidebarNews: NewsItem[];
  lastUpdated: string;
}

const NewsSectionLive = () => {
  const [newsData, setNewsData] = useState<NewsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [sidebarPage, setSidebarPage] = useState(1);

  const fetchNews = async () => {
    try {
      setRefreshing(true);
      const response = await fetch('/api/news');
      const result = await response.json();

      if (result.success) {
        setNewsData(result.data);
        setError(null);
      } else {
        setError(result.error || 'Không thể tải tin tức');
      }
    } catch (err) {
      setError('Lỗi kết nối đến máy chủ');
      console.error('Error fetching news:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, []);

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      'TIN TỨC': 'bg-red-600',
      'THÔNG BÁO': 'bg-blue-600',
      'TUYỂN SINH': 'bg-green-600',
      'SỰ KIỆN': 'bg-purple-600',
      'NGHIÊN CỨU': 'bg-orange-600',
      'ĐÀO TẠO': 'bg-cyan-600',
      'HOẠT ĐỘNG': 'bg-pink-600',
      'HỘI NGHỊ': 'bg-indigo-600',
      'HỌC BỔNG': 'bg-yellow-600',
      'KHOA HỌC': 'bg-teal-600',
    };
    return colors[category] || 'bg-gray-600';
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin text-red-700 mx-auto mb-4" />
            <p className="text-gray-600">Đang tải tin tức...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700 mb-4">{error}</p>
          <button
            onClick={fetchNews}
            className="bg-red-700 hover:bg-red-800 text-white px-4 py-2 rounded transition-colors"
          >
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  // CHỈ HIỂN THỊ TIN CÓ THUMBNAIL
  const mainNews = (newsData?.mainNews || []).filter(item => item.image && item.image.trim() !== '');
  const sidebarNews = (newsData?.sidebarNews || []).filter(item => item.image && item.image.trim() !== '');

  return (
    <section className="py-16 bg-gradient-to-b from-gray-50 via-slate-50 to-slate-100 border-t border-slate-200">
      <div className="container mx-auto px-4">
        {/* Premium Section Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-semibold mb-4">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
            Cập nhật từ DHANND
          </div>
          <h2 className="text-3xl md:text-4xl font-black text-gray-900 mb-3">
            Tin Tức & Sự Kiện
          </h2>
          <p className="text-gray-600 max-w-xl mx-auto">
            Thông tin mới nhất từ Trường Đại học An ninh Nhân dân
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content Area */}
          <div className="lg:col-span-2">
            <div className="mb-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-red-600 to-red-700 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white text-lg">📰</span>
                </div>
                <h3 className="text-xl font-bold text-gray-800">
                  TIN TỨC MỚI NHẤT
                </h3>
              </div>
              <button
                onClick={fetchNews}
                disabled={refreshing}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-gray-600 hover:text-red-700 hover:border-red-300 transition-all duration-200 disabled:opacity-50 shadow-sm"
                title="Làm mới tin tức"
              >
                <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                <span className="text-sm font-medium hidden sm:inline">Làm mới</span>
              </button>
            </div>

            <div className="space-y-6">
              {mainNews.map((news) => (
                <article
                  key={news.id}
                  className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200"
                >
                  <div className="md:flex">
                    <div className="md:w-1/3">
                      <div className="h-48 md:h-full bg-gray-100 flex items-center justify-center relative overflow-hidden group">
                        {news.image ? (
                          <img
                            src={news.image}
                            alt={news.title}
                            className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                              // Show fallback if image fails
                              const sibling = e.currentTarget.nextElementSibling;
                              if (sibling) sibling.classList.remove('opacity-0');
                            }}
                          />
                        ) : null}

                        <div className={`text-red-800 text-center p-4 transition-opacity duration-300 ${news.image ? 'opacity-0 absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-red-100 to-red-200' : 'bg-gradient-to-br from-red-100 to-red-200 w-full h-full flex flex-col items-center justify-center'}`}>
                          <div className="text-5xl mb-2">📰</div>
                          <div className="text-xs opacity-75">DHANND News</div>
                        </div>
                        {/* Badge nguồn */}
                        <div className="absolute top-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded">
                          {news.source}
                        </div>
                      </div>
                    </div>
                    <div className="md:w-2/3 p-6">
                      <div className="flex items-center flex-wrap gap-2 mb-2">
                        <span className={`${getCategoryColor(news.category)} text-white text-xs font-bold px-2 py-1 rounded`}>
                          {news.category}
                        </span>
                        <div className="flex items-center text-gray-500 text-sm">
                          <Calendar className="w-4 h-4 mr-1" />
                          {news.date}
                        </div>
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 mb-3 hover:text-red-700 cursor-pointer line-clamp-2">
                        {news.title}
                      </h3>
                      {news.excerpt && (
                        <p className="text-gray-600 mb-4 line-clamp-3">
                          {news.excerpt}
                        </p>
                      )}
                      <div className="flex items-center justify-between">
                        <button className="flex items-center text-red-700 hover:text-red-800 font-medium">
                          Đọc tiếp
                          <ArrowRight className="w-4 h-4 ml-1" />
                        </button>
                        {news.url && (
                          <a
                            href={news.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center text-gray-500 hover:text-red-700 text-sm"
                          >
                            <ExternalLink className="w-4 h-4 mr-1" />
                            Nguồn gốc
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            {/* Source Attribution */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>
                  📍 Nguồn: <a href="https://dhannd.bocongan.gov.vn" target="_blank" rel="noopener noreferrer" className="text-red-700 hover:underline">dhannd.bocongan.gov.vn</a>
                </span>
                {newsData?.lastUpdated && (
                  <span>
                    Cập nhật: {new Date(newsData.lastUpdated).toLocaleString('vi-VN')}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-4 border border-gray-100">
              <div className="flex items-center gap-3 mb-4 pb-4 border-b border-gray-100">
                <div className="w-10 h-10 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white text-lg">⭐</span>
                </div>
                <h3 className="text-lg font-bold text-gray-800">
                  TIN BÀI NỔI BẬT
                </h3>
              </div>
              <div className="space-y-4">
                {sidebarNews.slice((sidebarPage - 1) * 5, sidebarPage * 5).map((news, index) => (
                  <article key={news.id} className="border-b border-gray-200 pb-4 last:border-b-0 hover:bg-gray-50 rounded transition-colors -mx-2 px-2">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-20 h-14 relative overflow-hidden rounded bg-gray-100 border border-gray-200">
                        {news.image ? (
                          <img
                            src={news.image}
                            alt={news.title}
                            className="absolute inset-0 w-full h-full object-cover"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                              e.currentTarget.nextElementSibling?.classList.remove('hidden');
                            }}
                          />
                        ) : null}
                        <div className={`w-full h-full flex items-center justify-center bg-red-700 text-white font-bold text-sm ${news.image ? 'hidden' : ''}`}>
                          {(sidebarPage - 1) * 5 + index + 1}
                        </div>
                      </div>
                      <div className="flex-1">
                        <h4 className="text-sm font-medium text-gray-900 hover:text-red-700 cursor-pointer line-clamp-2 mb-2">
                          {news.title}
                        </h4>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center text-xs text-gray-500">
                            <Calendar className="w-3 h-3 mr-1" />
                            {news.date}
                          </div>
                          <span className={`${getCategoryColor(news.category)} text-white text-[10px] px-1.5 py-0.5 rounded`}>
                            {news.category}
                          </span>
                        </div>
                      </div>
                    </div>
                  </article>
                ))}
              </div>

              {/* Pagination Controls */}
              {sidebarNews.length > 5 && (
                <div className="flex items-center justify-between mt-4 border-t border-gray-100 pt-4">
                  <button
                    onClick={() => setSidebarPage(p => Math.max(1, p - 1))}
                    disabled={sidebarPage === 1}
                    className="p-1 rounded hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent text-gray-600 transition-colors"
                  >
                    <ArrowRight className="w-5 h-5 rotate-180" />
                  </button>
                  <span className="text-sm font-medium text-gray-600">
                    {sidebarPage} / {Math.ceil(sidebarNews.length / 5)}
                  </span>
                  <button
                    onClick={() => setSidebarPage(p => Math.min(Math.ceil(sidebarNews.length / 5), p + 1))}
                    disabled={sidebarPage === Math.ceil(sidebarNews.length / 5)}
                    className="p-1 rounded hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent text-gray-600 transition-colors"
                  >
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              )}
              <div className="mt-6 space-y-3">
                <a
                  href="https://dhannd.bocongan.gov.vn/tin-tuc"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full bg-red-700 hover:bg-red-800 text-white font-bold py-2 px-4 rounded transition-colors duration-200 flex items-center justify-center gap-2"
                >
                  Xem tất cả tin tức
                  <ExternalLink className="w-4 h-4" />
                </a>
                <button
                  onClick={fetchNews}
                  disabled={refreshing}
                  className="w-full border border-red-700 text-red-700 hover:bg-red-50 font-medium py-2 px-4 rounded transition-colors duration-200 flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                  Cập nhật tin tức
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default NewsSectionLive;
