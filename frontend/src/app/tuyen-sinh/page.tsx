import Layout from '@/components/Layout';
import { Calendar, AlertCircle } from 'lucide-react';

export default function TuyenSinh() {
  const admissionPrograms = [
    {
      name: "An ninh chính trị",
      code: "7229001",
      quota: 200,
      duration: "4 năm",
      degree: "Cử nhân"
    },
    {
      name: "An ninh kinh tế",
      code: "7229002", 
      quota: 150,
      duration: "4 năm",
      degree: "Cử nhân"
    },
    {
      name: "An ninh mạng",
      code: "7480201",
      quota: 180,
      duration: "4 năm", 
      degree: "Cử nhân"
    },
    {
      name: "Điều tra hình sự",
      code: "7380107",
      quota: 120,
      duration: "4 năm",
      degree: "Cử nhân"
    }
  ];

  const importantDates = [
    {
      event: "Công bố đề án tuyển sinh",
      date: "15/03/2025",
      status: "upcoming"
    },
    {
      event: "Đăng ký xét tuyển",
      date: "15/07 - 30/07/2025",
      status: "upcoming"
    },
    {
      event: "Thi đánh giá năng lực",
      date: "15/08/2025",
      status: "upcoming"
    },
    {
      event: "Công bố kết quả",
      date: "30/08/2025",
      status: "upcoming"
    }
  ];

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg p-8 mb-8">
          <h1 className="text-4xl font-bold mb-4">Tuyển sinh 2025</h1>
          <p className="text-xl text-green-100">
            Thông tin chi tiết về tuyển sinh các ngành đào tạo tại Trường Đại học An ninh Nhân dân
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Admission Programs */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-red-700 mb-4">Các ngành tuyển sinh</h2>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-300 px-4 py-2 text-left">Tên ngành</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Mã ngành</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Chỉ tiêu</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Thời gian</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Bằng cấp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {admissionPrograms.map((program, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="border border-gray-300 px-4 py-2 font-medium">{program.name}</td>
                        <td className="border border-gray-300 px-4 py-2">{program.code}</td>
                        <td className="border border-gray-300 px-4 py-2">{program.quota}</td>
                        <td className="border border-gray-300 px-4 py-2">{program.duration}</td>
                        <td className="border border-gray-300 px-4 py-2">{program.degree}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Admission Requirements */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-red-700 mb-4">Điều kiện xét tuyển</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Điều kiện chung</h3>
                  <ul className="list-disc list-inside text-gray-700 space-y-1">
                    <li>Công dân Việt Nam, có đủ sức khỏe theo quy định</li>
                    <li>Có phẩm chất chính trị, đạo đức tốt</li>
                    <li>Tốt nghiệp THPT hoặc tương đương</li>
                    <li>Tuổi từ 17 đến 21 (tính đến 31/12/2025)</li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Điều kiện riêng</h3>
                  <ul className="list-disc list-inside text-gray-700 space-y-1">
                    <li>Chiều cao nam ≥ 1.65m, nữ ≥ 1.55m</li>
                    <li>Thị lực hai mắt ≥ 8/10</li>
                    <li>Không có tiền sử bệnh tâm thần, truyền nhiễm</li>
                    <li>Lý lịch bản thân và gia đình rõ ràng</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Application Process */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-red-700 mb-4">Quy trình xét tuyển</h2>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Đăng ký xét tuyển</h4>
                    <p className="text-gray-600 text-sm">Nộp hồ sơ trực tuyến hoặc trực tiếp tại trường</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Kiểm tra sức khỏe</h4>
                    <p className="text-gray-600 text-sm">Khám sức khỏe tại bệnh viện quân y</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Thi đánh giá năng lực</h4>
                    <p className="text-gray-600 text-sm">Thi kiến thức cơ bản và năng lực chuyên môn</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center text-sm font-bold">4</div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Xét duyệt hồ sơ</h4>
                    <p className="text-gray-600 text-sm">Kiểm tra lý lịch và phẩm chất chính trị</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Important Dates */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-xl font-bold text-red-700 mb-4 flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                Lịch tuyển sinh
              </h3>
              <div className="space-y-3">
                {importantDates.map((item, index) => (
                  <div key={index} className="border-l-4 border-red-600 pl-3">
                    <h4 className="font-semibold text-gray-900 text-sm">{item.event}</h4>
                    <p className="text-red-600 text-sm font-medium">{item.date}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-xl font-bold text-red-700 mb-4">Thao tác nhanh</h3>
              <div className="space-y-3">
                <button className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
                  Đăng ký xét tuyển
                </button>
                <button className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
                  Tải hồ sơ mẫu
                </button>
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
                  Tra cứu kết quả
                </button>
              </div>
            </div>

            {/* Contact Info */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-bold text-yellow-800 mb-3 flex items-center">
                <AlertCircle className="w-5 h-5 mr-2" />
                Hỗ trợ tuyển sinh
              </h3>
              <div className="space-y-2 text-sm">
                <p><strong>Hotline:</strong> 024.3854.2222</p>
                <p><strong>Email:</strong> tuyensinh@psu.edu.vn</p>
                <p><strong>Địa chỉ:</strong> 125 Trần Phú, Văn Quán, Hà Đông, Hà Nội</p>
                <p><strong>Giờ làm việc:</strong> 7:30-17:00 (T2-T6)</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
