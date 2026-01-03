import Layout from '@/components/Layout';
import { MapPin, Phone, Mail, Clock, Globe, Facebook, MessageCircle } from 'lucide-react';

export default function LienHe() {
  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg p-8 mb-8">
          <h1 className="text-4xl font-bold mb-4">Liên Hệ</h1>
          <p className="text-xl text-green-100">
            Chúng tôi sẵn sàng hỗ trợ và giải đáp mọi thắc mắc của bạn
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-green-700 mb-6">Thông tin liên hệ</h2>
              <div className="space-y-6">
                <div className="flex items-start space-x-4 p-4 bg-green-50 rounded-lg">
                  <MapPin className="w-8 h-8 text-green-600 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Địa chỉ</h3>
                    <p className="text-gray-700">
                      Km18 Xa Lộ Hà Nội, Phường Linh Trung, Quận Thủ Đức, Thành phố Hồ Chí Minh
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-blue-50 rounded-lg">
                  <Phone className="w-8 h-8 text-blue-600 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Số điện thoại</h3>
                    <p className="text-gray-700 mb-2">
                      <span className="font-semibold">Tổng đài:</span> 0283.896.3883
                    </p>
                    <p className="text-gray-700 mb-2">
                      <span className="font-semibold">Fax:</span> 0283.896.3883
                    </p>
                    <p className="text-gray-700">
                      <span className="font-semibold">Hotline:</span> 0283.896.3883 (24/7)
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-purple-50 rounded-lg">
                  <Mail className="w-8 h-8 text-purple-600 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Email</h3>
                    <p className="text-gray-700 mb-2">
                      <span className="font-semibold">Chung:</span> info@dhannd.edu.vn
                    </p>
                    <p className="text-gray-700 mb-2">
                      <span className="font-semibold">Tuyển sinh:</span> tuyensinh@dhannd.edu.vn
                    </p>
                    <p className="text-gray-700">
                      <span className="font-semibold">Hỗ trợ:</span> support@dhannd.edu.vn
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-orange-50 rounded-lg">
                  <Clock className="w-8 h-8 text-orange-600 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Giờ làm việc</h3>
                    <p className="text-gray-700 mb-2">
                      <span className="font-semibold">Thứ 2 - Thứ 6:</span> 8:00 - 17:00
                    </p>
                    <p className="text-gray-700 mb-2">
                      <span className="font-semibold">Thứ 7:</span> 8:00 - 12:00
                    </p>
                    <p className="text-gray-700">
                      <span className="font-semibold">Chủ nhật:</span> Nghỉ
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-red-50 rounded-lg">
                  <Globe className="w-8 h-8 text-red-600 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Website & Mạng xã hội</h3>
                    <p className="text-gray-700 mb-2">
                      <span className="font-semibold">Website:</span>{' '}
                      <a href="https://dhannd.bocongan.gov.vn/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800">
                        dhannd.bocongan.gov.vn
                      </a>
                    </p>
                    <div className="flex items-center space-x-4 mt-3">
                      <a
                        href="#"
                        className="flex items-center text-blue-600 hover:text-blue-800"
                      >
                        <Facebook className="w-5 h-5 mr-1" />
                        <span className="text-sm">Facebook</span>
                      </a>
                      <a
                        href="#"
                        className="flex items-center text-green-600 hover:text-green-800"
                      >
                        <MessageCircle className="w-5 h-5 mr-1" />
                        <span className="text-sm">Zalo</span>
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-green-700 mb-4">Các phòng ban</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border border-gray-200 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">Phòng Đào tạo</h4>
                  <p className="text-sm text-gray-600 mb-1">📞 0283.896.3883</p>
                  <p className="text-sm text-gray-600">✉️ daotao@dhannd.edu.vn</p>
                </div>
                <div className="p-4 border border-gray-200 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">Phòng Tuyển sinh</h4>
                  <p className="text-sm text-gray-600 mb-1">📞 0283.896.3883</p>
                  <p className="text-sm text-gray-600">✉️ tuyensinh@dhannd.edu.vn</p>
                </div>
                <div className="p-4 border border-gray-200 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">Phòng Công tác sinh viên</h4>
                  <p className="text-sm text-gray-600 mb-1">📞 0283.896.3883</p>
                  <p className="text-sm text-gray-600">✉️ ctsv@dhannd.edu.vn</p>
                </div>
                <div className="p-4 border border-gray-200 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">Phòng Khoa học Công nghệ</h4>
                  <p className="text-sm text-gray-600 mb-1">📞 0283.896.3883</p>
                  <p className="text-sm text-gray-600">✉️ khcn@dhannd.edu.vn</p>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-xl font-bold mb-3 flex items-center">
                <MessageCircle className="w-6 h-6 mr-2" />
                Chat với AI
              </h3>
              <p className="text-blue-100 text-sm mb-4">
                Nhận tư vấn nhanh chóng 24/7 thông qua hệ thống AI chatbot thông minh
              </p>
              <a
                href="/chat-bot"
                className="block w-full bg-white text-blue-600 text-center font-semibold py-3 px-4 rounded-lg hover:bg-blue-50 transition-colors"
              >
                Bắt đầu Chat
              </a>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-xl font-bold text-green-700 mb-4">Bản đồ</h3>
              <div className="aspect-video bg-gray-200 rounded-lg flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <MapPin className="w-12 h-12 mx-auto mb-2" />
                  <p className="text-sm">Bản đồ Google Maps</p>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Nhấn vào để xem đường đi chi tiết
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-green-700 mb-4">Gửi câu hỏi</h3>
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Họ và tên
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Nhập họ tên của bạn"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Nhập email của bạn"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nội dung
                  </label>
                  <textarea
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Nhập câu hỏi của bạn"
                  ></textarea>
                </div>
                <button
                  type="submit"
                  className="w-full bg-green-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-green-700 transition-colors"
                >
                  Gửi câu hỏi
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="mt-8 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Liên kết hữu ích</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <a
              href="/gioi-thieu"
              className="bg-white p-4 rounded-lg text-center hover:shadow-lg transition-shadow"
            >
              <h4 className="font-semibold text-gray-900">Giới thiệu</h4>
            </a>
            <a
              href="/dao-tao"
              className="bg-white p-4 rounded-lg text-center hover:shadow-lg transition-shadow"
            >
              <h4 className="font-semibold text-gray-900">Đào tạo</h4>
            </a>
            <a
              href="/tuyen-sinh"
              className="bg-white p-4 rounded-lg text-center hover:shadow-lg transition-shadow"
            >
              <h4 className="font-semibold text-gray-900">Tuyển sinh</h4>
            </a>
            <a
              href="/nghien-cuu"
              className="bg-white p-4 rounded-lg text-center hover:shadow-lg transition-shadow"
            >
              <h4 className="font-semibold text-gray-900">Nghiên cứu</h4>
            </a>
          </div>
        </div>
      </div>
    </Layout>
  );
}
