import React from 'react';
import { Calendar, ArrowRight } from 'lucide-react';
import { MAIN_NEWS, SIDEBAR_NEWS } from '@/data/constants';

const NewsSection = () => {
  const mainNews = MAIN_NEWS;
  const sidebarNews = SIDEBAR_NEWS;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content Area */}
        <div className="lg:col-span-2">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-red-700 border-b-2 border-red-700 pb-2 mb-4">
              TIN TỨC
            </h2>
          </div>

          <div className="space-y-6">
            {mainNews.map((news) => (
              <article key={news.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200">
                <div className="md:flex">
                  <div className="md:w-1/3">
                    <div className="h-48 md:h-full bg-gradient-to-br from-blue-200 to-blue-300 flex items-center justify-center">
                      <div className="text-blue-800 text-center">
                        <div className="text-3xl mb-2">📰</div>
                        <div className="text-sm">Hình ảnh tin tức</div>
                      </div>
                    </div>
                  </div>
                  <div className="md:w-2/3 p-6">
                    <div className="flex items-center mb-2">
                      <span className="bg-red-600 text-white text-xs font-bold px-2 py-1 rounded">
                        {news.category}
                      </span>
                      <div className="flex items-center ml-4 text-gray-500 text-sm">
                        <Calendar className="w-4 h-4 mr-1" />
                        {news.date}
                      </div>
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 mb-3 hover:text-red-700 cursor-pointer">
                      {news.title}
                    </h3>
                    <p className="text-gray-600 mb-4 line-clamp-3">
                      {news.excerpt}
                    </p>
                    <button className="flex items-center text-red-700 hover:text-red-800 font-medium">
                      Đọc tiếp
                      <ArrowRight className="w-4 h-4 ml-1" />
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-red-700 border-b-2 border-red-700 pb-2 mb-4">
              TIN BÀI NỔI BẬT
            </h3>
            <div className="space-y-4">
              {sidebarNews.map((news, index) => (
                <article key={news.id} className="border-b border-gray-200 pb-4 last:border-b-0">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-red-700 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-900 hover:text-red-700 cursor-pointer line-clamp-2 mb-2">
                        {news.title}
                      </h4>
                      <div className="flex items-center text-xs text-gray-500">
                        <Calendar className="w-3 h-3 mr-1" />
                        {news.date}
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>
            <div className="mt-6">
              <button className="w-full bg-red-700 hover:bg-red-800 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
                Xem tất cả tin tức
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewsSection;
