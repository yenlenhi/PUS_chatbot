'use client';

import React, { useState } from 'react';
import Layout from '@/components/Layout';
import Link from 'next/link';
import { Calendar, Eye, ArrowRight, Search, Filter, ChevronLeft, ChevronRight, Tag, Clock, TrendingUp } from 'lucide-react';

// Extended news data
const ALL_NEWS = [
  {
    id: 1,
    title: "Nền tảng pháp lý thúc đẩy khoa học, công nghệ, đổi mới sáng tạo và chuyển đổi số",
    excerpt: "Luật Khoa học và Công nghệ năm 2013 đã tạo nền tảng pháp lý quan trọng cho việc phát triển khoa học công nghệ trong lĩnh vực an ninh quốc gia. Trường Đại học An ninh Nhân dân đã và đang triển khai nhiều đề tài nghiên cứu quan trọng...",
    content: "Nội dung chi tiết của bài viết...",
    date: "15/01/2025",
    category: "TIN TỨC",
    views: 1250,
    featured: true
  },
  {
    id: 2,
    title: "Hướng dẫn tổng hợp ý kiến góp ý của cán bộ, đảng viên về dự thảo các văn kiện",
    excerpt: "Thực hiện chỉ đạo của Ban Thường vụ Đảng ủy Công an Trung ương về việc lấy ý kiến góp ý của cán bộ, đảng viên trong toàn lực lượng về dự thảo văn kiện Đại hội...",
    date: "14/01/2025",
    category: "THÔNG BÁO",
    views: 980,
    featured: true
  },
  {
    id: 3,
    title: "Kết quả thi đánh giá năng lực tuyển sinh năm 2024",
    excerpt: "Trường Đại học An ninh Nhân dân công bố kết quả thi đánh giá năng lực tuyển sinh năm 2024 với tỷ lệ đậu cao. Thí sinh có thể tra cứu kết quả trên hệ thống...",
    date: "13/01/2025",
    category: "TUYỂN SINH",
    views: 2100,
    featured: true
  },
  {
    id: 4,
    title: "Trường Đại học An ninh nhân dân tổ chức trao tặng căn hộ tình nghĩa cho cán bộ, chiến sĩ",
    excerpt: "Nhân dịp kỷ niệm ngày thành lập lực lượng Công an Nhân dân, trường đã tổ chức lễ trao tặng căn hộ tình nghĩa cho các cán bộ, chiến sĩ có hoàn cảnh khó khăn...",
    date: "13/01/2025",
    category: "TIN TỨC",
    views: 756
  },
  {
    id: 5,
    title: "Công đoàn Trường Đại học An ninh nhân dân tổ chức Hội thi nấu ăn",
    excerpt: "Hội thi nấu ăn với chủ đề 'Bữa cơm gia đình' đã thu hút sự tham gia của đông đảo cán bộ, giảng viên. Đây là hoạt động thường niên nhằm tăng cường giao lưu...",
    date: "12/01/2025",
    category: "HOẠT ĐỘNG",
    views: 543
  },
  {
    id: 6,
    title: "Lễ trao bằng tốt nghiệp cho sinh viên khóa 2021-2025",
    excerpt: "Trường Đại học An ninh Nhân dân long trọng tổ chức Lễ trao bằng tốt nghiệp cho 1.200 sinh viên khóa 2021-2025. Đây là những cán bộ an ninh tương lai của đất nước...",
    date: "11/01/2025",
    category: "ĐÀO TẠO",
    views: 1890
  },
  {
    id: 7,
    title: "Hội nghị tổng kết công tác năm 2024 và triển khai nhiệm vụ năm 2025",
    excerpt: "Hội nghị đã đánh giá toàn diện kết quả công tác năm 2024 và đề ra phương hướng, nhiệm vụ trọng tâm năm 2025. Nhiều tập thể, cá nhân xuất sắc được khen thưởng...",
    date: "10/01/2025",
    category: "HỘI NGHỊ",
    views: 892
  },
  {
    id: 8,
    title: "Chương trình học bổng khuyến khích học tập cho sinh viên xuất sắc",
    excerpt: "Nhà trường công bố chương trình học bổng khuyến khích học tập dành cho sinh viên có thành tích xuất sắc trong năm học 2024-2025. Tổng giá trị học bổng lên đến 2 tỷ đồng...",
    date: "09/01/2025",
    category: "HỌC BỔNG",
    views: 1567
  },
  {
    id: 9,
    title: "Hội thảo khoa học quốc tế về an ninh mạng và bảo mật thông tin",
    excerpt: "Hội thảo quy tụ các chuyên gia hàng đầu trong và ngoài nước về lĩnh vực an ninh mạng. Nhiều nghiên cứu mới được công bố và thảo luận tại hội thảo...",
    date: "08/01/2025",
    category: "KHOA HỌC",
    views: 1234
  },
  {
    id: 10,
    title: "Thông báo lịch nghỉ Tết Nguyên đán Ất Tỵ 2025",
    excerpt: "Trường thông báo lịch nghỉ Tết Nguyên đán Ất Tỵ 2025 cho toàn thể cán bộ, giảng viên và sinh viên. Thời gian nghỉ từ ngày 25/01/2025 đến hết ngày 02/02/2025...",
    date: "07/01/2025",
    category: "THÔNG BÁO",
    views: 3456
  },
  {
    id: 11,
    title: "Cuộc thi Olympic Tin học sinh viên toàn quốc 2025",
    excerpt: "Đội tuyển sinh viên trường đã xuất sắc giành giải Nhất toàn quốc tại cuộc thi Olympic Tin học sinh viên. Đây là năm thứ 3 liên tiếp trường đạt thành tích cao...",
    date: "06/01/2025",
    category: "THI ĐẤU",
    views: 2789
  },
  {
    id: 12,
    title: "Khai mạc Tuần lễ văn hóa sinh viên năm 2025",
    excerpt: "Tuần lễ văn hóa sinh viên với chủ đề 'Tuổi trẻ - Sáng tạo - Cống hiến' chính thức khai mạc. Nhiều hoạt động văn hóa, văn nghệ, thể thao sôi nổi được tổ chức...",
    date: "05/01/2025",
    category: "VĂN HÓA",
    views: 987
  }
];

