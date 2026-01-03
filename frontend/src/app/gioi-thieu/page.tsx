import Layout from '@/components/Layout';
import { Users, Award, BookOpen, Target } from 'lucide-react';

export default function GioiThieu() {
  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg p-8 mb-8">
          <h1 className="text-4xl font-bold mb-4">Giới thiệu về Trường</h1>
          <p className="text-xl text-red-100">
            Trường Đại học An ninh Nhân dân - Cơ sở đào tạo cán bộ an ninh chất lượng cao
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-red-700 mb-4">Lịch sử hình thành</h2>
              <p className="text-gray-700 mb-4">
                Trường Đại học An ninh Nhân dân được thành lập theo Quyết định số 53/2001/QĐ-TTg 
                ngày 10 tháng 4 năm 2001 của Thủ tướng Chính phủ trên cơ sở nâng cấp Trường Sĩ quan An ninh.
              </p>
              <p className="text-gray-700 mb-4">
                Trường có nhiệm vụ đào tạo cán bộ an ninh các trình độ đại học, thạc sĩ, tiến sĩ; 
                nghiên cứu khoa học; phục vụ cộng đồng trong lĩnh vực an ninh quốc gia.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-red-700 mb-4">Sứ mệnh và Tầm nhìn</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Sứ mệnh</h3>
                  <p className="text-gray-700">
                    Đào tạo nguồn nhân lực chất lượng cao trong lĩnh vực an ninh quốc gia, 
                    đáp ứng yêu cầu bảo vệ Tổ quốc trong tình hình mới.
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Tầm nhìn</h3>
                  <p className="text-gray-700">
                    Trở thành trường đại học hàng đầu trong lĩnh vực đào tạo an ninh, 
                    đạt tiêu chuẩn khu vực và quốc tế.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-red-700 mb-4">Thành tựu nổi bật</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-start space-x-3">
                  <Award className="w-6 h-6 text-yellow-500 mt-1" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Chất lượng đào tạo</h4>
                    <p className="text-gray-600 text-sm">Đạt chuẩn kiểm định chất lượng giáo dục</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <BookOpen className="w-6 h-6 text-blue-500 mt-1" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Nghiên cứu khoa học</h4>
                    <p className="text-gray-600 text-sm">Hàng trăm công trình nghiên cứu được công bố</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Users className="w-6 h-6 text-green-500 mt-1" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Đội ngũ giảng viên</h4>
                    <p className="text-gray-600 text-sm">100% giảng viên có trình độ thạc sĩ trở lên</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Target className="w-6 h-6 text-red-500 mt-1" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Tỷ lệ việc làm</h4>
                    <p className="text-gray-600 text-sm">98% sinh viên có việc làm sau tốt nghiệp</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-xl font-bold text-red-700 mb-4">Thông tin cơ bản</h3>
              <div className="space-y-3">
                <div>
                  <span className="font-semibold text-gray-900">Năm thành lập:</span>
                  <span className="text-gray-700 ml-2">2001</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-900">Địa chỉ:</span>
                  <span className="text-gray-700 ml-2">TP. Hồ Chí Minh</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-900">Số sinh viên:</span>
                  <span className="text-gray-700 ml-2">~15,000</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-900">Số giảng viên:</span>
                  <span className="text-gray-700 ml-2">~800</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-900">Số ngành đào tạo:</span>
                  <span className="text-gray-700 ml-2">25+</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-red-700 mb-4">Liên kết nhanh</h3>
              <div className="space-y-2">
                <a href="/dao-tao" className="block text-blue-600 hover:text-blue-800">
                  → Chương trình đào tạo
                </a>
                <a href="/tuyen-sinh" className="block text-blue-600 hover:text-blue-800">
                  → Thông tin tuyển sinh
                </a>
                <a href="/nghien-cuu" className="block text-blue-600 hover:text-blue-800">
                  → Hoạt động nghiên cứu
                </a>
                <a href="/lien-he" className="block text-blue-600 hover:text-blue-800">
                  → Thông tin liên hệ
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
