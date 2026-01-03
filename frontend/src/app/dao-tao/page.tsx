import Layout from '@/components/Layout';
import { GraduationCap, BookOpen, Award, Users, Clock, FileText } from 'lucide-react';

export default function DaoTao() {
  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg p-8 mb-8">
          <h1 className="text-4xl font-bold mb-4">Đào Tạo</h1>
          <p className="text-xl text-red-100">
            Chương trình đào tạo chất lượng cao trong lĩnh vực an ninh quốc gia
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-red-700 mb-4">Hệ đào tạo</h2>
              <div className="space-y-4">
                <div className="flex items-start space-x-4 p-4 bg-red-50 rounded-lg">
                  <GraduationCap className="w-8 h-8 text-red-600 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Đại học</h3>
                    <p className="text-gray-700">
                      Thời gian đào tạo: 4-5 năm. Cấp bằng cử nhân cho các ngành về an ninh, 
                      công nghệ thông tin, luật, quản trị kinh doanh và các chuyên ngành liên quan.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-blue-50 rounded-lg">
                  <Award className="w-8 h-8 text-blue-600 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Thạc sĩ</h3>
                    <p className="text-gray-700">
                      Thời gian đào tạo: 2 năm. Chương trình đào tạo chuyên sâu cho cán bộ 
                      có kinh nghiệm trong các lĩnh vực an ninh và quản lý nhà nước.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-purple-50 rounded-lg">
                  <BookOpen className="w-8 h-8 text-purple-600 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Tiến sĩ</h3>
                    <p className="text-gray-700">
                      Thời gian đào tạo: 3-4 năm. Đào tạo các chuyên gia nghiên cứu hàng đầu 
                      trong lĩnh vực an ninh quốc gia và các khoa học liên quan.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-red-700 mb-4">Các ngành đào tạo</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border border-gray-200 rounded-lg hover:border-red-500 transition-colors">
                  <h4 className="font-semibold text-gray-900 mb-2">An ninh chính trị</h4>
                  <p className="text-sm text-gray-600">Đào tạo cán bộ bảo vệ an ninh chính trị nội bộ</p>
                </div>
                <div className="p-4 border border-gray-200 rounded-lg hover:border-red-500 transition-colors">
                  <h4 className="font-semibold text-gray-900 mb-2">An ninh mạng</h4>
                  <p className="text-sm text-gray-600">Chuyên gia về bảo mật và an ninh không gian mạng</p>
                </div>
                <div className="p-4 border border-gray-200 rounded-lg hover:border-red-500 transition-colors">
                  <h4 className="font-semibold text-gray-900 mb-2">Luật An ninh</h4>
                  <p className="text-sm text-gray-600">Pháp luật liên quan đến an ninh quốc gia</p>
                </div>
                <div className="p-4 border border-gray-200 rounded-lg hover:border-red-500 transition-colors">
                  <h4 className="font-semibold text-gray-900 mb-2">Quản lý Nhà nước</h4>
                  <p className="text-sm text-gray-600">Quản trị công và quản lý hành chính</p>
                </div>
                <div className="p-4 border border-gray-200 rounded-lg hover:border-red-500 transition-colors">
                  <h4 className="font-semibold text-gray-900 mb-2">Kỹ thuật An ninh</h4>
                  <p className="text-sm text-gray-600">Công nghệ và kỹ thuật phục vụ an ninh</p>
                </div>
                <div className="p-4 border border-gray-200 rounded-lg hover:border-red-500 transition-colors">
                  <h4 className="font-semibold text-gray-900 mb-2">Điều tra An ninh</h4>
                  <p className="text-sm text-gray-600">Nghiệp vụ điều tra và phòng chống tội phạm</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-red-700 mb-4">Phương pháp đào tạo</h2>
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-red-600 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    <span className="font-semibold">Lý thuyết kết hợp thực hành:</span> Chương trình học cân bằng 
                    giữa kiến thức nền tảng và kỹ năng thực tế.
                  </p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-red-600 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    <span className="font-semibold">Thực tập thực chiến:</span> Sinh viên được tham gia thực tập 
                    tại các đơn vị an ninh thực tế.
                  </p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-red-600 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    <span className="font-semibold">Công nghệ hiện đại:</span> Ứng dụng công nghệ thông tin 
                    và các phương pháp giảng dạy tiên tiến.
                  </p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-red-600 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    <span className="font-semibold">Đào tạo theo quốc tế:</span> Liên kết với các trường đại học 
                    uy tín trong và ngoài nước.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-xl font-bold text-red-700 mb-4">Thông tin chung</h3>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <Clock className="w-5 h-5 text-red-600 mt-1" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Thời gian đào tạo</h4>
                    <p className="text-sm text-gray-600">4-5 năm (Đại học)</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Users className="w-5 h-5 text-red-600 mt-1" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Quy mô lớp</h4>
                    <p className="text-sm text-gray-600">30-40 sinh viên/lớp</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <FileText className="w-5 h-5 text-red-600 mt-1" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Chứng chỉ</h4>
                    <p className="text-sm text-gray-600">Bằng cử nhân, Thạc sĩ, Tiến sĩ</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-red-600 to-red-700 text-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-xl font-bold mb-3">Tuyển sinh 2026</h3>
              <p className="text-red-100 text-sm mb-4">
                Thông tin chi tiết về tuyển sinh năm 2026
              </p>
              <a
                href="/tuyen-sinh"
                className="block w-full bg-white text-red-600 text-center font-semibold py-2 px-4 rounded-lg hover:bg-red-50 transition-colors"
              >
                Xem chi tiết
              </a>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-red-700 mb-4">Liên hệ tư vấn</h3>
              <div className="space-y-2 text-sm">
                <p className="text-gray-700">
                  <span className="font-semibold">Hotline:</span> 0283.896.3883
                </p>
                <p className="text-gray-700">
                  <span className="font-semibold">Email:</span> daotao@dhannd.edu.vn
                </p>
                <a
                  href="/chat-bot"
                  className="block mt-4 w-full bg-blue-600 text-white text-center font-semibold py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Chat với AI
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
