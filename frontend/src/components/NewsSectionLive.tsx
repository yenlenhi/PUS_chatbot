'use client';

import React, { useEffect, useState } from 'react';
import {
  ArrowRight,
  Calendar,
  ExternalLink,
  Loader2,
  RefreshCw,
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
}

interface NewsData {
  mainNews: NewsItem[];
  sidebarNews: NewsItem[];
  lastUpdated: string;
}

const TUYEN_SINH_SOURCE_URL = 'https://dhannd.bocongan.gov.vn/tuyensinh';

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
        setSidebarPage(1);
      } else {
        setError(result.error || 'Không thể tải tin tuyển sinh');
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
    const colors: Record<string, string> = {
      'TUYỂN SINH': 'bg-emerald-600',
      'THÔNG BÁO': 'bg-blue-600',
      'ĐẠI HỌC': 'bg-red-600',
      'SAU ĐẠI HỌC': 'bg-indigo-600',
      'KẾT QUẢ': 'bg-amber-600',
    };

    return colors[category] || 'bg-slate-700';
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="text-center">
            <Loader2 className="mx-auto mb-4 h-12 w-12 animate-spin text-red-700" />
            <p className="text-gray-600">Đang tải tin tuyển sinh...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
          <p className="mb-4 text-red-700">{error}</p>
          <button
            onClick={fetchNews}
            className="rounded bg-red-700 px-4 py-2 text-white transition-colors hover:bg-red-800"
          >
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  const mainNews = (newsData?.mainNews || []).filter(
    (item) => item.image && item.image.trim() !== ''
  );
  const sidebarNews = (newsData?.sidebarNews || []).filter(
    (item) => item.image && item.image.trim() !== ''
  );
  const pagedSidebarNews = sidebarNews.slice((sidebarPage - 1) * 5, sidebarPage * 5);
  const totalSidebarPages = Math.max(1, Math.ceil(sidebarNews.length / 5));

  return (
    <section className="border-t border-slate-200 bg-gradient-to-b from-gray-50 via-slate-50 to-slate-100 py-16">
      <div className="container mx-auto px-4">
        <div className="mb-10 text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-700">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
            Cập nhật từ Kênh tuyển sinh DHANND
          </div>
          <h2 className="mb-3 text-3xl font-black text-gray-900 md:text-4xl">
            Tin Tuyển Sinh
          </h2>
          <p className="mx-auto max-w-2xl text-gray-600">
            Chỉ hiển thị các bài viết lấy từ trang tuyển sinh chính thức của Trường Đại học An ninh nhân dân.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <div className="mb-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-600 to-green-700 shadow-lg">
                  <span className="text-lg text-white">📘</span>
                </div>
                <h3 className="text-xl font-bold text-gray-800">BÀI VIẾT TUYỂN SINH MỚI</h3>
              </div>
              <button
                onClick={fetchNews}
                disabled={refreshing}
                className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-gray-600 shadow-sm transition-all duration-200 hover:border-emerald-300 hover:text-emerald-700 disabled:opacity-50"
                title="Làm mới tin tuyển sinh"
              >
                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                <span className="hidden text-sm font-medium sm:inline">Làm mới</span>
              </button>
            </div>

            <div className="space-y-6">
              {mainNews.map((news) => (
                <article
                  key={news.id}
                  className="overflow-hidden rounded-lg bg-white shadow-md transition-shadow duration-200 hover:shadow-lg"
                >
                  <div className="md:flex">
                    <div className="md:w-1/3">
                      <div className="group relative flex h-48 items-center justify-center overflow-hidden bg-gray-100 md:h-full">
                        {news.image ? (
                          <img
                            src={news.image}
                            alt={news.title}
                            className="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                              const sibling = e.currentTarget.nextElementSibling;
                              if (sibling) sibling.classList.remove('opacity-0');
                            }}
                          />
                        ) : null}

                        <div
                          className={`flex flex-col items-center justify-center bg-gradient-to-br from-emerald-100 to-emerald-200 p-4 text-center text-emerald-800 transition-opacity duration-300 ${
                            news.image
                              ? 'absolute inset-0 opacity-0'
                              : 'h-full w-full'
                          }`}
                        >
                          <div className="mb-2 text-5xl">📘</div>
                          <div className="text-xs opacity-75">Kênh tuyển sinh</div>
                        </div>

                        <div className="absolute right-2 top-2 rounded bg-black/50 px-2 py-1 text-xs text-white">
                          {news.source}
                        </div>
                      </div>
                    </div>

                    <div className="p-6 md:w-2/3">
                      <div className="mb-2 flex flex-wrap items-center gap-2">
                        <span
                          className={`${getCategoryColor(news.category)} rounded px-2 py-1 text-xs font-bold text-white`}
                        >
                          {news.category}
                        </span>
                        <div className="flex items-center text-sm text-gray-500">
                          <Calendar className="mr-1 h-4 w-4" />
                          {news.date}
                        </div>
                      </div>

                      <h3 className="mb-3 line-clamp-2 cursor-pointer text-xl font-bold text-gray-900 hover:text-emerald-700">
                        {news.title}
                      </h3>

                      {news.excerpt && (
                        <p className="mb-4 line-clamp-3 text-gray-600">{news.excerpt}</p>
                      )}

                      <div className="flex items-center justify-between">
                        <a
                          href={news.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center font-medium text-emerald-700 hover:text-emerald-800"
                        >
                          Đọc tiếp
                          <ArrowRight className="ml-1 h-4 w-4" />
                        </a>

                        {news.url && (
                          <a
                            href={news.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center text-sm text-gray-500 hover:text-emerald-700"
                          >
                            <ExternalLink className="mr-1 h-4 w-4" />
                            Nguồn gốc
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            <div className="mt-6 rounded-lg border border-gray-200 bg-gray-50 p-4">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>
                  📍 Nguồn:{' '}
                  <a
                    href={TUYEN_SINH_SOURCE_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-emerald-700 hover:underline"
                  >
                    dhannd.bocongan.gov.vn/tuyensinh
                  </a>
                </span>
                {newsData?.lastUpdated && (
                  <span>Cập nhật: {new Date(newsData.lastUpdated).toLocaleString('vi-VN')}</span>
                )}
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="sticky top-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-lg">
              <div className="mb-4 flex items-center gap-3 border-b border-gray-100 pb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 shadow-lg">
                  <span className="text-lg text-white">⭐</span>
                </div>
                <h3 className="text-lg font-bold text-gray-800">TIÊU ĐIỂM TUYỂN SINH</h3>
              </div>

              <div className="space-y-4">
                {pagedSidebarNews.map((news, index) => (
                  <article
                    key={news.id}
                    className="-mx-2 rounded border-b border-gray-200 px-2 pb-4 transition-colors hover:bg-gray-50 last:border-b-0"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="relative h-14 w-20 flex-shrink-0 overflow-hidden rounded border border-gray-200 bg-gray-100">
                        {news.image ? (
                          <img
                            src={news.image}
                            alt={news.title}
                            className="absolute inset-0 h-full w-full object-cover"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                              e.currentTarget.nextElementSibling?.classList.remove('hidden');
                            }}
                          />
                        ) : null}
                        <div
                          className={`flex h-full w-full items-center justify-center bg-emerald-700 text-sm font-bold text-white ${
                            news.image ? 'hidden' : ''
                          }`}
                        >
                          {(sidebarPage - 1) * 5 + index + 1}
                        </div>
                      </div>

                      <div className="flex-1">
                        <a
                          href={news.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mb-2 line-clamp-2 text-sm font-medium text-gray-900 hover:text-emerald-700"
                        >
                          {news.title}
                        </a>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center text-xs text-gray-500">
                            <Calendar className="mr-1 h-3 w-3" />
                            {news.date}
                          </div>
                          <span
                            className={`${getCategoryColor(news.category)} rounded px-1.5 py-0.5 text-[10px] text-white`}
                          >
                            {news.category}
                          </span>
                        </div>
                      </div>
                    </div>
                  </article>
                ))}
              </div>

              {sidebarNews.length > 5 && (
                <div className="mt-4 flex items-center justify-between border-t border-gray-100 pt-4">
                  <button
                    onClick={() => setSidebarPage((p) => Math.max(1, p - 1))}
                    disabled={sidebarPage === 1}
                    className="rounded p-1 text-gray-600 transition-colors hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent"
                  >
                    <ArrowRight className="h-5 w-5 rotate-180" />
                  </button>
                  <span className="text-sm font-medium text-gray-600">
                    {sidebarPage} / {totalSidebarPages}
                  </span>
                  <button
                    onClick={() =>
                      setSidebarPage((p) => Math.min(totalSidebarPages, p + 1))
                    }
                    disabled={sidebarPage === totalSidebarPages}
                    className="rounded p-1 text-gray-600 transition-colors hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent"
                  >
                    <ArrowRight className="h-5 w-5" />
                  </button>
                </div>
              )}

              <div className="mt-6 space-y-3">
                <a
                  href={TUYEN_SINH_SOURCE_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex w-full items-center justify-center gap-2 rounded bg-emerald-700 px-4 py-2 font-bold text-white transition-colors duration-200 hover:bg-emerald-800"
                >
                  Xem kênh tuyển sinh
                  <ExternalLink className="h-4 w-4" />
                </a>
                <button
                  onClick={fetchNews}
                  disabled={refreshing}
                  className="flex w-full items-center justify-center gap-2 rounded border border-emerald-700 px-4 py-2 font-medium text-emerald-700 transition-colors duration-200 hover:bg-emerald-50 disabled:opacity-50"
                >
                  <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                  Cập nhật tin tuyển sinh
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