const CATEGORIES = [
  { name: 'Tất cả', value: 'all', count: 12 },
  { name: 'Tin tức', value: 'TIN TỨC', count: 3 },
  { name: 'Thông báo', value: 'THÔNG BÁO', count: 2 },
  { name: 'Tuyển sinh', value: 'TUYỂN SINH', count: 1 },
  { name: 'Đào tạo', value: 'ĐÀO TẠO', count: 1 },
  { name: 'Hoạt động', value: 'HOẠT ĐỘNG', count: 1 },
  { name: 'Khoa học', value: 'KHOA HỌC', count: 1 },
  { name: 'Hội nghị', value: 'HỘI NGHỊ', count: 1 },
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
    'VĂN HÓA': 'bg-teal-500'
  };
  return colors[category] || 'bg-gray-500';
};

export default function TinTucPage() {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6;

  // Filter news
  const filteredNews = ALL_NEWS.filter(news => {
    const matchCategory = selectedCategory === 'all' || news.category === selectedCategory;
    const matchSearch = news.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                       news.excerpt.toLowerCase().includes(searchQuery.toLowerCase());
    return matchCategory && matchSearch;
  });

  // Pagination
  const totalPages = Math.ceil(filteredNews.length / itemsPerPage);
  const paginatedNews = filteredNews.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Featured news (top 3)
  const featuredNews = ALL_NEWS.filter(n => n.featured).slice(0, 3);

  // Most viewed
  const mostViewed = [...ALL_NEWS].sort((a, b) => b.views - a.views).slice(0, 5);

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
        {/* Featured News Section */}
        <div className="mb-12">
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp className="w-6 h-6 text-red-600" />
            <h2 className="text-2xl font-bold text-gray-900">Tin nổi bật</h2>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main featured */}
            <div className="lg:col-span-2">
              <article className="group relative h-[400px] rounded-2xl overflow-hidden shadow-lg">
                <div className="absolute inset-0 bg-gradient-to-br from-red-600 to-red-800">
                  <div className="absolute inset-0 bg-black/30 group-hover:bg-black/40 transition-colors" />
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                  <span className={`inline-block ${getCategoryColor(featuredNews[0]?.category)} px-3 py-1 rounded-full text-xs font-bold mb-3`}>
                    {featuredNews[0]?.category}
                  </span>
                  <h3 className="text-2xl font-bold mb-3 group-hover:text-yellow-300 transition-colors cursor-pointer">
                    {featuredNews[0]?.title}
                  </h3>
                  <p className="text-gray-200 mb-4 line-clamp-2">{featuredNews[0]?.excerpt}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-300">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {featuredNews[0]?.date}
                    </span>
                    <span className="flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      {featuredNews[0]?.views.toLocaleString()} lượt xem
                    </span>
                  </div>
                </div>
              </article>
            </div>

            {/* Side featured */}
            <div className="space-y-4">
              {featuredNews.slice(1, 3).map((news) => (
                <article key={news.id} className="group relative h-[190px] rounded-xl overflow-hidden shadow-md">
                  <div className="absolute inset-0 bg-gradient-to-br from-gray-700 to-gray-900">
                    <div className="absolute inset-0 bg-black/20 group-hover:bg-black/30 transition-colors" />
                  </div>
                  <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
                    <span className={`inline-block ${getCategoryColor(news.category)} px-2 py-0.5 rounded-full text-xs font-bold mb-2`}>
                      {news.category}
                    </span>
                    <h3 className="text-sm font-bold mb-2 group-hover:text-yellow-300 transition-colors cursor-pointer line-clamp-2">
                      {news.title}
                    </h3>
                    <div className="flex items-center gap-3 text-xs text-gray-300">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {news.date}
                      </span>
                      <span className="flex items-center gap-1">
                        <Eye className="w-3 h-3" />
                        {news.views.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </div>

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
                        {cat.name} ({cat.count})
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
                <article key={news.id} className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 hover:shadow-lg transition-all duration-300 group">
                  {/* Image placeholder */}
                  <div className="h-48 bg-gradient-to-br from-gray-100 to-gray-200 relative overflow-hidden">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="w-12 h-12 bg-gray-300/50 rounded-full flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
                          <span className="text-2xl">📰</span>
                        </div>
                      </div>
                    </div>
                    <span className={`absolute top-3 left-3 ${getCategoryColor(news.category)} text-white text-xs font-bold px-3 py-1 rounded-full`}>
                      {news.category}
                    </span>
                  </div>
                  
                  <div className="p-5">
                    <div className="flex items-center gap-3 text-sm text-gray-500 mb-3">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {news.date}
                      </span>
                      <span className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        {news.views.toLocaleString()}
                      </span>
                    </div>
                    
                    <h3 className="font-bold text-gray-900 mb-2 group-hover:text-red-600 transition-colors cursor-pointer line-clamp-2">
                      {news.title}
                    </h3>
                    
                    <p className="text-gray-600 text-sm line-clamp-2 mb-4">
                      {news.excerpt}
                    </p>
                    
                    <button className="flex items-center text-red-600 hover:text-red-700 font-medium text-sm group/btn">
                      Đọc tiếp
                      <ArrowRight className="w-4 h-4 ml-1 group-hover/btn:translate-x-1 transition-transform" />
                    </button>
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
                    className={`w-10 h-10 rounded-lg font-medium transition-colors ${
                      currentPage === page
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
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${
                      selectedCategory === cat.value
                        ? 'bg-red-50 text-red-600 font-medium'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <span>{cat.name}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs ${
                      selectedCategory === cat.value
                        ? 'bg-red-100 text-red-600'
                        : 'bg-gray-100 text-gray-600'
                    }`}>
                      {cat.count}
                    </span>
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
                    <div className="flex-shrink-0 w-8 h-8 bg-red-100 text-red-600 rounded-lg flex items-center justify-center font-bold text-sm">
                      {index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-gray-900 group-hover:text-red-600 transition-colors line-clamp-2 mb-1">
                        {news.title}
                      </h4>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Eye className="w-3 h-3" />
                        {news.views.toLocaleString()}
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

            {/* Recent Updates */}
            <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
              <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-red-600" />
                Cập nhật gần đây
              </h3>
              <div className="space-y-3">
                {ALL_NEWS.slice(0, 4).map((news) => (
                  <article key={news.id} className="border-b border-gray-100 pb-3 last:border-0 last:pb-0">
                    <h4 className="text-sm text-gray-900 hover:text-red-600 cursor-pointer transition-colors line-clamp-2 mb-1">
                      {news.title}
                    </h4>
                    <span className="text-xs text-gray-500">{news.date}</span>
                  </article>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
