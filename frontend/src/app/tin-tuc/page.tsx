'use client';

import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import Link from 'next/link';
import {
  Calendar, Eye, ArrowRight, Search, Filter, ChevronLeft, ChevronRight,
  Tag, TrendingUp, Loader2, Newspaper, MessageCircle, Sparkles
} from 'lucide-react';

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
  { name: 'Tất cả', value: 'all', color: 'from-gray-500 to-gray-600' },
  { name: 'Tin tức', value: 'TIN TỨC', color: 'from-blue-500 to-indigo-600' },
  { name: 'Thông báo', value: 'THÔNG BÁO', color: 'from-red-500 to-rose-600' },
  { name: 'Tuyển sinh', value: 'TUYỂN SINH', color: 'from-emerald-500 to-teal-600' },
  { name: 'Đào tạo', value: 'ĐÀO TẠO', color: 'from-amber-500 to-orange-600' },
  { name: 'Hoạt động', value: 'HOẠT ĐỘNG', color: 'from-purple-500 to-violet-600' },
  { name: 'Khoa học', value: 'KHOA HỌC', color: 'from-cyan-500 to-blue-600' },
  { name: 'Hội nghị', value: 'HỘI NGHỊ', color: 'from-indigo-500 to-purple-600' },
];

const getCategoryColor = (category: string) => {
  const colors: Record<string, string> = {
    'TIN TỨC': 'from-blue-500 to-indigo-600',
    'THÔNG BÁO': 'from-red-500 to-rose-600',
    'TUYỂN SINH': 'from-emerald-500 to-teal-600',
    'HOẠT ĐỘNG': 'from-purple-500 to-violet-600',
    'ĐÀO TẠO': 'from-amber-500 to-orange-600',
    'KHOA HỌC': 'from-cyan-500 to-blue-600',
    'HỘI NGHỊ': 'from-indigo-500 to-purple-600',
    'HỌC BỔNG': 'from-pink-500 to-rose-600',
    'THI ĐẤU': 'from-orange-500 to-red-600',
    'VĂN HÓA': 'from-teal-500 to-emerald-600',
    'NỔI BẬT': 'from-rose-500 to-red-600'
  };
  return colors[category] || 'from-gray-500 to-gray-600';
};

