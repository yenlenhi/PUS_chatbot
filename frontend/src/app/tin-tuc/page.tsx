'use client';

import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import Link from 'next/link';
import { Calendar, Eye, ArrowRight, Search, Filter, ChevronLeft, ChevronRight, Tag, Clock, TrendingUp, Loader2 } from 'lucide-react';

interface NewsItem {
  id: number;
  title: string;
  excerpt?: string;
  date: string;
  image?: string;
  category: string;
  source?: string;
  url?: string;
  views?: number;
}

const CATEGORIES = [
  { name: 'Tất cả', value: 'all' },
  { name: 'Tin tức', value: 'TIN TỨC' },
  { name: 'Thông báo', value: 'THÔNG BÁO' },
  { name: 'Tuyển sinh', value: 'TUYỂN SINH' },
  { name: 'Đào tạo', value: 'ĐÀO TẠO' },
  { name: 'Hoạt động', value: 'HOẠT ĐỘNG' },
  { name: 'Khoa học', value: 'KHOA HỌC' },
  { name: 'Hội nghị', value: 'HỘI NGHỊ' },
];

const getCategoryColor = (category: string) => {
  const colors: Record<string, string> = {
    'TIN TỨC': 'bg-blue-500',
    'THÔNG BÁO': 'bg-red-500',
    'TUYỂN SINH': 'bg-green-500',
    'HOẠT ĐỘNG': 'bg-purple-500',
    'ĐÀO TẠO': 'bg-amber-500',
    'KHOA HỌC': 'bg-cyan-500',
    'HỘI NGHỊ': 'bg-indigo-500',
    'HỌC BỔNG': 'bg-pink-500',
    'THI ĐẤU': 'bg-orange-500',
    'VĂN HÓA': 'bg-teal-500',
    'NỔI BẬT': 'bg-red-600'
  };
  return colors[category] || 'bg-gray-500';
};

