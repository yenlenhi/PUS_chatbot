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

  const mainNews = newsData?.mainNews || [];
  const sidebarNews = newsData?.sidebarNews || [];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content Area */}
        <div className="lg:col-span-2">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-2xl font-bold text-red-700 border-b-2 border-red-700 pb-2">
              TIN TỨC TỪ DHANND
            </h2>
            <button
              onClick={fetchNews}
              disabled={refreshing}
              className="flex items-center gap-2 text-gray-600 hover:text-red-700 transition-colors disabled:opacity-50"
              title="Làm mới tin tức"
            >
              <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
              <span className="text-sm hidden sm:inline">Làm mới</span>
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
                    <div className="h-48 md:h-full bg-gradient-to-br from-red-100 to-red-200 flex items-center justify-center relative overflow-hidden">
                      <div className="text-red-800 text-center p-4">
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
          <div className="bg-white rounded-lg shadow-md p-6 sticky top-4">
            <h3 className="text-xl font-bold text-red-700 border-b-2 border-red-700 pb-2 mb-4">
              TIN BÀI NỔI BẬT
            </h3>
            <div className="space-y-4">
              {sidebarNews.map((news, index) => (
                <article key={news.id} className="border-b border-gray-200 pb-4 last:border-b-0 hover:bg-gray-50 rounded transition-colors -mx-2 px-2">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-red-700 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      {index + 1}
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
  );
};

export default NewsSectionLive;
