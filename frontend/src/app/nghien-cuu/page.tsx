import Layout from '@/components/Layout';
import { Brain, MessageSquare, Search, Zap, BookOpen, Users, Sparkles, Shield } from 'lucide-react';

export default function NghienCuu() {
  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg p-8 mb-8">
          <h1 className="text-4xl font-bold mb-4">Hệ Thống AI Chatbot Hỗ Trợ Tuyển Sinh</h1>
          <p className="text-xl text-blue-100">
            Ứng dụng Trí tuệ nhân tạo trong tư vấn và hỗ trợ thông tin tuyển sinh
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-blue-700 mb-4">Giới thiệu về Hệ thống</h2>
              <p className="text-gray-700 mb-4">
                Hệ thống AI Chatbot Hỗ trợ Tuyển sinh là một ứng dụng trí tuệ nhân tạo tiên tiến, 
                được phát triển để tự động hóa và nâng cao chất lượng dịch vụ tư vấn tuyển sinh 
                tại Trường Đại học An ninh Nhân dân.
              </p>
              <p className="text-gray-700 mb-4">
                Hệ thống sử dụng công nghệ RAG (Retrieval-Augmented Generation) kết hợp với 
                các mô hình ngôn ngữ lớn (LLM) để cung cấp câu trả lời chính xác, ngữ cảnh phù hợp 
                và được cá nhân hóa cho từng câu hỏi của người dùng.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-blue-700 mb-4">Tính năng chính</h2>
              <div className="space-y-4">
                <div className="flex items-start space-x-4 p-4 bg-blue-50 rounded-lg">
                  <Brain className="w-8 h-8 text-blue-600 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Conversation</h3>
                    <p className="text-gray-700">
                      Trò chuyện tự nhiên với AI để được tư vấn về tuyển sinh, chương trình đào tạo, 
                      học phí, điều kiện tuyển sinh và nhiều thông tin khác. Hệ thống có khả năng 
                      hiểu ngữ cảnh và ghi nhớ lịch sử hội thoại.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-green-50 rounded-lg">
                  <Search className="w-8 h-8 text-green-600 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Tìm kiếm Thông minh</h3>
                    <p className="text-gray-700">
                      Tìm kiếm semantic dựa trên ý nghĩa của câu hỏi, không chỉ từ khóa. 
                      Hệ thống tìm kiếm trong hàng ngàn tài liệu để cung cấp thông tin chính xác nhất.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-purple-50 rounded-lg">
                  <MessageSquare className="w-8 h-8 text-purple-600 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Câu hỏi Gợi ý</h3>
                    <p className="text-gray-700">
                      Hệ thống tự động đề xuất các câu hỏi phổ biến và câu hỏi tiếp theo dựa trên 
                      ngữ cảnh hội thoại, giúp người dùng dễ dàng khám phá thông tin.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-orange-50 rounded-lg">
                  <Zap className="w-8 h-8 text-orange-600 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Phản hồi Nhanh</h3>
                    <p className="text-gray-700">
                      Thời gian phản hồi trung bình dưới 3 giây với độ chính xác cao. 
                      Hỗ trợ streaming để người dùng xem câu trả lời ngay khi được tạo ra.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-yellow-50 rounded-lg">
                  <BookOpen className="w-8 h-8 text-yellow-600 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Đa dạng Nguồn thông tin</h3>
                    <p className="text-gray-700">
                      Tích hợp thông tin từ văn bản, PDF, hình ảnh và các tài liệu tuyển sinh chính thống. 
                      Cập nhật thường xuyên để đảm bảo thông tin luôn mới nhất.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-red-50 rounded-lg">
                  <Shield className="w-8 h-8 text-red-600 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Bảo mật & Riêng tư</h3>
                    <p className="text-gray-700">
                      Dữ liệu người dùng được mã hóa và bảo vệ. Tuân thủ các quy định về bảo mật 
                      thông tin và quyền riêng tư của người dùng.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-blue-700 mb-4">Hướng dẫn Sử dụng</h2>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">1</span>
                    Truy cập Chatbot
                  </h3>
                  <p className="text-gray-700 ml-11">
                    Truy cập trang chủ và nhấn vào nút "Chat với AI" hoặc biểu tượng chatbot ở góc dưới bên phải màn hình. 
                    Không cần đăng nhập để bắt đầu sử dụng.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">2</span>
                    Đặt Câu hỏi
                  </h3>
                  <p className="text-gray-700 ml-11 mb-2">
                    Nhập câu hỏi của bạn vào ô chat. Bạn có thể hỏi về:
                  </p>
                  <ul className="list-disc list-inside text-gray-700 ml-11 space-y-1">
                    <li>Điều kiện tuyển sinh và hồ sơ cần thiết</li>
                    <li>Các ngành đào tạo và chương trình học</li>
                    <li>Học phí và chính sách miễn giảm</li>
                    <li>Cơ sở vật chất và đời sống sinh viên</li>
                    <li>Thông tin liên hệ và địa chỉ</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">3</span>
                    Sử dụng Câu hỏi Gợi ý
                  </h3>
                  <p className="text-gray-700 ml-11">
                    Nhấn vào các câu hỏi được đề xuất bên dưới ô chat hoặc sau mỗi câu trả lời 
                    để nhanh chóng tìm hiểu thêm thông tin liên quan.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">4</span>
                    Xem Lịch sử Chat
                  </h3>
                  <p className="text-gray-700 ml-11">
                    Lịch sử hội thoại được lưu tự động. Bạn có thể xem lại các cuộc trò chuyện trước đó 
                    bằng cách nhấn vào biểu tượng lịch sử.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">5</span>
                    Đánh giá & Phản hồi
                  </h3>
                  <p className="text-gray-700 ml-11">
                    Sau mỗi câu trả lời, bạn có thể đánh giá mức độ hữu ích bằng biểu tượng like/dislike 
                    để giúp cải thiện chất lượng hệ thống.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-6 mb-6">
              <h2 className="text-2xl font-bold text-blue-700 mb-4">Công nghệ Sử dụng</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg p-4 text-center shadow-sm">
                  <h4 className="font-semibold text-gray-900 mb-1">Frontend</h4>
                  <p className="text-gray-600 text-sm">Next.js, React, TypeScript</p>
                </div>
                <div className="bg-white rounded-lg p-4 text-center shadow-sm">
                  <h4 className="font-semibold text-gray-900 mb-1">Backend</h4>
                  <p className="text-gray-600 text-sm">Python, FastAPI</p>
                </div>
                <div className="bg-white rounded-lg p-4 text-center shadow-sm">
                  <h4 className="font-semibold text-gray-900 mb-1">AI Model</h4>
                  <p className="text-gray-600 text-sm">GPT-4, Gemini Pro</p>
                </div>
                <div className="bg-white rounded-lg p-4 text-center shadow-sm">
                  <h4 className="font-semibold text-gray-900 mb-1">Database</h4>
                  <p className="text-gray-600 text-sm">PostgreSQL, Supabase</p>
                </div>
                <div className="bg-white rounded-lg p-4 text-center shadow-sm">
                  <h4 className="font-semibold text-gray-900 mb-1">Vector DB</h4>
                  <p className="text-gray-600 text-sm">pgvector</p>
                </div>
                <div className="bg-white rounded-lg p-4 text-center shadow-sm">
                  <h4 className="font-semibold text-gray-900 mb-1">Deployment</h4>
                  <p className="text-gray-600 text-sm">Railway, Docker</p>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-xl font-bold text-blue-700 mb-4 flex items-center">
                <Users className="w-6 h-6 mr-2" />
                Nhóm Tác giả
              </h3>
              <div className="space-y-4">
                <div className="p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border-l-4 border-blue-600">
                  <h4 className="font-bold text-gray-900 mb-1">VŨ QUỐC HƯNG</h4>
                  <p className="text-sm text-gray-600 mb-1">Lớp: VB2 D5</p>
                  <div className="flex items-center text-xs text-blue-700 mt-2">
                    <Sparkles className="w-3 h-3 mr-1" />
                    <span>Trưởng nhóm</span>
                  </div>
                </div>

                <div className="p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-lg border-l-4 border-green-600">
                  <h4 className="font-bold text-gray-900 mb-1">TRƯƠNG VĂN KHẢI</h4>
                  <p className="text-sm text-gray-600 mb-1">Lớp: VB2 D5</p>
                  <div className="flex items-center text-xs text-green-700 mt-2">
                    <Sparkles className="w-3 h-3 mr-1" />
                    <span>Thành viên</span>
                  </div>
                </div>

                <div className="p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg border-l-4 border-purple-600">
                  <h4 className="font-bold text-gray-900 mb-1">NGUYỄN HỮU TẤN DŨNG</h4>
                  <p className="text-sm text-gray-600 mb-1">Lớp: D32C</p>
                  <div className="flex items-center text-xs text-purple-700 mt-2">
                    <Sparkles className="w-3 h-3 mr-1" />
                    <span>Thành viên</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-xl font-bold text-blue-700 mb-4">Thông tin Hệ thống</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="font-semibold text-gray-900">Phiên bản:</span>
                  <span className="text-gray-700 ml-2">2.0</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-900">Ngày ra mắt:</span>
                  <span className="text-gray-700 ml-2">01/2025</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-900">Tài liệu:</span>
                  <span className="text-gray-700 ml-2">1000+ trang</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-900">Độ chính xác:</span>
                  <span className="text-gray-700 ml-2">95%+</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-900">Ngôn ngữ:</span>
                  <span className="text-gray-700 ml-2">Tiếng Việt</span>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold mb-4">Trải nghiệm ngay!</h3>
              <p className="text-blue-100 text-sm mb-4">
                Bắt đầu trò chuyện với AI chatbot và khám phá thông tin tuyển sinh
              </p>
              <a
                href="/chat-bot"
                className="block w-full bg-white text-blue-600 text-center font-semibold py-3 px-4 rounded-lg hover:bg-blue-50 transition-colors"
              >
                Bắt đầu Chat
              </a>
            </div>
          </div>
        </div>

        {/* Additional Info Section */}
        <div className="mt-8 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Liên hệ & Hỗ trợ</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Email</h4>
              <p className="text-gray-600 text-sm">info@dhannd.edu.vn</p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Hotline</h4>
              <p className="text-gray-600 text-sm">0283.896.3883</p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Giờ hỗ trợ</h4>
              <p className="text-gray-600 text-sm">24/7 (AI tự động)</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