export default function TinTucPage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 9;

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/news');
        const result = await response.json();

        if (result.success) {
          const mainNews: NewsItem[] = result.data.mainNews || [];
          const sidebarNews: NewsItem[] = result.data.sidebarNews || [];

          // Combine and add mock views, FILTER ONLY NEWS WITH THUMBNAILS
          const allNews = [...mainNews, ...sidebarNews]
            .filter(item => item.image && item.image.trim() !== '') // CHỈ HIỂN THỊ TIN CÓ THUMBNAIL
            .map(item => ({
              ...item,
              views: item.views || Math.floor(Math.random() * 2000) + 100
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

  // Featured news (top 4 with images)
  const featuredNews = news.slice(0, 4);

  // Most viewed
  const mostViewed = [...news].sort((a, b) => (b.views || 0) - (a.views || 0)).slice(0, 5);

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-50 flex justify-center items-center">
          <div className="text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-rose-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-6 animate-pulse">
              <Newspaper className="w-10 h-10 text-white" />
            </div>
            <Loader2 className="w-8 h-8 text-rose-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600 font-medium">Đang cập nhật tin tức mới nhất...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Hero Section - Rose/Pink Theme */}
      <section className="relative bg-gradient-to-br from-rose-600 via-pink-700 to-fuchsia-800 text-white overflow-hidden">
        {/* Background Decorations */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-pink-400/10 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-rose-400/20 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto px-4 py-16 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full mb-6">
              <Sparkles className="w-4 h-4 text-pink-300" />
              <span className="text-sm font-bold text-pink-200 uppercase tracking-wider">Cập nhật liên tục</span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black mb-6 leading-tight">
              Tin Tức &
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-pink-300 to-white">
                Sự Kiện
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-lg md:text-xl text-rose-100 max-w-2xl mx-auto leading-relaxed">
              Cập nhật những tin tức mới nhất về hoạt động đào tạo, nghiên cứu khoa học
              và các sự kiện của Trường Đại học An ninh Nhân dân
            </p>
          </div>
        </div>

        {/* Bottom Wave */}
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-[#f9fafb] to-transparent"></div>
      </section>

      {/* Featured News Section */}
      {featuredNews.length > 0 && (
        <section className="py-12 bg-white">
          <div className="container mx-auto px-4">
            {/* Section Header */}
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 bg-gradient-to-br from-rose-500 to-pink-600 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Tin nổi bật</h2>
            </div>

            {/* Featured Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Main Featured */}
              <article className="group relative h-[400px] rounded-3xl overflow-hidden shadow-xl">
                <img
                  src={featuredNews[0].image}
                  alt={featuredNews[0].title}
                  className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent"></div>
                <div className="absolute bottom-0 left-0 right-0 p-8 text-white">
                  <span className={`inline-block bg-gradient-to-r ${getCategoryColor(featuredNews[0].category)} px-4 py-1.5 rounded-full text-xs font-bold mb-4 shadow-lg`}>
                    {featuredNews[0].category}
                  </span>
                  <h3 className="text-2xl font-bold mb-3 group-hover:text-pink-300 transition-colors">
                    {featuredNews[0].url ? (
                      <a href={featuredNews[0].url} target="_blank" rel="noopener noreferrer">{featuredNews[0].title}</a>
                    ) : featuredNews[0].title}
                  </h3>
                  {featuredNews[0].excerpt && (
                    <p className="text-gray-200 mb-4 line-clamp-2">{featuredNews[0].excerpt}</p>
                  )}
                  <div className="flex items-center gap-4 text-sm text-gray-300">
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

              {/* Side Featured */}
              <div className="grid grid-cols-1 gap-4">
                {featuredNews.slice(1, 4).map((item) => (
                  <article key={item.id} className="group relative h-[124px] rounded-2xl overflow-hidden shadow-md">
                    <img
                      src={item.image}
                      alt={item.title}
                      className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                    <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/50 to-transparent"></div>
                    <div className="absolute inset-0 p-5 flex flex-col justify-center text-white">
                      <span className={`inline-block w-fit bg-gradient-to-r ${getCategoryColor(item.category)} px-3 py-1 rounded-full text-xs font-bold mb-2`}>
                        {item.category}
                      </span>
                      <h3 className="text-sm font-bold group-hover:text-pink-300 transition-colors line-clamp-2">
                        {item.url ? (
                          <a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a>
                        ) : item.title}
                      </h3>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Main Content */}
      <section className="py-12 bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* News Grid - 3 columns */}
            <div className="lg:col-span-3">
              {/* Search & Filter Bar */}
              <div className="bg-white rounded-2xl shadow-lg p-6 mb-8 border border-gray-100">
                <div className="flex flex-col md:flex-row gap-4">
                  {/* Search */}
                  <div className="flex-1 relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Tìm kiếm tin tức..."
                      value={searchQuery}
                      onChange={(e) => {
                        setSearchQuery(e.target.value);
                        setCurrentPage(1);
                      }}
                      className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-rose-500 focus:border-transparent transition-all"
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
                      className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-rose-500 focus:border-transparent bg-white font-medium"
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
              <div className="mb-6 flex items-center gap-2">
                <Newspaper className="w-5 h-5 text-rose-600" />
                <span className="text-gray-600">
                  Tìm thấy <span className="font-bold text-rose-600">{filteredNews.length}</span> bài viết
                </span>
              </div>

              {/* News Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-10">
                {paginatedNews.map((item) => (
                  <article key={item.id} className="group bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 flex flex-col">
                    {/* Image */}
                    <div className="h-48 relative overflow-hidden">
                      <img
                        src={item.image}
                        alt={item.title}
                        className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                      />
                      <span className={`absolute top-4 left-4 bg-gradient-to-r ${getCategoryColor(item.category)} text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg`}>
                        {item.category}
                      </span>
                    </div>

                    <div className="p-5 flex flex-col flex-1">
                      <div className="flex items-center gap-3 text-sm text-gray-500 mb-3">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {item.date}
                        </span>
                        <span className="flex items-center gap-1">
                          <Eye className="w-4 h-4" />
                          {item.views?.toLocaleString()}
                        </span>
                      </div>

                      <h3 className="font-bold text-gray-900 mb-2 group-hover:text-rose-600 transition-colors line-clamp-2">
                        {item.url ? (
                          <a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a>
                        ) : item.title}
                      </h3>

                      <p className="text-gray-600 text-sm line-clamp-2 mb-4 flex-1">
                        {item.excerpt}
                      </p>

                      {item.url && (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center text-rose-600 hover:text-rose-700 font-medium text-sm group/btn"
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
                    className="p-3 rounded-xl bg-white border border-gray-200 hover:bg-rose-50 hover:border-rose-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>

                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let page;
                    if (totalPages <= 5) {
                      page = i + 1;
                    } else if (currentPage <= 3) {
                      page = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      page = totalPages - 4 + i;
                    } else {
                      page = currentPage - 2 + i;
                    }
                    return (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`w-12 h-12 rounded-xl font-bold transition-all ${currentPage === page
                          ? 'bg-gradient-to-r from-rose-500 to-pink-600 text-white shadow-lg'
                          : 'bg-white border border-gray-200 hover:bg-rose-50 hover:border-rose-300 shadow-sm'
                          }`}
                      >
                        {page}
                      </button>
                    );
                  })}

                  <button
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="p-3 rounded-xl bg-white border border-gray-200 hover:bg-rose-50 hover:border-rose-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1 space-y-6">
              {/* Categories */}
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Tag className="w-5 h-5 text-rose-600" />
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
                      className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all ${selectedCategory === cat.value
                        ? 'bg-gradient-to-r from-rose-500 to-pink-600 text-white shadow-lg'
                        : 'bg-gray-50 hover:bg-rose-50 text-gray-700 hover:text-rose-600'
                        }`}
                    >
                      <span>{cat.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Most Viewed */}
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Eye className="w-5 h-5 text-rose-600" />
                  Xem nhiều nhất
                </h3>
                <div className="space-y-4">
                  {mostViewed.map((item, index) => (
                    <article key={item.id} className="flex gap-3 group cursor-pointer">
                      <div className="flex-shrink-0 w-16 h-12 relative overflow-hidden rounded-lg">
                        <img
                          src={item.image}
                          alt={item.title}
                          className="absolute inset-0 w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                          <span className="text-white font-bold text-xs">{index + 1}</span>
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-900 group-hover:text-rose-600 transition-colors line-clamp-2">
                          {item.url ? (
                            <a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a>
                          ) : item.title}
                        </h4>
                        <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                          <Eye className="w-3 h-3" />
                          {item.views?.toLocaleString()}
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              </div>

              {/* CTA - Chatbot */}
              <div className="bg-gradient-to-br from-rose-600 via-pink-600 to-fuchsia-700 rounded-2xl p-6 text-white shadow-xl">
                <div className="text-center">
                  <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <MessageCircle className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="font-bold text-xl mb-2">Cần hỗ trợ?</h3>
                  <p className="text-pink-100 text-sm mb-5">
                    Chatbot AI sẵn sàng giải đáp thắc mắc 24/7
                  </p>
                  <Link
                    href="/chat-bot"
                    className="inline-flex items-center gap-2 bg-white text-rose-600 hover:bg-pink-100 font-bold py-3 px-6 rounded-xl transition-all shadow-lg hover:shadow-xl"
                  >
                    <MessageCircle className="w-5 h-5" />
                    Chat ngay
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
}