export default function TinTucPage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8; // Increased items per page

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/news');
        const result = await response.json();

        if (result.success) {
          const mainNews: NewsItem[] = result.data.mainNews || [];
          const sidebarNews: NewsItem[] = result.data.sidebarNews || [];

          // Combine and add mock views for demo purpose
          const allNews = [...mainNews, ...sidebarNews].map(item => ({
            ...item,
            views: item.views || Math.floor(Math.random() * 2000) + 100 // Mock views
          }));

          setNews(allNews);
        }
      } catch (error) {
        console.error('Failed to fetch news:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  // Filter news
  const filteredNews = news.filter(item => {
    const matchCategory = selectedCategory === 'all' || item.category === selectedCategory || (selectedCategory === 'TIN TỨC' && item.category === 'NỔI BẬT');
    const matchSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.excerpt && item.excerpt.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchCategory && matchSearch;
  });

  // Pagination
  const totalPages = Math.ceil(filteredNews.length / itemsPerPage);
  const paginatedNews = filteredNews.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Featured news (Main news items are usually featured)
  const featuredNews = news.slice(0, 3); // Take top 3 as featured

  // Most viewed (random sort for demo)
  const mostViewed = [...news].sort((a, b) => (b.views || 0) - (a.views || 0)).slice(0, 5);

  if (loading) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-20 flex justify-center items-center min-h-[500px]">
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-red-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Đang cập nhật tin tức mới nhất...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-red-700 via-red-600 to-red-700 text-white">
        <div className="container mx-auto px-4 py-12">
          <div className="flex items-center gap-2 text-red-200 text-sm mb-2">
            <Link href="/" className="hover:text-white">Trang chủ</Link>
            <span>/</span>
            <span className="text-white">Tin tức</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-4">Tin tức & Sự kiện</h1>
          <p className="text-red-100 max-w-2xl">
            Cập nhật những tin tức mới nhất về hoạt động đào tạo, nghiên cứu khoa học và các sự kiện của Trường Đại học An ninh Nhân dân
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Featured News Section - Only show if we have enough news */}
        {featuredNews.length > 0 && (
          <div className="mb-12">
            <div className="flex items-center gap-2 mb-6">
              <TrendingUp className="w-6 h-6 text-red-600" />
              <h2 className="text-2xl font-bold text-gray-900">Tin nổi bật</h2>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main featured */}
              <div className="lg:col-span-2">
                <article className="group relative h-[400px] rounded-2xl overflow-hidden shadow-lg bg-gray-100">
                  {featuredNews[0].image ? (
                    <img
                      src={featuredNews[0].image}
                      alt={featuredNews[0].title}
                      className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                      onError={(e) => e.currentTarget.style.display = 'none'}
                    />
                  ) : null}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent">
                    <div className="absolute inset-0 bg-black/10 group-hover:bg-black/20 transition-colors" />
                  </div>
                  <div className="absolute bottom-0 left-0 right-0 p-6 text-white text-shadow-sm">
                    <span className={`inline-block ${getCategoryColor(featuredNews[0].category)} px-3 py-1 rounded-full text-xs font-bold mb-3 shadow-sm`}>
                      {featuredNews[0].category}
                    </span>
                    <h3 className="text-2xl font-bold mb-3 group-hover:text-yellow-300 transition-colors cursor-pointer drop-shadow-md">
                      {featuredNews[0].title}
                    </h3>
                    {featuredNews[0].excerpt && (
                      <p className="text-gray-100 mb-4 line-clamp-2 drop-shadow-sm">{featuredNews[0].excerpt}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-200">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {featuredNews[0].date}
                      </span>
                      <span className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        {featuredNews[0].views?.toLocaleString()} lượt xem
                      </span>
                    </div>
                  </div>
                </article>
              </div>

              {/* Side featured */}
              <div className="space-y-4">
                {featuredNews.slice(1, 3).map((news) => (
                  <article key={news.id} className="group relative h-[190px] rounded-xl overflow-hidden shadow-md bg-gray-100">
                    {news.image ? (
                      <img
                        src={news.image}
                        alt={news.title}
                        className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                        onError={(e) => e.currentTarget.style.display = 'none'}
                      />
                    ) : null}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent">
                      <div className="absolute inset-0 bg-black/10 group-hover:bg-black/20 transition-colors" />
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
                      <span className={`inline-block ${getCategoryColor(news.category)} px-2 py-0.5 rounded-full text-xs font-bold mb-2 shadow-sm`}>
                        {news.category}
                      </span>
                      <h3 className="text-sm font-bold mb-2 group-hover:text-yellow-300 transition-colors cursor-pointer line-clamp-2 drop-shadow-md">
                        {news.title}
                      </h3>
                      <div className="flex items-center gap-3 text-xs text-gray-300">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {news.date}
                        </span>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Search & Filter Bar */}
            <div className="bg-white rounded-xl shadow-sm p-4 mb-6 border border-gray-100">
              <div className="flex flex-col md:flex-row gap-4">
                {/* Search */}
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Tìm kiếm tin tức..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>

                {/* Category Filter */}
                <div className="flex items-center gap-2">
                  <Filter className="w-5 h-5 text-gray-400" />
                  <select
                    value={selectedCategory}
                    onChange={(e) => {
                      setSelectedCategory(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent bg-white"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Results count */}
            <div className="mb-4 text-gray-600">
              Tìm thấy <span className="font-semibold text-red-600">{filteredNews.length}</span> bài viết
            </div>

            {/* News Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {paginatedNews.map((news) => (
                <article key={news.id} className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 hover:shadow-lg transition-all duration-300 group flex flex-col h-full">
                  {/* Image */}
                  <div className="h-48 bg-gray-100 relative overflow-hidden flex-shrink-0">
                    {news.image ? (
                      <img
                        src={news.image}
                        alt={news.title}
                        className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                          e.currentTarget.nextElementSibling?.classList.remove('hidden');
                        }}
                      />
                    ) : null}
                    {/* Fallback Placeholder */}
                    <div className={`absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 ${news.image ? 'hidden' : ''}`}>
                      <div className="text-center">
                        <div className="w-12 h-12 bg-gray-300/50 rounded-full flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
                          <span className="text-2xl">📰</span>
                        </div>
                      </div>
                    </div>
                    <span className={`absolute top-3 left-3 ${getCategoryColor(news.category)} text-white text-xs font-bold px-3 py-1 rounded-full shadow-sm`}>
                      {news.category}
                    </span>
                  </div>

                  <div className="p-5 flex flex-col flex-1">
                    <div className="flex items-center gap-3 text-sm text-gray-500 mb-3">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {news.date}
                      </span>
                      <span className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        {news.views?.toLocaleString()}
                      </span>
                    </div>

                    <h3 className="font-bold text-gray-900 mb-2 group-hover:text-red-600 transition-colors cursor-pointer line-clamp-2">
                      {news.url ? (
                        <a href={news.url} target="_blank" rel="noopener noreferrer">{news.title}</a>
                      ) : news.title}
                    </h3>

                    <p className="text-gray-600 text-sm line-clamp-2 mb-4 flex-1">
                      {news.excerpt}
                    </p>

                    {news.url && (
                      <a
                        href={news.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center text-red-600 hover:text-red-700 font-medium text-sm group/btn mt-auto"
                      >
                        Đọc tiếp
                        <ArrowRight className="w-4 h-4 ml-1 group-hover/btn:translate-x-1 transition-transform" />
                      </a>
                    )}
                  </div>
                </article>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-2 rounded-lg border border-gray-200 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>

                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`w-10 h-10 rounded-lg font-medium transition-colors ${currentPage === page
                        ? 'bg-red-600 text-white'
                        : 'border border-gray-200 hover:bg-gray-100'
                      }`}
                  >
                    {page}
                  </button>
                ))}

                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="p-2 rounded-lg border border-gray-200 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Categories */}
            <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
              <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Tag className="w-5 h-5 text-red-600" />
                Danh mục
              </h3>
              <div className="space-y-2">
                {CATEGORIES.map((cat) => (
                  <button
                    key={cat.value}
                    onClick={() => {
                      setSelectedCategory(cat.value);
                      setCurrentPage(1);
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${selectedCategory === cat.value
                        ? 'bg-red-50 text-red-600 font-medium'
                        : 'hover:bg-gray-50 text-gray-700'
                      }`}
                  >
                    <span>{cat.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Most Viewed */}
            <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
              <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Eye className="w-5 h-5 text-red-600" />
                Xem nhiều nhất
              </h3>
              <div className="space-y-4">
                {mostViewed.map((news, index) => (
                  <article key={news.id} className="flex gap-3 group cursor-pointer">
                    <div className="flex-shrink-0 w-16 h-12 relative overflow-hidden rounded bg-gray-100">
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
                      <div className={`absolute inset-0 flex items-center justify-center bg-red-100 text-red-600 font-bold text-sm ${news.image ? 'hidden' : ''}`}>
                        {index + 1}
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-gray-900 group-hover:text-red-600 transition-colors line-clamp-2 mb-1">
                        {news.url ? <a href={news.url} target="_blank" rel="noopener noreferrer">{news.title}</a> : news.title}
                      </h4>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Eye className="w-3 h-3" />
                        {news.views?.toLocaleString()}
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </div>

            {/* CTA - Chatbot */}
            <div className="bg-gradient-to-br from-red-600 to-red-700 rounded-xl p-5 text-white">
              <div className="text-center">
                <div className="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">🤖</span>
                </div>
                <h3 className="font-bold mb-2">Cần hỗ trợ?</h3>
                <p className="text-red-100 text-sm mb-4">
                  Chatbot AI sẵn sàng giải đáp thắc mắc 24/7
                </p>
                <Link
                  href="/chat-bot"
                  className="inline-block bg-white text-red-600 hover:bg-yellow-400 hover:text-red-700 font-bold py-2 px-5 rounded-lg transition-colors text-sm"
                >
                  💬 Chat ngay
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
